#!/usr/bin/env python3
"""M37J Phase 0: pilot-model backward-pass feasibility gate (V100 host).

Runs standalone on the lens host. Gates (docs/M37J_..._AUTOLOOP.md):
  - one 128-token forward + activation-gradient backward completes;
  - peak allocated + reserved GPU memory <= 30 GiB;
  - no unbounded CPU offload (model fully on the GPU);
  - residual-stream hidden states and final unembedding accessible;
  - the official jlens.from_hf adapter wraps the model;
  - normal forward outputs unchanged when no lens is applied.

Aggregate-only public artifact; the model path never appears in it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

GATE_GIB = 30.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--model-name", required=True,
                    help="public model identity for the artifact")
    ap.add_argument("--seq-len", type=int, default=128)
    ap.add_argument("--out", default="m37j_phase0_feasibility.json")
    args = ap.parse_args()

    import torch
    import transformers

    device = torch.device("cuda:0")
    torch.zeros(1, device=device)   # init CUDA context before stats reset
    torch.cuda.reset_peak_memory_stats(device)

    t0 = time.time()
    tok = transformers.AutoTokenizer.from_pretrained(args.model_ref)
    model = transformers.AutoModelForCausalLM.from_pretrained(
        args.model_ref, torch_dtype=torch.float16).to(device)
    model.eval()
    model.requires_grad_(False)
    load_s = round(time.time() - t0, 1)

    # All parameters on the GPU (no unbounded CPU offload).
    devices = {str(p.device) for p in model.parameters()}
    fully_on_gpu = devices == {"cuda:0"}

    text = ("Research notes: the value of careful measurement is that it "
            "turns argument into arithmetic. ") * 40
    ids = tok(text, return_tensors="pt", truncation=True,
              max_length=args.seq_len).input_ids.to(device)
    n_tokens = int(ids.shape[1])

    # Forward with residual-stream access.
    t0 = time.time()
    with torch.no_grad():
        ref_out = model(ids, output_hidden_states=True)
    forward_s = round(time.time() - t0, 2)
    n_layers = len(ref_out.hidden_states) - 1
    unembed_ok = model.get_output_embeddings() is not None

    # Activation-gradient backward smoke (the Jacobian fit pattern:
    # gradients w.r.t. activations only; parameters stay frozen).
    t0 = time.time()
    embeddings = model.get_input_embeddings()(ids).detach()
    embeddings.requires_grad_(True)
    out = model(inputs_embeds=embeddings, output_hidden_states=True)
    probe = torch.randn_like(out.hidden_states[-1])
    (out.hidden_states[-1] * probe).sum().backward()
    backward_s = round(time.time() - t0, 2)
    grad = embeddings.grad
    backward_ok = grad is not None and bool(torch.isfinite(grad).all())

    # Forward determinism with no lens applied (same inputs, no_grad).
    with torch.no_grad():
        again = model(ids, output_hidden_states=False)
    forward_unchanged = bool(torch.equal(ref_out.logits, again.logits))

    # Official adapter.
    adapter_ok, adapter_error = False, None
    jlens_version = None
    try:
        import jlens

        jlens_version = getattr(jlens, "__version__", "unversioned")
        wrapped = jlens.from_hf(model, tok)
        adapter_ok = wrapped is not None
    except Exception as exc:                     # noqa: BLE001
        adapter_error = f"{type(exc).__name__}: {exc}"

    peak_alloc = torch.cuda.max_memory_allocated(device) / 2**30
    peak_reserved = torch.cuda.max_memory_reserved(device) / 2**30

    gates = {
        "backward_smoke_completes": backward_ok,
        "peak_memory_within_30gib": peak_reserved <= GATE_GIB,
        "fully_on_gpu_no_offload": fully_on_gpu,
        "hidden_states_accessible": n_layers > 0,
        "unembedding_accessible": unembed_ok,
        "jlens_adapter_works": adapter_ok,
        "forward_unchanged_without_lens": forward_unchanged,
    }
    payload = {
        "schema_version": 1,
        "run_kind": "m37j_phase0_feasibility",
        "pilot_model": args.model_name,
        "model_ref_hash": "[h:" + hashlib.sha256(
            args.model_ref.encode()).hexdigest()[:16] + "]",
        "gpu": torch.cuda.get_device_name(device),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "jlens_version": jlens_version,
        "dtype": "float16",
        "seq_len": n_tokens,
        "n_layers": n_layers,
        "load_seconds": load_s,
        "forward_seconds": forward_s,
        "backward_seconds": backward_s,
        "peak_allocated_gib": round(peak_alloc, 2),
        "peak_reserved_gib": round(peak_reserved, 2),
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "adapter_error": adapter_error,
        "privacy_check_status": "aggregate feasibility metrics only",
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[m37j] phase0: all_gates={payload['all_gates_passed']} "
          f"peak={payload['peak_reserved_gib']}GiB layers={n_layers} "
          f"backward={backward_s}s", flush=True)
    for name, value in gates.items():
        if value is not True:
            print(f"[m37j]  GATE FAIL: {name} = {value}", flush=True)
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
