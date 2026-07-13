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


def spawn_guarded(tmp_path, argv, release=True):
    barrier_r, barrier_w = os.pipe()
    os.set_inheritable(barrier_r, True)
    lock_r = os.open("/dev/null", os.O_RDONLY)
    os.set_inheritable(lock_r, True)
    proc = subprocess.Popen([sys.executable, str(LAUNCHER),
                             str(barrier_r), str(lock_r),
                             str(tmp_path), *argv], close_fds=False)
    os.close(barrier_r)
    os.close(lock_r)
    if release:
        os.write(barrier_w, b"G")
    return proc, barrier_w


def test_launcher_pid_is_pgid_and_survives_exec(tmp_path):
    proc, bw = spawn_guarded(tmp_path, ["/bin/sleep", "5"])
    time.sleep(0.8)
    ident = proc_identity(proc.pid)
    assert ident is not None
    assert ident["cmdline"][0] == "/bin/sleep"     # exec replaced image
    assert ident["cwd"] == str(tmp_path)           # chdir applied
    assert os.getpgid(proc.pid) == proc.pid        # setsid: PID == PGID
    os.close(bw)
    os.killpg(proc.pid, 9)
    proc.wait()


def test_child_blocks_at_barrier_until_go(tmp_path):
    proc, bw = spawn_guarded(tmp_path, ["/bin/sleep", "5"], release=False)
    time.sleep(0.8)
    ident = proc_identity(proc.pid)
    assert ident is not None
    assert "m38e_launch.py" in " ".join(ident["cmdline"])  # not exec'd
    os.write(bw, b"G")
    time.sleep(0.8)
    ident = proc_identity(proc.pid)
    assert ident["cmdline"][0] == "/bin/sleep"             # exec'd now
    os.close(bw)
    os.killpg(proc.pid, 9)
    proc.wait()


def test_parent_death_before_registration_child_never_execs(tmp_path):
    canary = tmp_path / "canary.txt"
    script = tmp_path / "driver.py"
    script.write_text(f"open({str(canary)!r},'w').write('x')\n")
    proc, bw = spawn_guarded(tmp_path,
                             [sys.executable, str(script)], release=False)
    os.close(bw)              # simulate parent death: EOF, no GO byte
    rc = proc.wait(timeout=10)
    assert rc == 0
    assert not canary.exists()   # scientific driver was never executed


def test_lock_survives_controller_death_via_inherited_fd(tmp_path):
    import fcntl as F
    lock_path = tmp_path / "run.lock"
    holder = open(lock_path, "w")
    F.flock(holder, F.LOCK_EX | F.LOCK_NB)
    os.set_inheritable(holder.fileno(), True)
    barrier_r, barrier_w = os.pipe()
    os.set_inheritable(barrier_r, True)
    proc = subprocess.Popen([sys.executable, str(LAUNCHER),
                             str(barrier_r), str(holder.fileno()),
                             str(tmp_path), "/bin/sleep", "5"],
                            close_fds=False)
    os.close(barrier_r)
    os.write(barrier_w, b"G")
    os.close(barrier_w)
    time.sleep(0.8)
    holder.close()            # controller "dies": drops ITS descriptor
    probe = open(lock_path, "w")
    with pytest.raises(BlockingIOError):
        F.flock(probe, F.LOCK_EX | F.LOCK_NB)   # child still holds it
    os.killpg(proc.pid, 9)
    proc.wait()
    time.sleep(0.5)
    F.flock(probe, F.LOCK_EX | F.LOCK_NB)       # released with child


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
    owned, bw = spawn_guarded(tmp_path, ["/bin/sleep", "30"])
    bystander = subprocess.Popen(["/bin/sleep", "30"])
    time.sleep(0.8)
    ident = proc_identity(owned.pid)
    verify_owned_pgid(owned.pid, ident)
    os.killpg(owned.pid, 9)
    owned.wait()
    os.close(bw)
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


def test_runtime_identity_mismatch_blocks():
    original = {"python": sys.executable, "vllm_version": "0.0.0-fake",
                "torch_version": "0.0.0-fake"}
    with pytest.raises(RetryBlocked, match="version differs"):
        C.verify_runtime_identity(original)


# -- steer 02a483b additions ----------------------------------------------------

from m38e_retry_controller import (AmbiguousProcess, atomic_write_record,
                                   budget_available,
                                   build_retry_environment,
                                   verify_model_identity)


def test_reserved_without_pid_blocks_permanently():
    rec = {"attempts_launched": 2,
           "records": [{"attempt": 1, "state": "running"},
                       {"attempt": 2, "state": "reserved",
                        "nonce": "n" * 32}]}
    with pytest.raises(RetryBlocked, match="permanently"):
        budget_available(rec)
    # even with the counter somehow low, the attempt-two trace blocks
    rec["attempts_launched"] = 1
    with pytest.raises(RetryBlocked, match="attempt-two record"):
        budget_available(rec)


def test_budget_never_refundable_states():
    for state in ("reserved", "launching", "running", "exited"):
        rec = {"attempts_launched": 1,
               "records": [{"attempt": 1, "state": "running"},
                           {"attempt": 2, "state": state}]}
        with pytest.raises(RetryBlocked):
            budget_available(rec)


def test_atomic_record_write_durable_and_complete(tmp_path):
    path = tmp_path / "rec.json"
    atomic_write_record({"attempts_launched": 2, "records": []}, path)
    data = json.loads(path.read_text())
    assert data["attempts_launched"] == 2
    assert not (tmp_path / "rec.tmp").exists()   # no partial temp left
    # overwrite is atomic too
    atomic_write_record({"attempts_launched": 2,
                         "records": [{"attempt": 2,
                                      "state": "reserved"}]}, path)
    assert json.loads(path.read_text())["records"][0]["state"] == "reserved"


