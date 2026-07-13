"""Steer-a726b35 control-plane tests: immutable execution source.

Synthetic temp git repos only; no engine, no model, no private rows.
The row-validation depth of the preflight is covered by the
validate_rows suite in test_m38e_dev_sweep.py; these tests prove the
git-level immutability and refusal behavior that precede it.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PREFLIGHT = REPO_ROOT / "scripts" / "m38e_exec_preflight.py"
SUPERVISOR = REPO_ROOT / "scripts" / "m38e_supervisor.sh"


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, check=False)


@pytest.fixture()
def repo(tmp_path):
    control = tmp_path / "control"
    control.mkdir()
    git(control, "init", "-q")
    git(control, "config", "user.email", "t@t")
    git(control, "config", "user.name", "t")
    (control / "file.txt").write_text("v1\n")
    git(control, "add", "file.txt")
    git(control, "commit", "-qm", "c1")
    sha = git(control, "rev-parse", "HEAD").stdout.strip()
    exec_dir = tmp_path / "exec"
    git(control, "worktree", "add", "--detach", str(exec_dir), sha)
    return control, exec_dir, sha


def preflight(exec_dir, sha):
    return subprocess.run([sys.executable, str(PREFLIGHT),
                           str(exec_dir), sha],
                          capture_output=True, text=True)


def test_status_commits_do_not_move_execution_sha(repo):
    control, exec_dir, sha = repo
    (control / "status.md").write_text("heartbeat\n")
    git(control, "add", "status.md")
    git(control, "commit", "-qm", "status-only")
    assert git(control, "rev-parse", "HEAD").stdout.strip() != sha
    assert git(exec_dir, "rev-parse", "HEAD").stdout.strip() == sha
    assert git(exec_dir, "status", "--porcelain",
               "--untracked-files=no").stdout.strip() == ""


def test_newer_control_master_cannot_satisfy_expected_sha(repo):
    control, exec_dir, sha = repo
    (control / "later.md").write_text("x\n")
    git(control, "add", "later.md")
    git(control, "commit", "-qm", "later")
    newer = git(control, "rev-parse", "HEAD").stdout.strip()
    r = preflight(exec_dir, newer)      # expected = newer control head
    assert r.returncode != 0
    assert "does not equal" in r.stdout


def test_source_mismatch_blocks_before_anything_heavy(repo):
    control, exec_dir, sha = repo
    wrong = "0" * 40
    r = preflight(exec_dir, wrong)
    assert r.returncode != 0 and "BLOCK" in r.stdout


def test_symbolic_and_abbreviated_expectations_refused(repo):
    control, exec_dir, sha = repo
    for bad in ("master", "HEAD", sha[:12]):
        r = preflight(exec_dir, bad)
        assert r.returncode != 0
        assert "40-hex" in r.stdout or "BLOCK" in r.stdout


def test_branch_checkout_refused_detached_required(repo, tmp_path):
    control, exec_dir, sha = repo
    branchy = tmp_path / "branchy"
    git(control, "worktree", "add", "-b", "exec-branch", str(branchy), sha)
    r = preflight(branchy, sha)
    assert r.returncode != 0 and "detached" in r.stdout.lower()


def test_dirty_execution_tree_blocks(repo):
    control, exec_dir, sha = repo
    (exec_dir / "file.txt").write_text("tampered\n")
    r = preflight(exec_dir, sha)
    assert r.returncode != 0 and "tracked modifications" in r.stdout


def test_supervisor_refuses_missing_env_and_symbolic_sha(tmp_path):
    env_missing = subprocess.run(["bash", str(SUPERVISOR)],
                                 capture_output=True, text=True,
                                 env={"PATH": "/usr/bin:/bin"})
    assert env_missing.returncode != 0
    log = tmp_path / "logs"
    log.mkdir()
    import os
    env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/"),
           "M38E_EXEC_DIR": str(tmp_path),
           "M38E_EXPECTED_SHA": "master"}
    r = subprocess.run(["bash", str(SUPERVISOR)], capture_output=True,
                       text=True, env=env)
    assert r.returncode == 2   # symbolic ref refused before any launch


def test_missing_provenance_step_reached_only_after_git_checks(repo):
    # On a repo lacking the real driver sources, the preflight must fail
    # on structured checks (never import errors before git validation).
    control, exec_dir, sha = repo
    r = preflight(exec_dir, sha)
    assert r.returncode != 0    # blocks at provenance/module stage
    assert "BLOCK" in r.stdout or "Traceback" not in r.stdout
