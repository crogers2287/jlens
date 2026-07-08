#!/usr/bin/env python3
"""Domain classifier probe on MoE routing signatures.

Feature per capture: per-layer expert-usage histogram (fraction of tokens
routing to each expert in top-k), concatenated across layers → one vector.
Classifier: multinomial logistic regression, leave-one-out CV (small n).

Answers: can prompt domain be predicted from routing alone, and which
layers carry the signal?

CLI:
  python src/routing_probe.py data/captures/run1 [--top-k 8] [--json PATH]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from expert_overlap import domain_of
from load_captures import iter_captures


def build_features(captures_dir: str | Path, top_k: int):
    import torch

    X, y, names = [], [], []
    n_layers = n_experts = 0
    for name, cap in iter_captures(captures_dir):
        feats = []
        for logits in cap["router_logits"]:
            n_experts = logits.shape[1]
            picks = torch.topk(logits.float(), k=min(top_k, n_experts),
                               dim=-1).indices.flatten().tolist()
            hist = np.zeros(n_experts, dtype=np.float32)
            for e, c in Counter(picks).items():
                hist[e] = c
            hist /= max(len(picks), 1)
            feats.append(hist)
        n_layers = len(feats)
        X.append(np.concatenate(feats))
        y.append(domain_of(name))
        names.append(name)
    return np.stack(X), np.array(y), names, n_layers, n_experts


def loo_accuracy(X: np.ndarray, y: np.ndarray) -> tuple[float, list]:
    from sklearn.linear_model import LogisticRegression

    hits, preds = 0, []
    for i in range(len(y)):
        mask = np.ones(len(y), bool)
        mask[i] = False
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X[mask], y[mask])
        p = clf.predict(X[i:i + 1])[0]
        preds.append(p)
        hits += int(p == y[i])
    return hits / len(y), preds


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captures_dir")
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--json", metavar="PATH", default=None)
    args = ap.parse_args(argv)

    X, y, names, n_layers, n_experts = build_features(args.captures_dir, args.top_k)
    print(f"[jlens] {len(y)} captures, {n_layers} layers x {n_experts} experts "
          f"-> {X.shape[1]}-dim features, domains={sorted(set(y))}")

    acc_full, preds = loo_accuracy(X, y)
    chance = max(Counter(y).values()) / len(y)
    print(f"  LOO accuracy (all layers): {acc_full:.3f}  (majority-chance {chance:.3f})")
    misses = [(n, t, p) for n, t, p in zip(names, y, preds) if t != p]
    for n, t, p in misses:
        print(f"    miss: {n} true={t} pred={p}")

    # per-layer probe: which depth carries the signal?
    per_layer = []
    for li in range(n_layers):
        sl = X[:, li * n_experts:(li + 1) * n_experts]
        acc, _ = loo_accuracy(sl, y)
        per_layer.append(round(acc, 4))
    best = int(np.argmax(per_layer))
    print(f"  per-layer LOO acc: best L{best:02d}={per_layer[best]:.3f}, "
          f"L00={per_layer[0]:.3f}, L{n_layers-1}={per_layer[-1]:.3f}")
    t = n_layers // 3
    print(f"  tercile means: early={np.mean(per_layer[:t]):.3f} "
          f"mid={np.mean(per_layer[t:2*t]):.3f} late={np.mean(per_layer[2*t:]):.3f}")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "top_k": args.top_k,
            "n_captures": len(y),
            "loo_accuracy_all_layers": acc_full,
            "majority_chance": chance,
            "misclassified": [{"name": n, "true": t_, "pred": p}
                              for n, t_, p in misses],
            "per_layer_loo_accuracy": per_layer,
            "best_layer": best,
        }, indent=1))
        print(f"[jlens] report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
