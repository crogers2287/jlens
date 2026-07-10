#!/usr/bin/env python3
"""M25 identical-input metadata-counterfactual router falsification."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import action_executor as EXEC  # noqa: E402
from hf_telemetry_backend import HFTelemetryBackend  # noqa: E402
import m23_within_model as M23  # noqa: E402
import m24_frozen_holdout as M24  # noqa: E402


MATH_FIXTURES = {
    "math_00": (12, 7), "math_01": (15, 9),
    "math_02": (18, 6), "math_03": (21, 8),
    "math_04": (24, 5), "math_05": (27, 4),
    "math_06": (30, 3), "math_07": (33, 2),
}
TOPIC_FIXTURES = {
    "topic_00": "the water cycle", "topic_01": "photosynthesis",
    "topic_02": "urban transit", "topic_03": "ocean tides",
    "topic_04": "renewable energy", "topic_05": "public libraries",
    "topic_06": "soil erosion", "topic_07": "cloud formation",
}


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("selection_status") != "frozen_before_m25_pair_capture":
        raise ValueError("M25 manifest is not frozen before capture")
    pairs = manifest.get("pairs") or []
    if manifest.get("n_pairs") != 16 or manifest.get("n_tasks") != 32:
        raise ValueError("M25 manifest must contain 16 pairs / 32 tasks")
    ids = [member["task_id"] for pair in pairs for member in pair["members"]]
    if len(pairs) != 16 or len(ids) != 32 or len(set(ids)) != 32:
        raise ValueError("M25 pair/task IDs must be unique")
    if manifest.get("frozen_features") != [
            "router_entropy", "expert_concentration"]:
        raise ValueError("M25 frozen router features changed")
    return manifest


def _task_for_member(pair, member):
    pair_id, pair_type = pair["pair_id"], pair["pair_type"]
    action = member["intended_action"]
    task = {
        "prompt_id": member["task_id"],
        "m25_pair_id": pair_id,
        "m25_pair_type": pair_type,
        "m25_intended_action": action,
    }
    if pair_type == "checker_vs_no_action":
        a, b = MATH_FIXTURES[pair_id]
        task["prompt"] = f"What is {a} + {b}? Reply with the final number only."
        task["known_answer"] = str(a + b)
        if action == "checker_needed":
            task["task_category"] = "math"
            task["expression"] = f"{a}+{b}"
        elif action == "no_action":
            task["task_category"] = "exact_answer"
        else:
            raise ValueError(f"unexpected math pair action: {action}")
    elif pair_type == "retrieval_vs_review":
        topic = TOPIC_FIXTURES[pair_id]
        task["prompt"] = f"Explain the status of {topic}."
        if action == "retrieval_needed":
            task["task_category"] = "current_info"
        elif action == "review_needed":
            task["task_category"] = "explain"
        else:
            raise ValueError(f"unexpected topic pair action: {action}")
    else:
        raise ValueError(f"unexpected pair type: {pair_type}")
    return task


def prepare_private_tasks(manifest_path, output_path):
    manifest = load_manifest(manifest_path)
    tasks = [_task_for_member(pair, member) for pair in manifest["pairs"]
             for member in pair["members"]]
    by_pair = defaultdict(list)
    for task in tasks:
        by_pair[task["m25_pair_id"]].append(task)
    if len(by_pair) != 16 or any(len(rows) != 2 for rows in by_pair.values()):
        raise ValueError("M25 private tasks do not form 16 pairs")
    for pair_id, rows in by_pair.items():
        if rows[0]["prompt"] != rows[1]["prompt"]:
            raise ValueError(f"M25 pair prompt mismatch: {pair_id}")
        if rows[0]["m25_intended_action"] == rows[1]["m25_intended_action"]:
            raise ValueError(f"M25 pair labels are not counterfactual: {pair_id}")
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(task) + "\n" for task in tasks))
    return tasks


def _router_features(record):
    return {
        "router_entropy": float(record["router"]["router_entropy_mean"]),
        "expert_concentration": float(
            record["router"]["expert_concentration_mean"]),
    }


def evaluate_pairs(tasks, captures, telemetry, actions, classifier):
    telemetry_by_id = {row["task_id"]: row for row in telemetry}
    action_by_id = {row["task_id"]: row["action_type"] for row in actions}
    capture_by_id = {row["prompt_id"]: row for row in captures}
    by_pair = defaultdict(list)
    for task in tasks:
        by_pair[task["m25_pair_id"]].append(task)

    pair_rows = []
    actual, predicted = [], []
    intended_match = 0
    for pair_id in sorted(by_pair):
        pair_tasks = by_pair[pair_id]
        first, second = pair_tasks
        t1, t2 = (telemetry_by_id[first["prompt_id"]],
                  telemetry_by_id[second["prompt_id"]])
        a1, a2 = (action_by_id[first["prompt_id"]],
                  action_by_id[second["prompt_id"]])
        p1, p2 = classifier.predict(t1), classifier.predict(t2)
        for task, label, prediction in ((first, a1, p1), (second, a2, p2)):
            actual.append(label); predicted.append(prediction)
            intended_match += label == task["m25_intended_action"]
        f1, f2 = _router_features(t1), _router_features(t2)
        pair_rows.append({
            "pair_type": first["m25_pair_type"],
            "actual_labels_discordant": a1 != a2,
            "outputs_identical": (
                capture_by_id[first["prompt_id"]].get("generated_output") ==
                capture_by_id[second["prompt_id"]].get("generated_output")),
            "predictions_identical": p1 == p2,
            "router_entropy_abs_diff": abs(
                f1["router_entropy"] - f2["router_entropy"]),
            "expert_concentration_abs_diff": abs(
                f1["expert_concentration"] - f2["expert_concentration"]),
        })

    classes = sorted(set(actual))
    metrics = M24.classification_metrics(actual, predicted, classes)

    def pair_summary(rows):
        entropy = [row["router_entropy_abs_diff"] for row in rows]
        concentration = [row["expert_concentration_abs_diff"] for row in rows]
        return {
            "n_pairs": len(rows),
            "actual_labels_discordant": sum(
                row["actual_labels_discordant"] for row in rows),
            "outputs_identical": sum(row["outputs_identical"] for row in rows),
            "predictions_identical": sum(
                row["predictions_identical"] for row in rows),
            "prediction_divergence_rate": (
                sum(not row["predictions_identical"] for row in rows) / len(rows)),
            "router_entropy_abs_diff_mean": statistics.fmean(entropy),
            "router_entropy_abs_diff_max": max(entropy),
            "expert_concentration_abs_diff_mean": statistics.fmean(concentration),
            "expert_concentration_abs_diff_max": max(concentration),
        }

    grouped = defaultdict(list)
    for row in pair_rows:
        grouped[row["pair_type"]].append(row)
    overall = pair_summary(pair_rows)
    return {
        "schema_version": 1,
        "run_kind": "m25_identical_input_router_falsification",
        "n_pairs": len(pair_rows),
        "n_tasks": len(actual),
        "actual_class_distribution": dict(sorted(Counter(actual).items())),
        "intended_action_match_count": intended_match,
        "majority_class_baseline_accuracy": max(Counter(actual).values()) / len(actual),
        "frozen_router_classifier_metrics": metrics,
        "overall_pair_checks": overall,
        "pair_type_checks": {
            key: pair_summary(value) for key, value in sorted(grouped.items())},
        "classifier_training_source": "M23_only",
        "classifier_refit_or_holdout_update": False,
        "frozen_features": ["router_entropy", "expert_concentration"],
        "telemetry_only_observability_test": True,
        "per_task_or_pair_predictions_persisted_publicly": False,
        "raw_text_hash_id_path_or_tensor_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate pair counts/differences/confusion only",
    }


def build_run_summary(telemetry, actions, results, tasks):
    capped = [task for task, record in zip(tasks, telemetry)
              if record["decode_step_count"] == 64]
    return {
        "schema_version": 1,
        "run_kind": "m25_identical_input_same_run",
        "n_pairs": 16,
        "n_records": len(telemetry),
        "pair_type_task_distribution": dict(sorted(Counter(
            task["m25_pair_type"] for task in tasks).items())),
        "capture_status_distribution": dict(sorted(Counter(
            row["capture_status"] for row in telemetry).items())),
        "logits_status_distribution": dict(sorted(Counter(
            row["logits"]["status"] for row in telemetry).items())),
        "router_status_distribution": dict(sorted(Counter(
            row["router"]["status"] for row in telemetry).items())),
        "actual_action_type_distribution": dict(sorted(Counter(
            row["action_type"] for row in actions).items())),
        "checker_verdict_distribution": dict(sorted(Counter(
            row["checker_verdict"] for row in results
            if row.get("checker_verdict") is not None).items())),
        "decode_cap_tokens": 64,
        "decode_cap_reached_count": len(capped),
        "decode_cap_reached_pair_type_distribution": dict(sorted(Counter(
            task["m25_pair_type"] for task in capped).items())),
        "same_capture_supplied_telemetry_and_output": True,
        "prompts_equal_within_pairs_pre_capture": True,
        "hidden_capture": "disabled",
        "architecture_family": "qwen2_moe",
        "raw_text_token_tensor_or_path_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only identical-input run summary",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default="data/prompts/m25_pair_manifest.json")
    ap.add_argument("--tasks-out",
                    default="reports/shadow/private/m25_hf_prompts_local.jsonl")
    ap.add_argument("--captures", default="data/captures/m25_qwen15_moe")
    ap.add_argument("--model-ref")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--training-telemetry",
                    default="reports/shadow/private/m23_hf_telemetry_records_local.jsonl")
    ap.add_argument("--training-actions",
                    default="reports/shadow/private/m23_qwen_actions_local.jsonl")
    ap.add_argument("--telemetry-out",
                    default="reports/shadow/private/m25_hf_telemetry_records_local.jsonl")
    ap.add_argument("--runtime-out",
                    default="reports/shadow/private/m25_qwen_auto_outcomes_local.jsonl")
    ap.add_argument("--actions-out",
                    default="reports/shadow/private/m25_qwen_actions_local.jsonl")
    ap.add_argument("--results-out",
                    default="reports/shadow/private/m25_qwen_action_results_local.jsonl")
    ap.add_argument("--summary-out", default="reports/telemetry/hf_m25_pair_run_summary.json")
    ap.add_argument("--report-out", default="reports/telemetry/hf_m25_pair_falsification.json")
    args = ap.parse_args(argv)

    tasks = prepare_private_tasks(args.manifest, args.tasks_out)
    if args.prepare_only:
        completion = M23.capture_completion(args.captures, tasks)
        print(f"[jlens] M25 private pairs: 16/16 prompt-equal; "
              f"existing={len(completion['complete'])}, "
              f"pending={len(completion['missing_or_invalid'])}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required for M25 real capture processing")

    training = M23.read_jsonl(args.training_telemetry)
    training_actions = M23.read_jsonl(args.training_actions)
    classifier = M24.fit_frozen_classifiers(
        training, training_actions)["router_only"]

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
              "context": "M25 controlled local fixture context",
              "confidence": 0.8}
    })
    cfg = M23._qwen_config()
    captures, telemetry, runtimes, actions, results = [], [], [], [], []
    for task in tasks:
        path = Path(args.captures) / f"{task['prompt_id']}.pt"
        if not path.exists():
            raise FileNotFoundError(f"missing M25 capture: {task['prompt_id']}")
        capture = torch.load(path, map_location="cpu", weights_only=False)
        rows = M23.process_same_capture(
            task, capture, backend, cfg=cfg, retrieval_adapter=adapter)
        for kind, row in zip(("telemetry", "runtime", "action", "result"), rows):
            errors = list(schemas[kind].iter_errors(row))
            if errors:
                raise ValueError(
                    f"invalid {kind} for {task['prompt_id']}: {errors[0].message}")
        t, runtime, action, result = rows
        captures.append(capture); telemetry.append(t); runtimes.append(runtime)
        actions.append(action); results.append(result)

    M23.write_jsonl(args.telemetry_out, telemetry)
    M23.write_jsonl(args.runtime_out, runtimes)
    M23.write_jsonl(args.actions_out, actions)
    M23.write_jsonl(args.results_out, results)
    summary = build_run_summary(telemetry, actions, results, tasks)
    report = evaluate_pairs(tasks, captures, telemetry, actions, classifier)
    for path, payload in ((args.summary_out, summary), (args.report_out, report)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n")
    print("[jlens] M25: 16 identical-input pairs / 32 records evaluated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
