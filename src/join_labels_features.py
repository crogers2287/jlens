#!/usr/bin/env python3
"""Inner-join benchmark risk labels (v2) to telemetry feature rows by prompt_id.

Produces the training table for prototype heads: each matched row carries the
feature vector (from reports/features/*.jsonl) and the benchmark labels (from
data/labels/benchmark/*.jsonl). Reports matched count, per-label class balance
in the JOINED set, and unmatched ids on each side.

CLI:
  python src/join_labels_features.py \
      --features reports/features/benchmark_m5_features.jsonl \
      --labels data/labels/benchmark \
      --out reports/benchmark_m5_join.json
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

LABELS = [
    "answerable_from_memory", "needs_current_info", "needs_exact_citation",
    "needs_math_verification", "needs_code_execution", "needs_user_file_context",
    "high_stakes_or_sensitive", "context_attack_present",
    "unsupported_or_hallucinated", "format_or_tool_mode_shift",
]


def _load_labels(path):
    files = ([path] if Path(path).is_file()
             else sorted(glob.glob(f"{path}/*.jsonl")))
    out = {}
    for fp in files:
        for line in open(fp, encoding="utf-8"):
            r = json.loads(line)
            out[r["prompt_id"]] = r["labels"]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--features", default="reports/features/benchmark_m5_features.jsonl")
    ap.add_argument("--labels", default="data/labels/benchmark")
    ap.add_argument("--out", default="reports/benchmark_m5_join.json")
    args = ap.parse_args(argv)

    feats = {json.loads(l)["prompt_id"]: json.loads(l)
             for l in open(args.features, encoding="utf-8")}
    labels = _load_labels(args.labels)

    matched = sorted(set(feats) & set(labels))
    feat_only = sorted(set(feats) - set(labels))
    label_only_n = len(set(labels) - set(feats))

    balance = {}
    for L in LABELS:
        t = sum(1 for pid in matched if labels[pid].get(L) is True)
        f = sum(1 for pid in matched if labels[pid].get(L) is False)
        n = sum(1 for pid in matched if labels[pid].get(L) is None)
        if t or f:  # only report labels present in the joined set
            balance[L] = {"n_true": t, "n_false": f, "n_null": n}

    report = {
        "n_matched": len(matched),
        "n_features": len(feats),
        "n_labels": len(labels),
        "n_features_without_labels": len(feat_only),
        "n_labels_without_features": label_only_n,
        "joined_label_balance": balance,
        "features_without_labels": feat_only,
        "matched_ids": matched,
    }
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))

    print(f"[jlens] joined {len(matched)} prompt_ids "
          f"({len(feats)} features x {len(labels)} label records)")
    for L, b in balance.items():
        print(f"  {L}: n_true={b['n_true']} n_false={b['n_false']} n_null={b['n_null']}")
    if feat_only:
        print(f"[jlens] {len(feat_only)} feature rows had NO matching label")
    print(f"[jlens] report written: {out}")
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
