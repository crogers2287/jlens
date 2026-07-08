#!/usr/bin/env python3
"""Token-level domain probe on MoE routing, with prompt-held-out splits.

Each token contributes one sample: its per-layer top-k expert multi-hot
vector (optionally a single layer). Splits are grouped by prompt so no
tokens from a test prompt ever appear in training (no leakage).

CLI:
  python src/token_probe.py data/captures/run [--top-k 8] [--layer N]
                            [--json PATH]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from expert_overlap import domain_of
from load_captures import iter_captures


def build_token_features(captures_dir: str | Path, top_k: int,
                         layer: int | None):
    """Returns X (tokens x feat), y (domain), g (prompt group id)."""
    import torch

    X, y, g = [], [], []
    for gi, (name, cap) in enumerate(iter_captures(captures_dir)):
        dom = domain_of(name)
        layers = cap["router_logits"]
        sel = [layers[layer]] if layer is not None else layers
        # per-token multi-hot over experts, concatenated across chosen layers
        per_layer_hots = []
        for logits in sel:
            lg = logits.float()
            n_tok, n_exp = lg.shape
            hot = torch.zeros(n_tok, n_exp)
            idx = torch.topk(lg, k=min(top_k, n_exp), dim=-1).indices
            hot.scatter_(1, idx, 1.0)
            per_layer_hots.append(hot)
        feats = torch.cat(per_layer_hots, dim=1).numpy()
        X.append(feats)
        y.extend([dom] * feats.shape[0])
        g.extend([gi] * feats.shape[0])
    return np.concatenate(X), np.array(y), np.array(g)


def grouped_cv_accuracy(X, y, g, n_splits: int = 4) -> float:
    # StratifiedGroupKFold: keeps each prompt's tokens wholly in one fold
    # (no leakage) AND balances domain proportions across folds. Matches
    # sidecar_bakeoff.py. Falls back to GroupKFold only if stratification is
    # infeasible (a domain with fewer prompts than n_splits).
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold, StratifiedGroupKFold

    try:
        splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True,
                                        random_state=0)
        splits = list(splitter.split(X, y, g))
    except ValueError:
        splits = list(GroupKFold(n_splits=n_splits).split(X, y, g))

    accs = []
    for tr, te in splits:
        if len(set(y[tr])) < len(set(y)):  # a domain fully held out -> skip fold
            continue
        clf = LogisticRegression(max_iter=1000, C=1.0)
        clf.fit(X[tr], y[tr])
        accs.append((clf.predict(X[te]) == y[te]).mean())
    return float(np.mean(accs)) if accs else float("nan")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captures_dir")
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--layer", type=int, default=None,
                    help="probe a single layer instead of all concatenated")
    ap.add_argument("--per-layer-sweep", action="store_true",
                    help="probe every layer individually")
    ap.add_argument("--json", metavar="PATH", default=None)
    args = ap.parse_args(argv)

    report: dict = {"top_k": args.top_k}
    if args.per_layer_sweep:
        # discover layer count from one capture
        first = next(iter_captures(args.captures_dir))[1]
        n_layers = len(first["router_logits"])
        sweep = []
        for li in range(n_layers):
            X, y, g = build_token_features(args.captures_dir, args.top_k, li)
            acc = grouped_cv_accuracy(X, y, g)
            sweep.append(round(acc, 4))
            print(f"  L{li:02d} token-acc={acc:.3f}")
        report["per_layer_token_accuracy"] = sweep
        best = int(np.nanargmax(sweep))
        print(f"[jlens] best layer L{best:02d}={sweep[best]:.3f}")
        report["best_layer"] = best
    else:
        X, y, g = build_token_features(args.captures_dir, args.top_k, args.layer)
        chance = max(Counter(y).values()) / len(y)
        acc = grouped_cv_accuracy(X, y, g)
        where = f"layer {args.layer}" if args.layer is not None else "all layers"
        print(f"[jlens] {X.shape[0]} tokens, {X.shape[1]} feats ({where})")
        print(f"  grouped-4fold token accuracy: {acc:.3f} (chance {chance:.3f})")
        report.update({"n_tokens": int(X.shape[0]), "layer": args.layer,
                       "grouped_cv_accuracy": acc, "chance": chance})

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
        print(f"[jlens] report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
