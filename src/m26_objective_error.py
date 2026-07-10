#!/usr/bin/env python3
"""M26 objective within-category error-prediction dataset over Qwen telemetry."""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import action_executor as EXEC  # noqa: E402
from hf_telemetry_backend import HFTelemetryBackend  # noqa: E402
import m23_within_model as M23  # noqa: E402


FEATURES = {
    **M23.METRICS,
    "decode_step_count": lambda r: r["decode_step_count"],
    "windowed_expert_shift": lambda r: r["router"]["windowed_expert_shift"],
    "high_entropy_count": lambda r: r["logits"]["window"]["high_entropy_count"],
    "low_confidence_count": lambda r: r["logits"]["window"]["low_confidence_count"],
    "top_k_margin_trend": lambda r: r["logits"]["window"]["top_k_margin_trend"],
}
DECODE_CAP_TOKENS = 64


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("selection_status") != "predeclared_before_m26_task_generation":
        raise ValueError("M26 manifest is not predeclared before generation")
    bands = manifest.get("bands") or []
    tasks = manifest.get("tasks") or []
    if manifest.get("n_tasks") != 96 or len(tasks) != 96 or len(bands) != 4:
        raise ValueError("M26 manifest must declare four bands and 96 tasks")
    ids = [task["task_id"] for task in tasks]
    if len(set(ids)) != 96:
        raise ValueError("M26 task ids must be unique")
    split_counts = Counter((task["band"], task["split"]) for task in tasks)
    for band in bands:
        if band.get("n_tasks") != 24 or band.get("n_train") != 16 \
                or band.get("n_holdout") != 8:
            raise ValueError("each M26 band must declare 24 tasks split 16/8")
        if split_counts[(band["band_id"], "train")] != 16 \
                or split_counts[(band["band_id"], "holdout")] != 8:
            raise ValueError(f"M26 split mismatch for {band['band_id']}")
    feature_sets = manifest.get("frozen_feature_sets") or {}
    expected_full = (feature_sets.get("logits_only", [])
                     + feature_sets.get("router_only", [])
                     + ["decode_step_count", "windowed_expert_shift",
                        "high_entropy_count", "low_confidence_count",
                        "top_k_margin_trend"])
    if feature_sets.get("full_telemetry") != expected_full:
        raise ValueError("M26 frozen full_telemetry feature set changed")
    for feature in expected_full:
        if feature not in FEATURES:
            raise ValueError(f"M26 frozen feature has no getter: {feature}")
    if not manifest.get("holdout_seal", {}).get("no_refit_after_holdout_capture"):
        raise ValueError("M26 manifest must seal the holdout before capture")
    return manifest


def generate_tasks(manifest):
    """Deterministically expand the predeclared manifest into private tasks."""
    seed = manifest["generation"]["seed"]
    template = manifest["prompt_template"]
    by_band = {band["band_id"]: band for band in manifest["bands"]}
    manifest_tasks = defaultdict(list)
    for task in manifest["tasks"]:
        manifest_tasks[task["band"]].append(task)

    tasks = []
    for band_id in sorted(manifest_tasks):
        band = by_band[band_id]
        rng = random.Random(f"{seed}:{band_id}")
        a_lo, a_hi = band["operand_a_range"]
        b_lo, b_hi = band["operand_b_range"]
        seen = set()
        tuples = []
        while len(tuples) < band["n_tasks"]:
            pair = (rng.randint(a_lo, a_hi), rng.randint(b_lo, b_hi))
            if pair in seen:
                continue
            seen.add(pair)
            tuples.append(pair)
        for slot, (a, b) in zip(manifest_tasks[band_id], tuples):
            op = band["operator"]
            expression = f"{a}{op}{b}"
            answer = a + b if op == "+" else a * b
            tasks.append({
                "prompt_id": slot["task_id"],
                "m26_band": band_id,
                "m26_split": slot["split"],
                "task_category": "math",
                "expression": expression,
                "known_answer": str(answer),
                "prompt": template.format(a=a, op=op, b=b),
            })
    if len(tasks) != 96 or len({t["prompt_id"] for t in tasks}) != 96:
        raise ValueError("M26 generation did not produce 96 unique tasks")
    order = {task["task_id"]: index
             for index, task in enumerate(manifest["tasks"])}
    tasks.sort(key=lambda task: order[task["prompt_id"]])
    return tasks


def prepare_private_tasks(manifest_path, output_path):
    manifest = load_manifest(manifest_path)
    tasks = generate_tasks(manifest)
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(task) + "\n" for task in tasks))
    return manifest, tasks


def label_from_result(result):
    verdict = result.get("checker_verdict")
    if verdict in ("pass", "fail"):
        return verdict
    return "undecided"


