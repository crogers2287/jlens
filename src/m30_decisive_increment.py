#!/usr/bin/env python3
"""M30 decisive telemetry-vs-metadata increment test (768 tasks, n=192 holdout)."""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import action_executor as EXEC  # noqa: E402
from hf_telemetry_backend import HFTelemetryBackend  # noqa: E402
import m23_within_model as M23  # noqa: E402
import m26_objective_error as M26  # noqa: E402
import m29_scaled_error_power as M29  # noqa: E402

SPLITS = ("train", "validation", "holdout")
SPLIT_SIZES = {"train": 64, "validation": 32, "holdout": 32}
CALIBRATED_MODELS = ("full_telemetry", "metadata_plus_telemetry")


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("selection_status") != "predeclared_before_m30_task_generation":
        raise ValueError("M30 manifest is not predeclared before generation")
    bands = manifest.get("bands") or []
    tasks = manifest.get("tasks") or []
    if manifest.get("n_tasks") != 768 or len(tasks) != 768 or len(bands) != 6:
        raise ValueError("M30 manifest must declare six bands and 768 tasks")
    if len({task["task_id"] for task in tasks}) != 768:
        raise ValueError("M30 task ids must be unique")
    counts = Counter((task["band"], task["split"]) for task in tasks)
    for band in bands:
        for split, n in SPLIT_SIZES.items():
            if counts[(band["band_id"], split)] != n:
                raise ValueError(f"M30 split mismatch: {band['band_id']}/{split}")
    sets = manifest.get("frozen_feature_sets") or {}
    metadata = [band["band_id"] for band in bands]
    if sets.get("metadata_only") != metadata:
        raise ValueError("M30 metadata_only features must be the band one-hots")
    expected_full = (sets.get("logits_only", []) + sets.get("router_only", [])
                     + ["decode_step_count", "windowed_expert_shift",
                        "high_entropy_count", "low_confidence_count",
                        "top_k_margin_trend"])
    if sets.get("full_telemetry") != expected_full:
        raise ValueError("M30 frozen full_telemetry feature set changed")
    if sets.get("metadata_plus_telemetry") != metadata + expected_full:
        raise ValueError("M30 metadata_plus_telemetry must be metadata + full")
    if manifest.get("primary_comparison") != ["full_telemetry", "metadata_only"]:
        raise ValueError("M30 primary comparison changed")
    for feature in expected_full:
        if feature not in M26.FEATURES:
            raise ValueError(f"M30 frozen feature has no getter: {feature}")
    if not manifest.get("split_seal", {}).get("no_refit_after_holdout_capture"):
        raise ValueError("M30 manifest must seal the holdout before capture")
    return manifest


def _draw_tuples(rng, band, count, seen):
    a_lo, a_hi = band["operand_a_range"]
    b_lo, b_hi = band["operand_b_range"]
    tuples = []
    while len(tuples) < count:
        pair = (rng.randint(a_lo, a_hi), rng.randint(b_lo, b_hi))
        if pair in seen:
            continue
        seen.add(pair)
        tuples.append(pair)
    return tuples


def m29_tuples_by_band(m29_manifest_path):
    """Reproduce the operand tuples the committed M29 manifest generates."""
    manifest = M29.load_manifest(m29_manifest_path)
    seed = manifest["generation"]["seed"]
    result = {}
    for band in manifest["bands"]:
        rng = random.Random(f"{seed}:{band['band_id']}")
        result[band["band_id"]] = set(
            _draw_tuples(rng, band, band["n_tasks"], set()))
    return result


def generate_tasks(manifest, m29_manifest_path):
    """Expand the manifest into private tasks, disjoint from M29 tuples."""
    seed = manifest["generation"]["seed"]
    template = manifest["prompt_template"]
    prior = m29_tuples_by_band(m29_manifest_path)
    slots = defaultdict(list)
    for task in manifest["tasks"]:
        slots[task["band"]].append(task)

    tasks = []
    for band in manifest["bands"]:
        band_id = band["band_id"]
        rng = random.Random(f"{seed}:{band_id}")
        seen = set(prior.get(band_id, set()))
        tuples = _draw_tuples(rng, band, band["n_tasks"], seen)
        op = band["operator"]
        for slot, (a, b) in zip(slots[band_id], tuples):
            answer = a + b if op == "+" else a * b
            tasks.append({
                "prompt_id": slot["task_id"],
                "m30_band": band_id,
                "m30_split": slot["split"],
                "task_category": "math",
                "expression": f"{a}{op}{b}",
                "known_answer": str(answer),
                "prompt": template.format(a=a, op=op, b=b),
            })
    if len(tasks) != 768 or len({t["prompt_id"] for t in tasks}) != 768:
        raise ValueError("M30 generation did not produce 768 unique tasks")
    order = {task["task_id"]: index
             for index, task in enumerate(manifest["tasks"])}
    tasks.sort(key=lambda task: order[task["prompt_id"]])
    return tasks


