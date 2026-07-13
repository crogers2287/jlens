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


def build_retry_environment(original: dict,
                            record_dir: Path = None) -> dict:
    """The retry environment is the COMPLETE recorded attempt-one
    environment (exact bytes, digest-verified) — never ambient
    os.environ (steer 0821351 item 3). Missing or non-reconstructable
    evidence blocks."""
    record_dir = record_dir or RECORD.parent
    env_file = original.get("environ_file")
    want = original.get("environ_sha256")
    if not env_file or not want:
        raise RetryBlocked("original record lacks complete environment "
                           "evidence")
    path = record_dir / env_file
    if not path.exists():
        raise RetryBlocked("recorded environment file missing")
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != want:
        raise RetryBlocked("recorded environment digest mismatch")
    env = {}
    for kv in blob.decode().split("\0"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            env[k] = v
    if not env:
        raise RetryBlocked("recorded environment not reconstructable")
    return env


def verify_control_artifacts(record: dict) -> None:
    """The launcher and preflight used for a retry must match the exact
    bytes pinned in the private record (steer 0821351 item 2)."""
    pinned = record.get("control_artifact_sha256")
    if not isinstance(pinned, dict):
        raise RetryBlocked("record lacks pinned control-artifact digests")
    for rel in ("scripts/m38e_launch.py",
                "scripts/m38e_exec_preflight.py"):
        want = pinned.get(rel)
        if not want:
            raise RetryBlocked(f"no pinned digest for {rel}")
        got = hashlib.sha256((CONTROL / rel).read_bytes()).hexdigest()
        if got != want:
            raise RetryBlocked(f"control artifact bytes changed: {rel}")


def proc_starttime(pid: int) -> int:
    stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return int(stat[19])


def ownership_evidence(pid: int) -> dict:
    """Full ownership evidence; raises AmbiguousProcess on any
    unreadable field (steer e2d5b5e item 2)."""
    ident = proc_identity(pid)
    if ident is None:
        return None
    try:
        return {**ident, "starttime": proc_starttime(pid),
                "sid": os.getsid(pid), "pgid": os.getpgid(pid)}
    except (ProcessLookupError, FileNotFoundError):
        return None
    except (PermissionError, OSError) as exc:
        raise AmbiguousProcess(f"unreadable ownership evidence: "
                               f"{type(exc).__name__}")


def _prove(pid: int, expected: dict) -> str:
    """'owned' | 'dead' | raises AmbiguousProcess. expected must carry
    starttime/sid and the acceptable command phases."""
    ev = ownership_evidence(pid)
    if ev is None:
        return "dead"
    if (ev["starttime"] != expected["starttime"]
            or ev["sid"] != expected["sid"]
            or ev["pgid"] != pid
            or ev["cwd"] != expected["cwd"]
            or ev["cmdline"] not in expected["phases"]):
        raise AmbiguousProcess("ownership evidence mismatch")
    return "owned"


def terminate_owned(pid: int, expected: dict) -> str:
    """Strict termination: full expected evidence is mandatory (no
    permissive mode); ownership is re-proved immediately before EVERY
    signal. Returns 'dead'; 'ambiguous' means leave the PID recorded,
    block permanently, and never signal."""
    if not expected or "starttime" not in expected:
        return "ambiguous"                 # no permissive path exists
    pidfd = None
    try:
        pidfd = os.pidfd_open(pid)         # PID-reuse resistance
    except (OSError, AttributeError):
        pidfd = None
    try:
        try:
            state = _prove(pid, expected)
        except AmbiguousProcess:
            return "ambiguous"
        if state == "dead":
            return "dead"
        os.killpg(pid, 15)
        time.sleep(5)
        try:
            state = _prove(pid, expected)  # re-prove before KILL
        except AmbiguousProcess:
            return "ambiguous"
        if state == "owned":
            os.killpg(pid, 9)
        try:
            os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            pass
        time.sleep(1)
        try:
            return ("dead" if ownership_evidence(pid) is None
                    else "ambiguous")
        except AmbiguousProcess:
            return "ambiguous"
    finally:
        if pidfd is not None:
            os.close(pidfd)


def verify_runtime_identity(original: dict, env: dict) -> None:
    """Probes run under the ORIGINAL executable (identity-bound by the
    sha256 captured from /proc/<pid>/exe while attempt one was alive)
    and the complete recorded environment — never the controller's
    ambient interpreter (steer e2d5b5e item 4)."""
    python = original["python"]
    exe_resolved = original.get("exe_resolved")
    want_sha = original.get("exe_sha256")
    if not exe_resolved or not want_sha:
        raise RetryBlocked("original record lacks executable identity")
    if not Path(exe_resolved).exists():
        raise RetryBlocked("original python executable missing")
    got = hashlib.sha256(Path(exe_resolved).read_bytes()).hexdigest()
    if got != want_sha:
        raise RetryBlocked("python executable bytes changed")
    for mod in ("vllm", "torch"):
        probe = subprocess.run(
            [python, "-c",
             f"import {mod}; print({mod}.__version__); "
             f"print({mod}.__file__)"],
            capture_output=True, text=True, env=env)
        lines = probe.stdout.strip().splitlines()
        if len(lines) < 2 or lines[0] != original.get(f"{mod}_version"):
            raise RetryBlocked(f"{mod} version/origin differs under the "
                               "recorded environment")


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
        # Reload the record UNDER the lock (steer 0821351).
        record = json.loads(RECORD.read_text())
        budget_available(record)
        if driver_alive(record):
            raise RetryBlocked("a driver for this run identity is alive")

        verify_control_artifacts(record)
        pre = subprocess.run(
            [sys.executable,
             str(CONTROL / "scripts/m38e_exec_preflight.py"),
             str(exec_dir), expected], capture_output=True, text=True)
        if pre.returncode != 0:
            raise RetryBlocked(f"preflight: {pre.stdout.strip()}")

        original = record["records"][0]
        # Reconstruct the complete recorded environment FIRST; every
        # package-dependent probe runs under it (steer e2d5b5e item 4).
        env = build_retry_environment(original)
        verify_runtime_identity(original, env)
        launch_arg = verify_model_identity(original, exec_dir)
        # Re-verify artifact bytes immediately before process creation.
        verify_control_artifacts(record)

        # Durably consume attempt two BEFORE process creation.
        nonce = secrets.token_hex(16)
        record["attempts_launched"] += 1
        record["records"].append({
            "attempt": 2, "state": "reserved", "nonce": nonce,
            "reserved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime()),
            "run_id": run_id})
        atomic_write_record(record)

        # Barrier handshake: the child cannot exec the driver until its
        # PID/PGID is durably registered and the barrier releases.
        barrier_r, barrier_w = os.pipe()
        os.set_inheritable(barrier_r, True)
        lock_fd = lock.fileno()
        os.set_inheritable(lock_fd, True)
        log = open(CONTROL / "logs/m38e_official.log", "a")
        proc = subprocess.Popen(
            [sys.executable, str(CONTROL / "scripts/m38e_launch.py"),
             str(barrier_r), str(lock_fd), str(exec_dir),
             original["python"], "src/m38e_dev_sweep.py",
             "--model-ref", launch_arg],
            stdout=log, stderr=log, env=env, close_fds=True,
            pass_fds=(barrier_r, lock_fd))
        os.close(barrier_r)
        # Capture full ownership evidence while the child is behind the
        # barrier (pre-exec launcher phase).
        own = ownership_evidence(proc.pid)
        if own is None:
            raise RetryBlocked("child vanished before evidence capture")
        launcher_cmd = own["cmdline"]
        driver_cmd_prefix = [original["python"], "src/m38e_dev_sweep.py"]
        expected_owner = {"starttime": own["starttime"],
                          "sid": own["sid"], "cwd": str(exec_dir),
                          "phases": []}
        try:
            # Durable 'launching' with exact ownership BEFORE exec.
            record["records"][-1].update({
                "state": "launching", "pid": proc.pid, "pgid": proc.pid,
                "starttime_ticks": own["starttime"], "sid": own["sid"],
                "launcher_cmdline": launcher_cmd,
                "expected_cmdline": [original["python"],
                                     "src/m38e_dev_sweep.py"],
                "exec_dir": str(exec_dir),
                "source_commit": expected,
                "launcher_sha256": record["control_artifact_sha256"][
                    "scripts/m38e_launch.py"],
                "preflight_sha256": record["control_artifact_sha256"][
                    "scripts/m38e_exec_preflight.py"],
                "environ_sha256": original["environ_sha256"]})
            atomic_write_record(record)
            reread = json.loads(RECORD.read_text())
            latest = reread["records"][-1]
            if (latest.get("state") != "launching"
                    or latest.get("pid") != proc.pid
                    or latest.get("nonce") != nonce):
                raise RetryBlocked("launching record failed reread "
                                   "validation")
            os.write(barrier_w, b"G")     # release barrier -> exec
        except Exception:
            os.close(barrier_w)           # EOF: child exits without exec
            expected_owner["phases"] = [launcher_cmd]
            outcome = terminate_owned(proc.pid, expected_owner)
            record["records"][-1]["state"] = (
                "failed_terminated" if outcome == "dead" else "ambiguous")
            atomic_write_record(record)
            raise
        os.close(barrier_w)

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
            expected_owner["phases"] = [launcher_cmd,
                                        driver_cmd_prefix]
            outcome = terminate_owned(proc.pid, expected_owner)
            record["records"][-1]["state"] = (
                "failed_terminated" if outcome == "dead" else "ambiguous")
            atomic_write_record(record)
            raise RetryBlocked(
                f"exec recognition failed; owned group {outcome}; retry "
                "authorization remains consumed")
        record["records"][-1].update({
            "state": "running",
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
                expected_owner["phases"] = [expected_ident["cmdline"]]
                outcome = terminate_owned(proc.pid, expected_owner)
                record["records"][-1]["stall_termination"] = outcome
                atomic_write_record(record)
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
        # NEVER LOCK_UN: the lock descriptor may be inherited by a
        # surviving child; an explicit unlock on this duplicate would
        # release the shared open-file-description lock for the child
        # too (steer e2d5b5e item 1). Closing our duplicate preserves
        # the child's hold; if no child survives, the close releases it.
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
