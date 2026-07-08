#!/usr/bin/env python3
"""Export decode-capture .pt files to jlens decode schema v2 (JSONL).

Consumes captures produced by `capture_router_logits.py --max-new-tokens K`
(each .pt has a `decode_steps` list). Emits one JSON object per GENERATED
token: the per-layer routing signature at that step plus decode-time signal
(final-logit entropy, selected-token prob) and two routing-drift measures:

  drift_from_prefill_signature: cosine distance of the token's per-layer
    expert-usage vector from the prompt's PREFILL signature (from the same
    .pt's prefill router_logits).
  drift_from_previous_token: cosine distance from the previous generated
    token's routing (null at index 0).

Schema: schema/v2_decode.json. Prefill schema/v1.json is untouched.

CLI:
  python src/export_decode_schema.py data/captures/<run>_decode \
      --run-id r4 --top-k 8 --out reports/schema/r4_decode.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from expert_overlap import domain_of
from load_captures import iter_captures

SCHEMA_VERSION = 2


def _usage_vector(per_layer_logits, top_k: int, num_experts: int) -> np.ndarray:
    """Concatenated per-layer top-k expert-usage histogram (L*E,), L2 pieces."""
    import torch

    vecs = []
    for logits in per_layer_logits:
        lg = logits.float()
        if lg.dim() == 1:
            lg = lg.unsqueeze(0)
        hist = np.zeros(num_experts, dtype=np.float32)
        idx = torch.topk(lg, k=min(top_k, lg.shape[-1]), dim=-1).indices
        for e in idx.flatten().tolist():
            hist[e] += 1.0
        s = hist.sum()
        if s:
            hist /= s
        vecs.append(hist)
    return np.concatenate(vecs)


def _cosine_dist(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(1.0 - np.dot(a, b) / (na * nb))


def _layer_record(logits, top_k: int, num_experts: int) -> dict:
    import torch

    lg = logits.float()
    if lg.dim() == 1:
        lg = lg.unsqueeze(0)
    probs = torch.softmax(lg, dim=-1)
    ent = float((-(probs * probs.clamp_min(1e-12).log()).sum(-1)).mean())
    tk = torch.topk(lg, k=min(top_k, num_experts), dim=-1)
    # decode step is a single token -> flatten the (1,k) rows
    return {
        "topk_experts": tk.indices.reshape(-1).tolist(),
        "topk_probs": [round(p, 6) for p in
                       torch.softmax(tk.values, dim=-1).reshape(-1).tolist()],
        "full_entropy": round(ent, 6),
    }


def export_capture(cap: dict, prompt_id: str, run_id: str, top_k: int):
    steps = cap.get("decode_steps")
    if not steps:
        return []
    num_experts = cap["router_logits"][0].shape[-1]
    prefill_sig = _usage_vector(cap["router_logits"], top_k, num_experts)

    out, prev_sig = [], None
    for s in steps:
        rl = s["router_logits"]
        tok_sig = _usage_vector(rl, top_k, num_experts)
        layers = []
        for li, logits in enumerate(rl):
            rec = _layer_record(logits, top_k, num_experts)
            rec["layer"] = li
            layers.append(rec)
        out.append({
            "schema_version": SCHEMA_VERSION,
            "model": cap.get("model_path", "?"),
            "model_type": cap.get("model_type", "?"),
            "run_id": run_id,
            "prompt_id": prompt_id,
            "domain": domain_of(prompt_id),
            "generated_token_index": int(s["generated_token_index"]),
            "generated_token_id": int(s["generated_token_id"]),
            "generated_token_text": s["generated_token_text"],
            "selected_token_prob": round(float(s["selected_token_prob"]), 6),
            "entropy_final_logits": round(float(s["entropy_final_logits"]), 6),
            "num_experts": int(num_experts),
            "top_k": top_k,
            "router_layers": layers,
            "drift_from_prefill_signature": round(
                _cosine_dist(tok_sig, prefill_sig), 6),
            "drift_from_previous_token": (None if prev_sig is None else
                round(_cosine_dist(tok_sig, prev_sig), 6)),
        })
        prev_sig = tok_sig
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captures_dir")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n_prompts = n_tokens = 0
    with out.open("w", encoding="utf-8") as fh:
        for name, cap in iter_captures(args.captures_dir):
            recs = export_capture(cap, Path(name).stem, args.run_id, args.top_k)
            for r in recs:
                fh.write(json.dumps(r) + "\n")
            n_prompts += 1
            n_tokens += len(recs)
    print(f"[jlens] exported {n_tokens} decode tokens from {n_prompts} prompts "
          f"-> {out} (schema v{SCHEMA_VERSION})")
    return 0 if n_tokens else 1


if __name__ == "__main__":
    raise SystemExit(main())
