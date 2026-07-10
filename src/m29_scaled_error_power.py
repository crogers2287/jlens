#!/usr/bin/env python3
"""M29 scaled objective error prediction power test (telemetry vs metadata)."""
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
from hf_telemetry_backend import HFTelemetryBackend  # noqa: E402
import m23_within_model as M23  # noqa: E402
import m26_objective_error as M26  # noqa: E402
import m27_frozen_error_holdout as M27  # noqa: E402
import m28_ablation_calibration as M28  # noqa: E402

SPLITS = ("train", "validation", "holdout")
CLASSES = ("fail", "pass")
CALIBRATED_MODELS = ("full_telemetry", "metadata_plus_telemetry")


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("selection_status") != "predeclared_before_m29_task_generation":
        raise ValueError("M29 manifest is not predeclared before generation")
    bands = manifest.get("bands") or []
    tasks = manifest.get("tasks") or []
    if manifest.get("n_tasks") != 384 or len(tasks) != 384 or len(bands) != 6:
        raise ValueError("M29 manifest must declare six bands and 384 tasks")
    if len({task["task_id"] for task in tasks}) != 384:
        raise ValueError("M29 task ids must be unique")
    counts = Counter((task["band"], task["split"]) for task in tasks)
    for band in bands:
        expected = {"train": 32, "validation": 16, "holdout": 16}
        for split, n in expected.items():
            if counts[(band["band_id"], split)] != n:
                raise ValueError(f"M29 split mismatch: {band['band_id']}/{split}")
    sets = manifest.get("frozen_feature_sets") or {}
    metadata = [band["band_id"] for band in bands]
    if sets.get("metadata_only") != metadata:
        raise ValueError("M29 metadata_only features must be the band one-hots")
    expected_full = (sets.get("logits_only", []) + sets.get("router_only", [])
                     + ["decode_step_count", "windowed_expert_shift",
                        "high_entropy_count", "low_confidence_count",
                        "top_k_margin_trend"])
    if sets.get("full_telemetry") != expected_full:
        raise ValueError("M29 frozen full_telemetry feature set changed")
    if sets.get("metadata_plus_telemetry") != metadata + expected_full:
        raise ValueError("M29 metadata_plus_telemetry must be metadata + full")
    if sets.get("window_entropy") != ["decode_window_entropy",
                                      "high_entropy_count"]:
        raise ValueError("M29 window_entropy feature set changed")
    for feature in expected_full:
        if feature not in M26.FEATURES:
            raise ValueError(f"M29 frozen feature has no getter: {feature}")
    if manifest.get("baseline_order") != [
            "majority_class", "metadata_only", "logits_only", "router_only",
            "window_entropy", "full_telemetry", "metadata_plus_telemetry"]:
        raise ValueError("M29 baseline order changed")
    if not manifest.get("split_seal", {}).get("no_refit_after_holdout_capture"):
        raise ValueError("M29 manifest must seal the holdout before capture")
    return manifest


def generate_tasks(manifest):
    """Deterministically expand the predeclared manifest into private tasks."""
    seed = manifest["generation"]["seed"]
    template = manifest["prompt_template"]
    by_band = {band["band_id"]: band for band in manifest["bands"]}
    slots = defaultdict(list)
    for task in manifest["tasks"]:
        slots[task["band"]].append(task)

    tasks = []
    for band_id in sorted(slots):
        band = by_band[band_id]
        rng = random.Random(f"{seed}:{band_id}")
        a_lo, a_hi = band["operand_a_range"]
        b_lo, b_hi = band["operand_b_range"]
        seen, tuples = set(), []
        while len(tuples) < band["n_tasks"]:
            pair = (rng.randint(a_lo, a_hi), rng.randint(b_lo, b_hi))
            if pair in seen:
                continue
            seen.add(pair)
            tuples.append(pair)
        op = band["operator"]
        for slot, (a, b) in zip(slots[band_id], tuples):
            answer = a + b if op == "+" else a * b
            tasks.append({
                "prompt_id": slot["task_id"],
                "m29_band": band_id,
                "m29_split": slot["split"],
                "task_category": "math",
                "expression": f"{a}{op}{b}",
                "known_answer": str(answer),
                "prompt": template.format(a=a, op=op, b=b),
            })
    if len(tasks) != 384 or len({t["prompt_id"] for t in tasks}) != 384:
        raise ValueError("M29 generation did not produce 384 unique tasks")
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


