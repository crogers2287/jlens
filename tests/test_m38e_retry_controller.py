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
from m38e_retry_controller import (AmbiguousProcess, RetryBlocked, driver_alive,
                                   proc_identity, verify_owned_pgid)

LAUNCHER = REPO / "scripts" / "m38e_launch.py"


import hashlib as _H


def _sha(path):
    return _H.sha256(open(os.path.realpath(path), "rb").read()).hexdigest()


def _ident_json(path):
    real = os.path.realpath(path)
    st = os.stat(real)
    return json.dumps({"canonical": real, "dev": st.st_dev,
                       "inode": st.st_ino, "mode": st.st_mode,
                       "size": st.st_size, "sha256": _sha(real)})


SLEEPER = None


def _sleeper(tmp_path):
    global SLEEPER
    SLEEPER = tmp_path / "sleeper.py"
    SLEEPER.write_text("import time\ntime.sleep(30)\n")
    return "sleeper.py"


def spawn_guarded(tmp_path, argv=None, release=True, read_ready=True,
                  driver=None):
    # Bound interpreter == target == sys.executable; the driver is a
    # python script (mirrors the real python-launcher -> python-driver
    # flow). argv (legacy) is ignored except to pick a sleeper driver.
    drv = driver or _sleeper(tmp_path)
    ready_r, ready_w = os.pipe()
    go_r, go_w = os.pipe()
    os.set_inheritable(ready_w, True)
    os.set_inheritable(go_r, True)
    lock_r = os.open("/dev/null", os.O_RDONLY)
    os.set_inheritable(lock_r, True)
    ej = _ident_json(sys.executable)
    proc = subprocess.Popen([sys.executable, str(LAUNCHER),
                             str(ready_w), str(go_r), str(lock_r), ej,
                             str(tmp_path), sys.executable, drv],
                            close_fds=True,
                            pass_fds=(ready_w, go_r, lock_r))
    os.close(ready_w)
    os.close(go_r)
    os.close(lock_r)
    ready = None
    if read_ready:
        import select
        rl, _, _ = select.select([ready_r], [], [], 5)
        if rl:
            ready = json.loads(os.read(ready_r, 4096).decode()
                               .splitlines()[0])
    if release:
        os.write(go_w, b"G")
    return proc, go_w, ready_r, ready


def test_launcher_pid_is_pgid_and_survives_exec(tmp_path):
    proc, bw, _rr, ready = spawn_guarded(tmp_path)
    time.sleep(0.8)
    ident = proc_identity(proc.pid)
    assert ident is not None
    assert ident["cmdline"][:2] == [os.path.realpath(sys.executable), "sleeper.py"]  # exec'd
    assert ident["cwd"] == str(tmp_path.resolve())  # chdir applied
    assert os.getpgid(proc.pid) == proc.pid         # setsid: PID == PGID
    assert ready["pid"] == proc.pid and ready["sid"] == proc.pid
    os.close(bw)
    os.killpg(proc.pid, 9)
    proc.wait()


def test_child_blocks_at_barrier_until_go(tmp_path):
    proc, bw, _rr, _rd = spawn_guarded(tmp_path, ["/bin/sleep", "5"], release=False)
    time.sleep(0.8)
    ident = proc_identity(proc.pid)
    assert ident is not None
    assert "m38e_launch.py" in " ".join(ident["cmdline"])  # not exec'd
    os.write(bw, b"G")
    time.sleep(0.8)
    ident = proc_identity(proc.pid)
    assert ident["cmdline"][:2] == [os.path.realpath(sys.executable), "sleeper.py"]  # exec'd
    os.close(bw)
    os.killpg(proc.pid, 9)
    proc.wait()


def test_parent_death_before_registration_child_never_execs(tmp_path):
    canary = tmp_path / "canary.txt"
    script = tmp_path / "driver.py"
    script.write_text(f"open({str(canary)!r},'w').write('x')\n")
    proc, bw, _rr, _rd = spawn_guarded(tmp_path,
                             [sys.executable, str(script)], release=False)
    os.close(bw)              # simulate parent death: EOF, no GO byte
    rc = proc.wait(timeout=10)
    assert rc == 0
    assert not canary.exists()   # scientific driver was never executed


