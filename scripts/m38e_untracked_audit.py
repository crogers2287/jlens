#!/usr/bin/env python3
"""Reusable read-only untracked-import audit (steer 32d5918 item 5).

Used by both the retry preflight and M38E finalization. Enumerates ALL
untracked files, directories, and symlinks in a checkout; derives the
import and executable search roots from the exact recorded environment
and the bound executable's site-packages; blocks any artifact capable
of changing import or execution resolution (modules, packages,
extension modules, executable scripts, .pth path-configuration files,
sitecustomize/usercustomize startup hooks, editable-install pointers,
symlinks into roots). Only the explicit private operational-data
allowlist outside those roots passes. Aggregate pass/block only.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PRIVATE_ALLOWLIST_PREFIXES = (
    "reports/shadow/private/", "private/", "logs/", ".m36c_model_ref",
    ".context/", ".gstack/", ".plugin-config/", ".jlens-project-structure",
    ".project-structure",
)
BLOCK_SUFFIXES = (".py", ".pyc", ".so", ".pth", ".egg-link")
BLOCK_NAMES = ("sitecustomize.py", "usercustomize.py", "__init__.py",
               "__editable__", "conftest.py")


def import_roots(checkout: Path, env: dict, exe: str) -> list[Path]:
    roots = [checkout / "src", checkout / "src/jlens_vllm_telemetry"]
    for part in (env.get("PYTHONPATH") or "").split(os.pathsep):
        if part:
            roots.append(Path(part))
    probe = subprocess.run(
        [exe, "-c", "import sys; [print(p) for p in sys.path if p]"],
        capture_output=True, text=True, env=env)
    for line in probe.stdout.splitlines():
        roots.append(Path(line))
    return [r.resolve() for r in roots]


def audit(checkout: Path, env: dict, exe: str) -> dict:
    out = subprocess.run(
        ["git", "-C", str(checkout), "status", "--porcelain",
         "--untracked-files=all"], capture_output=True, text=True)
    untracked = [line[3:] for line in out.stdout.splitlines()
                 if line.startswith("??")]
    roots = import_roots(checkout, env, exe)
    blocked = []
    for rel in untracked:
        path = (checkout / rel)
        resolved = path.resolve()
        in_root = any(str(resolved).startswith(str(r) + os.sep)
                      or resolved == r for r in roots)
        allowlisted = any(rel.startswith(p)
                          for p in PRIVATE_ALLOWLIST_PREFIXES)
        is_symlink = path.is_symlink()
        importable = (rel.endswith(BLOCK_SUFFIXES)
                      or any(rel.endswith(n) or f"/{n}" in rel
                             for n in BLOCK_NAMES)
                      or (path.exists() and not path.is_dir()
                          and os.access(path, os.X_OK)
                          and not allowlisted))
        symlink_into_root = is_symlink and any(
            str(resolved).startswith(str(r)) for r in roots)
        if in_root or symlink_into_root or (importable and not allowlisted):
            blocked.append(rel)
        elif not allowlisted and importable:
            blocked.append(rel)
    return {"untracked_total": len(untracked),
            "blocked_count": len(blocked),
            "result": "pass" if not blocked else "block"}


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: m38e_untracked_audit.py <checkout> "
                         "<environ_bin> <exe>")
    checkout = Path(sys.argv[1])
    env_blob = Path(sys.argv[2]).read_bytes()
    env = dict(kv.split("=", 1)
               for kv in env_blob.decode().split("\0") if "=" in kv)
    result = audit(checkout, env, sys.argv[3])
    print(f"[m38e-audit] {result['result']}: "
          f"untracked={result['untracked_total']} "
          f"blocked={result['blocked_count']}", flush=True)
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
