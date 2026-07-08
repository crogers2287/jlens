#!/usr/bin/env python3
"""Aggregate-only summary of an autonomous supervisor run (M10).

Reads auto_outcome_v1 records and emits ONLY counts / distributions / rates —
NEVER any prompt/output/notes text. Safe to commit even when the input is a
private run log, because the output dict is built from a fixed set of
numeric/label keys and a recursive guard hard-fails on any text value.

Summary contents:
  - n_total, n_telemetry_missing
  - level_distribution / recommended_action_distribution (policy; "unscored"
    when policy is null, e.g. GGUF telemetry_missing)
  - verifier_name_distribution
  - escalation: count + rate
  - auto_field_nonnull_counts (auto_judged / auto_was_wrong / ...)
  - confidence_buckets (none / low / medium / high over verifier_confidence)
  - auto_vs_human_agreement: computed ONLY over rows a human reviewed
    (auto_was_wrong vs human was_wrong); null when no human-reviewed rows.

CLI:
  python src/autonomous_outcome_report.py \
      --in reports/shadow/private/autonomous_local.jsonl \
      --out reports/outcomes/autonomous_summary_sample.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

FORBIDDEN_KEYS = {"prompt_preview", "output_preview", "notes", "auto_notes",
                  "prompt", "output", "text"}
AUTO_FIELDS = ["auto_judged", "auto_was_wrong", "auto_needed_retrieval",
               "auto_needed_checker", "escalate_for_review"]


def _dist(records, path):
    c = Counter()
    for r in records:
        pol = r.get("policy") or {}
        c[pol.get(path)] += 1
    return {(k if k is not None else "unscored"): v for k, v in c.items()}


def _conf_bucket(v):
    if v is None:
        return "none"
    if v < 0.55:
        return "low[0,0.55)"
    if v < 0.75:
        return "medium[0.55,0.75)"
    return "high[0.75,1]"


def _human_reviewed(r):
    return r.get("outcome", {}).get("was_wrong") is not None


def summarize(records) -> dict:
    n = len(records)
    esc = sum(1 for r in records if r.get("auto_outcome", {}).get("escalate_for_review"))
    vnames = Counter()
    for r in records:
        for name in r.get("auto_outcome", {}).get("verifier_names", []):
            vnames[name] += 1
    auto_nonnull = {f: sum(1 for r in records
                           if r.get("auto_outcome", {}).get(f) is not None)
                    for f in AUTO_FIELDS}
    conf = Counter(_conf_bucket(r.get("auto_outcome", {}).get("verifier_confidence"))
                   for r in records)

    # auto-vs-human agreement over human-reviewed rows only
    reviewed = [r for r in records if _human_reviewed(r)
                and r.get("auto_outcome", {}).get("auto_was_wrong") is not None]
    agreement = None
    if reviewed:
        agree = sum(1 for r in reviewed
                    if r["auto_outcome"]["auto_was_wrong"] == r["outcome"]["was_wrong"])
        agreement = {"n_compared": len(reviewed),
                     "agreement_rate": round(agree / len(reviewed), 4)}

    return {
        "n_total": n,
        "n_telemetry_missing": sum(1 for r in records if r.get("telemetry_missing")),
        "level_distribution": _dist(records, "level"),
        "recommended_action_distribution": _dist(records, "recommended_action"),
        "verifier_name_distribution": dict(vnames),
        "escalation": {"count": esc, "rate": round(esc / n, 4) if n else None},
        "auto_field_nonnull_counts": auto_nonnull,
        "confidence_buckets": dict(conf),
        "auto_vs_human_agreement": agreement,  # null until humans review
        "note": ("Aggregate-only; no prompt/output/notes text. auto_outcome is a "
                 "CANDIDATE, not gold — auto-vs-human agreement is computed only "
                 "over human-reviewed rows. Prototype numbers; production/final "
                 "thresholds stay gold/audit gated."),
    }


def _assert_no_text(obj, where="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS and isinstance(v, str):
                raise AssertionError(f"forbidden text value at {where}.{k}")
            _assert_no_text(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _assert_no_text(v, f"{where}[{i}]")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    records = [json.loads(l) for l in open(args.inp, encoding="utf-8") if l.strip()]
    summary = summarize(records)
    _assert_no_text(summary)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[jlens] autonomous summary ({summary['n_total']} records, "
          f"escalated={summary['escalation']['count']}) -> {out} — no text keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