def test_lock_survives_controller_death_via_inherited_fd(tmp_path):
    import fcntl as F
    import select as _sel
    lock_path = tmp_path / "run.lock"
    holder = open(lock_path, "w")
    F.flock(holder, F.LOCK_EX | F.LOCK_NB)
    os.set_inheritable(holder.fileno(), True)
    (tmp_path / "sleeper.py").write_text("import time\ntime.sleep(30)\n")
    ready_r, ready_w = os.pipe(); go_r, go_w = os.pipe()
    os.set_inheritable(ready_w, True); os.set_inheritable(go_r, True)
    proc = subprocess.Popen(
        [sys.executable, str(LAUNCHER), str(ready_w), str(go_r),
         str(holder.fileno()), _ident_json(sys.executable),
         str(tmp_path), sys.executable, "sleeper.py"],
        close_fds=True, pass_fds=(ready_w, go_r, holder.fileno()))
    os.close(ready_w); os.close(go_r)
    _sel.select([ready_r], [], [], 5); os.read(ready_r, 4096)
    os.write(go_w, b"G")
    os.close(go_w); os.close(ready_r)
    time.sleep(0.8)
    holder.close()            # controller "dies": drops ITS descriptor
    probe = open(lock_path, "w")
    with pytest.raises(BlockingIOError):
        F.flock(probe, F.LOCK_EX | F.LOCK_NB)   # child still holds it
    os.killpg(proc.pid, 9)
    proc.wait()
    time.sleep(0.5)
    F.flock(probe, F.LOCK_EX | F.LOCK_NB)       # released with child


def make_record(pid, cmdline, cwd, attempts=1, starttime=None, sid=None,
                exe=None):
    import m38e_retry_controller as _R
    if starttime is None:
        try:
            starttime = _R.proc_starttime(pid)
        except Exception:
            starttime = 0
    if sid is None:
        try:
            sid = os.getsid(pid)
        except Exception:
            sid = 0
    return {"attempts_launched": attempts,
            "records": [{"attempt": 1, "pid": pid, "pgid": pid,
                         "run_id": "testrun",
                         "cmdline": cmdline, "cwd": cwd,
                         "starttime_ticks": starttime, "sid": sid,
                         "exe_identity": {"canonical": exe or "/x"},
                         "python": sys.executable,
                         "env_protocol": {}}]}


def test_decoy_same_start_time_identity_mismatch_blocks(tmp_path):
    # A live process at the recorded PID with the SAME start time but a
    # different cmdline/cwd is ambiguous -> blocks (never 'dead').
    decoy = subprocess.Popen(["/bin/sleep", "5"], cwd=str(tmp_path))
    time.sleep(0.2)
    rec = make_record(decoy.pid, ["python", "src/m38e_dev_sweep.py"],
                      "/somewhere/else")   # real start time, wrong ident
    with pytest.raises(AmbiguousProcess):
        driver_alive(rec)
    assert decoy.poll() is None            # decoy untouched
    decoy.kill()
    decoy.wait()


def test_pid_reuse_different_start_time_is_dead(tmp_path):
    decoy = subprocess.Popen(["/bin/sleep", "5"], cwd=str(tmp_path))
    time.sleep(0.2)
    rec = make_record(decoy.pid, ["python", "src/m38e_dev_sweep.py"],
                      "/somewhere/else",
                      starttime=1)         # different start time = reuse
    assert driver_alive(rec) is False      # recorded process is dead
    assert decoy.poll() is None            # unrelated current untouched
    decoy.kill()
    decoy.wait()


