#!/usr/bin/env python3
"""Evaluate calibrated risk heads — GATED on human labels.

Provides the metric functions the risk heads are scored with and refuses to run
until labels exist (delegates the gate to train_risk_heads.check_trainable).

Metrics per label:
  AUROC, AUPRC, ECE (expected calibration error),
  false-low-risk rate  (missed real risk — the costly error),
  false-high-risk rate (unnecessary caution),
  latency (per-prompt predict time).

Policy priority: false-low-risk is WORSE than false-high-risk. Operating points
are tuned to bound false-low-risk first, then minimize false-high-risk. Never
hand-pick thresholds as final policy — calibrate on held-out labeled data.

CLI:
  python src/eval_risk_heads.py \
      --features reports/features/r4_risk_features.jsonl \
      --labels data/labels/risk_labels_seed.jsonl
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

from train_risk_heads import check_trainable, load_features, load_labels


def auroc(y_true, y_score):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y_true, y_score))


def auprc(y_true, y_score):
    from sklearn.metrics import average_precision_score
    return float(average_precision_score(y_true, y_score))


def ece(y_true, y_prob, n_bins: int = 10):
    y_true = np.asarray(y_true, float)
    y_prob = np.asarray(y_prob, float)
    edges = np.linspace(0, 1, n_bins + 1)
    e = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (y_prob > lo) & (y_prob <= hi)
        if m.any():
            e += m.mean() * abs(y_true[m].mean() - y_prob[m].mean())
    return float(e)


def false_low_risk_rate(y_true, y_pred):
    """P(pred negative | truly positive) — missed real risk (costly)."""
    y_true = np.asarray(y_true, bool)
    y_pred = np.asarray(y_pred, bool)
    pos = y_true.sum()
    return float(((~y_pred) & y_true).sum() / pos) if pos else float("nan")


def false_high_risk_rate(y_true, y_pred):
    """P(pred positive | truly negative) — unnecessary caution."""
    y_true = np.asarray(y_true, bool)
    y_pred = np.asarray(y_pred, bool)
    neg = (~y_true).sum()
    return float((y_pred & (~y_true)).sum() / neg) if neg else float("nan")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--features", default="reports/features/r4_risk_features.jsonl")
    ap.add_argument("--labels", default="data/labels/risk_labels_seed.jsonl")
    ap.add_argument("--min-per-label", type=int, default=10)
    args = ap.parse_args(argv)

    load_features(args.features)               # validates features load
    labels = load_labels(args.labels)
    check_trainable(labels, args.min_per_label)  # LABEL GATE — refuses on seed

    print("[jlens] labels ready — evaluation would run here (not implemented in "
          "the scaffolding milestone).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
