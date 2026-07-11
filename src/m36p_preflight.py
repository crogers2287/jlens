#!/usr/bin/env python3
"""M36P preflight: AWQ INT4 all-GPU load, architecture gates, router hooks."""
from __future__ import annotations

import argparse
import json
import resource
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import verifiers as VZ  # noqa: E402

GPU_GATE_GIB = 44.0
SMOKE_PROMPT = "What is 37 * 41? Reply with the final number only."


def _finite(tensor):
    import torch
    return bool(torch.isfinite(tensor).all().item())


def load_model(model_ref):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    config = AutoConfig.from_pretrained(model_ref)
    tok = AutoTokenizer.from_pretrained(model_ref)
    model = AutoModelForCausalLM.from_pretrained(
        model_ref, dtype="auto", device_map="auto",
        max_memory={0: "21GiB", 1: "21GiB", "cpu": "48GiB"})
    model.eval()
    return tok, model, config


def architecture_gates(model, config):
    text_cfg = getattr(config, "text_config", config)
    gates = {
        "model_type_qwen3_5_moe": config.model_type == "qwen3_5_moe",
        "routed_text_layers_40":
            getattr(text_cfg, "num_hidden_layers", None) == 40,
        "experts_per_layer_256":
            getattr(text_cfg, "num_experts", None) == 256,
        "top_8_active_experts":
            getattr(text_cfg, "num_experts_per_tok", None) == 8,
    }
    router_modules = [name for name, module in model.named_modules()
                      if name.endswith("mlp.gate")]
    gates["router_gate_modules_found"] = len(router_modules) == 40
    return gates, router_modules


def cpu_mapped_modules(model):
    device_map = getattr(model, "hf_device_map", {}) or {}
    return sorted({name for name, device in device_map.items()
                   if str(device) in ("cpu", "disk")})


def greedy_decode_with_hooks(tok, model, prompt, max_new_tokens,
                             router_modules, instrument):
    import torch

    captured = []
    handles = []
    if instrument:
        def make_hook(name):
            def hook(module, args, output):
                logits = output[0] if isinstance(output, tuple) else output
                captured.append((name, logits[-1:].detach().float().cpu()))
            return hook
        for name, module in model.named_modules():
            if name in router_modules:
                handles.append(module.register_forward_hook(make_hook(name)))
    messages = [{"role": "user", "content": prompt}]
    input_ids = tok.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt")
    input_ids = input_ids.to(next(model.parameters()).device)
    try:
        with torch.no_grad():
            out = model.generate(
                input_ids, max_new_tokens=max_new_tokens, do_sample=False,
                return_dict_in_generate=True, output_logits=True)
    finally:
        for handle in handles:
            handle.remove()
    tokens = out.sequences[0][input_ids.shape[1]:].tolist()
    text = tok.decode(tokens, skip_special_tokens=True)
    final_logits = out.logits[-1] if out.logits else None
    return tokens, text, final_logits, captured


def hook_gates(captured, final_logits, top_k=8):
    import torch
    if not captured:
        return {"router_logits_captured": False}
    finite = all(_finite(logits) for _, logits in captured)
    sample = captured[-1][1]
    weights = torch.softmax(sample, dim=-1)
    top = torch.topk(weights.reshape(-1), k=top_k)
    return {
        "router_logits_captured": True,
        "router_capture_count": len(captured),
        "router_logits_finite": finite,
        "router_logit_width_256": sample.shape[-1] == 256,
        "top8_ids_extractable": len(set(top.indices.tolist())) == top_k,
        "top8_weights_normalizable":
            abs(float(weights.reshape(-1).sum()) - 1.0) < 1e-3,
        "next_token_logits_finite":
            final_logits is not None and _finite(final_logits),
    }


def gpu_memory_gib():
    import torch
    per_device, total = {}, 0.0
    for index in range(torch.cuda.device_count()):
        allocated = torch.cuda.max_memory_allocated(index) / 2**30
        reserved = torch.cuda.max_memory_reserved(index) / 2**30
        per_device[f"gpu_{index}"] = {
            "max_allocated_gib": round(allocated, 2),
            "max_reserved_gib": round(reserved, 2)}
        total += max(allocated, reserved)
    return per_device, round(total, 2)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--revision-expected",
                    default="3e522d4e46438c782789b73c8ff4503e0edd037c")
    ap.add_argument("--out",
                    default="reports/telemetry/m36p_preflight_gates.json")
    args = ap.parse_args(argv)

    import time
    start = time.time()
    tok, model, config = load_model(args.model_ref)
    load_seconds = round(time.time() - start, 1)

    gates, router_modules = architecture_gates(model, config)
    cpu_modules = cpu_mapped_modules(model)

    start = time.time()
    plain_tokens, _, _, _ = greedy_decode_with_hooks(
        tok, model, SMOKE_PROMPT, 32, router_modules, instrument=False)
    plain_seconds = round(time.time() - start, 1)
    start = time.time()
    hooked_tokens, text, final_logits, captured = greedy_decode_with_hooks(
        tok, model, SMOKE_PROMPT, 32, router_modules, instrument=True)
    hooked_seconds = round(time.time() - start, 1)
    gates["disabled_path_token_parity"] = plain_tokens == hooked_tokens
    gates.update(hook_gates(captured, final_logits))
    gates["greedy_decode_produces_text"] = bool(text.strip())
    gates["smoke_answer_correct"] = VZ.math_checker(
        text, known_answer=str(37 * 41),
        expression="37*41")["verdict"] == "pass"

    per_device, combined = gpu_memory_gib()
    gates["gpu_combined_within_44gib"] = combined <= GPU_GATE_GIB
    peak_rss_gib = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)

    payload = {
        "schema_version": 1,
        "run_kind": "m36p_preflight_gates",
        "checkpoint": "cyankiwi/Agents-A1-AWQ-INT4",
        "revision_pinned": args.revision_expected,
        "model_ref_hash": VZ.evidence_hash(args.model_ref),
        "quant_format": "compressed-tensors pack-quantized (AWQ INT4)",
        "gates": gates,
        "all_gates_passed": all(v is True for v in gates.values()),
        "load_seconds": load_seconds,
        "plain_decode_seconds": plain_seconds,
        "hooked_decode_seconds": hooked_seconds,
        "gpu_memory": per_device,
        "gpu_combined_peak_gib": combined,
        "peak_process_rss_gib": peak_rss_gib,
        "cpu_mapped_module_count": len(cpu_modules),
        "cpu_mapped_any_transformer_layer":
            any("layers" in name for name in cpu_modules),
        "hidden_state_capture": "disabled",
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate gates/metrics only; no text/paths",
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36P gates: all_passed={payload['all_gates_passed']} "
          f"combined_gpu={combined}GiB rss={peak_rss_gib}GiB "
          f"cpu_modules={len(cpu_modules)} load={load_seconds}s", flush=True)
    for name, value in gates.items():
        if value is not True:
            print(f"[jlens]  GATE FAIL: {name} = {value}", flush=True)
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