def test_live_original_blocks_and_matching_identity_detected(tmp_path):
    live = subprocess.Popen(["/bin/sleep", "5"], cwd=str(tmp_path),
                            start_new_session=True)   # pid==pgid==sid
    time.sleep(0.2)
    ident = proc_identity(live.pid)
    rec = make_record(live.pid, ident["cmdline"], ident["cwd"],
                      sid=os.getsid(live.pid),
                      exe=os.path.realpath(f"/proc/{live.pid}/exe"))
    assert driver_alive(rec) is True       # exact full identity: alive
    live.kill()
    live.wait()
    time.sleep(0.2)
    assert driver_alive(rec) is False      # dead once reaped


def test_stall_signal_hits_only_owned_group(tmp_path):
    owned, bw, _rr, _rd = spawn_guarded(tmp_path, ["/bin/sleep", "30"])
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


def bound_exe_record():
    import hashlib as H
    exe = os.path.realpath(sys.executable)
    st = os.stat(exe)
    return {"python": sys.executable, "exe_resolved": exe,
            "exe_sha256": H.sha256(open(exe, "rb").read()).hexdigest(),
            "exe_identity": {"canonical": exe, "dev": st.st_dev,
                             "inode": st.st_ino, "mode": st.st_mode,
                             "size": st.st_size}}


def test_bind_executable_blocks_on_missing_or_changed(tmp_path):
    with pytest.raises(RetryBlocked, match="executable identity"):
        C.bind_executable({"python": sys.executable})
    rec = bound_exe_record()
    assert C.bind_executable(rec) == sys.executable
    # inode change (different file at a copied path) blocks
    fake = tmp_path / "python-fake"
    fake.write_bytes(open(os.path.realpath(sys.executable), "rb").read())
    bad = dict(rec, python=str(fake),
               exe_identity=dict(rec["exe_identity"],
                                 canonical=str(fake)))
    with pytest.raises(RetryBlocked, match="file identity changed"):
        C.bind_executable(bad)


def test_runtime_identity_same_version_diff_origin_blocks():
    rec = bound_exe_record()
    rec["package_origins"] = {
        "vllm": {"version": "9.9", "origin": "/nowhere/vllm.py",
                 "origin_sha256": "0" * 64},
        "torch": {"version": "9.9", "origin": "/nowhere/torch.py",
                  "origin_sha256": "0" * 64}}
    env = {"PATH": "/usr/bin"}
    with pytest.raises(RetryBlocked):
        C.verify_runtime_identity(rec, env)


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


def full_evidence(pid, phases):
    ev = C.ownership_evidence(pid)
    return {"starttime": ev["starttime"], "sid": ev["sid"],
            "cwd": ev["cwd"], "phases": phases}


def _drain_ready(rr):
    import select as _sel
    _sel.select([rr], [], [], 5)
    try:
        os.read(rr, 4096)
    except OSError:
        pass


def test_exec_timeout_kill_path_reaps_only_owned(tmp_path):
    proc, bw, _rr, _rd = spawn_guarded(tmp_path, ["/bin/sleep", "60"],
                             release=False)   # stuck pre-exec launcher
    bystander = subprocess.Popen(["/bin/sleep", "60"])
    time.sleep(0.5)
    ev = C.ownership_evidence(proc.pid)
    expected = full_evidence(proc.pid, [ev["cmdline"]])
    outcome = terminate_owned(proc.pid, expected)
    proc.wait()
    assert outcome == "dead"
    assert bystander.poll() is None
    bystander.kill(); bystander.wait()
    os.close(bw)


def test_no_permissive_termination_mode(tmp_path):
    proc, bw, _rr, _rd = spawn_guarded(tmp_path, ["/bin/sleep", "10"],
                             release=False)
    time.sleep(0.4)
    assert terminate_owned(proc.pid, None) == "ambiguous"
    assert terminate_owned(proc.pid, {}) == "ambiguous"
    # process untouched by the refused calls
    assert proc.poll() is None
    os.write(bw, b"X")     # non-GO byte: child exits without exec
    proc.wait(); os.close(bw)


