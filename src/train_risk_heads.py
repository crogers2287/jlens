#!/usr/bin/env python3
"""Train calibrated risk heads — GATED on human labels.

This milestone (M3 scaffolding) ships the skeleton and the LABEL GATE. With the
current all-null seed it MUST refuse: no head is trained until a human provides
labels. The training path is wired but only executes once the gate passes.

Baselines (when labels exist): logistic regression, linear SVM, tiny MLP — all
CALIBRATED (CalibratedClassifierCV) — plus a hand-score baseline for comparison
only. Per-label, prompt-held-out (StratifiedGroupKFold). Metrics live in
eval_risk_heads.py.

CLI:
  python src/train_risk_heads.py \
      --features reports/features/r4_risk_features.jsonl \
      --labels data/labels/risk_labels_seed.jsonl \
      [--min-per-label 10] [--out reports/risk_heads.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

LABELS = [
    "answerable_from_memory", "needs_current_info", "needs_exact_citation",
    "needs_math_verification", "needs_code_execution", "needs_user_file_context",
    "high_stakes_or_sensitive", "context_attack_present",
    "unsupported_or_hallucinated", "format_or_tool_mode_shift",
]


def _flatten_features(row: dict):
    """Numeric feature vector from a risk_features row (drift already excluded)."""
    feats, names = [], []
    for k in ("prefill_pred_margin", "prefill_pred_correct",
              "decode_offdomain_frac", "decode_domain_switches",
              "low_conf_spike_count", "high_entropy_spike_count"):
        feats.append(float(row.get(k) or 0.0))
        names.append(k)
    for grp in ("entropy_final", "selected_token_prob", "topk_mass"):
        g = row.get(grp, {}) or {}
        for stat in ("mean", "extreme", "std"):
            feats.append(float(g.get(stat) or 0.0))
            names.append(f"{grp}.{stat}")
    return feats, names


def load_features(path):
    X, ids, names = {}, [], None
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        f, n = _flatten_features(r)
        names = names or n
        X[r["prompt_id"]] = np.array(f, dtype=np.float32)
        ids.append(r["prompt_id"])
    return X, names


def load_labels(path):
    if not Path(path).exists():
        return None
    out = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        out[r["prompt_id"]] = r["labels"]
    return out


def check_trainable(labels, min_per_label: int):
    """Raise SystemExit unless every label has >= min_per_label non-null values
    with both classes present. This is the M3 LABEL GATE."""
    if labels is None:
        raise SystemExit("[jlens] REFUSE: label file missing. "
                         "Provide human labels before training.")
    non_null = {L: [] for L in LABELS}
    for rec in labels.values():
        for L in LABELS:
            v = rec.get(L)
            if v is not None:
                non_null[L].append(bool(v))
    problems = []
    for L in LABELS:
        vals = non_null[L]
        if len(vals) < min_per_label:
            problems.append(f"{L}: {len(vals)} non-null (< {min_per_label})")
        elif len(set(vals)) < 2:
            problems.append(f"{L}: only one class present")
    if problems:
        raise SystemExit(
            "[jlens] REFUSE to train — labels not ready (human labeling "
            "required). Per-label issues:\n  " + "\n  ".join(problems) +
            "\n  See LABELING_HANDOFF.md. Never fabricate labels.")


def build_models():
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: F401
    from sklearn.linear_model import LogisticRegression
    from sklearn.neural_network import MLPClassifier
    from sklearn.svm import SVC

    return {
        "logreg_cal": CalibratedClassifierCV(
            LogisticRegression(max_iter=3000), method="isotonic", cv=3),
        "linsvm_cal": CalibratedClassifierCV(
            SVC(kernel="linear", probability=False), method="isotonic", cv=3),
        "tiny_mlp_cal": CalibratedClassifierCV(
            MLPClassifier(hidden_layer_sizes=(32,), max_iter=1500),
            method="isotonic", cv=3),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--features", default="reports/features/r4_risk_features.jsonl")
    ap.add_argument("--labels", default="data/labels/risk_labels_seed.jsonl")
    ap.add_argument("--min-per-label", type=int, default=10)
    ap.add_argument("--out", default="reports/risk_heads.json")
    args = ap.parse_args(argv)

    X, feat_names = load_features(args.features)
    labels = load_labels(args.labels)

    # LABEL GATE — refuses on the all-null seed (nonzero exit).
    check_trainable(labels, args.min_per_label)

    # ---- Reached only when human labels exist (not this milestone) ----
    from sklearn.model_selection import StratifiedGroupKFold  # noqa: F401
    print(f"[jlens] labels ready — {len(X)} prompts, {len(feat_names)} features. "
          "Training calibrated heads per label...")
    # (training body intentionally minimal in the scaffolding milestone)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(
        {"status": "labels_present_training_not_implemented_in_scaffold",
         "features": feat_names, "models": list(build_models())}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
