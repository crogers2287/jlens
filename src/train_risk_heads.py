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
    """Back-compat: {prompt_id: labels-dict}. Accepts a file or glob/dir of v1/v2 JSONL."""
    recs = load_records(path)
    if recs is None:
        return None
    return {r["prompt_id"]: r["labels"] for r in recs}


def load_records(path):
    """Full label records from a file, a glob, or a directory of *.jsonl (v1/v2)."""
    import glob
    if path is None:
        return None
    paths = ([path] if Path(path).is_file()
             else sorted(glob.glob(f"{path}/*.jsonl")) if Path(path).is_dir()
             else sorted(glob.glob(path)))
    if not paths:
        return None
    out = []
    for p in paths:
        for line in open(p, encoding="utf-8"):
            out.append(json.loads(line))
    return out or None


def check_trainable(labels, min_per_label: int):
    """M3 LABEL GATE: raise SystemExit unless EVERY label has >= min_per_label
    non-null values with both classes. Kept for eval + the all-null seed check."""
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


# Tiers acceptable per training mode. Prototype may use benchmark_gold; FINAL
# threshold calibration requires human-audited gold only.
MODE_TIERS = {"prototype": {"benchmark_gold", "gold"}, "final": {"gold"}}


def trainable_labels(records, min_per_label: int, mode: str):
    """Per-label coverage gate honoring the training mode's allowed tiers.
    Returns (passing_labels, diagnostics). A label passes if it has >=
    min_per_label non-null values of the ALLOWED TIER with both classes."""
    allowed = MODE_TIERS[mode]
    counts = {L: {"true": 0, "false": 0} for L in LABELS}
    for r in records:
        if r.get("label_source", "gold") not in allowed:
            continue  # wrong tier for this mode (e.g. benchmark_gold in final)
        for L in LABELS:
            v = r["labels"].get(L)
            if v is True:
                counts[L]["true"] += 1
            elif v is False:
                counts[L]["false"] += 1
    passing, diag = [], {}
    for L in LABELS:
        t, f = counts[L]["true"], counts[L]["false"]
        ok = t >= 1 and f >= 1 and min(t, f) >= min_per_label
        diag[L] = {"n_true": t, "n_false": f, "pass": ok}
        if ok:
            passing.append(L)
    return passing, diag


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
    ap.add_argument("--labels", default="data/labels/risk_labels_seed.jsonl",
                    help="file, glob, or dir of v1/v2 label JSONL")
    ap.add_argument("--mode", choices=["prototype", "final"], default="prototype",
                    help="prototype: benchmark_gold allowed; final: gold only")
    ap.add_argument("--min-per-label", type=int, default=10)
    ap.add_argument("--out", default="reports/risk_heads.json")
    args = ap.parse_args(argv)

    X, feat_names = load_features(args.features)
    records = load_records(args.labels)
    if records is None:
        raise SystemExit(f"[jlens] REFUSE: no label records at {args.labels!r}. "
                         "Provide labels (see LABELING_HANDOFF.md).")

    # COVERAGE GATE — select only labels with enough both-class data of the
    # mode's allowed tier. Refuse if none pass. NEVER fabricates labels.
    passing, diag = trainable_labels(records, args.min_per_label, args.mode)
    if not passing:
        lines = [f"{L}: n_true={d['n_true']} n_false={d['n_false']}"
                 for L, d in diag.items()]
        raise SystemExit(
            f"[jlens] REFUSE to train (mode={args.mode}) — no label passes the "
            f"coverage gate (need >= {args.min_per_label} of BOTH classes at "
            f"tier {sorted(MODE_TIERS[args.mode])}). Per-label:\n  "
            + "\n  ".join(lines) +
            ("\n  final calibration requires human-audited GOLD labels; "
             "benchmark_gold only qualifies for --mode prototype."
             if args.mode == "final" else
             "\n  Add sources/negatives (see coverage report) or human labels."))

    # ---- Reached only when the coverage gate passes for >=1 label ----
    print(f"[jlens] mode={args.mode}: coverage gate PASSES for {passing}. "
          f"{len(X)} feature prompts, {len(feat_names)} features. "
          "Prototype-training calibrated heads for the passing labels...")
    if args.mode == "final":
        print("[jlens] NOTE: final-threshold calibration on gold-tier labels.")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(
        {"status": "coverage_gate_passed_training_not_implemented_in_scaffold",
         "mode": args.mode, "trainable_labels": passing,
         "features": feat_names, "models": list(build_models())}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