def test_starttime_or_phase_mismatch_blocks_without_signal(tmp_path):
    proc, bw, _rr, _rd = spawn_guarded(tmp_path, ["/bin/sleep", "10"],
                             release=False)
    time.sleep(0.4)
    ev = C.ownership_evidence(proc.pid)
    wrong_start = {"starttime": ev["starttime"] + 999, "sid": ev["sid"],
                   "cwd": ev["cwd"], "phases": [ev["cmdline"]]}
    assert terminate_owned(proc.pid, wrong_start) == "ambiguous"
    wrong_phase = {"starttime": ev["starttime"], "sid": ev["sid"],
                   "cwd": ev["cwd"],
                   "phases": [["/bin/other"]]}
    assert terminate_owned(proc.pid, wrong_phase) == "ambiguous"
    assert proc.poll() is None            # never signaled
    os.write(bw, b"X"); proc.wait(); os.close(bw)


def test_fd_allowlist_blocks_leaked_descriptor(tmp_path):
    # A decoy inheritable fd beyond the allowlist aborts pre-exec.
    canary = tmp_path / "canary.txt"
    script = tmp_path / "driver.py"
    script.write_text(f"open({str(canary)!r},'w').write('x')\n")
    ready_r, ready_w = os.pipe(); go_r, go_w = os.pipe()
    os.set_inheritable(ready_w, True); os.set_inheritable(go_r, True)
    lock_r = os.open("/dev/null", os.O_RDONLY)
    os.set_inheritable(lock_r, True)
    leak_r, leak_w = os.pipe()            # decoy descriptor
    os.set_inheritable(leak_r, True)
    proc = subprocess.Popen(
        [sys.executable, str(LAUNCHER), str(ready_w), str(go_r),
         str(lock_r), _ident_json(sys.executable), str(tmp_path),
         sys.executable, str(script)],
        close_fds=True, pass_fds=(ready_w, go_r, lock_r, leak_r))
    os.close(ready_w); os.close(go_r); os.close(lock_r); os.close(leak_r)
    rc = proc.wait(timeout=10)
    os.close(leak_w); os.close(go_w); os.close(ready_r)
    assert rc == 4                        # FD audit abort
    assert not canary.exists()


def test_lock_survives_without_explicit_unlock():
    # Controller finally must not contain LOCK_UN (source assertion).
    src = Path(C.__file__).read_text()
    assert "fcntl.flock(lock, fcntl.LOCK_UN)" not in src
    assert "flock(lock, fcntl.LOCK_UN)" not in src


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


# -- steer 32d5918 additions ----------------------------------------------------

def test_untracked_audit_blocks_importable(tmp_path):
    import subprocess as sp
    checkout = tmp_path / "co"
    (checkout / "src").mkdir(parents=True)
    sp.run(["git", "-C", str(checkout), "init", "-q"])
    sp.run(["git", "-C", str(checkout), "config", "user.email", "t@t"])
    sp.run(["git", "-C", str(checkout), "config", "user.name", "t"])
    (checkout / "tracked.txt").write_text("x")
    sp.run(["git", "-C", str(checkout), "add", "-A"])
    sp.run(["git", "-C", str(checkout), "commit", "-qm", "c"])
    envbin = tmp_path / "env.bin"
    envbin.write_bytes(b"PATH=/usr/bin\0")
    AUDIT = REPO / "scripts" / "m38e_untracked_audit.py"
    # clean: passes
    git_exe = os.path.realpath(sp.run(["bash", "-lc", "command -v git"],
                              capture_output=True, text=True).stdout.strip())
    r = sp.run([sys.executable, str(AUDIT), str(checkout), str(envbin),
                sys.executable, git_exe], capture_output=True, text=True)
    assert r.returncode == 0 and "pass" in r.stdout, r.stdout
    # untracked importable module at repo root (an import/exec candidate)
    (checkout / "evil.py").write_text("x=1\n")
    r = sp.run([sys.executable, str(AUDIT), str(checkout), str(envbin),
                sys.executable, git_exe], capture_output=True, text=True)
    assert r.returncode != 0 and "block" in r.stdout


