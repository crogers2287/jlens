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
    """Fail-closed liveness (steer 32d5918 item 4): proven nonexistence
    or a DIFFERENT start time (PID reuse) means the recorded process is
    dead; the same start time with ANY identity mismatch, unreadable
    evidence, or missing recorded fields raises AmbiguousProcess."""
    for rec in record["records"]:
        if "pid" not in rec:
            continue
        for field in ("cmdline", "cwd", "starttime_ticks", "sid"):
            if field not in rec:
                raise AmbiguousProcess(
                    f"recorded attempt lacks identity field {field}")
        ident = proc_identity(rec["pid"])
        if ident is None:
            continue                       # proven nonexistent: dead
        current_start = proc_starttime(rec["pid"])
        if current_start != rec["starttime_ticks"]:
            continue                       # PID reuse: recorded is dead
        # Same start time -> the recorded process. Full identity must
        # match exactly or it is ambiguous (steer 4cb5caa item 3).
        pid = rec["pid"]
        try:
            cur_sid = os.getsid(pid)
            cur_pgid = os.getpgid(pid)
            cur_exe = os.path.realpath(f"/proc/{pid}/exe")
        except (ProcessLookupError, PermissionError, OSError) as exc:
            raise AmbiguousProcess(f"unreadable liveness field: "
                                   f"{type(exc).__name__}")
        want_exe = (rec.get("exe_identity") or {}).get("canonical")
        mism = (ident["cmdline"] != rec["cmdline"]
                or ident["cwd"] != rec["cwd"]
                or cur_sid != rec["sid"]
                or (rec.get("pgid") is not None
                    and cur_pgid != rec["pgid"])
                or (want_exe is not None and cur_exe != want_exe))
        if mism:
            raise AmbiguousProcess(
                "same start time with full-identity mismatch — blocked")
        return True                        # exact full identity: alive
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
                "scripts/m38e_exec_preflight.py",
                "scripts/m38e_untracked_audit.py"):
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


def _session_descendants(sid: int, leader_start: int) -> list[int]:
    """PIDs in the recorded session, each individually provable."""
    out = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            if os.getsid(pid) == sid and proc_starttime(pid) >= leader_start:
                out.append(pid)
        except (ProcessLookupError, FileNotFoundError, PermissionError,
                OSError):
            continue
    return out


def terminate_owned(pid: int, expected: dict,
                    pidfd: int | None = None) -> str:
    """pidfd-enforced termination (steer 32d5918 item 6): the leader is
    signaled through its pidfd (immune to PID reuse); descendants in the
    recorded session are each signaled only through their own freshly
    opened pidfd after per-process proof. Platforms without pidfd fail
    closed ('ambiguous', no automatic termination). Ownership is
    re-proved immediately before every signal; ambiguity never
    signals."""
    import signal as _signal

    if not expected or "starttime" not in expected:
        return "ambiguous"                 # no permissive path exists
    if not hasattr(_signal, "pidfd_send_signal"):
        return "ambiguous"                 # fail closed without pidfd
    own_fd = pidfd
    opened = False
    if own_fd is None:
        try:
            own_fd = os.pidfd_open(pid)
            opened = True
        except OSError:
            try:
                return ("dead" if ownership_evidence(pid) is None
                        else "ambiguous")
            except AmbiguousProcess:
                return "ambiguous"
    try:
        for sig in (15, 9):
            try:
                state = _prove(pid, expected)   # re-prove pre-signal
            except AmbiguousProcess:
                return "ambiguous"
            if state == "dead":
                break
            try:
                _signal.pidfd_send_signal(own_fd, sig)
            except ProcessLookupError:
                break
            # descendants: per-process pidfd proof, never bare killpg
            for dpid in _session_descendants(expected["sid"],
                                             expected["starttime"]):
                if dpid == pid:
                    continue
                try:
                    dfd = os.pidfd_open(dpid)
                except OSError:
                    continue
                try:
                    if os.getsid(dpid) == expected["sid"]:
                        _signal.pidfd_send_signal(dfd, sig)
                except (ProcessLookupError, OSError):
                    pass
                finally:
                    os.close(dfd)
            if sig == 15:
                time.sleep(5)
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
        if opened and own_fd is not None:
            os.close(own_fd)


