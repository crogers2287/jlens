#!/usr/bin/env python3
"""M38E one-retry controller (steer 3f422ad). Control-plane only.

Authorized to launch AT MOST one retry of the official run, and only
when every condition holds:

  - an exclusive nonblocking flock keyed to the row-bound run id is
    acquired before preflight and held for the retry's lifetime;
  - the persisted private attempt record proves the original launch
    consumed attempt one and no more than one additional launch has
    ever been permitted (a second retry request blocks permanently);
  - no driver for this run identity is alive (the recorded PID is
    checked by exact cmdline + cwd; ambiguity blocks);
  - immutable-source + exact-ledger preflight passes after the lock;
  - the runtime identity (python executable, vllm/torch versions,
    protocol environment variables, model pointer bytes, execution
    directory) matches the original private launch record exactly;
  - the driver is launched through scripts/m38e_launch.py (chdir +
    setsid + exec) so the recorded PID IS the owned PGID; stall
    signals go only to that PGID after re-proving its cmdline and cwd.

Aggregate-only public output; PIDs, paths, and environment values stay
in the private operational record.
"""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path

CONTROL = Path(__file__).resolve().parent.parent
RECORD = CONTROL / "reports/shadow/private/m38e_launch_record.json"
STALL_SECONDS = 1200
MAX_TOTAL_ATTEMPTS = 2


class RetryBlocked(Exception):
    pass


def proc_identity(pid: int) -> dict | None:
    try:
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes() \
            .decode().split("\0")[:-1]
        cwd = os.readlink(f"/proc/{pid}/cwd")
        return {"cmdline": cmdline, "cwd": cwd}
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None


def driver_alive(record: dict) -> bool:
    """True only when the recorded PID is alive AND provably the same
    driver (cmdline tail + cwd). PID-reuse mismatch counts as dead;
    partial evidence (readable proc but unreadable fields) blocks."""
    for rec in record["records"]:
        ident = proc_identity(rec["pid"])
        if ident is None:
            continue
        same = (ident["cmdline"] == rec["cmdline"]
                and ident["cwd"] == rec["cwd"])
        if same:
            return True
        # Alive PID with different identity = reused PID = that attempt
        # is dead; continue checking others.
    return False


def verify_owned_pgid(pid: int, expected: dict) -> None:
    """Re-prove the PGID we are about to signal is our exact driver."""
    ident = proc_identity(pid)
    if ident is None:
        raise RetryBlocked("owned process vanished before signal")
    if ident["cmdline"] != expected["cmdline"] \
            or ident["cwd"] != expected["cwd"]:
        raise RetryBlocked("owned PID identity changed — refusing signal")
    if os.getpgid(pid) != pid:
        raise RetryBlocked("owned PID is not its own process group")


def verify_runtime_identity(original: dict, exec_dir: Path) -> None:
    python = original["python"]
    if not Path(python).exists():
        raise RetryBlocked("original python executable missing")
    for mod in ("vllm", "torch"):
        v = subprocess.run([python, "-c",
                            f"import {mod}; print({mod}.__version__)"],
                           capture_output=True, text=True).stdout.strip()
        if v != original.get(f"{mod}_version"):
            raise RetryBlocked(f"{mod} version differs from launch record")
    for key, want in original["env_protocol"].items():
        if os.environ.get(key, want) != want and want is not None:
            raise RetryBlocked(f"protocol env var {key} differs")
    control_ptr = (CONTROL / ".m36c_model_ref").read_bytes()
    exec_ptr = (exec_dir / ".m36c_model_ref").read_bytes()
    if control_ptr != exec_ptr:
        raise RetryBlocked("model pointer differs between checkouts")


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
        if record["attempts_launched"] >= MAX_TOTAL_ATTEMPTS:
            raise RetryBlocked(
                "retry budget consumed — blocked permanently for this run")
        if driver_alive(record):
            raise RetryBlocked("a driver for this run identity is alive")

        pre = subprocess.run(
            [sys.executable, str(CONTROL / "scripts/m38e_exec_preflight.py"),
             str(exec_dir), expected], capture_output=True, text=True)
        if pre.returncode != 0:
            raise RetryBlocked(f"preflight: {pre.stdout.strip()}")

        original = record["records"][0]
        verify_runtime_identity(original, exec_dir)

        env = dict(os.environ)
        env.update({k: v for k, v in original["env_protocol"].items()
                    if v is not None})
        log = open(CONTROL / "logs/m38e_official.log", "a")
        proc = subprocess.Popen(
            [sys.executable, str(CONTROL / "scripts/m38e_launch.py"),
             str(exec_dir), original["python"], "src/m38e_dev_sweep.py",
             "--model-ref",
             (exec_dir / ".m36c_model_ref").read_text().strip()],
            stdout=log, stderr=log, env=env)
        expected_ident = None
        for _ in range(50):                    # wait for exec to settle
            time.sleep(0.2)
            ident = proc_identity(proc.pid)
            if ident and ident["cmdline"][:2] == [original["python"],
                                                  "src/m38e_dev_sweep.py"]:
                expected_ident = ident
                break
        if expected_ident is None:
            raise RetryBlocked("launcher did not exec into the driver")
        record["attempts_launched"] += 1
        record["records"].append({**original, "attempt": 2,
                                  "pid": proc.pid, "pgid": proc.pid,
                                  "cmdline": expected_ident["cmdline"],
                                  "cwd": expected_ident["cwd"],
                                  "started_utc": time.strftime(
                                      "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        RECORD.write_text(json.dumps(record, indent=1))
        print(f"[m38e-retry] attempt 2 launched (owned pgid recorded "
              f"privately)", flush=True)

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