def prepare_private_tasks(manifest_path, m29_manifest_path, output_path):
    manifest = load_manifest(manifest_path)
    tasks = generate_tasks(manifest, m29_manifest_path)
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(task) + "\n" for task in tasks))
    return manifest, tasks


def load_dataset(manifest, labels_path, telemetry_path):
    labels = M23.read_jsonl(labels_path)
    telemetry = {row["task_id"]: row for row in M23.read_jsonl(telemetry_path)}
    if len(labels) != 768:
        raise ValueError("M30 requires the full 768-task label file")
    missing = [row["task_id"] for row in labels
               if row["task_id"] not in telemetry]
    if missing:
        raise ValueError(f"M30 telemetry missing task ids: {len(missing)}")
    split = {name: [] for name in SPLITS}
    undecided = Counter()
    for row in labels:
        if row["label"] == "undecided":
            undecided[row["split"]] += 1
            continue
        split[row["split"]].append(
            (row, M29.feature_row(manifest, row, telemetry[row["task_id"]])))
    return split, dict(undecided)


def classify_increment(primary_delta, powered):
    lo, hi = primary_delta["delta_accuracy_bootstrap_95pct"]
    if lo > 0 and powered:
        return "established"
    if hi < 0:
        return "negative"
    return "not_established"


def evaluate(manifest, split, undecided):
    power = M29.check_power(manifest, split, undecided)
    baselines = M29.fit_baselines(manifest, split)
    thresholds = {name: M29.select_threshold(baselines[name],
                                             split["validation"])
                  for name in CALIBRATED_MODELS}

    holdout_rows = [row for _, row in split["holdout"]]
    actual = [label_row["label"] for label_row, _ in split["holdout"]]
    classes = sorted(set(actual) | set(M29.CLASSES))
    predictions, evaluations = {}, {}
    for name in manifest["baseline_order"]:
        predicted = [baselines[name].predict(row) for row in holdout_rows]
        predictions[name] = predicted
        metrics = M29.M27.classification_metrics(
            actual, predicted, classes, f"m30:frozen:{name}:accuracy")
        metrics["features"] = list(baselines[name].features)
        metrics["feature_count"] = len(baselines[name].features)
        evaluations[name] = metrics

    incremental = {}
    for name_a, name_b in manifest["incremental_value_protocol"]["comparisons"]:
        delta = M29.paired_delta_bootstrap(
            actual, predictions[name_a], predictions[name_b],
            f"m30:delta:{name_a}-vs-{name_b}")
        delta["comparison"] = f"{name_a} minus {name_b}"
        lo, hi = delta["delta_accuracy_bootstrap_95pct"]
        delta["interval_excludes_zero"] = lo > 0 or hi < 0
        incremental[f"{name_a}_vs_{name_b}"] = delta

    primary_key = "full_telemetry_vs_metadata_only"
    verdict = classify_increment(
        incremental[primary_key],
        power["increment_test_adequately_powered"])

    calibration = {
        name: M29.calibration_block(
            baselines[name], thresholds[name][0], thresholds[name][1],
            split["holdout"])
        for name in CALIBRATED_MODELS}

    distribution = Counter(actual)
    return {
        "schema_version": 1,
        "run_kind": "m30_decisive_increment_evaluation",
        "task_category": manifest["task_category"],
        "label_classes": list(M29.CLASSES),
        "n_train_used": len(split["train"]),
        "n_validation_used": len(split["validation"]),
        "n_holdout_used": len(holdout_rows),
        "power": power,
        "holdout_label_distribution": dict(sorted(distribution.items())),
        "majority_class_baseline_accuracy": (
            max(distribution.values()) / len(actual)),
        "classifier_family": "train-standardized nearest centroid",
        "identical_to_m29_family": True,
        "baseline_order": list(manifest["baseline_order"]),
        "primary_comparison": list(manifest["primary_comparison"]),
        "evaluations": evaluations,
        "incremental_value_over_metadata": incremental,
        "primary_increment_classification": verdict,
        "classification_rule": dict(
            manifest["incremental_value_protocol"]["classification_rule"]),
        "calibration": calibration,
        "holdout_evaluated_once": True,
        "refit_or_threshold_tuning_after_holdout": False,
        "threshold_status": "candidate-only",
        "production_threshold_set": False,
        "per_task_predictions_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate metrics/intervals only; no ids/text/paths",
    }


