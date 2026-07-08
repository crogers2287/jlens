#!/usr/bin/env python3
"""Capture per-layer router logits + hidden states from a Qwen3.5/3.6 MoE model.

Part of jlens (interpretability sidecar). Verified against transformers 5.13.0:
  - Qwen3_5MoeForCausalLM forward accepts output_router_logits (L1818) and
    falls back to config.output_router_logits (L1845-1846); router logits are
    emitted per-layer from Qwen3_5MoeTopKRouter (L779, F.linear at L789) and
    surfaced in the output dataclass (fields at L1229/L1242).
  - output_hidden_states is standard PreTrainedModel plumbing.

VRAM plan (see STATE.md iter 4): 4-bit NF4 35B-A3B ~= 19.3 GB weights ->
device_map="auto" across 2x RTX 3090. Captures are streamed to CPU per
forward: hidden states ~400 MB / 1k tokens, router logits ~12 MB / 1k tokens.

GATED prerequisites (do not run until user approves):
  1. bitsandbytes not yet installed (pip download — needs approval).
  2. Both 3090s currently serve llama-swap; needs a temporary unload window.

Usage:
  python src/capture_router_logits.py \
      --model /path/to/Qwen3.5-35B-A3B --prompts data/prompts.jsonl \
      --out data/captures/run1 [--max-new-tokens 0] [--dtype nf4|bf16]

Outputs (one .pt file per prompt in --out):
  {"prompt_id", "input_ids", "router_logits": [L x (T, E)] fp16 cpu,
   "hidden_states": [L+1 x (T, H)] fp16 cpu, "model_type", "revision"}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--model", required=True, help="HF model path or id")
    p.add_argument("--prompts", required=True,
                   help="JSONL with {'id': str, 'text': str} per line")
    p.add_argument("--out", required=True, help="output directory for .pt files")
    p.add_argument("--dtype", choices=["nf4", "bf16"], default="nf4",
                   help="nf4 = 4-bit bitsandbytes (default), bf16 = full")
    p.add_argument("--max-new-tokens", type=int, default=0,
                   help="0 = prefill-only capture (default); >0 also captures "
                        "per-step logits during greedy decode")
    p.add_argument("--max-prompt-tokens", type=int, default=4096)
    p.add_argument("--device-map", default="auto")
    p.add_argument("--trust-remote-code", action="store_true",
                   help="needed only if model_type is not in transformers "
                        "(e.g. a qwen3_6 arch newer than the installed lib)")
    return p.parse_args(argv)


def check_arch(config) -> None:
    """Fail fast with a clear message if the checkpoint arch is unsupported."""
    known = {"qwen3_5_moe", "qwen3_next", "qwen2_moe", "qwen3_moe"}
    mt = getattr(config, "model_type", "?")
    if mt not in known:
        sys.exit(
            f"[jlens] model_type={mt!r} not in verified set {sorted(known)}. "
            "transformers 5.13.0 has no qwen3_6 arch — check config.json or "
            "retry with --trust-remote-code (records a Decision in STATE.md "
            "first)."
        )
    if not hasattr(config, "num_experts") and not hasattr(config, "num_local_experts"):
        sys.exit(f"[jlens] {mt} config has no expert count — not a MoE checkpoint?")


def load_model(args):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    cfg = AutoConfig.from_pretrained(args.model,
                                     trust_remote_code=args.trust_remote_code)
    check_arch(cfg)

    kwargs: dict = dict(
        device_map=args.device_map,
        trust_remote_code=args.trust_remote_code,
        torch_dtype=torch.bfloat16,
    )
    if args.dtype == "nf4":
        from transformers import BitsAndBytesConfig  # requires bitsandbytes
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
    tok = AutoTokenizer.from_pretrained(args.model,
                                        trust_remote_code=args.trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(args.model, **kwargs)
    model.eval()
    return tok, model, cfg


def capture_one(tok, model, text: str, max_prompt_tokens: int):
    import torch

    ids = tok(text, return_tensors="pt", truncation=True,
              max_length=max_prompt_tokens)
    ids = {k: v.to(model.device) for k, v in ids.items()}
    with torch.inference_mode():
        out = model(**ids, output_router_logits=True,
                    output_hidden_states=True, use_cache=False)
    # Stream everything to CPU fp16 immediately to free GPU activations.
    router = [r.squeeze(0).to("cpu", torch.float16) for r in out.router_logits]
    hidden = [h.squeeze(0).to("cpu", torch.float16) for h in out.hidden_states]
    return ids["input_ids"].squeeze(0).cpu(), router, hidden


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    import torch  # deferred so --help works without GPU deps

    tok, model, cfg = load_model(args)
    n = 0
    with open(args.prompts, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            input_ids, router, hidden = capture_one(
                tok, model, rec["text"], args.max_prompt_tokens)
            torch.save(
                {
                    "prompt_id": rec["id"],
                    "input_ids": input_ids,
                    "router_logits": router,
                    "hidden_states": hidden,
                    "model_type": cfg.model_type,
                    "model_path": str(args.model),
                },
                out_dir / f"{rec['id']}.pt",
            )
            n += 1
            print(f"[jlens] captured {rec['id']}: "
                  f"{len(router)} router layers, {len(hidden)} hidden layers, "
                  f"{input_ids.shape[0]} tokens")
    print(f"[jlens] done — {n} prompts -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
