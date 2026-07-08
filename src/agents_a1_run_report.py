#!/usr/bin/env python3
"""Aggregate-only report for an Agents-A1 shadow run (M11).

Merges run metadata (from the runner's run-meta sidecar) with distributions over
the run log, emitting ONLY counts / rates / label distributions — NEVER any
prompt/output/notes text. Safe to commit even when the input is a private run
log: the output is built from fixed numeric/label keys and a recursive guard
hard-fails on any text value.

auto_outcome is a CANDIDATE, not gold. auto-vs-human agreement is computed ONLY
over rows a human reviewed (outcome.was_wrong set); null otherwise.

CLI:
  python src/agents_a1_run_report.py \
      --in reports/shadow/private/agents_a1_run_local.jsonl \
      --meta reports/shadow/private/agents_a1_run_meta_local.json \
      --out reports/outcomes/agents_a1_run_summary_sample.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

FORBIDDEN_KEYS = {"prompt_preview", "output_preview", "notes", "auto_notes",
                  "prompt", "output", "text"}


def _pol_dist(records, key):
    c = Counter()
    for r in records:
        pol = r.get("policy") or {}
        c[pol.get(key)] += 1
    return {(k if k is not None else "unscored"): v for k, v in c.items()}


def _bool_count(records, field):
    return sum(1 for r in records
              if r.get("auto_outcome", {}).get(field) is True)


def _human_reviewed(r):
    return r.get("outcome", {}).get("was_wrong") is not None


def summarize(records, meta=None) -> dict:
    n = len(records)
    meta = meta or {}
    verdicts = Counter(r.get("auto_outcome", {}).get("auto_was_wrong") for r in records)
    verdict_dist = {("wrong" if k is True else "ok" if k is False else "undecided"): v
                    for k, v in verdicts.items()}
    vnames = Counter()
    for r in records:
        for name in r.get("auto_outcome", {}).get("verifier_names", []):
            vnames[name] += 1
    esc = _bool_count(records, "escalate_for_review")

    reviewed = [r for r in records if _human_reviewed(r)
                and r.get("auto_outcome", {}).get("auto_was_wrong") is not None]
    agreement = None
    if reviewed:
        agree = sum(1 for r in reviewed
                    if r["auto_outcome"]["auto_was_wrong"] == r["outcome"]["was_wrong"])
        agreement = {"n_compared": len(reviewed),
                     "agreement_rate": round(agree / len(reviewed), 4)}

    return {
        "run_id": meta.get("run_id"),
        "model": meta.get("model"),
        "endpoint_alias": meta.get("endpoint_alias"),
        "n_tasks": meta.get("n_tasks", n),
        "n_completed": n,
        "n_failed": meta.get("n_failed", 0),
        "n_telemetry_missing": sum(1 for r in records if r.get("telemetry_missing")),
        "level_distribution": _pol_dist(records, "level"),
        "recommended_action_distribution": _pol_dist(records, "recommended_action"),
        "auto_verdict_distribution": verdict_dist,
        "escalation_count": esc,
        "escalation_rate": round(esc / n, 4) if n else None,
        "verifier_distribution": dict(vnames),
        "auto_needed_retrieval_count": _bool_count(records, "auto_needed_retrieval"),
        "auto_needed_checker_count": _bool_count(records, "auto_needed_checker"),
        "auto_was_wrong_count": _bool_count(records, "auto_was_wrong"),
        "human_reviewed_count": sum(1 for r in records if _human_reviewed(r)),
        "auto_vs_human_agreement": agreement,   # null until humans review
        "privacy_check_status": "aggregate-only: no prompt/output/notes text",
        "note": ("auto_outcome is a CANDIDATE, not gold. Prototype numbers; "
                 "production/final thresholds stay gold/audit gated."),
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
    ap.add_argument("--meta", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    records = [json.loads(l) for l in open(args.inp, encoding="utf-8") if l.strip()]
    meta = json.loads(Path(args.meta).read_text()) if args.meta and Path(args.meta).exists() else {}
    summary = summarize(records, meta)
    _assert_no_text(summary)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[jlens] agents-a1 run report ({summary['n_completed']} records, "
          f"escalated={summary['escalation_count']}) -> {out} — no text keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
