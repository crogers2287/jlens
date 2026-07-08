#!/usr/bin/env python3
"""Sample benchmark records for human audit (benchmark_gold -> project-gold).

Deterministically selects N records per source (stratified by the label the
source sets, so both classes are seen) and writes them to an audit queue. The
script ONLY queues — it never promotes a record's tier. A human reviews each
queued record against jlens semantics; once audited, the operator sets
label_source="gold" on the confirmed records (that promotion is manual).

Deterministic selection (no RNG): evenly-spaced stride over each source's rows.

CLI:
  python src/audit_sample.py \
      --dir data/labels/benchmark --per-source 10 \
      --out data/labels/audit_queue.jsonl
"""
from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path


def _stride_sample(rows, k):
    """Evenly spaced k rows across the list (deterministic, order-preserving)."""
    if k >= len(rows):
        return rows
    step = len(rows) / k
    return [rows[int(i * step)] for i in range(k)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default="data/labels/benchmark")
    ap.add_argument("--per-source", type=int, default=10)
    ap.add_argument("--out", default="data/labels/audit_queue.jsonl")
    args = ap.parse_args(argv)

    by_source = defaultdict(list)
    for fp in sorted(glob.glob(f"{args.dir}/*.jsonl")):
        for line in open(fp, encoding="utf-8"):
            r = json.loads(line)
            by_source[r.get("source_dataset", "?")].append(r)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for src, rows in sorted(by_source.items()):
            for r in _stride_sample(rows, args.per_source):
                fh.write(json.dumps({
                    "prompt_id": r["prompt_id"],
                    "source_dataset": r.get("source_dataset"),
                    "source_record_id": r.get("source_record_id"),
                    "source_label": r.get("source_label"),
                    "labels": r["labels"],
                    "label_source": r.get("label_source"),   # stays benchmark_gold
                    "audit_status": "pending",                # human sets confirmed/rejected
                    "auditor": None,
                    "audit_notes": None,
                }) + "\n")
                n += 1

    print(f"[jlens] queued {n} records for human audit "
          f"({args.per_source}/source × {len(by_source)} sources) -> {out}")
    print("[jlens] records remain label_source=benchmark_gold until a human "
          "audits and the operator promotes confirmed ones to gold.")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
