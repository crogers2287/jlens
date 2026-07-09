#!/usr/bin/env python3
"""Reviewed calibration report (M17).

Consolidates the accumulated reviewed records (M11-M16) into a CATEGORY-LEVEL
calibration summary. Reads the PRIVATE reviewed logs locally for per-category
detail but emits ONLY aggregate counts / rates / labels — never any prompt/output
/notes text. Agreement is computed ONLY over comparable rows (both auto_was_wrong
and human was_wrong set).

  python src/reviewed_calibration_report.py \
      --out reports/outcomes/agents_a1_reviewed_calibration_summary.json
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

# Private reviewed logs (read locally, NEVER committed).
REVIEWED_LOGS = [
    "reports/shadow/private/agents_a1_reviewed_live.jsonl",
    "reports/shadow/private/agents_a1_m13_reviewed_subset_local.jsonl",
    "reports/shadow/private/agents_a1_m15_reviewed_subset_local.jsonl",
]
ACTION_SUMMARY = "reports/outcomes/agents_a1_m16_action_summary_sample.json"
FORBIDDEN_KEYS = {"prompt_preview", "output_preview", "notes", "auto_notes",
                  "prompt", "output", "text"}

# priority of correctness verifiers when assigning a category
_CAT_BY_VERIFIER = [
    ("numeric_tolerant_check", "numeric"),
    ("json_object_check", "json"),
    ("math_checker", "math"),
    ("exact_answer_match", "exact"),
    ("regex_or_schema_check", "regex"),
    ("explain_rubric_check", "explain-rubric"),
]


def category_of(rec):
    vnames = set(rec.get("auto_outcome", {}).get("verifier_names", []) or [])
    for vname, cat in _CAT_BY_VERIFIER:
        if vname in vnames:
            return cat
    # no decisive correctness verifier — plain explain vs current-info look the
    # same by verifier name (only retrieval_required_heuristic), so use task_category
    tc = rec.get("task_category")
    if tc == "current_info":
        return "retrieval/current-info"
    if tc == "explain":
        return "open-explain"
    return "open-explain"


def _human_wrong(r):
    return r.get("outcome", {}).get("was_wrong")


def _auto_wrong(r):
    return r.get("auto_outcome", {}).get("auto_was_wrong")


def load_reviewed(root=Path(".")):
    recs = []
    for p in REVIEWED_LOGS:
        fp = root / p
        if fp.exists():
            recs += [json.loads(l) for l in open(fp, encoding="utf-8") if l.strip()]
    return recs


def per_category(records):
    buckets = defaultdict(list)
    for r in records:
        buckets[category_of(r)].append(r)
    out = {}
    for cat, rows in sorted(buckets.items()):
        reviewed = [r for r in rows if _human_wrong(r) is not None]
        comparable = [r for r in reviewed if _auto_wrong(r) is not None]
        agreement = None
        flr = fhr = None
        if comparable:
            agree = sum(1 for r in comparable if _auto_wrong(r) == _human_wrong(r))
            agreement = {"n_compared": len(comparable),
                         "agreement_rate": round(agree / len(comparable), 4)}
            # false-low-risk: human wrong but auto said not-wrong; false-high: reverse
            pos = [r for r in comparable if _human_wrong(r) is True]
            neg = [r for r in comparable if _human_wrong(r) is False]
            if pos:
                flr = round(sum(1 for r in pos if _auto_wrong(r) is False) / len(pos), 4)
            if neg:
                fhr = round(sum(1 for r in neg if _auto_wrong(r) is True) / len(neg), 4)
        out[cat] = {
            "reviewed_count": len(reviewed),
            "comparable_count": len(comparable),
            "auto_vs_human_agreement": agreement,
            "false_low_risk": flr,
            "false_high_risk": fhr,
            "calibration_status": _status(cat, len(reviewed), len(comparable)),
            "note": (None if comparable else "insufficient reviewed comparable data"),
        }
    return out


def _status(cat, reviewed, comparable):
    if cat == "open-explain":
        return "verifier_gap"          # no objective verifier for open-ended text
    if cat == "explain-rubric":
        return "needs_more_review"     # rubric synonym matching still basic
    if comparable == 0:
        return "needs_more_review"     # nothing objectively comparable yet
    # checkable categories with clean comparable data
    return "usable_shadow"


def _load_action_counts(root=Path(".")):
    p = root / ACTION_SUMMARY
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    dist = d.get("action_type_distribution", {})
    return {k: dist.get(k, 0) for k in
            ("retrieval_needed", "checker_needed", "review_needed", "no_action")}


def build(root=Path(".")):
    records = load_reviewed(root)
    cats = per_category(records)
    total_reviewed = sum(c["reviewed_count"] for c in cats.values())
    total_comparable = sum(c["comparable_count"] for c in cats.values())
    return {
        "reviewed_sources": len(REVIEWED_LOGS),
        "total_records_scanned": len(records),
        "total_reviewed": total_reviewed,
        "total_comparable": total_comparable,
        "per_category": cats,
        "fixed_findings": [
            "JSON false-positive (exact-anchor regex on valid JSON) found by review, fixed M12 json_object_check",
            "numeric false-positive (approx/unit-converted answers) found by review, fixed M14 numeric_tolerant_check + M16 metadata normalization",
        ],
        "remaining_gaps": [
            "open-ended explain has no objective verifier (escalates on low confidence; not comparable)",
            "explain-rubric synonym matching is basic (synonym mismatch escalates, as designed)",
        ],
        "action_routing_planned_only": _load_action_counts(root),
        "note": ("Aggregate-only; no prompt/output/notes text. Agreement is over "
                 "comparable reviewed rows only (both auto and human was_wrong set); "
                 "tiny-n — indicative, not production. Action-routing counts are "
                 "PLANNED-only (nothing executed). auto_outcome is a CANDIDATE; "
                 "production/final thresholds stay gold/audit gated."),
    }


def assert_no_text(obj, where="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS and isinstance(v, str):
                raise AssertionError(f"forbidden text value at {where}.{k}")
            assert_no_text(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            assert_no_text(v, f"{where}[{i}]")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="reports/outcomes/agents_a1_reviewed_calibration_summary.json")
    args = ap.parse_args(argv)
    summary = build()
    assert_no_text(summary)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[jlens] reviewed calibration: {summary['total_reviewed_records']} records "
          f"across {len(summary['per_category'])} categories -> {out} (no text keys)")
    for cat, d in summary["per_category"].items():
        print(f"  {cat:22s} reviewed={d['reviewed_count']:2d} comparable={d['comparable_count']:2d} "
              f"agreement={d['auto_vs_human_agreement']} status={d['calibration_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