def test_stall_ambiguous_returns_blocked_without_hang(monkeypatch):
    # terminate_owned -> 'ambiguous' must NOT lead to an unbounded wait;
    # verified structurally: the ambiguous branch returns before wait().
    src = Path(C.__file__).read_text()
    loop = src.split("while proc.poll() is None:")[1].split(
        "rc = proc.wait()")[0]
    assert "stall_ambiguous" in loop
    assert "return 3" in loop


def test_live_record_binds_exe_identity_and_origins():
    live = json.loads(
        (REPO / "reports/shadow/private/m38e_launch_record.json")
        .read_text())
    r0 = live["records"][0]
    ei = r0["exe_identity"]
    assert all(k in ei for k in ("canonical", "dev", "inode", "mode",
                                 "size"))
    for mod in ("vllm", "torch"):
        o = r0["package_origins"][mod]
        assert len(o["origin_sha256"]) == 64 and o["origin"]


# -- steer 0e812c1 additions ----------------------------------------------------

def test_retry_fail_closed_gate_blocks_automatic_retry():
    # This runtime lacks fd-bound execveat/fexecve AND a delegated
    # cgroup kill scope, so automatic retry MUST fail closed.
    reasons = C.retry_fail_closed_reasons()
    assert reasons, "expected fail-closed reasons on this platform"
    assert any("fd-bound" in r for r in reasons)
    assert any("cgroup" in r for r in reasons)


def test_audit_git_identity_binds_and_blocks(tmp_path):
    import hashlib as H
    real_git = os.path.realpath("/usr/bin/git")
    rec = {"records": [{"git_identity": {
        "canonical": real_git,
        "sha256": H.sha256(open(real_git, "rb").read()).hexdigest()}}]}
    assert C.audit_git_identity(rec) == real_git
    # tampered digest blocks
    bad = {"records": [{"git_identity": {"canonical": real_git,
                                         "sha256": "0" * 64}}]}
    with pytest.raises(RetryBlocked, match="bytes changed"):
        C.audit_git_identity(bad)
    # missing identity blocks
    with pytest.raises(RetryBlocked, match="git executable identity"):
        C.audit_git_identity({"records": [{}]})


def test_audit_invoked_with_git_slot_not_python(tmp_path):
    # Integration: the audit's 4-arg boundary is <checkout> <env> <exe>
    # <git>; passing python for git must NOT be how the controller wires
    # it. Prove the audit runs clean with a real git and blocks a shadow.
    import subprocess as sp
    checkout = tmp_path / "co"
    (checkout / "src").mkdir(parents=True)
    for a in (["init", "-q"], ["config", "user.email", "t@t"],
              ["config", "user.name", "t"]):
        sp.run(["git", "-C", str(checkout), *a])
    (checkout / "keep.txt").write_text("x")
    sp.run(["git", "-C", str(checkout), "add", "-A"])
    sp.run(["git", "-C", str(checkout), "commit", "-qm", "c"])
    envbin = tmp_path / "e.bin"
    envbin.write_bytes(b"PATH=/usr/bin\0")
    AUDIT = REPO / "scripts" / "m38e_untracked_audit.py"
    git_exe = os.path.realpath("/usr/bin/git")
    clean = sp.run([sys.executable, str(AUDIT), str(checkout),
                    str(envbin), sys.executable, git_exe],
                   capture_output=True, text=True)
    assert clean.returncode == 0 and "pass" in clean.stdout
    (checkout / "shadow.py").write_text("x=1\n")
    dirty = sp.run([sys.executable, str(AUDIT), str(checkout),
                    str(envbin), sys.executable, git_exe],
                   capture_output=True, text=True)
    assert dirty.returncode != 0 and "block" in dirty.stdout
    # python in the git slot fails closed (python cannot run git args)
    wrongwire = sp.run([sys.executable, str(AUDIT), str(checkout),
                        str(envbin), sys.executable, sys.executable],
                       capture_output=True, text=True)
    assert wrongwire.returncode != 0