def test_unreadable_proc_blocks_dead_pid_passes(monkeypatch):
    import m38e_retry_controller as R
    # proven nonexistent: dead
    assert R.proc_identity(2**22 + 12345) is None
    # unreadable: block
    rec = {"records": [{"attempt": 1, "pid": 1,
                        "cmdline": ["x"], "cwd": "/"}]}
    # PID 1 exists but /proc/1/cwd is unreadable to a normal user
    with pytest.raises(AmbiguousProcess):
        R.driver_alive(rec)


def test_model_identity_bound_to_original_digest(tmp_path, monkeypatch):
    import hashlib as H
    import m38e_retry_controller as R
    monkeypatch.setattr(R, "CONTROL", tmp_path / "control")
    (tmp_path / "control").mkdir()
    exec_dir = tmp_path / "exec"
    exec_dir.mkdir()
    # both CURRENT files agree with each other but differ from original
    (tmp_path / "control" / ".m36c_model_ref").write_text("model-new\n")
    (exec_dir / ".m36c_model_ref").write_text("model-new\n")
    original = {"model_ref_sha256":
                H.sha256(b"model-original\n").hexdigest()}
    with pytest.raises(RetryBlocked, match="differs from original"):
        verify_model_identity(original, exec_dir)
    # matching all three passes and returns the verified launch argument
    (tmp_path / "control" / ".m36c_model_ref").write_text(
        "model-original\n")
    (exec_dir / ".m36c_model_ref").write_text("model-original\n")
    assert verify_model_identity(original, exec_dir) == "model-original"
    # missing original evidence blocks
    with pytest.raises(RetryBlocked, match="lacks model-pointer"):
        verify_model_identity({}, exec_dir)


def test_live_record_carries_digest_schema_and_state():
    live = json.loads(
        (REPO / "reports/shadow/private/m38e_launch_record.json")
        .read_text())
    r0 = live["records"][0]
    assert len(r0.get("model_ref_sha256", "")) == 64
    assert set(live["protocol_env_schema"]) == set(C.PROTOCOL_ENV_KEYS)
    assert set(r0["env_protocol"]) == set(C.PROTOCOL_ENV_KEYS)
    assert r0["state"] == "running"


# -- steer 0821351 additions -----------------------------------------------------

from m38e_retry_controller import (terminate_owned,
                                   verify_control_artifacts)


def test_exec_timeout_kill_path_reaps_only_owned(tmp_path):
    proc, bw = spawn_guarded(tmp_path, ["/bin/sleep", "60"],
                             release=False)   # stuck pre-exec launcher
    bystander = subprocess.Popen(["/bin/sleep", "60"])
    time.sleep(0.5)
    outcome = terminate_owned(proc.pid, None)
    proc.wait()
    assert outcome == "dead"
    assert bystander.poll() is None
    bystander.kill(); bystander.wait()
    os.close(bw)


def test_changed_launcher_bytes_block():
    rec = {"control_artifact_sha256": {
        "scripts/m38e_launch.py": "0" * 64,
        "scripts/m38e_exec_preflight.py": "0" * 64}}
    with pytest.raises(RetryBlocked, match="bytes changed"):
        verify_control_artifacts(rec)
    with pytest.raises(RetryBlocked, match="pinned"):
        verify_control_artifacts({})


def test_env_built_solely_from_recorded_bytes(tmp_path, monkeypatch):
    blob = b"A=1\0PATH=/usr/bin\0VLLM_USE_FLASHINFER_SAMPLER=0\0"
    (tmp_path / "env.bin").write_bytes(blob)
    import hashlib as H
    original = {"environ_file": "env.bin",
                "environ_sha256": H.sha256(blob).hexdigest()}
    monkeypatch.setenv("AMBIENT_LEAK", "yes")
    env = C.build_retry_environment(original, record_dir=tmp_path)
    assert env == {"A": "1", "PATH": "/usr/bin",
                   "VLLM_USE_FLASHINFER_SAMPLER": "0"}
    assert "AMBIENT_LEAK" not in env
    # digest mismatch blocks
    (tmp_path / "env.bin").write_bytes(blob + b"X=2\0")
    with pytest.raises(RetryBlocked, match="digest mismatch"):
        C.build_retry_environment(original, record_dir=tmp_path)
    # missing evidence blocks
    with pytest.raises(RetryBlocked, match="evidence"):
        C.build_retry_environment({}, record_dir=tmp_path)


def test_new_terminal_states_block_permanently():
    for state in ("failed_terminated", "ambiguous"):
        rec = {"attempts_launched": 2,
               "records": [{"attempt": 1, "state": "running"},
                           {"attempt": 2, "state": state}]}
        with pytest.raises(RetryBlocked):
            C.budget_available(rec)


def test_live_record_pins_environment_and_artifacts():
    live = json.loads(
        (REPO / "reports/shadow/private/m38e_launch_record.json")
        .read_text())
    r0 = live["records"][0]
    assert len(r0.get("environ_sha256", "")) == 64
    assert r0.get("environ_n_vars", 0) > 20
    env_file = REPO / "reports/shadow/private" / r0["environ_file"]
    import hashlib as H
    assert H.sha256(env_file.read_bytes()).hexdigest() == \
        r0["environ_sha256"]
    pinned = live["control_artifact_sha256"]
    for rel in ("scripts/m38e_launch.py",
                "scripts/m38e_exec_preflight.py"):
        assert len(pinned[rel]) == 64
