#!/usr/bin/env python3
"""Outcome coverage + calibration over a reviewed shadow-outcome log (M8).

Coverage: reviewed vs unreviewed counts, per-outcome-field non-null counts,
per-reviewer counts -> reports/outcomes/outcome_coverage.json.

Calibration: compares the PolicyEngine recommendation (level / action) to the
HUMAN-reviewed outcomes, WHERE reviewed ONLY. Reports false-low-risk /
false-high-risk from reviewed rows. When 0 reviewed it writes exactly
"calibration pending — no reviewed outcomes yet" and never infers an outcome.

CLI:
  python src/outcome_report.py \
      --queue reports/shadow/review_queue_sample.jsonl \
      --json reports/outcomes/outcome_coverage.json \
      --calibration reports/outcomes/calibration_notes.md
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

OUTCOME_FIELDS = ["user_agreed", "was_wrong", "needed_retrieval",
                  "needed_checker", "notes"]
# A record counts as REVIEWED if a human set the reviewer OR any outcome value.
def _is_reviewed(rec: dict) -> bool:
    if rec.get("review_meta", {}).get("reviewer") is not None:
        return True
    return any(rec.get("outcome", {}).get(f) is not None for f in OUTCOME_FIELDS)


def coverage(records):
    reviewed = [r for r in records if _is_reviewed(r)]
    field_nonnull = {f: sum(1 for r in records
                            if r.get("outcome", {}).get(f) is not None)
                     for f in OUTCOME_FIELDS}
    reviewers = Counter(r["review_meta"].get("reviewer") for r in reviewed
                        if r["review_meta"].get("reviewer"))
    return {
        "n_total": len(records),
        "n_reviewed": len(reviewed),
        "n_unreviewed": len(records) - len(reviewed),
        "outcome_field_nonnull_counts": field_nonnull,
        "reviewers": dict(reviewers),
    }


def calibration(records):
    """Compare policy recommendation to reviewed was_wrong, reviewed rows only."""
    rev = [r for r in records if _is_reviewed(r) and r.get("policy")]
    with_flag = [r for r in rev if r["outcome"].get("was_wrong") is not None]
    if not with_flag:
        return None  # nothing to calibrate

    # "flagged risky" = policy level in {high, critical}
    def risky(r):
        return r["policy"].get("level") in ("high", "critical")
    tp = sum(1 for r in with_flag if r["outcome"]["was_wrong"] and risky(r))
    fn = sum(1 for r in with_flag if r["outcome"]["was_wrong"] and not risky(r))
    fp = sum(1 for r in with_flag if not r["outcome"]["was_wrong"] and risky(r))
    tn = sum(1 for r in with_flag if not r["outcome"]["was_wrong"] and not risky(r))
    pos = tp + fn
    neg = fp + tn
    return {
        "n_reviewed_with_was_wrong": len(with_flag),
        "false_low_risk_rate": round(fn / pos, 4) if pos else None,
        "false_high_risk_rate": round(fp / neg, 4) if neg else None,
        "confusion": {"tp": tp, "fn": fn, "fp": fp, "tn": tn},
    }


def write_calibration_md(path, cov, cal):
    lines = ["# Shadow-outcome calibration notes", ""]
    if cov["n_reviewed"] == 0 or cal is None:
        lines += ["calibration pending — no reviewed outcomes yet", "",
                  "Human review has not yet set any `was_wrong` outcomes, so the "
                  "policy recommendation cannot be compared to reality. "
                  "Production/final thresholds stay gold/audit gated until enough "
                  "reviewed outcomes exist (see docs/SHADOW_OUTCOME_REVIEW.md)."]
    else:
        lines += [
            f"Reviewed rows with `was_wrong` set: {cal['n_reviewed_with_was_wrong']}",
            f"- false-low-risk rate (missed a wrong answer at low/med risk): "
            f"{cal['false_low_risk_rate']}",
            f"- false-high-risk rate (flagged risky but answer was fine): "
            f"{cal['false_high_risk_rate']}",
            f"- confusion (risky-flag vs was_wrong): {cal['confusion']}", "",
            "PROTOTYPE numbers on a tiny reviewed set — indicative, not "
            "production. Production/final thresholds stay gold/audit gated.",
        ]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--queue", default="reports/shadow/review_queue_sample.jsonl")
    ap.add_argument("--json", default="reports/outcomes/outcome_coverage.json")
    ap.add_argument("--calibration", default="reports/outcomes/calibration_notes.md")
    args = ap.parse_args(argv)

    records = [json.loads(l) for l in open(args.queue, encoding="utf-8") if l.strip()]
    cov = coverage(records)
    cal = calibration(records)

    out = Path(args.json); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"coverage": cov, "calibration": cal}, indent=1))
    write_calibration_md(args.calibration, cov, cal)

    print(f"[jlens] coverage: reviewed={cov['n_reviewed']}/{cov['n_total']}")
    print(f"[jlens] calibration: "
          f"{'pending (0 reviewed)' if cal is None else cal}")
    print(f"[jlens] wrote {out} + {args.calibration}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