def _feature_values(rows, feature):
    import math
    getter = FEATURES[feature]
    values = []
    for row in rows:
        value = getter(row)
        if value is not None and math.isfinite(float(value)):
            values.append(float(value))
    return values


def compare_pass_fail(fail_rows, pass_rows):
    """Aggregate train-split fail-versus-pass telemetry comparison."""
    comparison = {
        "orientation": "positive=fail; negative=pass",
        "fail": {"n": len(fail_rows)},
        "pass": {"n": len(pass_rows)},
        "effects": {},
    }
    for feature in FEATURES:
        fail_values = _feature_values(fail_rows, feature)
        pass_values = _feature_values(pass_rows, feature)
        comparison["fail"][feature] = {
            "mean": statistics.fmean(fail_values) if fail_values else None,
            "median": statistics.median(fail_values) if fail_values else None,
        }
        comparison["pass"][feature] = {
            "mean": statistics.fmean(pass_values) if pass_values else None,
            "median": statistics.median(pass_values) if pass_values else None,
        }
        if len(fail_values) < 4 or len(pass_values) < 4:
            comparison["effects"][feature] = {
                "status": "insufficient_group_size",
                "minimum_per_group": 4,
                "fail_n": len(fail_values),
                "pass_n": len(pass_values),
            }
            continue
        comparison["effects"][feature] = {
            "status": "descriptive_only",
            "mean_difference_fail_minus_pass": (
                statistics.fmean(fail_values) - statistics.fmean(pass_values)),
            "hedges_g": M23._hedges_g(fail_values, pass_values),
            "bootstrap_mean_difference_95pct": M23._bootstrap_mean_difference(
                fail_values, pass_values, f"m26:train_fail_vs_pass:{feature}"),
            "bootstrap_iterations": 2000,
        }
    return comparison


def build_run_summary(manifest, tasks, telemetry, actions, labels):
    label_by_id = {row["task_id"]: row["label"] for row in labels}
    train_tasks = [task for task in tasks if task["m26_split"] == "train"]
    train_labels = Counter(label_by_id[task["prompt_id"]] for task in train_tasks)
    train_band_labels = {}
    for band in sorted({task["m26_band"] for task in train_tasks}):
        rows = [task for task in train_tasks if task["m26_band"] == band]
        train_band_labels[band] = dict(sorted(Counter(
            label_by_id[task["prompt_id"]] for task in rows).items()))
    telemetry_by_id = {row["task_id"]: row for row in telemetry}
    train_capped = sum(
        telemetry_by_id[task["prompt_id"]]["decode_step_count"]
        == DECODE_CAP_TOKENS for task in train_tasks)
    requirement = manifest["minimum_modeling_requirement"]
    requirement_met = (train_labels.get("pass", 0) >= requirement["train_pass_min"]
                       and train_labels.get("fail", 0) >= requirement["train_fail_min"])
    return {
        "schema_version": 1,
        "run_kind": "m26_objective_error_dataset",
        "task_category": manifest["task_category"],
        "prompt_family_constant": True,
        "n_records": len(telemetry),
        "band_split_task_counts": {
            band["band_id"]: {"train": band["n_train"],
                              "holdout": band["n_holdout"]}
            for band in manifest["bands"]},
        "capture_status_distribution": dict(sorted(Counter(
            row["capture_status"] for row in telemetry).items())),
        "logits_status_distribution": dict(sorted(Counter(
            row["logits"]["status"] for row in telemetry).items())),
        "router_status_distribution": dict(sorted(Counter(
            row["router"]["status"] for row in telemetry).items())),
        "actual_action_type_distribution": dict(sorted(Counter(
            row["action_type"] for row in actions).items())),
        "action_applicability_constant": True,
        "deterministic_verifier_labeler": "math_checker",
        "train_label_distribution": dict(sorted(train_labels.items())),
        "train_band_label_distribution": train_band_labels,
        "holdout_label_distribution": "sealed_until_m27",
        "holdout_telemetry_aggregates": "sealed_until_m27",
        "decode_cap_tokens": DECODE_CAP_TOKENS,
        "train_decode_cap_reached_count": train_capped,
        "minimum_modeling_requirement": dict(requirement),
        "minimum_modeling_requirement_met": requirement_met,
        "no_posthoc_selection": True,
        "all_generated_tasks_retained": True,
        "same_capture_supplied_telemetry_and_output": True,
        "hidden_capture": "disabled",
        "architecture_family": "qwen2_moe",
        "per_task_labels_or_predictions_persisted_publicly": False,
        "raw_text_token_tensor_or_path_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only dataset summary; holdout sealed",
    }


