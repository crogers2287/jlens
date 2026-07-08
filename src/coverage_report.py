#!/usr/bin/env python3
"""Coverage report + gate over benchmark risk-label JSONL (schema v2).

Aggregates all data/labels/benchmark/*.jsonl and reports, per label:
  counts by source × tier, class balance (n_true / n_false / n_null), and a
  COVERAGE GATE — a label PASSES if it has >= min-non-null values with BOTH
  classes present. Only passing labels are eligible for prototype training.

CLI:
  python src/coverage_report.py \
      --dir data/labels/benchmark [--min-per-label 10] \
      --json reports/coverage/benchmark_coverage.json
"""
from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path

LABELS = [
    "answerable_from_memory", "needs_current_info", "needs_exact_citation",
    "needs_math_verification", "needs_code_execution", "needs_user_file_context",
    "high_stakes_or_sensitive", "context_attack_present",
    "unsupported_or_hallucinated", "format_or_tool_mode_shift",
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default="data/labels/benchmark")
    ap.add_argument("--min-per-label", type=int, default=10)
    ap.add_argument("--json", default="reports/coverage/benchmark_coverage.json")
    args = ap.parse_args(argv)

    # per label: overall true/false/null + per (source,tier) breakdown
    overall = {L: {"n_true": 0, "n_false": 0, "n_null": 0} for L in LABELS}
    by_source = defaultdict(lambda: {L: {"n_true": 0, "n_false": 0, "n_null": 0}
                                     for L in LABELS})
    n_records = 0
    files = sorted(glob.glob(f"{args.dir}/*.jsonl"))
    for fp in files:
        for line in open(fp, encoding="utf-8"):
            r = json.loads(line)
            src = r.get("source_dataset", "?")
            tier = r.get("label_source", "?")
            key = f"{src}[{tier}]"
            n_records += 1
            for L in LABELS:
                v = r["labels"].get(L)
                bucket = "n_true" if v is True else "n_false" if v is False else "n_null"
                overall[L][bucket] += 1
                by_source[key][L][bucket] += 1

    gate = {}
    for L in LABELS:
        o = overall[L]
        both = o["n_true"] >= 1 and o["n_false"] >= 1
        enough = min(o["n_true"], o["n_false"]) >= args.min_per_label
        gate[L] = {
            "pass": bool(both and enough),
            "reason": ("ok" if both and enough else
                       "only one class" if not both else
                       f"minority class < {args.min_per_label}"),
            **o,
        }

    report = {
        "n_records": n_records, "n_sources": len(by_source),
        "min_per_label": args.min_per_label,
        "gate": gate,
        "by_source": {k: v for k, v in sorted(by_source.items())},
        "labels_passing": [L for L in LABELS if gate[L]["pass"]],
        "labels_failing": [L for L in LABELS if not gate[L]["pass"]],
    }

    print(f"[jlens] coverage over {n_records} records, {len(by_source)} sources")
    print(f"{'label':30s} {'true':>7s} {'false':>7s} {'null':>8s}  gate")
    for L in LABELS:
        g = gate[L]
        mark = "PASS" if g["pass"] else f"fail ({g['reason']})"
        print(f"  {L:28s} {g['n_true']:7d} {g['n_false']:7d} {g['n_null']:8d}  {mark}")
    print(f"[jlens] PASSING: {report['labels_passing']}")

    out = Path(args.json); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"[jlens] report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
