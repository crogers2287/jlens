#!/usr/bin/env python3
"""Aggregate-only summary of a shadow / outcome JSONL (M9).

Emits ONLY counts and distributions — NEVER any prompt/output/notes text. Safe
to commit even when the input is a private real-use log, because the output dict
is built from scratch with a fixed set of numeric/label keys; free text simply
never enters it.

Reuses M8 outcome_report (read-only) for the reviewed/calibration definitions so
this stays consistent with the review tooling.

Summary contents:
  - n_total / n_reviewed / n_unreviewed
  - level_distribution           (policy.level -> count)
  - recommended_action_distribution (policy.recommended_action -> count)
  - outcome_field_nonnull_counts (per outcome boolean/notes -> non-null count)
  - calibration                  (false-low-risk / false-high-risk, REVIEWED only;
                                  null when nothing reviewed)

CLI:
  python src/private_outcome_summary.py \
      --in reports/shadow/realuse_sample.jsonl \
      --out reports/outcomes/private_summary_sample.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import outcome_report as OR  # noqa: E402  (reuse reviewed/calibration defs)

# Keys that would carry free text — asserted absent from the output.
FORBIDDEN_KEYS = {"prompt_preview", "output_preview", "notes",
                  "prompt", "output", "text"}


def _dist(records, path):
    """Count records by a nested policy field, keeping None as a bucket."""
    c = Counter()
    for r in records:
        pol = r.get("policy") or {}
        c[pol.get(path)] = c[pol.get(path)] + 1
    return {(k if k is not None else "unscored"): v for k, v in c.items()}


def summarize(records) -> dict:
    cov = OR.coverage(records)          # n_total/reviewed/unreviewed + field counts
    cal = OR.calibration(records)       # reviewed-only FLR/FHR (or None)
    return {
        "n_total": cov["n_total"],
        "n_reviewed": cov["n_reviewed"],
        "n_unreviewed": cov["n_unreviewed"],
        "level_distribution": _dist(records, "level"),
        "recommended_action_distribution": _dist(records, "recommended_action"),
        "outcome_field_nonnull_counts": cov["outcome_field_nonnull_counts"],
        "reviewers": cov["reviewers"],
        "calibration": cal,  # null when 0 reviewed — never fabricated
        "note": ("Aggregate-only; contains no prompt/output/notes text. "
                 "Calibration (if any) is from human-reviewed rows only; "
                 "prototype numbers — production/final thresholds stay "
                 "gold/audit gated."),
    }


def _assert_no_text(obj, _where="root"):
    """Fail loudly if any forbidden key holds a STRING value (i.e. real text).

    A forbidden key holding an int is fine — e.g. outcome_field_nonnull_counts
    legitimately has a `notes` COUNT (how many records had a non-null note). We
    only reject an actual text payload, never an aggregate count.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS and isinstance(v, str):
                raise AssertionError(f"forbidden text value at {_where}.{k}")
            _assert_no_text(v, f"{_where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _assert_no_text(v, f"{_where}[{i}]")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    records = [json.loads(l) for l in open(args.inp, encoding="utf-8") if l.strip()]
    summary = summarize(records)
    _assert_no_text(summary)  # hard guarantee before we write anything

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[jlens] aggregate summary ({summary['n_total']} records, "
          f"{summary['n_reviewed']} reviewed) -> {out} — no text keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
