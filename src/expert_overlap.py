#!/usr/bin/env python3
"""Cross-domain expert-overlap analysis on jlens captures.

Groups captures by domain (prompt-id prefix before the last `_NN`), builds
per-layer sets of top-k-selected experts per domain, then reports:
  - pairwise Jaccard similarity of domain expert sets, per layer + averaged
  - per-domain exclusive experts (selected by exactly one domain), per layer
  - global summary: mean Jaccard by depth tercile (early/mid/late stack)

CLI:
  python src/expert_overlap.py data/captures/run1 [--top-k 8] [--json PATH]
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from load_captures import iter_captures


def domain_of(name: str) -> str:
    """code_py_01.pt -> code ; json_tool_01.pt -> json_tool ; lang_es_01 -> lang."""
    stem = Path(name).stem
    parts = stem.split("_")
    while parts and (parts[-1].isdigit() or len(parts[-1]) == 2 and parts[-1].isalpha() and parts[0] == "lang"):
        parts.pop()
    return "_".join(parts) or stem


def domain_expert_sets(captures_dir: str | Path, top_k: int):
    import torch

    sets: dict[str, dict[int, set[int]]] = defaultdict(lambda: defaultdict(set))
    n_layers = 0
    for name, cap in iter_captures(captures_dir):
        dom = domain_of(name)
        for li, logits in enumerate(cap["router_logits"]):
            picks = torch.topk(logits.float(), k=min(top_k, logits.shape[1]),
                               dim=-1).indices
            sets[dom][li].update(picks.flatten().tolist())
            n_layers = max(n_layers, li + 1)
    return sets, n_layers


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captures_dir")
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--json", metavar="PATH", default=None)
    args = ap.parse_args(argv)

    sets, n_layers = domain_expert_sets(args.captures_dir, args.top_k)
    domains = sorted(sets)
    if len(domains) < 2:
        print(f"[jlens] need >=2 domains, found {domains}")
        return 1
    print(f"[jlens] domains: {domains} | layers: {n_layers}")

    pair_by_layer: dict[str, list[float]] = {}
    for a, b in combinations(domains, 2):
        key = f"{a}|{b}"
        pair_by_layer[key] = [
            round(jaccard(sets[a][li], sets[b][li]), 4) for li in range(n_layers)
        ]

    # per-layer mean across pairs + depth-tercile summary
    layer_means = [
        round(sum(v[li] for v in pair_by_layer.values()) / len(pair_by_layer), 4)
        for li in range(n_layers)
    ]
    t = n_layers // 3
    terciles = {
        "early(L0..)": round(sum(layer_means[:t]) / t, 4),
        "mid": round(sum(layer_means[t:2 * t]) / t, 4),
        "late": round(sum(layer_means[2 * t:]) / (n_layers - 2 * t), 4),
    }

    exclusive = {
        dom: [
            len(sets[dom][li] - set().union(
                *(sets[d][li] for d in domains if d != dom)))
            for li in range(n_layers)
        ]
        for dom in domains
    }

    for key, vals in sorted(pair_by_layer.items()):
        mean = sum(vals) / len(vals)
        print(f"  {key:24s} meanJ={mean:.3f} min=L{vals.index(min(vals)):02d}"
              f"({min(vals):.3f}) max=L{vals.index(max(vals)):02d}({max(vals):.3f})")
    print(f"  depth terciles (mean Jaccard): {terciles}")
    for dom in domains:
        tot = sum(exclusive[dom])
        print(f"  exclusive experts {dom:12s}: total {tot:4d} "
              f"peak L{exclusive[dom].index(max(exclusive[dom])):02d}"
              f"({max(exclusive[dom])})")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "top_k": args.top_k,
            "domains": domains,
            "pairwise_jaccard_by_layer": pair_by_layer,
            "layer_mean_jaccard": layer_means,
            "depth_terciles": terciles,
            "exclusive_experts_by_layer": exclusive,
        }, indent=1))
        print(f"[jlens] report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
