#!/usr/bin/env python3
"""Validate task-batch metadata (M16).

Detects the M15 gap: numeric-looking exact_answer rows that carry a NUMERIC
known_answer but no numeric metadata, so they route to the strict
exact_answer_match instead of numeric_tolerant_check. Also basic sanity checks
(json rows need json_required; numeric rows need expected_value).

Reports offending prompt_ids (non-sensitive) grouped by issue. Exits nonzero if
any issue is found.

  python src/validate_task_metadata.py --in data/prompts/agents_a1_m15_batch.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verifiers as VZ  # reuse _all_numbers


def _is_numeric_answer(ans) -> bool:
    """True if the answer is a single clean numeric value (not e.g. 'Au', 'Paris')."""
    if ans is None:
        return False
    nums = VZ._all_numbers(str(ans))
    # exactly one number and the answer is essentially just that number
    return len(nums) == 1 and str(ans).strip().replace(",", "").lstrip("-").replace(".", "", 1).isdigit()


def validate(rows):
    issues = {"numeric_metadata_gap": [], "numeric_missing_expected": [],
              "json_missing_required": []}
    for r in rows:
        pid = r.get("prompt_id")
        cat = r.get("task_category")
        # numeric-looking exact_answer WITHOUT numeric metadata
        if cat == "exact_answer" and not r.get("numeric") \
                and r.get("expected_value") is None \
                and _is_numeric_answer(r.get("known_answer")):
            issues["numeric_metadata_gap"].append(pid)
        # numeric rows must carry expected_value
        if r.get("numeric") and r.get("expected_value") is None:
            issues["numeric_missing_expected"].append(pid)
        # json rows should declare required keys
        if r.get("json_check") and not r.get("json_required"):
            issues["json_missing_required"].append(pid)
    return {k: v for k, v in issues.items() if v}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    args = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(args.inp, encoding="utf-8") if l.strip()]
    issues = validate(rows)
    if not issues:
        print(f"[jlens] metadata OK: {len(rows)} rows, no issues")
        return 0
    print(f"[jlens] metadata ISSUES in {len(rows)} rows:")
    for kind, ids in issues.items():
        print(f"  {kind}: {len(ids)} -> {ids[:8]}{' ...' if len(ids) > 8 else ''}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
