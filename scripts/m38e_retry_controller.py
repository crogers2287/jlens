#!/usr/bin/env python3
"""M38E one-retry controller (steers 3f422ad + 02a483b). Control-plane
only; crash-consistent and identity-exact.

Retry authorization is durably consumed BEFORE any process creation:
the private launch record is atomically replaced (temp file +
os.replace + fsync of file and parent directory) with attempt two in
state ``reserved`` carrying a unique private nonce. A crash after that
point may waste the retry; it can never refund it — any record showing
attempt two as reserved/launching/running/exited blocks every later
launch, including a ``reserved`` entry with no PID. After the
setsid/exec identity proof, the same record is atomically updated to
``running`` with the exact owned PID/PGID.

Identity exactness: the model pointer is verified against the DIGEST
captured in the original launch record (control pointer, execution
pointer, and the actual launch argument must all match it — two
current files agreeing is insufficient). The protocol environment is
rebuilt from the frozen key schema: recorded values set exactly,
recorded absences explicitly removed; missing schema evidence blocks.
Unreadable or partial /proc evidence for a recorded PID BLOCKS (only a
proven-nonexistent process is dead).

Aggregate-only public output; PIDs, paths, env values, and pointers
stay in the private record.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

CONTROL = Path(__file__).resolve().parent.parent
RECORD = CONTROL / "reports/shadow/private/m38e_launch_record.json"
STALL_SECONDS = 1200
MAX_TOTAL_ATTEMPTS = 2
PROTOCOL_ENV_KEYS = ("VLLM_USE_FLASHINFER_SAMPLER", "PYTHONPATH",
                     "CUDA_VISIBLE_DEVICES",
                     "VLLM_WORKER_MULTIPROC_METHOD",
                     "PYTORCH_CUDA_ALLOC_CONF")


class RetryBlocked(Exception):
    pass


class AmbiguousProcess(RetryBlocked):
    pass


# -- durable record I/O -----------------------------------------------------

def atomic_write_record(record: dict, path: Path = None) -> None:
    path = path or RECORD
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(record, f, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dirfd = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)


# -- process identity ---------------------------------------------------------

def proc_identity(pid: int) -> dict | None:
    """dict when fully readable; None when PROVEN nonexistent; raises
    AmbiguousProcess on unreadable/partial evidence (02a483b item 3)."""
    proc = Path(f"/proc/{pid}")
    if not proc.exists():
        return None
    try:
        cmdline = (proc / "cmdline").read_bytes().decode().split("\0")[:-1]
        cwd = os.readlink(proc / "cwd")
    except (FileNotFoundError, ProcessLookupError):
        return None                        # vanished while reading: dead
    except (PermissionError, OSError) as exc:
        raise AmbiguousProcess(
            f"unreadable /proc evidence for recorded pid: "
            f"{type(exc).__name__}")
    if not cmdline:
        raise AmbiguousProcess("partial /proc evidence (empty cmdline)")
    return {"cmdline": cmdline, "cwd": cwd}


def driver_alive(record: dict) -> bool:
    """True when any recorded attempt is provably alive; AmbiguousProcess
    propagates and blocks."""
    for rec in record["records"]:
        if "pid" not in rec:
            continue
        ident = proc_identity(rec["pid"])
        if ident is None:
            continue
        if (ident["cmdline"] == rec["cmdline"]
                and ident["cwd"] == rec["cwd"]):
            return True
    return False


def verify_owned_pgid(pid: int, expected: dict) -> None:
    ident = proc_identity(pid)
    if ident is None:
        raise RetryBlocked("owned process vanished before signal")
    if ident["cmdline"] != expected["cmdline"] \
            or ident["cwd"] != expected["cwd"]:
        raise RetryBlocked("owned PID identity changed — refusing signal")
    if os.getpgid(pid) != pid:
        raise RetryBlocked("owned PID is not its own process group")


# -- identity verification -----------------------------------------------------

def verify_model_identity(original: dict, exec_dir: Path) -> str:
    """All three values — control pointer, execution pointer, and the
    launch argument — must match the ORIGINAL recorded digest."""
    want = original.get("model_ref_sha256")
    if not want:
        raise RetryBlocked("original record lacks model-pointer digest")
    control_ptr = (CONTROL / ".m36c_model_ref").read_bytes()
    exec_ptr = (exec_dir / ".m36c_model_ref").read_bytes()
    for name, blob in (("control", control_ptr), ("execution", exec_ptr)):
        if hashlib.sha256(blob).hexdigest() != want:
            raise RetryBlocked(
                f"{name} model pointer differs from original record")
    return exec_ptr.decode().strip()       # verified launch argument


def build_retry_environment(original: dict) -> dict:
    """Clean env from the frozen schema: recorded values set exactly,
    recorded absences removed; missing schema evidence blocks."""
    recorded = original.get("env_protocol")
    if not isinstance(recorded, dict):
        raise RetryBlocked("original record lacks protocol environment")
    for key in PROTOCOL_ENV_KEYS:
        if key not in recorded:
            raise RetryBlocked(f"protocol schema key missing from "
                               f"original record: {key}")
    env = dict(os.environ)
    for key in PROTOCOL_ENV_KEYS:
        value = recorded[key]
        if value is None:
            env.pop(key, None)             # recorded absent: remove
        else:
            env[key] = value               # recorded value: set exactly
    return env


def verify_runtime_identity(original: dict) -> None:
    python = original["python"]
    if not Path(python).exists():
        raise RetryBlocked("original python executable missing")
    for mod in ("vllm", "torch"):
        v = subprocess.run([python, "-c",
                            f"import {mod}; print({mod}.__version__)"],
                           capture_output=True, text=True).stdout.strip()
        if v != original.get(f"{mod}_version"):
            raise RetryBlocked(f"{mod} version differs from launch record")


def budget_available(record: dict) -> None:
    """Any attempt-two trace (reserved/launching/running/exited/counted)
    blocks permanently; a reserved entry without a PID also blocks."""
    if record["attempts_launched"] >= MAX_TOTAL_ATTEMPTS:
        raise RetryBlocked(
            "retry budget consumed — blocked permanently for this run")
    for rec in record["records"]:
        if rec.get("attempt", 0) >= 2:
            raise RetryBlocked(
                f"attempt-two record exists in state "
                f"'{rec.get('state', 'unknown')}' — blocked permanently")


# -- main ---------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: m38e_retry_controller.py <exec_dir> "
                         "<expected_sha>")
    exec_dir, expected = Path(sys.argv[1]), sys.argv[2]

    record = json.loads(RECORD.read_text())
    run_id = record["records"][0]["run_id"]
    lock_path = CONTROL / f"reports/shadow/private/m38e_{run_id}.lock"
    lock = open(lock_path, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("[m38e-retry] BLOCK: run lock held by another controller",
              flush=True)
        return 3

    try:
        budget_available(record)
        if driver_alive(record):
            raise RetryBlocked("a driver for this run identity is alive")

        pre = subprocess.run(
            [sys.executable,
             str(CONTROL / "scripts/m38e_exec_preflight.py"),
             str(exec_dir), expected], capture_output=True, text=True)
        if pre.returncode != 0:
            raise RetryBlocked(f"preflight: {pre.stdout.strip()}")

        original = record["records"][0]
        verify_runtime_identity(original)
        launch_arg = verify_model_identity(original, exec_dir)
        env = build_retry_environment(original)

        # Durably consume attempt two BEFORE process creation.
        nonce = secrets.token_hex(16)
        record["attempts_launched"] += 1
        record["records"].append({
            "attempt": 2, "state": "reserved", "nonce": nonce,
            "reserved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime()),
            "run_id": run_id})
        atomic_write_record(record)

        log = open(CONTROL / "logs/m38e_official.log", "a")
        proc = subprocess.Popen(
            [sys.executable, str(CONTROL / "scripts/m38e_launch.py"),
             str(exec_dir), original["python"], "src/m38e_dev_sweep.py",
             "--model-ref", launch_arg],
            stdout=log, stderr=log, env=env)
        expected_ident = None
        for _ in range(50):
            time.sleep(0.2)
            try:
                ident = proc_identity(proc.pid)
            except AmbiguousProcess:
                continue
            if ident and ident["cmdline"][:2] == [original["python"],
                                                  "src/m38e_dev_sweep.py"]:
                expected_ident = ident
                break
        if expected_ident is None:
            # Budget stays consumed; record remains 'reserved' (blocks
            # forever) — never refunded.
            raise RetryBlocked("launcher did not exec into the driver; "
                               "retry authorization remains consumed")
        record["records"][-1].update({
            "state": "running", "pid": proc.pid, "pgid": proc.pid,
            "cmdline": expected_ident["cmdline"],
            "cwd": expected_ident["cwd"],
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                         time.gmtime())})
        atomic_write_record(record)
        print("[m38e-retry] attempt 2 running (owned pgid recorded "
              "privately)", flush=True)

        rows = exec_dir / "reports/shadow/private/m38e_dev_rows.jsonl"
        logf = CONTROL / "logs/m38e_official.log"
        while proc.poll() is None:
            time.sleep(60)
            ages = [time.time() - p.stat().st_mtime
                    for p in (rows, logf) if p.exists()]
            if ages and min(ages) > STALL_SECONDS:
                verify_owned_pgid(proc.pid, expected_ident)
                os.killpg(proc.pid, 15)
                time.sleep(30)
                try:
                    verify_owned_pgid(proc.pid, expected_ident)
                    os.killpg(proc.pid, 9)
                except RetryBlocked:
                    pass
                break
        rc = proc.wait()
        record["records"][-1].update({"state": "exited", "rc": rc})
        atomic_write_record(record)
        print(f"[m38e-retry] attempt 2 exit rc={rc}", flush=True)
        return 0 if rc == 0 else 1
    except RetryBlocked as exc:
        print(f"[m38e-retry] BLOCK: {exc}", flush=True)
        return 3
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
