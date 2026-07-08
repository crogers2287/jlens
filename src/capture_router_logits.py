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
    p.add_argument("--max-gpu-mem-gib", type=float, default=23.0,
                   help="per-GPU max_memory cap passed to accelerate "
                        "(default 23.0 for an empty 24GiB 3090)")
    p.add_argument("--router-only", "--no-hidden-states", dest="router_only",
                   action="store_true",
                   help="do not request or store hidden states (router logits "
                        "only) — smaller payload; DecodeGuard needs no hidden "
                        "states")
    p.add_argument("--overwrite", action="store_true",
                   help="re-capture prompts whose output .pt already exists "
                        "(default: skip existing valid captures / resume)")
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
    # Multimodal wrappers (…ForConditionalGeneration) nest the LM config under
    # text_config (e.g. Qwen3.6-35B-A3B: text_config.num_experts=256).
    moe_cfg = getattr(config, "text_config", None) or config
    if not hasattr(moe_cfg, "num_experts") and not hasattr(moe_cfg, "num_local_experts"):
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
    # accelerate's auto-map default headroom spills modules to CPU even when
    # both 3090s are empty; bnb-4bit then refuses to load. Cap explicitly.
    if torch.cuda.is_available():
        kwargs["max_memory"] = {
            i: f"{args.max_gpu_mem_gib}GiB" for i in range(torch.cuda.device_count())
        }
        if args.dtype == "bf16":
            # bf16 (~66GiB weights) can't fit 2x3090 — the fused 3D expert
            # tensors (32.7B of 34.7B params, meta-verified 2026-07-08) are
            # invisible to bnb, so nf4 is a dead end for qwen3_5_moe. Allow
            # accelerate to stream the overflow from RAM; prefill-only capture
            # makes the PCIe cost irrelevant. Cap below the 60GiB available so
            # the OS/tokenizer keep headroom.
            kwargs["max_memory"]["cpu"] = "52GiB"
            kwargs["offload_folder"] = None  # RAM only, never disk
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


def _final_logit_stats(logits, tok_id):
    """entropy (nats) of softmax(final logits) + prob of the chosen token."""
    import torch

    probs = torch.softmax(logits.float(), dim=-1)
    ent = float(-(probs * probs.clamp_min(1e-12).log()).sum(-1).mean())
    return ent, float(probs.reshape(-1)[tok_id].item())


def capture_one(tok, model, text: str, max_prompt_tokens: int,
                max_new_tokens: int = 0, router_only: bool = False):
    """Prefill capture; when max_new_tokens>0 ALSO greedily decodes that many
    tokens, capturing per-generated-token router logits, final-logit entropy,
    and the selected-token probability.

    Returns (input_ids, prefill_router, prefill_hidden, decode_steps).
    prefill_hidden is None when router_only=True (hidden states not requested).
    decode_steps is None when max_new_tokens==0 (prefill-only, no regression).
    Each decode step is a dict:
      {generated_token_index, generated_token_id, generated_token_text,
       selected_token_prob, entropy_final_logits, router_logits[per-layer]}
    router_logits on a step are the routing activations of the forward pass
    that CONSUMED that generated token; entropy/prob are the predictive-
    distribution stats that SELECTED it.
    """
    import torch

    ids = tok(text, return_tensors="pt", truncation=True,
              max_length=max_prompt_tokens)
    ids = {k: v.to(model.device) for k, v in ids.items()}
    want_decode = max_new_tokens > 0
    with torch.inference_mode():
        out = model(**ids, output_router_logits=True,
                    output_hidden_states=not router_only, use_cache=want_decode)
    # Stream everything to CPU fp16 immediately to free GPU activations.
    router = [r.squeeze(0).to("cpu", torch.float16) for r in out.router_logits]
    hidden = (None if router_only else
              [h.squeeze(0).to("cpu", torch.float16) for h in out.hidden_states])
    input_ids = ids["input_ids"].squeeze(0).cpu()

    if not want_decode:
        return input_ids, router, hidden, None

    decode_steps = []
    past = out.past_key_values
    next_logits = out.logits[:, -1, :]  # predicts the first generated token
    eos = getattr(tok, "eos_token_id", None)
    for step in range(max_new_tokens):
        tok_id = int(next_logits.argmax(-1).item())
        ent, sel_prob = _final_logit_stats(next_logits, tok_id)
        with torch.inference_mode():
            out = model(input_ids=torch.tensor([[tok_id]], device=model.device),
                        past_key_values=past, output_router_logits=True,
                        use_cache=True)
        past = out.past_key_values
        decode_steps.append({
            "generated_token_index": step,
            "generated_token_id": tok_id,
            "generated_token_text": tok.decode([tok_id]),
            "selected_token_prob": sel_prob,
            "entropy_final_logits": ent,
            "router_logits": [r.squeeze(0).to("cpu", torch.float16)
                              for r in out.router_logits],
        })
        if eos is not None and tok_id == eos:
            break
        next_logits = out.logits[:, -1, :]
    return input_ids, router, hidden, decode_steps


def _valid_capture(path: Path) -> bool:
    """True if path exists and loads as a capture with router_logits (resume-skip)."""
    if not path.exists():
        return False
    try:
        import torch
        d = torch.load(path, map_location="cpu", weights_only=False)
        return isinstance(d, dict) and bool(d.get("router_logits"))
    except Exception:
        return False  # corrupt/partial -> re-capture


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    import torch  # deferred so --help works without GPU deps

    tok, model, cfg = load_model(args)
    n = skipped = 0
    with open(args.prompts, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            dest = out_dir / f"{rec['id']}.pt"
            if not args.overwrite and _valid_capture(dest):
                skipped += 1
                print(f"[jlens] skip {rec['id']}: existing valid capture "
                      f"(use --overwrite to replace)")
                continue
            input_ids, router, hidden, decode_steps = capture_one(
                tok, model, rec["text"], args.max_prompt_tokens,
                max_new_tokens=args.max_new_tokens, router_only=args.router_only)
            payload = {
                "prompt_id": rec["id"],
                "input_ids": input_ids,
                "router_logits": router,
                "hidden_states": hidden,  # None when --router-only
                "model_type": cfg.model_type,
                "model_path": str(args.model),
            }
            if decode_steps is not None:
                payload["decode_steps"] = decode_steps
            torch.save(payload, dest)
            n += 1
            gen = f", {len(decode_steps)} gen tokens" if decode_steps else ""
            hid = "0 (router-only)" if hidden is None else str(len(hidden))
            print(f"[jlens] captured {rec['id']}: "
                  f"{len(router)} router layers, {hid} hidden layers, "
                  f"{input_ids.shape[0]} tokens{gen}")
    print(f"[jlens] done — {n} captured, {skipped} skipped -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
