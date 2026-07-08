#!/usr/bin/env python3
"""Export raw .pt captures to jlens routing-signature schema v1 (JSONL).

Schema v1 is the FROZEN, versioned contract the sidecar heads consume. It
carries only router-derived signal (no hidden states, no raw logits) so the
export is small and shareable. One JSON object per prompt, one per line.

Per-object contract (see schema/v1.json for the machine-readable version):
{
  "schema_version": 1,
  "model": "Qwen/Qwen3.6-35B-A3B",
  "model_type": "qwen3_5_moe",
  "run_id": "r3",
  "prompt_id": "math_03",
  "domain": "math",
  "tokens": 28,
  "num_layers": 40,
  "num_experts": 256,
  "top_k": 8,
  "layers": [
    {
      "layer": 0,
      "logits_shape": [28, 256],
      "topk_experts": [[...8 ints...], ...per token...],
      "topk_probs":   [[...8 floats...], ...per token...],
      "entropy": 4.91          # token-mean entropy of softmax(router_logits)
    }, ...
  ]
}

CLI:
  python src/export_schema.py data/captures/qwen3_6_35b_a3b_r3 \
      --run-id r3 --out reports/schema/r3.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from expert_overlap import domain_of
from load_captures import iter_captures

SCHEMA_VERSION = 1


def export_capture(cap: dict, prompt_id: str, run_id: str, top_k: int) -> dict:
    import torch

    router = cap["router_logits"]
    num_layers = len(router)
    num_experts = router[0].shape[1]
    tokens = int(router[0].shape[0])

    layers = []
    for li, logits in enumerate(router):
        lg = logits.float()
        probs = torch.softmax(lg, dim=-1)
        # token-mean entropy over the full expert distribution (nats)
        ent = float((-(probs * torch.log(probs.clamp_min(1e-12)))
                     .sum(-1)).mean())
        tk = torch.topk(lg, k=min(top_k, num_experts), dim=-1)
        layers.append({
            "layer": li,
            "logits_shape": [tokens, num_experts],
            "topk_experts": tk.indices.tolist(),
            "topk_probs": [[round(p, 6) for p in row]
                           for row in torch.softmax(tk.values, dim=-1).tolist()],
            "entropy": round(ent, 6),
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "model": cap.get("model_path", "?"),
        "model_type": cap.get("model_type", "?"),
        "run_id": run_id,
        "prompt_id": prompt_id,
        "domain": domain_of(prompt_id),
        "tokens": tokens,
        "num_layers": num_layers,
        "num_experts": num_experts,
        "top_k": top_k,
        "layers": layers,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captures_dir")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--out", required=True, help="output .jsonl path")
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for name, cap in iter_captures(args.captures_dir):
            pid = Path(name).stem
            obj = export_capture(cap, pid, args.run_id, args.top_k)
            fh.write(json.dumps(obj) + "\n")
            n += 1
    print(f"[jlens] exported {n} prompts -> {out} (schema v{SCHEMA_VERSION})")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
