#!/usr/bin/env python3
"""Commit-safety guard for jlens real-use artifacts (M9).

Scans one or more files and EXITS NONZERO if any is unsafe to commit:
  1. the file's own path is a private-log path (reports/shadow/private/*.jsonl,
     which is gitignored and must never be staged — the README is exempt);
  2. its content references a private-log path (reports/shadow/private/…);
  3. it carries UNREDACTED free text in prompt_preview / output_preview /
     outcome.notes (a non-empty string that is not a redaction marker).

It PASSES (exit 0) for aggregate-only summaries (no text keys), all-null review
queues, and redacted files (text == '[redacted]' or '[redacted:<hash>]').

Run this before staging anything under reports/:
  python src/check_commit_safe.py reports/outcomes/private_summary_sample.json \
      reports/shadow/review_queue_sample.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXT_FIELDS = ("prompt_preview", "output_preview")  # top-level free text
PRIVATE_DIR = "reports/shadow/private/"
REDACTION_RE = re.compile(r"^\[redacted(:[0-9a-fA-F]+)?\]$")


def _is_redacted(v) -> bool:
    return isinstance(v, str) and bool(REDACTION_RE.match(v.strip()))


def _text_violations(rec: dict) -> list[str]:
    """Unredacted free-text values in a single record."""
    bad = []
    for f in TEXT_FIELDS:
        v = rec.get(f)
        if isinstance(v, str) and v != "" and not _is_redacted(v):
            bad.append(f)
    oc = rec.get("outcome")
    if isinstance(oc, dict):
        v = oc.get("notes")
        if isinstance(v, str) and v != "" and not _is_redacted(v):
            bad.append("outcome.notes")
    return bad


def _refs_private_path(obj) -> bool:
    """True if any string anywhere in the parsed object names the private dir."""
    if isinstance(obj, str):
        return PRIVATE_DIR in obj
    if isinstance(obj, dict):
        return any(_refs_private_path(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_refs_private_path(v) for v in obj)
    return False


def check_file(path: str) -> list[str]:
    """Return a list of reasons the file is unsafe (empty == safe)."""
    reasons = []
    p = Path(path)
    norm = p.as_posix()

    # (1) the file itself is a private log (README is the only allowed member)
    if PRIVATE_DIR in norm and p.name != "README.md":
        reasons.append(f"{path}: is a private-log path ({PRIVATE_DIR}*) — never commit")
        return reasons  # no need to read content

    try:
        raw = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        reasons.append(f"{path}: unreadable ({e})")
        return reasons

    # Parse as JSONL first (record per line); fall back to a single JSON doc.
    records = []
    stripped = raw.strip()
    try:
        for line in stripped.splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
    except json.JSONDecodeError:
        try:
            records = [json.loads(stripped)]
        except json.JSONDecodeError:
            # Not JSON — only guard the private-path substring for non-JSON files.
            if PRIVATE_DIR in raw:
                reasons.append(f"{path}: text references private path {PRIVATE_DIR}")
            return reasons

    for i, rec in enumerate(records):
        if _refs_private_path(rec):
            reasons.append(f"{path}: record {i} references private path {PRIVATE_DIR}")
        for field in _text_violations(rec if isinstance(rec, dict) else {}):
            reasons.append(f"{path}: record {i} has UNREDACTED {field} text")
    return reasons


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+")
    args = ap.parse_args(argv)

    all_reasons = []
    for f in args.files:
        all_reasons += check_file(f)

    if all_reasons:
        print("[jlens] COMMIT-UNSAFE — do NOT commit:", file=sys.stderr)
        for r in all_reasons:
            print(f"  ✗ {r}", file=sys.stderr)
        return 1
    print(f"[jlens] commit-safe: {len(args.files)} file(s) — "
          "no private paths, no unredacted prompt/output/notes text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
