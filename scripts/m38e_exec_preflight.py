#!/usr/bin/env python3
"""M38E immutable-retry preflight (steer a726b35).

Verifies, BEFORE any engine construction, that a retry would execute as
a resume of the same official run identity:

  1. the execution directory is a git checkout with a DETACHED head —
     symbolic refs (master/main/HEAD-as-branch) are refused;
  2. the detached SHA equals the explicit expected full 40-char SHA
     (symbolic or abbreviated expectations are refused);
  3. the tracked tree is clean and every provenance-pinned file is
     byte-identical to that commit;
  4. the private official ledger exists in the expected private
     location and every row's source_commit and run identity fields
     match the expected SHA-derived identity (exact-validated via the
     driver's own validator — no row-count shortcut);
  5. the frozen model pointer is present and matches the control
     checkout's pointer.

Exit 0 only if every check passes; any failure prints an aggregate
reason and exits nonzero. No private row content is printed.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def fail(reason: str) -> None:
    print(f"[m38e-preflight] BLOCK: {reason}", flush=True)
    raise SystemExit(1)


def main() -> int:
    if len(sys.argv) != 3:
        fail("usage: m38e_exec_preflight.py <exec_dir> <expected_sha>")
    exec_dir, expected = Path(sys.argv[1]), sys.argv[2]

    if not re.fullmatch(r"[0-9a-f]{40}", expected):
        fail("expected SHA must be a full 40-hex commit, never a "
             "symbolic ref or abbreviation")
    if not exec_dir.is_dir():
        fail("execution directory missing")

    def git(*args):
        return subprocess.run(["git", "-C", str(exec_dir), *args],
                              capture_output=True, text=True)

    if git("symbolic-ref", "-q", "HEAD").returncode == 0:
        fail("execution checkout is on a branch — detached HEAD required")
    head = git("rev-parse", "HEAD").stdout.strip()
    if head != expected:
        fail("execution HEAD does not equal the expected source SHA")
    if git("status", "--porcelain",
           "--untracked-files=no").stdout.strip():
        fail("execution tree has tracked modifications")

    sys.path.insert(0, str(exec_dir / "src"))
    import m38e_dev_sweep as D                        # noqa: E402

    for rel in D.PROVENANCE_FILES:
        blob = subprocess.run(
            ["git", "-C", str(exec_dir), "show", f"HEAD:{rel}"],
            capture_output=True).stdout
        if blob != (exec_dir / rel).read_bytes():
            fail(f"provenance file differs from pinned commit: {rel}")

    model_ptr = exec_dir / ".m36c_model_ref"
    if not model_ptr.exists():
        fail("frozen model pointer missing in execution checkout")

    rows_path = exec_dir / D.OFFICIAL_ROWS
    if not rows_path.exists():
        fail("official ledger missing from expected private location")

    import json
    from m36v_phase1 import override_hash  # noqa: E402  (exec-tree src)
    rows = [json.loads(l) for l in rows_path.read_text().splitlines()]
    import os
    cwd = os.getcwd()
    os.chdir(exec_dir)                     # driver derives HEAD from cwd
    try:
        ident = D.run_identity(model_ptr.read_text().strip())
        D.validate_rows(rows, ident, override_hash())
    except D.SweepBlocked as exc:
        fail(f"row validation: {exc}")
    finally:
        os.chdir(cwd)
    if ident["provenance"]["source_commit"] != expected:
        fail("derived identity does not match expected SHA")

    print(f"[m38e-preflight] OK: exec={exec_dir} sha={expected[:12]} "
          f"rows={len(rows)} exact-validated", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