def feature_row(manifest, label_row, record):
    row = {band["band_id"]: 1.0 if label_row["band"] == band["band_id"] else 0.0
           for band in manifest["bands"]}
    for name, getter in M26.FEATURES.items():
        value = getter(record)
        if value is None or not math.isfinite(float(value)):
            raise ValueError(
                f"missing/non-finite feature {name} for {label_row['task_id']}")
        row[name] = float(value)
    return row


def load_dataset(manifest, labels_path, telemetry_path):
    labels = M23.read_jsonl(labels_path)
    telemetry = {row["task_id"]: row for row in M23.read_jsonl(telemetry_path)}
    if len(labels) != 384:
        raise ValueError("M29 requires the full 384-task label file")
    missing = [row["task_id"] for row in labels
               if row["task_id"] not in telemetry]
    if missing:
        raise ValueError(f"M29 telemetry missing task ids: {len(missing)}")
    split = {name: [] for name in SPLITS}
    undecided = Counter()
    for row in labels:
        if row["label"] == "undecided":
            undecided[row["split"]] += 1
            continue
        split[row["split"]].append(
            (row, feature_row(manifest, row, telemetry[row["task_id"]])))
    return split, dict(undecided)


def check_power(manifest, split, undecided):
    requirements = manifest["power_requirements"]
    counts, met = {}, {}
    for name in SPLITS:
        distribution = Counter(
            label_row["label"] for label_row, _ in split[name])
        counts[name] = dict(sorted(distribution.items()))
        met[name] = (distribution.get("pass", 0)
                     >= requirements[f"{name}_pass_min"]
                     and distribution.get("fail", 0)
                     >= requirements[f"{name}_fail_min"])
    return {
        "requirements": dict(requirements),
        "label_counts_by_split": counts,
        "undecided_excluded_counts": undecided,
        "met_by_split": met,
        "increment_test_adequately_powered": all(met.values()),
    }


def fit_baselines(manifest, split):
    train_rows = [row for _, row in split["train"]]
    train_labels = [label_row["label"] for label_row, _ in split["train"]]
    if len(set(train_labels)) < 2:
        raise ValueError("M29 train split lacks both classes; cannot fit")
    sets = manifest["frozen_feature_sets"]
    baselines = {"majority_class": M27.MajorityBaseline(train_labels)}
    for name in manifest["baseline_order"][1:]:
        baselines[name] = M27.FrozenDictCentroid.fit(
            train_rows, train_labels, sets[name])
    return baselines


def paired_delta_bootstrap(actual, pred_a, pred_b, seed, iterations=2000):
    """Paired bootstrap intervals for accuracy/balanced-accuracy differences."""
    rng = random.Random(seed)
    n = len(actual)

    def scores(indices, predictions):
        correct = Counter()
        support = Counter()
        for i in indices:
            support[actual[i]] += 1
            correct[actual[i]] += predictions[i] == actual[i]
        accuracy = sum(correct.values()) / len(indices)
        recalls = [correct[c] / support[c] for c in CLASSES if support[c]]
        return accuracy, statistics.fmean(recalls) if recalls else 0.0

    acc_deltas, bacc_deltas = [], []
    for _ in range(iterations):
        indices = [rng.randrange(n) for _ in range(n)]
        acc_a, bacc_a = scores(indices, pred_a)
        acc_b, bacc_b = scores(indices, pred_b)
        acc_deltas.append(acc_a - acc_b)
        bacc_deltas.append(bacc_a - bacc_b)
    acc_deltas.sort(); bacc_deltas.sort()
    lo, hi = int(0.025 * (iterations - 1)), int(0.975 * (iterations - 1))
    discordant = Counter()
    for a, b, truth in zip(pred_a, pred_b, actual):
        key = ("a_right_b_wrong" if a == truth and b != truth else
               "a_wrong_b_right" if a != truth and b == truth else
               "both_right" if a == truth else "both_wrong")
        discordant[key] += 1
    point_acc = (sum(a == t for a, t in zip(pred_a, actual))
                 - sum(b == t for b, t in zip(pred_b, actual))) / n
    return {
        "delta_accuracy": point_acc,
        "delta_accuracy_bootstrap_95pct": [acc_deltas[lo], acc_deltas[hi]],
        "delta_balanced_accuracy_bootstrap_95pct": [
            bacc_deltas[lo], bacc_deltas[hi]],
        "bootstrap_iterations": iterations,
        "paired": True,
        "prediction_agreement_counts": dict(sorted(discordant.items())),
    }