def build_telemetry_summary(tasks, telemetry, labels):
    label_by_id = {row["task_id"]: row["label"] for row in labels}
    telemetry_by_id = {row["task_id"]: row for row in telemetry}
    train_rows = defaultdict(list)
    for task in tasks:
        if task["m26_split"] != "train":
            continue
        label = label_by_id[task["prompt_id"]]
        train_rows[label].append(telemetry_by_id[task["prompt_id"]])
    return {
        "schema_version": 1,
        "run_kind": "m26_train_pass_fail_telemetry_summary",
        "split_scope": "train_only",
        "holdout_excluded": True,
        "n_train_records": sum(len(rows) for rows in train_rows.values()),
        "train_label_distribution": {
            label: len(rows) for label, rows in sorted(train_rows.items())},
        "train_fail_vs_pass": compare_pass_fail(
            train_rows.get("fail", []), train_rows.get("pass", [])),
        "effect_size_interpretation": (
            "descriptive Hedges g and fixed-seed bootstrap mean-difference "
            "intervals on the train split only; no classifier, threshold, or "
            "predictive-value claim before the frozen M27 evaluation"),
        "predictive_value_claimed": False,
        "per_task_labels_or_predictions_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate train groups only; no ids/text/paths/tensors",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default="data/prompts/m26_error_manifest.json")
    ap.add_argument("--tasks-out",
                    default="reports/shadow/private/m26_hf_prompts_local.jsonl")
    ap.add_argument("--captures", default="data/captures/m26_qwen15_moe")
    ap.add_argument("--model-ref")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--telemetry-out",
                    default="reports/shadow/private/m26_hf_telemetry_records_local.jsonl")
    ap.add_argument("--runtime-out",
                    default="reports/shadow/private/m26_qwen_auto_outcomes_local.jsonl")
    ap.add_argument("--actions-out",
                    default="reports/shadow/private/m26_qwen_actions_local.jsonl")
    ap.add_argument("--results-out",
                    default="reports/shadow/private/m26_qwen_action_results_local.jsonl")
    ap.add_argument("--labels-out",
                    default="reports/shadow/private/m26_error_labels_local.jsonl")
    ap.add_argument("--summary-out",
                    default="reports/telemetry/hf_m26_error_run_summary.json")
    ap.add_argument("--telemetry-summary-out",
                    default="reports/telemetry/hf_m26_error_telemetry_summary.json")
    args = ap.parse_args(argv)

    manifest, tasks = prepare_private_tasks(args.manifest, args.tasks_out)
    if args.prepare_only:
        completion = M23.capture_completion(args.captures, tasks)
        print(f"[jlens] M26 predeclared tasks: {len(tasks)}; "
              f"existing={len(completion['complete'])}, "
              f"pending={len(completion['missing_or_invalid'])}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required for M26 real capture processing")

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
              "context": "M26 controlled local fixture context",
              "confidence": 0.8}
    })
    cfg = M23._qwen_config()
    telemetry, runtimes, actions, results, labels = [], [], [], [], []
    for task in tasks:
        path = Path(args.captures) / f"{task['prompt_id']}.pt"
        if not path.exists():
            raise FileNotFoundError(f"missing M26 capture: {task['prompt_id']}")
        capture = torch.load(path, map_location="cpu", weights_only=False)
        rows = M23.process_same_capture(
            task, capture, backend, cfg=cfg, retrieval_adapter=adapter)
        for kind, row in zip(("telemetry", "runtime", "action", "result"), rows):
            errors = list(schemas[kind].iter_errors(row))
            if errors:
                raise ValueError(
                    f"invalid {kind} for {task['prompt_id']}: {errors[0].message}")
        t, runtime, action, result = rows
        if action["action_type"] != "checker_needed":
            raise ValueError(
                "M26 action applicability drifted: "
                f"{task['prompt_id']} -> {action['action_type']}")
        telemetry.append(t); runtimes.append(runtime)
        actions.append(action); results.append(result)
        labels.append({
            "task_id": task["prompt_id"],
            "band": task["m26_band"],
            "split": task["m26_split"],
            "label": label_from_result(result),
        })

    M23.write_jsonl(args.telemetry_out, telemetry)
    M23.write_jsonl(args.runtime_out, runtimes)
    M23.write_jsonl(args.actions_out, actions)
    M23.write_jsonl(args.results_out, results)
    M23.write_jsonl(args.labels_out, labels)
    summary = build_run_summary(manifest, tasks, telemetry, actions, labels)
    telemetry_summary = build_telemetry_summary(tasks, telemetry, labels)
    for path, payload in ((args.summary_out, summary),
                          (args.telemetry_summary_out, telemetry_summary)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n")
    train = summary["train_label_distribution"]
    print(f"[jlens] M26: 96 records labeled; train pass/fail/undecided = "
          f"{train.get('pass', 0)}/{train.get('fail', 0)}/"
          f"{train.get('undecided', 0)}; holdout sealed until M27")
    if not summary["minimum_modeling_requirement_met"]:
        print("[jlens] M26 STOP: train split below the predeclared "
              "pass/fail minimum for modeling")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
