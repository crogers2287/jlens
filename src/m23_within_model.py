#!/usr/bin/env python3
"""M23 same-run Qwen telemetry, verifier outcomes, and public-safe analysis."""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import action_executor as EXEC  # noqa: E402
import action_router as ROUTER  # noqa: E402
import autonomous_shadow_supervisor as SUP  # noqa: E402
from hf_telemetry_backend import HFTelemetryBackend  # noqa: E402
from m22_real_telemetry import record_from_capture  # noqa: E402


METRICS = {
    "decode_window_entropy": lambda r: r["logits"]["window"]["mean_entropy"],
    "final_selected_probability": lambda r: r["logits"]["selected_token_probability"],
    "final_top_k_margin": lambda r: r["logits"]["top_k_margin"],
    "router_entropy": lambda r: r["router"]["router_entropy_mean"],
    "expert_concentration": lambda r: r["router"]["expert_concentration_mean"],
}


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines()
            if line.strip()]


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    groups = manifest.get("groups") or []
    if manifest.get("selection_status") != "predeclared_before_m23_telemetry_run":
        raise ValueError("M23 manifest is not marked predeclared")
    if manifest.get("n_tasks") != 32 or len(groups) != 4:
        raise ValueError("M23 manifest must contain four groups and 32 tasks")
    mapping = {}
    for group in groups:
        task_ids = group.get("task_ids") or []
        if len(task_ids) != 8:
            raise ValueError("each M23 group must contain exactly eight task ids")
        for task_id in task_ids:
            if task_id in mapping:
                raise ValueError(f"duplicate M23 task id: {task_id}")
            mapping[task_id] = group["group"]
    if len(mapping) != 32:
        raise ValueError("M23 manifest task ids must be unique")
    return manifest, mapping


def prepare_selected_batch(manifest_path, source_path, output_path):
    manifest, groups = load_manifest(manifest_path)
    by_id = {row["prompt_id"]: row for row in read_jsonl(source_path)}
    ordered_ids = [task_id for group in manifest["groups"]
                   for task_id in group["task_ids"]]
    missing = [task_id for task_id in ordered_ids if task_id not in by_id]
    if missing:
        raise ValueError(f"M23 source missing ids: {missing}")
    selected = []
    for task_id in ordered_ids:
        row = dict(by_id[task_id])
        row["m23_predeclared_group"] = groups[task_id]
        selected.append(row)
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(row) + "\n" for row in selected))
    return selected


def capture_completion(capture_dir, tasks):
    from capture_router_logits import _valid_capture
    complete, missing = [], []
    for task in tasks:
        task_id = task["prompt_id"]
        if _valid_capture(Path(capture_dir) / f"{task_id}.pt"):
            complete.append(task_id)
        else:
            missing.append(task_id)
    return {"complete": complete, "missing_or_invalid": missing}


def _qwen_config():
    cfg = SUP.load_config("config/agents_a1_m19_run.json")
    cfg["endpoint"] = {
        "alias": "local-hf-qwen2-moe",
        "model": "Qwen1.5-MoE-A2.7B-Chat",
    }
    cfg["run"]["mode"] = "local_hf_same_run"
    cfg["verifiers"]["self_consistency_samples"] = 1
    return cfg


def process_same_capture(task, capture, backend, *, cfg=None,
                         retrieval_adapter=None):
    """Derive telemetry and Qwen-specific outcomes from one private capture."""
    cfg = cfg or _qwen_config()
    output = capture.get("generated_output")
    if not isinstance(output, str) or not output:
        raise ValueError(f"capture {task['prompt_id']} has no generated output")
    runtime, transient_output = SUP.run_task(
        task, lambda _prompt: output, cfg, feature_rows={task["prompt_id"]: {}},
        n_samples=1, return_full_output=True)
    runtime["feature_source"] = "hf_telemetry_record_v1"
    runtime["policy_note"] = "HF telemetry linked separately; no policy fitted"
    action = ROUTER.route(runtime)
    result = EXEC.execute_action(
        action, task=task, runtime={"output": transient_output}, enabled=True,
        retrieval_adapter=retrieval_adapter)
    telemetry = record_from_capture(
        capture, backend, {"auto_outcome": True, "action_result": True})
    return telemetry, runtime, action, result


def _dist(rows, key):
    values = []
    for row in rows:
        value = row.get(key)
        values.append("unknown" if value is None else value)
    return dict(sorted(Counter(values).items(), key=lambda item: str(item[0])))


def _metric_values(rows, metric):
    values = []
    getter = METRICS[metric]
    for row in rows:
        value = getter(row)
        if value is not None and math.isfinite(float(value)):
            values.append(float(value))
    return values


def _summary_values(values):
    return {
        "n": len(values),
        "mean": statistics.fmean(values) if values else None,
        "median": statistics.median(values) if values else None,
    }


def telemetry_group(rows):
    result = {"n": len(rows), "metrics": {}}
    for metric in METRICS:
        result["metrics"][metric] = _summary_values(_metric_values(rows, metric))
    return result


