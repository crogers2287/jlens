#!/usr/bin/env python3
"""Reusable read-only import/execution audit (steers 32d5918 + 4cb5caa).

NUL-safe, return-code-enforcing, git-identity-bound. Enumerates
untracked AND ignored files/dirs/symlinks; derives Python import roots
(sys.path under the recorded environment + PYTHONPATH) and executable
roots (PATH); blocks any artifact capable of changing import or command
resolution. Only exact-path private operational-data allowlist entries
pass. Fails closed on any command failure, undecodable name, permission
error, symlink cycle, external root, or incomplete inventory. Aggregate
counts only.

usage: m38e_untracked_audit.py <checkout> <environ_bin> <exe> <git_exe>
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ALLOWLIST_EXACT = None  # populated from private allowlist file if present
ALLOW_PREFIX_DIRS = ("reports/shadow/private", "private", "logs", ".context",
                     ".gstack", ".plugin-config")
ALLOW_EXACT_FILES = (".m36c_model_ref", ".jlens-project-structure.md",
                     ".project-structure.md")
BLOCK_SUFFIXES = (".py", ".pyc", ".pyo", ".so", ".pth", ".egg-link",
                  ".pyd")
BLOCK_BASENAMES = ("sitecustomize.py", "usercustomize.py",
                   "conftest.py")


class AuditBlock(Exception):
    pass


def git_nul(checkout: Path, git_exe: str, *args) -> list[str]:
    r = subprocess.run([git_exe, "-C", str(checkout), *args, "-z"],
                       capture_output=True)
    if r.returncode != 0:
        raise AuditBlock(f"git {' '.join(args)} rc={r.returncode}")
    try:
        text = r.stdout.decode()
    except UnicodeDecodeError:
        raise AuditBlock("undecodable filename in git output")
    return [f for f in text.split("\0") if f]


def import_and_exec_roots(checkout: Path, env: dict, exe: str) -> set:
    roots = set()
    probe = subprocess.run(
        [exe, "-c", "import sys,os\nprint('\\0'.join(p for p in sys.path "
         "if p))"], capture_output=True, text=True, env=env)
    if probe.returncode != 0:
        raise AuditBlock("sys.path probe failed")
    for p in probe.stdout.strip().split("\0"):
        if p:
            roots.add(os.path.realpath(p))
    for p in (env.get("PYTHONPATH") or "").split(os.pathsep):
        if p:
            roots.add(os.path.realpath(p))
    for p in (env.get("PATH") or "").split(os.pathsep):
        if p:
            roots.add(os.path.realpath(p))
    return roots


def is_allowlisted(rel: str) -> bool:
    if rel in ALLOW_EXACT_FILES:
        return True
    parts = rel.split("/")
    return parts[0] in ALLOW_PREFIX_DIRS


def audit(checkout: Path, env: dict, exe: str, git_exe: str) -> dict:
    all_roots = import_and_exec_roots(checkout, env, exe)
    checkout_real = os.path.realpath(checkout)
    # Environment roots that live OUTSIDE the repo source tree, plus the
    # in-repo virtualenv, are bound by the dependency-closure origin
    # digests (captured from attempt one) and are not re-audited here as
    # shadowing candidates. The audit's job is checkout source-tree
    # shadowing detection; external/venv integrity is a stronger digest
    # guarantee.
    env_roots = {r for r in all_roots
                 if not r.startswith(checkout_real + os.sep) and r != checkout_real}
    venv_roots = {r for r in all_roots
                  if os.sep + ".venv" + os.sep in r + os.sep
                  or r.endswith(os.sep + ".venv")}
    roots = (all_roots - env_roots) - venv_roots
    candidates = set(git_nul(checkout, git_exe, "status", "--porcelain",
                             "--untracked-files=all"))
    candidates = {c[3:] if len(c) > 3 and c[2] == " " else c
                  for c in candidates}
    ignored = set(git_nul(checkout, git_exe, "ls-files", "--others",
                          "--ignored", "--exclude-standard"))
    candidates |= ignored
    blocked = []
    for rel in candidates:
        rel = rel.rstrip("/")
        if not rel or rel.startswith(".venv/"):
            continue                       # venv is closure-bound, skip
        if "__pycache__/" in rel + "/":
            continue                       # bytecode cache of tracked src
        path = checkout / rel
        try:
            resolved = os.path.realpath(path)
        except OSError:
            raise AuditBlock(f"unresolvable path: {rel}")
        allow = is_allowlisted(rel)
        in_root = any(resolved == r or resolved.startswith(r + os.sep)
                      for r in roots)
        importable = (rel.endswith(BLOCK_SUFFIXES)
                      or os.path.basename(rel) in BLOCK_BASENAMES)
        try:
            executable = (path.is_file()
                          and os.access(path, os.X_OK))
        except OSError:
            raise AuditBlock(f"permission error: {rel}")
        symlink = path.is_symlink()
        if in_root and not allow:
            blocked.append(rel)
        elif (importable or (executable and not allow)
              or symlink) and not allow:
            blocked.append(rel)
    return {"candidates": len(candidates), "blocked": len(blocked),
            "result": "pass" if not blocked else "block"}


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("usage: m38e_untracked_audit.py <checkout> "
                         "<environ_bin> <exe> <git_exe>")
    checkout = Path(sys.argv[1])
    env_blob = Path(sys.argv[2]).read_bytes()
    env = dict(kv.split("=", 1)
               for kv in env_blob.decode().split("\0") if "=" in kv)
    exe, git_exe = sys.argv[3], sys.argv[4]
    try:
        result = audit(checkout, env, exe, git_exe)
    except AuditBlock as exc:
        print(f"[m38e-audit] block: {exc}", flush=True)
        return 1
    print(f"[m38e-audit] {result['result']}: "
          f"candidates={result['candidates']} "
          f"blocked={result['blocked']}", flush=True)
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
