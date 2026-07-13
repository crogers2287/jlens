"""M37J Phase 1: resumable Jacobian-lens fit on the V100 pilot host.

Fits the official jlens Jacobian lens on the 100-sequence private fit
corpus with atomic per-N-prompt checkpointing (resume=True), enforces
the 30 GiB peak-memory gate, and writes an aggregate-only public result:
fit time, peak memory, prompts done, numerical health, lens sha256.
Configuration here must match the committed pre-fit manifest exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

# Pinned in the pre-fit manifest; dim_batch amended 8 -> 4 by the
# steer-0497526 manifest amendment (sole permitted change) after the
# dim_batch=8 fit breached the 30.0 GiB gate at 31.18 GiB.
DIM_BATCH = 4
MAX_SEQ_LEN = 128
SKIP_FIRST = 16
CHECKPOINT_EVERY = 5
MEMORY_GATE_GIB = 30.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--lens-out", required=True)
    ap.add_argument("--result-out", required=True)
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from jlens.hf import from_hf
    from jlens.fitting import fit

    prompts = [json.loads(line)["text"]
               for line in Path(args.corpus).read_text().splitlines()
               if json.loads(line)["split"] == "fit"]
    assert len(prompts) == 100, len(prompts)

    device = "cuda:0"
    torch.zeros(1, device=device)  # init CUDA context before memory APIs
    torch.cuda.reset_peak_memory_stats(device)

    t0 = time.time()
    hf_model = AutoModelForCausalLM.from_pretrained(
        args.model_ref, dtype=torch.float16, device_map={"": device})
    hf_model.eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model_ref)
    model = from_hf(hf_model, tokenizer)
    load_s = time.time() - t0

    t0 = time.time()
    lens = fit(
        model, prompts,
        dim_batch=DIM_BATCH, max_seq_len=MAX_SEQ_LEN,
        skip_first=SKIP_FIRST,
        checkpoint_path=args.checkpoint,
        checkpoint_every=CHECKPOINT_EVERY,
        resume=True,
    )
    fit_s = time.time() - t0

    peak_alloc = torch.cuda.max_memory_allocated(device) / 2**30
    peak_reserved = torch.cuda.max_memory_reserved(device) / 2**30

    finite = all(torch.isfinite(j).all().item()
                 for j in lens.jacobians.values()) \
        if hasattr(lens, "jacobians") else None

    lens.save(args.lens_out)
    lens_sha = hashlib.sha256(Path(args.lens_out).read_bytes()).hexdigest()

    payload = {
        "schema_version": 1,
        "run_kind": "m37j_phase1_fit",
        "pilot_model": "Qwen1.5-MoE-A2.7B-Chat",
        "dim_batch": DIM_BATCH, "max_seq_len": MAX_SEQ_LEN,
        "skip_first": SKIP_FIRST, "checkpoint_every": CHECKPOINT_EVERY,
        "n_fit_prompts": len(prompts),
        "load_seconds": round(load_s, 1),
        "fit_seconds": round(fit_s, 1),
        "peak_allocated_gib": round(peak_alloc, 2),
        "peak_reserved_gib": round(peak_reserved, 2),
        "memory_gate_gib": MEMORY_GATE_GIB,
        "memory_gate_passed": peak_reserved <= MEMORY_GATE_GIB,
        "jacobians_finite": finite,
        "lens_sha256": lens_sha,
        "privacy_check_status": "aggregate fit metrics only",
    }
    Path(args.result_out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[m37j] fit done: {fit_s:.0f}s peak={peak_reserved:.2f}GiB "
          f"gate={'PASS' if payload['memory_gate_passed'] else 'FAIL'} "
          f"finite={finite} lens={lens_sha[:16]}", flush=True)
    return 0 if payload["memory_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