def _hedges_g(positive, negative):
    n1, n0 = len(positive), len(negative)
    if n1 < 2 or n0 < 2:
        return None
    v1, v0 = statistics.variance(positive), statistics.variance(negative)
    pooled_num = (n1 - 1) * v1 + (n0 - 1) * v0
    pooled_den = n1 + n0 - 2
    if pooled_den <= 0 or pooled_num <= 0:
        return None
    d = (statistics.fmean(positive) - statistics.fmean(negative)) / math.sqrt(
        pooled_num / pooled_den)
    correction = 1 - (3 / (4 * (n1 + n0) - 9))
    return d * correction


def _bootstrap_mean_difference(positive, negative, seed, iterations=2000):
    rng = random.Random(seed)
    diffs = []
    for _ in range(iterations):
        p = [rng.choice(positive) for _ in positive]
        n = [rng.choice(negative) for _ in negative]
        diffs.append(statistics.fmean(p) - statistics.fmean(n))
    diffs.sort()
    lo = diffs[int(0.025 * (iterations - 1))]
    hi = diffs[int(0.975 * (iterations - 1))]
    return [lo, hi]


def compare_groups(positive_rows, negative_rows, label):
    comparison = {
        "positive": telemetry_group(positive_rows),
        "negative": telemetry_group(negative_rows),
        "effects": {},
    }
    for metric in METRICS:
        positive = _metric_values(positive_rows, metric)
        negative = _metric_values(negative_rows, metric)
        if len(positive) < 4 or len(negative) < 4:
            comparison["effects"][metric] = {
                "status": "insufficient_group_size",
                "minimum_per_group": 4,
                "positive_n": len(positive),
                "negative_n": len(negative),
            }
            continue
        comparison["effects"][metric] = {
            "status": "descriptive_only",
            "mean_difference_positive_minus_negative": (
                statistics.fmean(positive) - statistics.fmean(negative)),
            "hedges_g": _hedges_g(positive, negative),
            "bootstrap_mean_difference_95pct": _bootstrap_mean_difference(
                positive, negative, f"m23:{label}:{metric}"),
            "bootstrap_iterations": 2000,
        }
    return comparison


def build_public_reports(telemetry, runtimes, actions, results, tasks):
    by_id = {row["task_id"]: row for row in telemetry}
    action_by_id = {row["task_id"]: row for row in actions}
    result_by_id = {row["task_id"]: row for row in results}
    groups = defaultdict(list)
    for task in tasks:
        groups[task["m23_predeclared_group"]].append(by_id[task["prompt_id"]])
    capped = [task for task in tasks
              if by_id[task["prompt_id"]]["decode_step_count"] == 64]

    summary = {
        "schema_version": 1,
        "run_kind": "m23_same_run_qwen_telemetry_outcomes",
        "within_model_alignment": True,
        "cross_model_alignment": False,
        "telemetry_model_scope": "qwen2_moe_internal_signals",
        "outcome_model_scope": "qwen2_moe_same_decode_output",
        "weights_loaded": 1,
        "model_kind": "moe",
        "architecture_family": "qwen2_moe",
        "hardware_plan": "two_24gib_nvidia_gpus_bf16",
        "hidden_capture": "disabled",
        "n_records": len(telemetry),
        "predeclared_group_distribution": dict(sorted(Counter(
            task["m23_predeclared_group"] for task in tasks).items())),
        "capture_status_distribution": _dist(telemetry, "capture_status"),
        "logits_status_distribution": dict(sorted(Counter(
            row["logits"]["status"] for row in telemetry).items())),
        "router_status_distribution": dict(sorted(Counter(
            row["router"]["status"] for row in telemetry).items())),
        "decode_step_count_distribution": dict(sorted(Counter(
            str(row["decode_step_count"]) for row in telemetry).items())),
        "decode_cap_tokens": 64,
        "decode_cap_reached_count": len(capped),
        "decode_cap_reached_group_distribution": dict(sorted(Counter(
            task["m23_predeclared_group"] for task in capped).items())),
        "actual_action_type_distribution": _dist(actions, "action_type"),
        "action_status_distribution": _dist(results, "action_status"),
        "checker_verdict_distribution": _dist(
            [row for row in results if row.get("checker_verdict") is not None],
            "checker_verdict"),
        "auto_wrong_distribution": _dist(
            [row["auto_outcome"] for row in runtimes], "auto_was_wrong"),
        "same_capture_supplied_telemetry_and_output": True,
        "captured_output_passed_transiently_to_verifiers": True,
        "full_output_available_for_all_tasks": len(capped) == 0,
        "checker_outputs_reached_eos_before_cap": all(
            by_id[task["prompt_id"]]["decode_step_count"] < 64
            for task in tasks
            if task["m23_predeclared_group"] == "checker_candidate"),
        "full_output_persisted_publicly": False,
        "raw_prompt_token_or_tensor_persisted_publicly": False,
        "model_path_or_weights_committed": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only; detailed same-run artifacts ignored",
    }

    actual_comparisons = {}
    for label, action_type in (("checker", "checker_needed"),
                               ("retrieval", "retrieval_needed"),
                               ("review", "review_needed")):
        positive = [row for row in telemetry
                    if action_by_id[row["task_id"]]["action_type"] == action_type]
        negative = [row for row in telemetry
                    if action_by_id[row["task_id"]]["action_type"] != action_type]
        actual_comparisons[label] = compare_groups(positive, negative, label)

    checker_pass = [row for row in telemetry
                    if result_by_id[row["task_id"]].get("checker_verdict") == "pass"]
    checker_fail = [row for row in telemetry
                    if result_by_id[row["task_id"]].get("checker_verdict") == "fail"]
    alignment = {
        "schema_version": 1,
        "run_kind": "m23_within_model_telemetry_alignment",
        "within_model_alignment": True,
        "cross_model_alignment": False,
        "n_records": len(telemetry),
        "predeclared_group_metrics": {
            group: telemetry_group(rows) for group, rows in sorted(groups.items())},
        "actual_need_comparisons": actual_comparisons,
        "checker_pass_vs_fail": compare_groups(
            checker_fail, checker_pass, "checker_fail_vs_pass"),
        "checker_comparison_orientation": "positive=fail; negative=pass",
        "effect_size_interpretation": (
            "descriptive Hedges g and fixed-seed bootstrap mean-difference intervals; "
            "not a fitted policy or inferential claim"),
        "features_and_comparisons_predeclared": True,
        "thresholds_fitted": False,
        "predictive_value_claimed": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate groups only; no ids, text, paths, or tensors",
    }
    return summary, alignment