def select_threshold(classifier, validation_pairs):
    """Candidate-only threshold from the validation split, per the manifest."""
    scores = [(M28.fail_probability(classifier, row), label_row["label"])
              for label_row, row in validation_pairs]

    def balanced_accuracy(threshold):
        correct = Counter()
        support = Counter()
        for score, label in scores:
            predicted = "fail" if score >= threshold else "pass"
            support[label] += 1
            correct[label] += predicted == label
        recalls = [correct[c] / support[c] for c in CLASSES if support[c]]
        return statistics.fmean(recalls) if recalls else 0.0

    grid = [round(0.05 * step, 2) for step in range(1, 20)]
    best = max(((balanced_accuracy(t), -t) for t in grid))
    threshold = -best[1]
    return threshold, best[0]


def calibration_block(classifier, threshold, validation_bacc, holdout_pairs):
    scores = [(M28.fail_probability(classifier, row), label_row["label"])
              for label_row, row in holdout_pairs]
    ordered = sorted(scores, key=lambda item: item[0])
    n_bins = 8
    bins, ece = [], 0.0
    for index in range(n_bins):
        chunk = ordered[index * len(ordered) // n_bins:
                        (index + 1) * len(ordered) // n_bins]
        if not chunk:
            continue
        mean_predicted = statistics.fmean(score for score, _ in chunk)
        observed = statistics.fmean(
            1.0 if label == "fail" else 0.0 for _, label in chunk)
        ece += (len(chunk) / len(ordered)) * abs(mean_predicted - observed)
        bins.append({"n": len(chunk),
                     "mean_predicted_fail_probability": mean_predicted,
                     "observed_fail_rate": observed})

    def holdout_bacc(threshold_value):
        correct = Counter()
        support = Counter()
        for score, label in scores:
            predicted = "fail" if score >= threshold_value else "pass"
            support[label] += 1
            correct[label] += predicted == label
        recalls = [correct[c] / support[c] for c in CLASSES if support[c]]
        return statistics.fmean(recalls) if recalls else 0.0

    return {
        "score_definition": ("softmax over negative squared centroid "
                             "distances; probability mass on the fail class"),
        "reliability_bins_equal_count": bins,
        "expected_calibration_error": ece,
        "candidate_threshold": {
            "status": "candidate-only",
            "not_for_production": True,
            "derived_from": "validation split balanced-accuracy grid only",
            "threshold_fail_probability": threshold,
            "validation_balanced_accuracy_at_threshold": validation_bacc,
            "holdout_balanced_accuracy_at_threshold_descriptive":
                holdout_bacc(threshold),
        },
    }


def evaluate(manifest, split, undecided):
    power = check_power(manifest, split, undecided)
    baselines = fit_baselines(manifest, split)
    thresholds = {name: select_threshold(baselines[name], split["validation"])
                  for name in CALIBRATED_MODELS}

    holdout_rows = [row for _, row in split["holdout"]]
    actual = [label_row["label"] for label_row, _ in split["holdout"]]
    classes = sorted(set(actual) | set(CLASSES))
    predictions = {}
    evaluations = {}
    for name in manifest["baseline_order"]:
        predicted = [baselines[name].predict(row) for row in holdout_rows]
        predictions[name] = predicted
        metrics = M27.classification_metrics(
            actual, predicted, classes, f"m29:frozen:{name}:accuracy")
        metrics["features"] = list(baselines[name].features)
        metrics["feature_count"] = len(baselines[name].features)
        evaluations[name] = metrics

    incremental = {}
    for name_a, name_b in manifest["incremental_value_protocol"]["comparisons"]:
        delta = paired_delta_bootstrap(
            actual, predictions[name_a], predictions[name_b],
            f"m29:delta:{name_a}-vs-{name_b}")
        lo, hi = delta["delta_accuracy_bootstrap_95pct"]
        delta["comparison"] = f"{name_a} minus {name_b}"
        delta["interval_excludes_zero"] = lo > 0 or hi < 0
        delta["meaningful_increment_established"] = bool(
            (lo > 0) and power["increment_test_adequately_powered"])
        incremental[f"{name_a}_vs_{name_b}"] = delta

    calibration = {
        name: calibration_block(
            baselines[name], thresholds[name][0], thresholds[name][1],
            split["holdout"])
        for name in CALIBRATED_MODELS}

    distribution = Counter(actual)
    return {
        "schema_version": 1,
        "run_kind": "m29_scaled_error_power_evaluation",
        "task_category": manifest["task_category"],
        "label_classes": list(CLASSES),
        "n_train_used": len(split["train"]),
        "n_validation_used": len(split["validation"]),
        "n_holdout_used": len(holdout_rows),
        "power": power,
        "holdout_label_distribution": dict(sorted(distribution.items())),
        "majority_class_baseline_accuracy": (
            max(distribution.values()) / len(actual)),
        "classifier_family": "train-standardized nearest centroid",
        "distance": "squared_euclidean",
        "tie_break": "lexicographic (fail before pass)",
        "baseline_order": list(manifest["baseline_order"]),
        "evaluations": evaluations,
        "incremental_value_over_metadata": incremental,
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
    by_split_band = defaultdict(Counter)
    for task in tasks:
        by_split_band[(task["m29_split"], task["m29_band"])][
            label_by_id[task["prompt_id"]]] += 1
    telemetry_by_id = {row["task_id"]: row for row in telemetry}
    capped = sum(row["decode_step_count"] == M26.DECODE_CAP_TOKENS
                 for row in telemetry)
    split_labels = defaultdict(Counter)
    for task in tasks:
        split_labels[task["m29_split"]][label_by_id[task["prompt_id"]]] += 1
    del telemetry_by_id
    return {
        "schema_version": 1,
        "run_kind": "m29_scaled_error_dataset",
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
            f"{split}:{band}": dict(sorted(counter.items()))
            for (split, band), counter in sorted(by_split_band.items())},
        "decode_cap_tokens": M26.DECODE_CAP_TOKENS,
        "decode_cap_reached_count": capped,
        "no_posthoc_selection": True,
        "all_generated_tasks_retained": True,
        "same_capture_supplied_telemetry_and_output": True,
        "hidden_capture": "disabled",
        "architecture_family": "qwen2_moe",
        "per_task_labels_or_predictions_persisted_publicly": False,
        "raw_text_token_tensor_or_path_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only scaled dataset summary",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default="data/prompts/m29_power_manifest.json")
    ap.add_argument("--tasks-out",
                    default="reports/shadow/private/m29_hf_prompts_local.jsonl")
    ap.add_argument("--captures", default="data/captures/m29_qwen15_moe")
    ap.add_argument("--model-ref")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--telemetry-out",
                    default="reports/shadow/private/m29_hf_telemetry_records_local.jsonl")
    ap.add_argument("--runtime-out",
                    default="reports/shadow/private/m29_qwen_auto_outcomes_local.jsonl")
    ap.add_argument("--actions-out",
                    default="reports/shadow/private/m29_qwen_actions_local.jsonl")
    ap.add_argument("--results-out",
                    default="reports/shadow/private/m29_qwen_action_results_local.jsonl")
    ap.add_argument("--labels-out",
                    default="reports/shadow/private/m29_error_labels_local.jsonl")
    ap.add_argument("--summary-out",
                    default="reports/telemetry/hf_m29_power_run_summary.json")
    ap.add_argument("--evaluation-out",
                    default="reports/telemetry/hf_m29_power_evaluation.json")
    args = ap.parse_args(argv)

    manifest, tasks = prepare_private_tasks(args.manifest, args.tasks_out)
    if args.prepare_only:
        completion = M23.capture_completion(args.captures, tasks)
        print(f"[jlens] M29 predeclared tasks: {len(tasks)}; "
              f"existing={len(completion['complete'])}, "
              f"pending={len(completion['missing_or_invalid'])}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required for M29 real capture processing")

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
              "context": "M29 controlled local fixture context",
              "confidence": 0.8}
    })
    cfg = M23._qwen_config()
    telemetry, runtimes, actions, results, labels = [], [], [], [], []
    for task in tasks:
        path = Path(args.captures) / f"{task['prompt_id']}.pt"
        if not path.exists():
            raise FileNotFoundError(f"missing M29 capture: {task['prompt_id']}")
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
                "M29 action applicability drifted: "
                f"{task['prompt_id']} -> {action['action_type']}")
        telemetry.append(t); runtimes.append(runtime)
        actions.append(action); results.append(result)
        labels.append({
            "task_id": task["prompt_id"],
            "band": task["m29_band"],
            "split": task["m29_split"],
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
    key = evaluation["incremental_value_over_metadata"][
        "metadata_plus_telemetry_vs_metadata_only"]
    print(f"[jlens] M29: 384 records; holdout n={evaluation['n_holdout_used']}; "
          f"delta_acc(meta+tel - meta)={key['delta_accuracy']:+.3f} "
          f"ci={key['delta_accuracy_bootstrap_95pct']}; "
          f"powered={evaluation['power']['increment_test_adequately_powered']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
