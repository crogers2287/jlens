#!/usr/bin/env python3
"""M22 real HF MoE telemetry conversion and aggregate-only reporting.

Raw prompts, generated token text, tensors, detailed records, and local paths
remain under gitignored private locations. Only numeric group summaries are
written to public report paths.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hf_telemetry_backend import HFTelemetryBackend, _mean  # noqa: E402


SELECTED_TASK_IDS = (
    "m15_n_000",       # exact answer / no action
    "m15_j_000",       # JSON / no action
    "m15_r_000",       # regex / no action
    "m15_c_000",       # current info / retrieval
    "m15_x_000",       # explain / reviewed escalation
    "m19_m_000",       # math / checker pass
    "m19_m_030",       # math / checker fail
    "m19_k_000",       # explain / no action
)


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines()
            if line.strip()]


def prepare_selected_batch(source_path, output_path):
    """Write the fixed 8-task shared batch to an ignored private path."""
    by_id = {row.get("prompt_id", row.get("id")): row
             for row in read_jsonl(source_path)}
    missing = [task_id for task_id in SELECTED_TASK_IDS if task_id not in by_id]
    if missing:
        raise ValueError(f"selected task ids missing from source: {missing}")
    selected = [by_id[task_id] for task_id in SELECTED_TASK_IDS]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(row) + "\n" for row in selected), encoding="utf-8")
    return selected


def build_alignment(runtime_rows, action_rows, grounded_rows, reviewed_rows):
    auto_ids = {row.get("prompt_id") for row in runtime_rows
                if row.get("auto_outcome")}
    actions = {row.get("task_id"): row for row in action_rows}
    grounded_ids = {row.get("task_id") for row in grounded_rows}
    reviewed_ids = set()
    for row in reviewed_rows:
        reviewer = (row.get("review_meta") or {}).get("reviewer")
        outcome = row.get("outcome") or {}
        if reviewer or any(value is not None for value in outcome.values()):
            reviewed_ids.add(row.get("prompt_id"))

    def for_task(task_id):
        return {
            "auto_outcome": task_id in auto_ids,
            "action_result": task_id in actions,
            "grounded_result": task_id in grounded_ids,
            "reviewed_outcome": task_id in reviewed_ids,
        }

    labels = {task_id: (row.get("action_type") or "unknown")
              for task_id, row in actions.items()}
    return for_task, labels


def _last_router_vectors(step):
    vectors = []
    for layer in step.get("router_logits") or []:
        if hasattr(layer, "detach"):
            layer = layer.detach().float().cpu()
            if layer.ndim == 0:
                continue
            layer = layer.reshape(-1, layer.shape[-1])[-1].tolist()
        elif isinstance(layer, (list, tuple)) and layer:
            if isinstance(layer[0], (list, tuple)):
                layer = layer[-1]
            layer = [float(value) for value in layer]
        else:
            continue
        vectors.append(layer)
    return vectors


def aggregate_steps(capture):
    """Drop text/tensors and retain scalar logits plus last-token router rows."""
    result = []
    for step in capture.get("decode_steps") or []:
        result.append({
            "generated_token_id": step.get("generated_token_id"),
            "entropy_final_logits": step.get("entropy_final_logits"),
            "selected_token_prob": step.get("selected_token_prob"),
            "top_k": step.get("top_k"),
            "top_k_mass": (min(1.0, step["top_k_mass"])
                           if step.get("top_k_mass") is not None else None),
            "top_k_margin": step.get("top_k_margin"),
            "router_logits": _last_router_vectors(step),
        })
    return result


def record_from_capture(capture, backend, alignment):
    input_ids = capture.get("input_ids")
    input_count = int(input_ids.numel()) if hasattr(input_ids, "numel") else len(input_ids or [])
    return backend.capture_precomputed(
        capture["prompt_id"], aggregate_steps(capture), model_kind="moe",
        input_token_count=input_count, router_supported=True,
        alignment=alignment)


def _distribution(records, path):
    def get(record):
        value = record
        for key in path:
            value = value[key]
        return value
    return dict(sorted(Counter(get(record) for record in records).items()))


def _telemetry_group(rows):
    available = [record for record in rows
                 if record["logits"]["status"] == "available"]
    router = [record for record in rows
              if record["router"]["status"] == "available"]
    return {
        "n": len(rows),
        "mean_decode_window_entropy": _mean(
            [r["logits"]["window"]["mean_entropy"] for r in available]),
        "mean_final_selected_probability": _mean(
            [r["logits"]["selected_token_probability"] for r in available]),
        "mean_final_top_k_margin": _mean(
            [r["logits"]["top_k_margin"] for r in available]),
        "mean_router_entropy": _mean(
            [r["router"]["router_entropy_mean"] for r in router]),
        "mean_expert_concentration": _mean(
            [r["router"]["expert_concentration_mean"] for r in router]),
    }


def build_public_reports(records, task_meta, action_labels):
    available = [r for r in records if r["logits"]["status"] == "available"]
    router = [r for r in records if r["router"]["status"] == "available"]
    summary = {
        "schema_version": 1,
        "run_kind": "real_local_hf_telemetry",
        "fixture_only": False,
        "weights_loaded": 1,
        "model_kind": "moe",
        "architecture_family": "qwen2_moe",
        "telemetry_model_scope": "qwen2_moe_internal_signals",
        "outcome_label_source": "agents_a1_shared_task_ids",
        "cross_model_alignment": True,
        "hardware_plan": "two_24gib_nvidia_gpus_bf16",
        "hidden_capture": "disabled",
        "n_records": len(records),
        "capture_status_distribution": _distribution(records, ("capture_status",)),
        "logits_status_distribution": _distribution(records, ("logits", "status")),
        "hidden_status_distribution": _distribution(records, ("hidden", "status")),
        "router_status_distribution": _distribution(records, ("router", "status")),
        "mean_decode_window_entropy": _mean(
            [r["logits"]["window"]["mean_entropy"] for r in available]),
        "mean_final_selected_probability": _mean(
            [r["logits"]["selected_token_probability"] for r in available]),
        "mean_router_entropy": _mean(
            [r["router"]["router_entropy_mean"] for r in router]),
        "mean_expert_concentration": _mean(
            [r["router"]["expert_concentration_mean"] for r in router]),
        "alignment_coverage": {key: sum(
            record["outcome_alignment"][key] for record in records)
            for key in ("auto_outcome", "action_result", "grounded_result",
                        "reviewed_outcome")},
        "raw_prompt_output_or_tensor_persisted_publicly": False,
        "model_path_or_weights_committed": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only; private captures and records ignored",
    }

    by_action = defaultdict(list)
    for record in records:
        by_action[action_labels.get(record["task_id"], "unknown")].append(record)
    action_groups = {key: _telemetry_group(value)
                     for key, value in sorted(by_action.items())}

    need_groups = {}
    for need, action_type in (
            ("retrieval", "retrieval_needed"),
            ("checker", "checker_needed"),
            ("review", "review_needed")):
        yes = [r for r in records
               if action_labels.get(r["task_id"]) == action_type]
        no = [r for r in records
              if action_labels.get(r["task_id"]) != action_type]
        need_groups[need] = {"needed": _telemetry_group(yes),
                             "not_needed": _telemetry_group(no)}

    categories = Counter(task_meta[r["task_id"]]["task_category"] for r in records)
    alignment = {
        "schema_version": 1,
        "run_kind": "real_local_hf_telemetry_alignment",
        "n_records": len(records),
        "telemetry_model_scope": "qwen2_moe_internal_signals",
        "outcome_label_source": "agents_a1_shared_task_ids",
        "cross_model_alignment": True,
        "task_category_distribution": dict(sorted(categories.items())),
        "action_type_groups": action_groups,
        "need_comparisons": need_groups,
        "observable_separation_only": True,
        "predictive_value_claimed": False,
        "within_model_error_prediction_tested": False,
        "tiny_n_warning": "Eight selected tasks cannot establish predictive value.",
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate groups only; no ids, text, paths, or tensors",
    }
    return summary, alignment


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--captures", default="data/captures/m22_qwen15_moe")
    ap.add_argument("--source-prompts", default="data/prompts/agents_a1_m19_batch.jsonl")
    ap.add_argument("--selected-prompts-out",
                    default="reports/shadow/private/m22_hf_prompts_local.jsonl")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--model-ref", default=None)
    ap.add_argument("--runtime", default="reports/shadow/private/agents_a1_m19_run_local.jsonl")
    ap.add_argument("--actions", default="reports/shadow/private/agents_a1_m19_action_results_local.jsonl")
    ap.add_argument("--grounded", default="reports/shadow/private/agents_a1_m20_grounded_results_local.jsonl")
    ap.add_argument("--reviewed", default="reports/shadow/private/agents_a1_m15_reviewed_subset_local.jsonl")
    ap.add_argument("--private-records-out",
                    default="reports/shadow/private/m22_hf_telemetry_records_local.jsonl")
    ap.add_argument("--summary-out", default="reports/telemetry/hf_m22_real_summary.json")
    ap.add_argument("--alignment-out", default="reports/telemetry/hf_m22_alignment.json")
    args = ap.parse_args(argv)

    selected = prepare_selected_batch(args.source_prompts, args.selected_prompts_out)
    if args.prepare_only:
        print(f"[jlens] prepared {len(selected)} private M22 prompts -> "
              f"{args.selected_prompts_out}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required for real capture conversion")

    import torch
    from jsonschema import Draft7Validator
    schema = json.loads(Path("schema/hf_telemetry_record_v1.json").read_text())
    validator = Draft7Validator(schema)
    alignment_for, action_labels = build_alignment(
        read_jsonl(args.runtime), read_jsonl(args.actions),
        read_jsonl(args.grounded), read_jsonl(args.reviewed))
    backend = HFTelemetryBackend(
        model_ref=args.model_ref, source_kind="local_path", top_k=5)
    records = []
    for row in selected:
        task_id = row["prompt_id"]
        path = Path(args.captures) / f"{task_id}.pt"
        if not path.exists():
            raise FileNotFoundError(f"missing private capture: {task_id}")
        capture = torch.load(path, map_location="cpu", weights_only=False)
        record = record_from_capture(capture, backend, alignment_for(task_id))
        errors = list(validator.iter_errors(record))
        if errors:
            raise ValueError(f"invalid telemetry for {task_id}: {errors[0].message}")
        records.append(record)

    private_out = Path(args.private_records_out)
    private_out.parent.mkdir(parents=True, exist_ok=True)
    private_out.write_text(
        "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
    task_meta = {row["prompt_id"]: row for row in selected}
    summary, comparison = build_public_reports(records, task_meta, action_labels)
    for path, payload in ((args.summary_out, summary),
                          (args.alignment_out, comparison)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"[jlens] M22: {len(records)} real records; public aggregates written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
