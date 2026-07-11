#!/usr/bin/env python3
"""M36V Phase 1: dispatch-validated, observation-only router telemetry gates.

Two arms, each a fresh engine (run stock first):

  --arm stock         unpatched stock vLLM (no extension, no routed-experts
                      flag); dumps greedy token ids privately as the
                      stock-parity reference.
  --arm instrumented  extension registered + enable_return_routed_experts;
                      runs the smoke set three times (pre-install,
                      installed-disabled, enabled) and evaluates all eight
                      Phase 1 gates against the stock reference.

Public artifact is aggregate-only and guarded; per-token data stays under
reports/shadow/private/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import verifiers as VZ                      # noqa: E402
from m36v_phase0 import (                   # noqa: E402
    EXPECTED_REVISION, GPU_GATE_GIB, GpuPeakSampler, smoke_prompts,
)
from jlens_vllm_telemetry.features import (  # noqa: E402
    derive_decode_records, summary_vs_raw_check,
)
from jlens_vllm_telemetry.report_guard import assert_aggregate_only  # noqa: E402

WEIGHT_IDENTITY_TOL = 1e-6     # router-return vs dispatch-entry, frozen
WEIGHT_NORMDEV_TOL = 5e-3      # |sum(top8 weights) - 1|, fp16-derived, frozen
SAMPLED_LAYER_POINTS = ("early", "middle", "late")
PRIVATE_DIR = Path("reports/shadow/private")

OVERRIDE_FILES = [
    "jlens_vllm_telemetry/__init__.py",
    "jlens_vllm_telemetry/capture.py",
    "jlens_vllm_telemetry/worker_ext.py",
    "jlens_vllm_telemetry/features.py",
    "jlens_vllm_telemetry/report_guard.py",
]


def override_hash() -> str:
    h = hashlib.sha256()
    for rel in OVERRIDE_FILES:
        h.update(rel.encode())
        h.update((ROOT / rel).read_bytes())
    return h.hexdigest()[:16]


def make_llm(model_ref: str, instrumented: bool):
    from vllm import LLM

    kwargs = dict(model=model_ref, tensor_parallel_size=2, max_model_len=1024,
                  gpu_memory_utilization=0.88, enforce_eager=True,
                  disable_log_stats=True, max_num_seqs=1)
    if instrumented:
        kwargs["enable_return_routed_experts"] = True
        kwargs["worker_extension_cls"] = (
            "jlens_vllm_telemetry.worker_ext.JlensWorkerExtension")
    return LLM(**kwargs)


def run_smoke(llm, items, max_tokens: int, want_routed: bool = False):
    """Greedy smoke pass, one prompt at a time (max_num_seqs=1 anyway).

    Returns per-prompt dicts with token ids and, when requested, the native
    routed-experts array.
    """
    from vllm import SamplingParams

    params = SamplingParams(temperature=0.0, max_tokens=max_tokens, logprobs=5)
    results = []
    for item in items:
        out = llm.chat([[{"role": "user", "content": item["prompt"]}]], params,
                       use_tqdm=False)[0]
        comp = out.outputs[0]
        rec = {
            "prompt_id": item["prompt_id"],
            "prompt_token_ids": list(out.prompt_token_ids),
            "output_token_ids": list(comp.token_ids),
            "text": comp.text,
        }
        if want_routed:
            rec["routed_experts"] = comp.routed_experts
        results.append(rec)
    return results


def ids_equal(a, b):
    return ([r["prompt_token_ids"] for r in a] ==
            [r["prompt_token_ids"] for r in b] and
            [r["output_token_ids"] for r in a] ==
            [r["output_token_ids"] for r in b])


def run_stock(args) -> int:
    sampler = GpuPeakSampler()
    sampler.start()
    llm = make_llm(args.model_ref, instrumented=False)
    items = smoke_prompts()
    results = run_smoke(llm, items, args.max_tokens)
    sampler.stop_flag = True
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    Path(args.stock_ids).write_text(
        "".join(json.dumps(r) + "\n" for r in results))
    print(f"[jlens] M36V phase1 stock arm: {len(results)} prompts, ids -> "
          f"{args.stock_ids}", flush=True)
    return 0


def _decode_rpc_array(value):
    """Decode one array field from a collective_rpc result.

    vLLM's msgpack layer encodes ndarrays as (dtype_str, shape, data)
    triples (vllm/v1/serial_utils.py:_encode_ndarray) and only rebuilds
    them for typed fields, so untyped dict values arrive as the raw
    triple. Plain nested lists (test/dry-run path) are handled too.
    """
    import numpy as np

    if isinstance(value, np.ndarray):
        return value
    if (isinstance(value, (list, tuple)) and len(value) == 3
            and isinstance(value[0], str)
            and isinstance(value[1], (list, tuple))
            and isinstance(value[2], (bytes, bytearray, memoryview))):
        dtype_str, shape, data = value
        return np.frombuffer(data, dtype=np.dtype(dtype_str)).reshape(shape)
    return np.asarray(value)


def normalize_capture(cap: dict) -> dict:
    """Coerce the array-valued capture fields back to typed ndarrays."""
    import numpy as np

    out = dict(cap)
    for key, dtype in (("ids", np.int64), ("weights", np.float64),
                       ("entropy", np.float64), ("mass", np.float64),
                       ("raw_logits_sample", np.float64)):
        if key in out:
            out[key] = _decode_rpc_array(out[key]).astype(dtype)
    return out


def run_instrumented(args) -> int:
    import numpy as np
    import torch
    import vllm

    stock = [json.loads(line)
             for line in Path(args.stock_ids).read_text().splitlines()]

    sampler = GpuPeakSampler()
    sampler.start()
    start = time.time()
    llm = make_llm(args.model_ref, instrumented=True)
    load_seconds = round(time.time() - start, 1)
    items = smoke_prompts()

    hf_config = llm.llm_engine.model_config.hf_config
    text_cfg = getattr(hf_config, "text_config", hf_config)
    num_experts = text_cfg.num_experts
    top_k = text_cfg.num_experts_per_tok

    # Arm B: extension class mixed in, telemetry not installed.
    t0 = time.time()
    arm_b = run_smoke(llm, items, args.max_tokens)
    arm_b_seconds = time.time() - t0

    # Install wrappers, keep capture disabled: still must be a no-op.
    install_info = llm.collective_rpc("jlens_install_telemetry", args=(
        {"num_experts": num_experts, "top_k": top_k,
         "capacity_tokens": 2048, "raw_sample_tokens": 64},))
    moe_layer_ids = install_info[0]["layer_ids"]
    t0 = time.time()
    arm_c = run_smoke(llm, items, args.max_tokens)
    arm_c_seconds = time.time() - t0

    # Arm D: telemetry enabled; per-prompt reset/fetch for alignment.
    llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))
    arm_d, captures = [], []
    t0 = time.time()
    for item in items:
        llm.collective_rpc("jlens_reset_telemetry")
        rec = run_smoke(llm, [item], args.max_tokens, want_routed=True)[0]
        fetches = [normalize_capture(f)
                   for f in llm.collective_rpc("jlens_fetch_telemetry")]
        arm_d.append(rec)
        captures.append(fetches)
    arm_d_seconds = time.time() - t0
    llm.collective_rpc("jlens_set_telemetry_enabled", args=(False,))

    # ---- gate evaluation -------------------------------------------------
    gates = {}
    detail = {}

    gates["stock_parity"] = ids_equal(stock, arm_b) and ids_equal(arm_b, arm_c)
    gates["observation_parity"] = ids_equal(arm_c, arm_d)

    # Architecture identity.
    gates["architecture_identity"] = (
        hf_config.model_type == "qwen3_5_moe"
        and text_cfg.num_hidden_layers == 40
        and num_experts == 256 and top_k == 8
        and len(moe_layer_ids) == 40
        and VZ.evidence_hash(args.model_ref) is not None)

    # Dispatch + weight identity, native cross-check, rank cross-check.
    id_mismatch_total = 0
    dispatch_missed_total = 0
    weight_maxdiff = 0.0
    weight_nonfinite = 0
    weight_min = float("inf")
    weight_normdev = 0.0
    native_mismatch_rows = 0
    native_len_delta_max = 0
    rank_mismatch_rows = 0
    sampled_layers = {"early": 0, "middle": len(moe_layer_ids) // 2,
                      "late": len(moe_layer_ids) - 1}
    sampled_layer_mismatch = {k: 0 for k in sampled_layers}
    rows_total = 0
    raw_checks = []
    feature_rows = 0

    for rec, fetches in zip(arm_d, captures):
        cap0 = fetches[0]
        rows = cap0["rows"]
        rows_total += rows
        id_mismatch_total += sum(cap0["id_mismatch"])
        dispatch_missed_total += sum(cap0["dispatch_missed"])
        weight_maxdiff = max(weight_maxdiff, max(cap0["weight_maxdiff"]))
        weight_nonfinite += sum(cap0["weight_nonfinite"])
        weight_min = min(weight_min, min(cap0["weight_min"]))
        weight_normdev = max(weight_normdev, max(cap0["weight_normdev"]))

        # Cross-check captured ids against the native routed-experts path.
        native = rec["routed_experts"]
        if native is None:
            native_mismatch_rows += rows or 1
        else:
            native = np.asarray(native)
            n = min(rows, native.shape[0])
            native_len_delta_max = max(native_len_delta_max,
                                       abs(rows - native.shape[0]))
            cap_ids = cap0["ids"][:n].astype(np.int64)
            nat_ids = native[:n].astype(np.int64)
            mismatch_rows = (np.sort(cap_ids, -1) != np.sort(nat_ids, -1)
                             ).any(axis=(1, 2))
            native_mismatch_rows += int(mismatch_rows.sum())
            for name, layer in sampled_layers.items():
                sampled_layer_mismatch[name] += int(
                    (np.sort(cap_ids[:, layer], -1) !=
                     np.sort(nat_ids[:, layer], -1)).any(axis=-1).sum())

        # TP rank agreement on captured ids.
        if len(fetches) > 1 and fetches[1].get("rows", 0) == rows and rows:
            rank_mismatch_rows += int(
                (cap0["ids"] != fetches[1]["ids"]).any(axis=(1, 2)).sum())

        raw_checks.append(summary_vs_raw_check(cap0))

        prompt_rows = len(rec["prompt_token_ids"])
        records = derive_decode_records(
            cap0["ids"], cap0["weights"], cap0["entropy"], cap0["mass"],
            prompt_rows=min(prompt_rows, rows), num_experts=num_experts)
        feature_rows += len(records)

    gates["dispatch_identity"] = (
        id_mismatch_total == 0 and dispatch_missed_total == 0
        and native_mismatch_rows == 0 and native_len_delta_max <= 1
        and rank_mismatch_rows == 0
        and all(v == 0 for v in sampled_layer_mismatch.values())
        and rows_total > 0)
    gates["weight_identity"] = (
        weight_maxdiff <= WEIGHT_IDENTITY_TOL and weight_nonfinite == 0
        and weight_min >= 0.0 and weight_normdev <= WEIGHT_NORMDEV_TOL)
    gates["feature_availability"] = (
        feature_rows > 0 and all(c.get("passed") for c in raw_checks))

    sampler.stop_flag = True
    time.sleep(3)
    peak_combined_gib = round(sum(sampler.peaks.values()) / 1024, 2)
    gates["bounded_overhead"] = peak_combined_gib <= GPU_GATE_GIB

    detail.update({
        "rows_total": rows_total,
        "id_mismatch_total": id_mismatch_total,
        "dispatch_missed_total": dispatch_missed_total,
        "native_mismatch_rows": native_mismatch_rows,
        "native_len_delta_max": native_len_delta_max,
        "rank_mismatch_rows": rank_mismatch_rows,
        "sampled_layer_mismatch": sampled_layer_mismatch,
        "weight_maxdiff": float(weight_maxdiff),
        "weight_nonfinite": int(weight_nonfinite),
        "weight_min": float(weight_min),
        "weight_normdev": float(weight_normdev),
        "raw_check_entropy_maxdev": max(
            (c.get("entropy_maxdev", 0.0) for c in raw_checks), default=0.0),
        "raw_check_mass_maxdev": max(
            (c.get("mass_maxdev", 0.0) for c in raw_checks), default=0.0),
        "raw_check_weight_maxdev": max(
            (c.get("weight_maxdev", 0.0) for c in raw_checks), default=0.0),
        "raw_check_rows": sum(c.get("raw_rows", 0) for c in raw_checks),
        "feature_decode_rows": feature_rows,
        "telemetry_overhead_ratio": round(arm_d_seconds / arm_c_seconds, 3)
        if arm_c_seconds else None,
        "seconds_pre_install": round(arm_b_seconds, 2),
        "seconds_installed_disabled": round(arm_c_seconds, 2),
        "seconds_enabled": round(arm_d_seconds, 2),
    })

    # Private per-token dump (never committed).
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    private_path = PRIVATE_DIR / "m36v_phase1_telemetry_local.npz"
    np.savez_compressed(
        private_path,
        **{f"p{i}_{k}": captures[i][0][k]
           for i in range(len(captures))
           for k in ("ids", "weights", "entropy", "mass", "raw_logits_sample")})

    payload = {
        "schema_version": 1,
        "run_kind": "m36v_phase1_router_telemetry_gate",
        "checkpoint": "cyankiwi/Agents-A1-AWQ-INT4",
        "revision_pinned": EXPECTED_REVISION,
        "model_ref_hash": VZ.evidence_hash(args.model_ref),
        "runtime": {
            "vllm": vllm.__version__,
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "tensor_parallel_size": 2, "max_model_len": 1024,
            "enforce_eager": True, "max_tokens": args.max_tokens,
            "max_num_seqs": 1,
            "vllm_source_patched": False,
            "override_mechanism":
                "worker_extension_cls + enable_return_routed_experts",
            "override_hash": override_hash(),
            "hidden_state_capture": "disabled",
        },
        "gates": gates,
        "all_gates_passed": all(v is True for v in gates.values()),
        "telemetry_path_classification": (
            "full_telemetry" if all(v is True for v in gates.values())
            else "black_box_only"),
        "load_seconds": load_seconds,
        "gpu_combined_peak_gib": peak_combined_gib,
        "detail": detail,
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate gates/metrics only; outputs private",
    }
    gates["privacy"] = True
    try:
        assert_aggregate_only(payload)
    except Exception as exc:
        gates["privacy"] = False
        payload["privacy_check_status"] = f"FAILED: {exc}"
    payload["all_gates_passed"] = all(v is True for v in gates.values())

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36V phase1: all_gates={payload['all_gates_passed']} "
          f"classification={payload['telemetry_path_classification']} "
          f"overhead={detail['telemetry_overhead_ratio']} "
          f"combined={peak_combined_gib}GiB", flush=True)
    for name, value in gates.items():
        if value is not True:
            print(f"[jlens]  GATE FAIL: {name} = {value}", flush=True)
    return 0 if payload["all_gates_passed"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--arm", choices=("stock", "instrumented"), required=True)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--stock-ids",
                    default=str(PRIVATE_DIR / "m36v_phase1_stock_ids.jsonl"))
    ap.add_argument("--out",
                    default="reports/telemetry/m36v_phase1_router_telemetry.json")
    args = ap.parse_args(argv)

    # Workers are spawned; they must be able to import the override module.
    src = str(ROOT)
    existing = os.environ.get("PYTHONPATH", "")
    if src not in existing.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            src + (os.pathsep + existing if existing else ""))

    if args.arm == "stock":
        return run_stock(args)
    return run_instrumented(args)


if __name__ == "__main__":
    raise SystemExit(main())