def build_run_summary(manifest, tasks, telemetry, actions, labels):
    label_by_id = {row["task_id"]: row["label"] for row in labels}
    split_labels = defaultdict(Counter)
    band_split = defaultdict(Counter)
    for task in tasks:
        label = label_by_id[task["prompt_id"]]
        split_labels[task["m30_split"]][label] += 1
        band_split[f"{task['m30_split']}:{task['m30_band']}"][label] += 1
    capped = sum(row["decode_step_count"] == M26.DECODE_CAP_TOKENS
                 for row in telemetry)
    return {
        "schema_version": 1,
        "run_kind": "m30_decisive_dataset",
        "task_category": manifest["task_category"],
        "prompt_family_constant": True,
        "n_records": len(telemetry),
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
        "label_distribution_by_split": {
            name: dict(sorted(split_labels[name].items())) for name in SPLITS},
        "label_distribution_by_split_band": {
            key: dict(sorted(counter.items()))
            for key, counter in sorted(band_split.items())},
        "decode_cap_tokens": M26.DECODE_CAP_TOKENS,
        "decode_cap_reached_count": capped,
        "operands_disjoint_from_m29": True,
        "no_posthoc_selection": True,
        "all_generated_tasks_retained": True,
        "same_capture_supplied_telemetry_and_output": True,
        "hidden_capture": "disabled",
        "architecture_family": "qwen2_moe",
        "per_task_labels_or_predictions_persisted_publicly": False,
        "raw_text_token_tensor_or_path_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only decisive dataset summary",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default="data/prompts/m30_decisive_manifest.json")
    ap.add_argument("--m29-manifest", default="data/prompts/m29_power_manifest.json")
    ap.add_argument("--tasks-out",
                    default="reports/shadow/private/m30_hf_prompts_local.jsonl")
    ap.add_argument("--captures", default="data/captures/m30_qwen15_moe")
    ap.add_argument("--model-ref")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--telemetry-out",
                    default="reports/shadow/private/m30_hf_telemetry_records_local.jsonl")
    ap.add_argument("--runtime-out",
                    default="reports/shadow/private/m30_qwen_auto_outcomes_local.jsonl")
    ap.add_argument("--actions-out",
                    default="reports/shadow/private/m30_qwen_actions_local.jsonl")
    ap.add_argument("--results-out",
                    default="reports/shadow/private/m30_qwen_action_results_local.jsonl")
    ap.add_argument("--labels-out",
                    default="reports/shadow/private/m30_error_labels_local.jsonl")
    ap.add_argument("--summary-out",
                    default="reports/telemetry/hf_m30_decisive_run_summary.json")
    ap.add_argument("--evaluation-out",
                    default="reports/telemetry/hf_m30_decisive_increment_evaluation.json")
    args = ap.parse_args(argv)

    manifest, tasks = prepare_private_tasks(
        args.manifest, args.m29_manifest, args.tasks_out)
    if args.prepare_only:
        completion = M23.capture_completion(args.captures, tasks)
        print(f"[jlens] M30 predeclared tasks: {len(tasks)}; "
              f"existing={len(completion['complete'])}, "
              f"pending={len(completion['missing_or_invalid'])}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required for M30 real capture processing")

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
              "context": "M30 controlled local fixture context",
              "confidence": 0.8}
    })
    cfg = M23._qwen_config()
    telemetry, runtimes, actions, results, labels = [], [], [], [], []
    for task in tasks:
        path = Path(args.captures) / f"{task['prompt_id']}.pt"
        if not path.exists():
            raise FileNotFoundError(f"missing M30 capture: {task['prompt_id']}")
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
                "M30 action applicability drifted: "
                f"{task['prompt_id']} -> {action['action_type']}")
        telemetry.append(t); runtimes.append(runtime)
        actions.append(action); results.append(result)
        labels.append({
            "task_id": task["prompt_id"],
            "band": task["m30_band"],
            "split": task["m30_split"],
            "label": M26.label_from_result(result),
        })

    M23.write_jsonl(args.telemetry_out, telemetry)
    M23.write_jsonl(args.runtime_out, runtimes)
    M23.write_jsonl(args.actions_out, actions)
    M23.write_jsonl(args.results_out, results)
    M23.write_jsonl(args.labels_out, labels)

    split, undecided = load_dataset(manifest, args.labels_out,
                                    args.telemetry_out)
    summary = build_run_summary(manifest, tasks, telemetry, actions, labels)
    evaluation = evaluate(manifest, split, undecided)
    for path, payload in ((args.summary_out, summary),
                          (args.evaluation_out, evaluation)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n")
    primary = evaluation["incremental_value_over_metadata"][
        "full_telemetry_vs_metadata_only"]
    print(f"[jlens] M30: 768 records; holdout n={evaluation['n_holdout_used']}; "
          f"primary delta={primary['delta_accuracy']:+.4f} "
          f"ci={primary['delta_accuracy_bootstrap_95pct']}; "
          f"verdict={evaluation['primary_increment_classification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