def bind_executable(original: dict) -> str:
    """Prove the invoked Python pathname resolves to the exact bound
    file identity (canonical path, dev, inode, mode, size, sha256).
    Returns the invoked pathname; any drift blocks (32d5918 item 2)."""
    invoked = original.get("python")
    ident = original.get("exe_identity")
    want_sha = original.get("exe_sha256")
    if not invoked or not isinstance(ident, dict) or not want_sha:
        raise RetryBlocked("original record lacks executable identity")
    resolved = os.path.realpath(invoked)
    if resolved != ident.get("canonical"):
        raise RetryBlocked("python pathname resolution changed")
    st = os.stat(resolved)
    if (st.st_dev != ident.get("dev") or st.st_ino != ident.get("inode")
            or st.st_mode != ident.get("mode")
            or st.st_size != ident.get("size")):
        raise RetryBlocked("executable file identity changed")
    got = hashlib.sha256(Path(resolved).read_bytes()).hexdigest()
    if got != want_sha:
        raise RetryBlocked("python executable bytes changed")
    return invoked


def verify_runtime_identity(original: dict, env: dict) -> None:
    """Probes run under the ORIGINAL executable (identity-bound by the
    sha256 captured from /proc/<pid>/exe while attempt one was alive)
    and the complete recorded environment — never the controller's
    ambient interpreter (steer e2d5b5e item 4)."""
    invoked = bind_executable(original)
    recorded_origins = original.get("package_origins")
    if not isinstance(recorded_origins, dict):
        raise RetryBlocked("original record lacks package origins")
    for mod in ("vllm", "torch"):
        want = recorded_origins.get(mod)
        if not want:
            raise RetryBlocked(f"no recorded origin for {mod}")
        probe = subprocess.run(
            [invoked, "-c",
             f"import {mod}, hashlib, os; print({mod}.__version__); "
             f"p=os.path.realpath({mod}.__file__); print(p); "
             f"print(hashlib.sha256(open(p,'rb').read()).hexdigest())"],
            capture_output=True, text=True, env=env)
        lines = probe.stdout.strip().splitlines()
        if len(lines) < 3:
            raise RetryBlocked(f"{mod} probe failed under recorded env")
        if (lines[0] != want["version"] or lines[1] != want["origin"]
                or lines[2] != want["origin_sha256"]):
            raise RetryBlocked(
                f"{mod} version/origin/bytes differ from the recorded "
                "identity (same-version different-origin blocks)")
    # Complete dependency-closure verification: every module origin +
    # sha256 recorded from attempt one must match under the bound
    # executable and recorded environment (steer 4cb5caa item 5).
    closure = original.get("dependency_closure")
    if not isinstance(closure, dict) or not closure:
        raise RetryBlocked("original record lacks dependency closure")
    mods = [m for m in closure if "origin" in closure[m]]
    probe = subprocess.run(
        [invoked, "-c",
         "import importlib, hashlib, os, json, sys\n"
         "sys.path.insert(0, 'src')\n"
         "mods = " + json.dumps(mods) + "\n"
         "out = {}\n"
         "for m in mods:\n"
         "    try:\n"
         "        mod = importlib.import_module(m)\n"
         "        p = os.path.realpath(mod.__file__)\n"
         "        out[m] = [p, hashlib.sha256(open(p,'rb').read())"
         ".hexdigest()]\n"
         "    except Exception as e:\n"
         "        out[m] = ['err', type(e).__name__]\n"
         "print(json.dumps(out))"],
        capture_output=True, text=True, env=env, cwd=str(CONTROL))
    if probe.returncode != 0:
        raise RetryBlocked("closure probe failed under recorded env")
    got = json.loads(probe.stdout.strip().splitlines()[-1])
    for m in mods:
        want_c = closure[m]
        cur = got.get(m)
        if (not cur or cur[0] != want_c["origin"]
                or cur[1] != want_c["sha256"]):
            raise RetryBlocked(
                f"dependency closure differs for {m} — blocked")


def retry_fail_closed_reasons() -> list[str]:
    """Kernel primitives required for a proven automatic retry that this
    runtime cannot supply (steer 0e812c1). Non-empty => block."""
    reasons = []
    # The guarded launcher performs pathname os.execv, not an fd-bound
    # execveat/fexecve with a proven replacement-race boundary. Even
    # where libc exposes fexecve, the implemented exec path is
    # pathname-based, so the final-lookup race is not proven closed —
    # fail closed until an fd-bound launcher and a deterministic
    # replacement-race test exist (steer 0e812c1 item 1).
    if not _launcher_uses_fd_bound_exec():
        reasons.append("no fd-bound execveat/fexecve exec path proven in "
                       "the guarded launcher")
    # Dedicated identity-bound process-tree kill scope.
    if not _has_cgroup_scope():
        reasons.append("no trustworthy cgroup-v2/systemd kill scope")
    return reasons


