#!/usr/bin/env python3
"""Load and summarize jlens capture files produced by capture_router_logits.py.

CPU-only analysis side. Provides:
  - load_capture(path) -> dict
  - iter_captures(dir) -> generator of dicts
  - routing_summary(capture, top_k=2) -> per-layer expert-usage stats
  - CLI: python src/load_captures.py data/captures/run1 [--top-k 2]

Expert-usage stats per layer:
  - entropy of the token->expert assignment distribution (nats)
  - top-k expert load fractions (how concentrated routing is)
  - number of dead experts (never selected in top-k for any token)
"""
from __future__ import annotations

import argparse
import math
from collections import Counter
from pathlib import Path


def load_capture(path: str | Path) -> dict:
    import torch
    return torch.load(Path(path), map_location="cpu", weights_only=False)


def iter_captures(dir_path: str | Path):
    for p in sorted(Path(dir_path).glob("*.pt")):
        yield p.name, load_capture(p)


def routing_summary(capture: dict, top_k: int = 2) -> list[dict]:
    """Per-layer routing stats from stored router logits [(T, E) per layer]."""
    import torch

    layers = []
    for li, logits in enumerate(capture["router_logits"]):
        t, e = logits.shape
        picks = torch.topk(logits.float(), k=min(top_k, e), dim=-1).indices  # (T, k)
        counts = Counter(picks.flatten().tolist())
        total = sum(counts.values())
        probs = [c / total for c in counts.values()]
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        max_entropy = math.log(e)
        top_loads = sorted(probs, reverse=True)[:5]
        layers.append({
            "layer": li,
            "tokens": t,
            "experts": e,
            "active_experts": len(counts),
            "dead_experts": e - len(counts),
            "entropy_nats": round(entropy, 4),
            "entropy_frac_of_max": round(entropy / max_entropy, 4) if max_entropy else 0.0,
            "top5_load_frac": [round(p, 4) for p in top_loads],
        })
    return layers


def aggregate_usage(captures_dir: str | Path, top_k: int) -> list[dict]:
    """Merge top-k expert selections across ALL captures, per layer.

    Per-prompt dead-expert counts are meaningless for short prompts
    (12 prompts x ~100 tokens can't touch 256 experts x 40 layers), so
    corpus-level aggregation is the number that matters.
    """
    import torch

    per_layer: dict[int, Counter] = {}
    experts_per_layer: dict[int, int] = {}
    tokens_total = 0
    n_caps = 0
    for _, cap in iter_captures(captures_dir):
        n_caps += 1
        tokens_total += cap["router_logits"][0].shape[0]
        for li, logits in enumerate(cap["router_logits"]):
            t, e = logits.shape
            experts_per_layer[li] = e
            picks = torch.topk(logits.float(), k=min(top_k, e), dim=-1).indices
            per_layer.setdefault(li, Counter()).update(picks.flatten().tolist())

    rows = []
    for li in sorted(per_layer):
        counts, e = per_layer[li], experts_per_layer[li]
        total = sum(counts.values())
        probs = [c / total for c in counts.values()]
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        rows.append({
            "layer": li,
            "experts": e,
            "captures": n_caps,
            "tokens": tokens_total,
            "active_experts": len(counts),
            "dead_experts": e - len(counts),
            "entropy_nats": round(entropy, 4),
            "entropy_frac_of_max": round(entropy / math.log(e), 4),
            "top5_load_frac": sorted(
                (round(p, 4) for p in probs), reverse=True)[:5],
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captures_dir")
    ap.add_argument("--top-k", type=int, default=8,
                    help="routing top-k to assume when counting selections "
                         "(default 8 = Qwen3.5/3.6 MoE num_experts_per_tok)")
    ap.add_argument("--json", metavar="PATH", default=None,
                    help="also write per-capture + aggregate summaries as JSON")
    args = ap.parse_args(argv)

    n = 0
    report: dict = {"top_k": args.top_k, "captures": {}, "aggregate": []}
    for name, cap in iter_captures(args.captures_dir):
        n += 1
        print(f"== {name} ({cap.get('model_type', '?')}) ==")
        rows = routing_summary(cap, top_k=args.top_k)
        report["captures"][name] = rows
        for row in rows:
            print(
                f"  L{row['layer']:02d}: {row['active_experts']}/{row['experts']} "
                f"experts active, {row['dead_experts']} dead, "
                f"H={row['entropy_nats']} ({row['entropy_frac_of_max']:.0%} of max), "
                f"top5={row['top5_load_frac']}"
            )
    if n == 0:
        print(f"[jlens] no .pt captures found in {args.captures_dir}")
        return 1

    print(f"== aggregate over {n} captures ==")
    agg = aggregate_usage(args.captures_dir, args.top_k)
    report["aggregate"] = agg
    for row in agg:
        print(
            f"  L{row['layer']:02d}: {row['active_experts']}/{row['experts']} "
            f"active, {row['dead_experts']} dead, "
            f"H={row['entropy_nats']} ({row['entropy_frac_of_max']:.0%} of max)"
        )
    if args.json:
        import json
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
        print(f"[jlens] report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
