#!/usr/bin/env python3
"""Sidecar head bakeoff: domain classifiers on routing signatures (schema v1).

Feature per prompt: per-layer expert-usage histogram (fraction of top-k
selections landing on each expert), concatenated across layers → one vector.
This is the prompt-level routing signature the sidecar reads at prefill.

Models compared: nearest-centroid, logistic regression, linear SVM, GBM
(HistGradientBoosting), tiny MLP. Evaluation: StratifiedGroupKFold with each
prompt as its own group (n=32, 8 domains × 4). Metrics: domain accuracy,
top-2 accuracy, and expected calibration error (ECE) for models with
predict_proba. Latency = mean per-prompt predict time (sidecar overhead proxy).

CLI:
  python src/sidecar_bakeoff.py reports/schema/r3.jsonl --json PATH
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np


def load_signatures(jsonl_path: str | Path):
    """schema v1 JSONL -> X (prompts x layers*experts hist), y, groups."""
    X, y, groups = [], [], []
    for i, line in enumerate(open(jsonl_path, encoding="utf-8")):
        obj = json.loads(line)
        ne, tk = obj["num_experts"], obj["top_k"]
        feats = []
        for layer in obj["layers"]:
            hist = np.zeros(ne, dtype=np.float32)
            picks = [e for row in layer["topk_experts"] for e in row]
            for e, c in Counter(picks).items():
                hist[e] = c
            hist /= max(len(picks), 1)
            feats.append(hist)
        X.append(np.concatenate(feats))
        y.append(obj["domain"])
        groups.append(i)  # each prompt its own group
    return np.stack(X), np.array(y), np.array(groups)


def ece(probs: np.ndarray, correct: np.ndarray, n_bins: int = 10) -> float:
    """Expected calibration error over max-prob confidence bins."""
    conf = probs.max(axis=1)
    edges = np.linspace(0, 1, n_bins + 1)
    e = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            e += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return float(e)


def build_models():
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import NearestCentroid
    from sklearn.neural_network import MLPClassifier
    from sklearn.svm import SVC

    return {
        "nearest_centroid": (NearestCentroid(), False),
        "logreg": (LogisticRegression(max_iter=3000, C=1.0), True),
        "linear_svm": (SVC(kernel="linear", probability=True, C=1.0), True),
        "hist_gbm": (HistGradientBoostingClassifier(max_iter=200,
                                                    learning_rate=0.1), True),
        "tiny_mlp": (MLPClassifier(hidden_layer_sizes=(64,), max_iter=1500,
                                   early_stopping=False), True),
    }


def evaluate(X, y, groups):
    from sklearn.base import clone
    from sklearn.model_selection import StratifiedGroupKFold

    classes = sorted(set(y))
    cls_idx = {c: i for i, c in enumerate(classes)}
    chance = max(Counter(y).values()) / len(y)
    skf = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=0)

    results = {}
    for name, (proto, has_proba) in build_models().items():
        acc, top2, eces, lat = [], [], [], []
        for tr, te in skf.split(X, y, groups):
            clf = clone(proto)
            clf.fit(X[tr], y[tr])
            t0 = time.perf_counter()
            pred = clf.predict(X[te])
            lat.append((time.perf_counter() - t0) / len(te))
            acc.append((pred == y[te]).mean())
            if has_proba and hasattr(clf, "predict_proba"):
                proba = clf.predict_proba(X[te])
                order = np.argsort(-proba, axis=1)[:, :2]
                model_classes = list(clf.classes_)
                true_idx = np.array([model_classes.index(t) for t in y[te]])
                top2.append(np.mean([ti in row for ti, row in zip(true_idx, order)]))
                correct = (proba.argmax(1) == true_idx).astype(float)
                eces.append(ece(proba, correct))
        results[name] = {
            "accuracy": round(float(np.mean(acc)), 4),
            "accuracy_std": round(float(np.std(acc)), 4),
            "top2_accuracy": round(float(np.mean(top2)), 4) if top2 else None,
            "ece": round(float(np.mean(eces)), 4) if eces else None,
            "predict_latency_ms": round(float(np.mean(lat)) * 1e3, 4),
        }
    return results, chance, classes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("schema_jsonl")
    ap.add_argument("--json", metavar="PATH", default=None)
    args = ap.parse_args(argv)

    X, y, g = load_signatures(args.schema_jsonl)
    results, chance, classes = evaluate(X, y, g)
    print(f"[jlens] {len(y)} prompts, {X.shape[1]}-dim signature, "
          f"{len(classes)} domains, chance={chance:.3f}")
    print(f"{'model':18s} {'acc':>7s} {'±std':>6s} {'top2':>7s} "
          f"{'ECE':>7s} {'lat_ms':>8s}")
    ranked = sorted(results.items(), key=lambda kv: -kv[1]["accuracy"])
    for name, m in ranked:
        t2 = f"{m['top2_accuracy']:.3f}" if m["top2_accuracy"] is not None else "  -  "
        ec = f"{m['ece']:.3f}" if m["ece"] is not None else "  -  "
        print(f"{name:18s} {m['accuracy']:7.3f} {m['accuracy_std']:6.3f} "
              f"{t2:>7s} {ec:>7s} {m['predict_latency_ms']:8.3f}")
    best = ranked[0][0]
    print(f"[jlens] best head: {best} (acc {results[best]['accuracy']:.3f} "
          f"vs chance {chance:.3f})")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "n_prompts": int(len(y)), "n_features": int(X.shape[1]),
            "domains": classes, "chance": chance,
            "results": results, "best_head": best,
        }, indent=1))
        print(f"[jlens] report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