def _launcher_uses_fd_bound_exec() -> bool:
    try:
        src = (CONTROL / "scripts/m38e_launch.py").read_text()
    except OSError:
        return False
    # Marker set only when the launcher exec's an identity-bound fd.
    return "FD_BOUND_EXEC = True" in src


def _has_cgroup_scope() -> bool:
    # A usable delegated cgroup-v2 scope needs writable cgroup.procs in a
    # delegated subtree; unprivileged sessions here do not have one.
    return False


def audit_git_identity(record: dict) -> str:
    """Return the canonical bound git executable, verified against the
    identity captured from attempt one (steer 0e812c1 item 3). Blocks on
    any drift; never falls back to PATH or the Python executable."""
    gi = record["records"][0].get("git_identity")
    if not isinstance(gi, dict) or not gi.get("canonical"):
        raise RetryBlocked("original record lacks git executable identity")
    real = os.path.realpath(gi["canonical"])
    if real != gi["canonical"]:
        raise RetryBlocked("git executable path resolution changed")
    got = hashlib.sha256(Path(real).read_bytes()).hexdigest()
    if got != gi.get("sha256"):
        raise RetryBlocked("git executable bytes changed")
    return real


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

        # FAIL-CLOSED retry gate (steer 0e812c1 items 1 & 7): automatic
        # retry requires two kernel primitives this pure-Python runtime
        # cannot provide with a proven replacement-race boundary — an
        # fd-bound execveat/fexecve exec path, and a dedicated
        # identity-bound cgroup-v2/systemd scope for complete
        # process-tree termination after GO. The steer authorizes
        # failing closed when the platform cannot supply them. Automatic
        # retry is therefore permanently blocked and requires private
        # operator review; the honest, safe default for a contingency
        # this critical.
        for reason in retry_fail_closed_reasons():
            raise RetryBlocked(f"fail-closed retry gate: {reason}")

        original = record["records"][0]
        # Order per steer 32d5918 item 1: environment, then bound
        # executable, THEN the Python-importing preflight under that
        # exact executable and environment — never sys.executable.
        env = build_retry_environment(original)
        invoked = bind_executable(original)
        verify_control_artifacts(record)
        pre = subprocess.run(
            [invoked, str(CONTROL / "scripts/m38e_exec_preflight.py"),
             str(exec_dir), expected], capture_output=True, text=True,
            env=env)
        if pre.returncode != 0:
            raise RetryBlocked(f"preflight: {pre.stdout.strip()}")
        git_exe = audit_git_identity(record)   # bound git, never PATH
        aud = subprocess.run(
            [invoked, str(CONTROL / "scripts/m38e_untracked_audit.py"),
             str(exec_dir),
             str(RECORD.parent / original["environ_file"]),
             invoked, git_exe],           # 4-arg boundary: exe THEN git
            capture_output=True, text=True, env=env)
        if aud.returncode != 0:
            raise RetryBlocked(f"untracked-import audit: "
                               f"{aud.stdout.strip()}")
        verify_runtime_identity(original, env)
        launch_arg = verify_model_identity(original, exec_dir)
        # Re-verify everything immediately before reservation.
        verify_control_artifacts(record)
        bind_executable(original)

        # Durably consume attempt two BEFORE process creation.
        nonce = secrets.token_hex(16)
        record["attempts_launched"] += 1
        record["records"].append({
            "attempt": 2, "state": "reserved", "nonce": nonce,
            "reserved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime()),
            "run_id": run_id})
        atomic_write_record(record)

        # Two-way handshake (steer 4cb5caa item 1): READY pipe proves the
        # child established its owned session/cwd post-setsid/post-chdir
        # BEFORE the parent durably registers ownership and sends GO.
        ready_r, ready_w = os.pipe()
        go_r, go_w = os.pipe()
        os.set_inheritable(ready_w, True)
        os.set_inheritable(go_r, True)
        lock_fd = lock.fileno()
        os.set_inheritable(lock_fd, True)
        exe_ident_json = json.dumps(original["exe_identity"])
        log = open(CONTROL / "logs/m38e_official.log", "a")
        proc = subprocess.Popen(
            [invoked, str(CONTROL / "scripts/m38e_launch.py"),
             str(ready_w), str(go_r), str(lock_fd), exe_ident_json,
             str(exec_dir), invoked, "src/m38e_dev_sweep.py",
             "--model-ref", launch_arg],
            stdout=log, stderr=log, env=env, close_fds=True,
            pass_fds=(ready_w, go_r, lock_fd))
        os.close(ready_w)
        os.close(go_r)
        try:
            leader_pidfd = os.pidfd_open(proc.pid)
        except OSError:
            leader_pidfd = None
        driver_cmd_prefix = [invoked, "src/m38e_dev_sweep.py"]
        try:
            # Read READY with a bounded timeout.
            import select
            rlist, _, _ = select.select([ready_r], [], [], 30)
            if not rlist:
                raise RetryBlocked("READY handshake timed out")
            raw = os.read(ready_r, 4096)
            if not raw:
                raise RetryBlocked("child closed READY without a record")
            ready = json.loads(raw.decode().splitlines()[0])
            # Verify the child's self-proof against the kernel's view.
            own = ownership_evidence(proc.pid)
            if own is None:
                raise RetryBlocked("child vanished before READY proof")
            want_exe = original["exe_identity"]
            if (ready["pid"] != proc.pid
                    or ready["pgid"] != proc.pid
                    or ready["sid"] != proc.pid
                    or own["pgid"] != proc.pid
                    or own["sid"] != proc.pid
                    or ready["cwd"] != str(Path(exec_dir).resolve())
                    or own["cwd"] != str(Path(exec_dir).resolve())
                    or own["cmdline"][:2] != [invoked,
                                              str(CONTROL /
                                                  "scripts/m38e_launch.py")]
                    or ready["self_exe"].get("canonical")
                    != want_exe["canonical"]
                    or ready["self_exe"].get("sha256")
                    != want_exe["sha256"]):
                raise RetryBlocked("READY proof mismatch")
            launcher_cmd = own["cmdline"]
            expected_owner = {"starttime": own["starttime"],
                              "sid": proc.pid, "cwd": str(exec_dir),
                              "phases": []}
            # Durable 'launching' with exact proven ownership BEFORE GO.
            record["records"][-1].update({
                "state": "launching", "pid": proc.pid, "pgid": proc.pid,
                "sid": proc.pid,
                "starttime_ticks": own["starttime"],
                "launcher_cmdline": launcher_cmd,
                "expected_cmdline": driver_cmd_prefix,
                "exec_dir": str(exec_dir), "source_commit": expected,
                "exe_identity": original["exe_identity"],
                "environ_sha256": original["environ_sha256"]})
            atomic_write_record(record)
            reread = json.loads(RECORD.read_text())["records"][-1]
            if (reread.get("state") != "launching"
                    or reread.get("pid") != proc.pid
                    or reread.get("nonce") != nonce):
                raise RetryBlocked("launching record failed reread")
            os.write(go_w, b"G")          # release barrier -> exec
        except Exception:
            os.close(go_w)                # EOF: child exits without exec
            os.close(ready_r)
            try:
                ev = ownership_evidence(proc.pid)
                phases = [ev["cmdline"]] if ev else []
                outcome = terminate_owned(
                    proc.pid,
                    {"starttime": ev["starttime"], "sid": proc.pid,
                     "cwd": str(exec_dir), "phases": phases}
                    if ev else {}, leader_pidfd)
            except AmbiguousProcess:
                outcome = "ambiguous"
            record["records"][-1]["state"] = (
                "failed_terminated" if outcome == "dead" else "ambiguous")
            atomic_write_record(record)
            raise
        os.close(go_w)
        os.close(ready_r)

        expected_ident = None
        for _ in range(50):
            time.sleep(0.2)
            try:
                ident = proc_identity(proc.pid)
            except AmbiguousProcess:
                continue
            if ident and ident["cmdline"][:2] == [invoked,
                                                  "src/m38e_dev_sweep.py"]:
                expected_ident = ident
                break
        if expected_ident is None:
            expected_owner["phases"] = [launcher_cmd,
                                        driver_cmd_prefix]
            outcome = terminate_owned(proc.pid, expected_owner,
                                      leader_pidfd)
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
                # No trustworthy cgroup/systemd scope is bound from pure
                # Python, so complete process-tree termination cannot be
                # proven (steer 4cb5caa item 6). Fail closed: do NOT
                # auto-terminate; record a durable ambiguous permanent
                # block and return without an unbounded wait or an
                # explicit unlock, leaving any surviving child its
                # inherited run lock for private operator review.
                record["records"][-1]["state"] = "stall_ambiguous"
                record["records"][-1]["stall_termination"] = (
                    "disabled_fail_closed")
                atomic_write_record(record)
                print("[m38e-retry] BLOCK: stall with no trustworthy "
                      "termination scope — auto-termination disabled, "
                      "private review required", flush=True)
                return 3
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