def write_jsonl(path, rows):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default="data/prompts/m23_manifest.json")
    ap.add_argument("--source-prompts", default="data/prompts/agents_a1_m19_batch.jsonl")
    ap.add_argument("--selected-prompts-out",
                    default="reports/shadow/private/m23_hf_prompts_local.jsonl")
    ap.add_argument("--captures", default="data/captures/m23_qwen15_moe")
    ap.add_argument("--model-ref")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--telemetry-out",
                    default="reports/shadow/private/m23_hf_telemetry_records_local.jsonl")
    ap.add_argument("--runtime-out",
                    default="reports/shadow/private/m23_qwen_auto_outcomes_local.jsonl")
    ap.add_argument("--actions-out",
                    default="reports/shadow/private/m23_qwen_actions_local.jsonl")
    ap.add_argument("--results-out",
                    default="reports/shadow/private/m23_qwen_action_results_local.jsonl")
    ap.add_argument("--summary-out", default="reports/telemetry/hf_m23_same_run_summary.json")
    ap.add_argument("--alignment-out", default="reports/telemetry/hf_m23_within_model_alignment.json")
    args = ap.parse_args(argv)

    tasks = prepare_selected_batch(
        args.manifest, args.source_prompts, args.selected_prompts_out)
    if args.prepare_only:
        completion = capture_completion(args.captures, tasks)
        print(f"[jlens] M23 predeclared prompts: {len(tasks)}; "
              f"existing={len(completion['complete'])}, "
              f"pending={len(completion['missing_or_invalid'])}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required for M23 real capture processing")

    import torch
    from jsonschema import Draft7Validator
    schemas = {
        "telemetry": Draft7Validator(json.loads(Path(
            "schema/hf_telemetry_record_v1.json").read_text())),
        "runtime": Draft7Validator(json.loads(Path(
            "schema/auto_outcome_v1.json").read_text())),
        "action": Draft7Validator(json.loads(Path(
            "schema/action_record_v1.json").read_text())),
        "result": Draft7Validator(json.loads(Path(
            "schema/action_result_v1.json").read_text())),
    }
    backend = HFTelemetryBackend(
        model_ref=args.model_ref, source_kind="local_path", top_k=5)
    adapter = EXEC.FixtureRetrievalAdapter({
        "*": {"source_kind": "public_fixture",
              "context": "M23 controlled local fixture context",
              "confidence": 0.8}
    })
    cfg = _qwen_config()
    telemetry, runtimes, actions, results = [], [], [], []
    for task in tasks:
        path = Path(args.captures) / f"{task['prompt_id']}.pt"
        if not path.exists():
            raise FileNotFoundError(f"missing M23 capture: {task['prompt_id']}")
        capture = torch.load(path, map_location="cpu", weights_only=False)
        rows = process_same_capture(
            task, capture, backend, cfg=cfg, retrieval_adapter=adapter)
        for kind, row in zip(("telemetry", "runtime", "action", "result"), rows):
            errors = list(schemas[kind].iter_errors(row))
            if errors:
                raise ValueError(
                    f"invalid {kind} for {task['prompt_id']}: {errors[0].message}")
        t, runtime, action, result = rows
        telemetry.append(t); runtimes.append(runtime)
        actions.append(action); results.append(result)

    write_jsonl(args.telemetry_out, telemetry)
    write_jsonl(args.runtime_out, runtimes)
    write_jsonl(args.actions_out, actions)
    write_jsonl(args.results_out, results)
    summary, alignment = build_public_reports(
        telemetry, runtimes, actions, results, tasks)
    for path, payload in ((args.summary_out, summary),
                          (args.alignment_out, alignment)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M23: {len(telemetry)} same-run telemetry/outcome records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
