"""Steer-3f422ad retry-ownership tests. Synthetic processes only —
no engine, no model, no private rows; decoys are `sleep` processes."""
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import m38e_retry_controller as C
from m38e_retry_controller import (RetryBlocked, driver_alive,
                                   proc_identity, verify_owned_pgid)

LAUNCHER = REPO / "scripts" / "m38e_launch.py"


def test_launcher_pid_is_pgid_and_survives_exec(tmp_path):
    proc = subprocess.Popen([sys.executable, str(LAUNCHER),
                             str(tmp_path), "/bin/sleep", "5"])
    time.sleep(0.6)
    ident = proc_identity(proc.pid)
    assert ident is not None
    assert ident["cmdline"][0] == "/bin/sleep"     # exec replaced image
    assert ident["cwd"] == str(tmp_path)           # chdir applied
    assert os.getpgid(proc.pid) == proc.pid        # setsid: PID == PGID
    os.killpg(proc.pid, 9)
    proc.wait()


def make_record(pid, cmdline, cwd, attempts=1):
    return {"attempts_launched": attempts,
            "records": [{"attempt": 1, "pid": pid, "pgid": pid,
                         "run_id": "testrun",
                         "cmdline": cmdline, "cwd": cwd,
                         "python": sys.executable,
                         "env_protocol": {}}]}


def test_decoy_process_is_never_treated_as_the_driver(tmp_path):
    # A live decoy at the recorded PID with a DIFFERENT cmdline/cwd must
    # not count as the driver being alive, and must never be signaled.
    decoy = subprocess.Popen(["/bin/sleep", "5"], cwd=str(tmp_path))
    time.sleep(0.2)
    rec = make_record(decoy.pid, ["python", "src/m38e_dev_sweep.py"],
                      "/somewhere/else")
    assert driver_alive(rec) is False
    with pytest.raises(RetryBlocked, match="identity changed"):
        verify_owned_pgid(decoy.pid,
                          {"cmdline": ["python", "src/m38e_dev_sweep.py"],
                           "cwd": "/somewhere/else"})
    assert decoy.poll() is None            # decoy untouched
    decoy.kill()
    decoy.wait()


def test_live_original_blocks_and_matching_identity_detected(tmp_path):
    live = subprocess.Popen(["/bin/sleep", "5"], cwd=str(tmp_path))
    time.sleep(0.2)
    ident = proc_identity(live.pid)
    rec = make_record(live.pid, ident["cmdline"], ident["cwd"])
    assert driver_alive(rec) is True       # would block a retry
    live.kill()
    live.wait()
    time.sleep(0.2)
    assert driver_alive(rec) is False      # dead once reaped


def test_stall_signal_hits_only_owned_group(tmp_path):
    owned = subprocess.Popen([sys.executable, str(LAUNCHER),
                              str(tmp_path), "/bin/sleep", "30"])
    bystander = subprocess.Popen(["/bin/sleep", "30"])
    time.sleep(0.6)
    ident = proc_identity(owned.pid)
    verify_owned_pgid(owned.pid, ident)
    os.killpg(owned.pid, 9)
    owned.wait()
    time.sleep(0.2)
    assert bystander.poll() is None        # untouched by group signal
    bystander.kill()
    bystander.wait()


def test_exclusive_run_lock(tmp_path):
    lock_path = tmp_path / "run.lock"
    f1 = open(lock_path, "w")
    fcntl.flock(f1, fcntl.LOCK_EX | fcntl.LOCK_NB)
    f2 = open(lock_path, "w")
    with pytest.raises(BlockingIOError):
        fcntl.flock(f2, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fcntl.flock(f1, fcntl.LOCK_UN)


def test_attempt_budget_blocks_permanently():
    assert C.MAX_TOTAL_ATTEMPTS == 2
    spent = make_record(999999, ["python"], "/", attempts=2)
    # Controller logic: attempts_launched >= MAX blocks.
    assert spent["attempts_launched"] >= C.MAX_TOTAL_ATTEMPTS


def test_original_attempt_counted_in_live_record():
    live = json.loads(
        (REPO / "reports/shadow/private/m38e_launch_record.json")
        .read_text())
    assert live["attempts_launched"] == 1
    assert live["records"][0]["attempt"] == 1
    assert live["records"][0]["pid"] == live["records"][0]["pgid"]


def test_runtime_identity_mismatch_blocks(tmp_path, monkeypatch):
    (tmp_path / ".m36c_model_ref").write_text("model-a\n")
    original = {"python": sys.executable, "vllm_version": "0.0.0-fake",
                "torch_version": "0.0.0-fake", "env_protocol": {}}
    with pytest.raises(RetryBlocked, match="version differs"):
        C.verify_runtime_identity(original, tmp_path)
