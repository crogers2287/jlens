#!/usr/bin/env python3
"""M31 telemetry-triggered retry intervention study on the frozen M30 score."""
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
import m27_frozen_error_holdout as M27  # noqa: E402
import m28_ablation_calibration as M28  # noqa: E402
import m29_scaled_error_power as M29  # noqa: E402
import m30_decisive_increment as M30  # noqa: E402
import verifiers as VZ  # noqa: E402

POLICIES = ("no_retry", "always_retry", "random_retry", "telemetry_triggered")
DELTAS = (("telemetry_triggered", "no_retry"),
          ("telemetry_triggered", "random_retry"),
          ("always_retry", "no_retry"),
          ("random_retry", "no_retry"))


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("selection_status") != "predeclared_before_m31_task_generation":
        raise ValueError("M31 manifest is not predeclared before generation")
    bands = manifest.get("bands") or []
    tasks = manifest.get("tasks") or []
    if manifest.get("n_tasks") != 192 or len(tasks) != 192 or len(bands) != 6:
        raise ValueError("M31 manifest must declare six bands and 192 tasks")
    if len({task["task_id"] for task in tasks}) != 192:
        raise ValueError("M31 task ids must be unique")
    counts = Counter(task["band"] for task in tasks)
    for band in bands:
        if band.get("n_tasks") != 32 or counts[band["band_id"]] != 32:
            raise ValueError(f"M31 band size mismatch: {band['band_id']}")
    frozen = manifest.get("frozen_score") or {}
    if frozen.get("threshold_fail_probability") != 0.5 \
            or not frozen.get("no_refit_or_threshold_change"):
        raise ValueError("M31 frozen-score declaration changed")
    retry = manifest.get("decode_protocols", {}).get("retry") or {}
    if retry.get("temperature") != 0.7 or retry.get("samples_per_task") != 1:
        raise ValueError("M31 retry decode protocol changed")
    return manifest


def prior_tuples_by_band(m29_manifest_path, m30_manifest_path):
    """Reproduce every operand tuple the M29 and M30 manifests generate."""
    prior = M30.m29_tuples_by_band(m29_manifest_path)
    m30_manifest = M30.load_manifest(m30_manifest_path)
    seed = m30_manifest["generation"]["seed"]
    for band in m30_manifest["bands"]:
        rng = random.Random(f"{seed}:{band['band_id']}")
        seen = set(prior[band["band_id"]])
        tuples = M30._draw_tuples(rng, band, band["n_tasks"], seen)
        prior[band["band_id"]] |= set(tuples)
    return prior


def generate_tasks(manifest, m29_manifest_path, m30_manifest_path):
    seed = manifest["generation"]["seed"]
    template = manifest["prompt_template"]
    prior = prior_tuples_by_band(m29_manifest_path, m30_manifest_path)
    slots = defaultdict(list)
    for task in manifest["tasks"]:
        slots[task["band"]].append(task)
    tasks = []
    for band in manifest["bands"]:
        band_id = band["band_id"]
        rng = random.Random(f"{seed}:{band_id}")
        seen = set(prior[band_id])
        tuples = M30._draw_tuples(rng, band, band["n_tasks"], seen)
        op = band["operator"]
        for slot, (a, b) in zip(slots[band_id], tuples):
            tasks.append({
                "prompt_id": slot["task_id"],
                "m31_band": band_id,
                "task_category": "math",
                "expression": f"{a}{op}{b}",
                "known_answer": str(a * b if op == "*" else a + b),
                "prompt": template.format(a=a, op=op, b=b),
            })
    if len(tasks) != 192 or len({t["prompt_id"] for t in tasks}) != 192:
        raise ValueError("M31 generation did not produce 192 unique tasks")
    order = {task["task_id"]: index
             for index, task in enumerate(manifest["tasks"])}
    tasks.sort(key=lambda task: order[task["prompt_id"]])
    return tasks


def prepare_private_tasks(manifest_path, m29_manifest_path, m30_manifest_path,
                          output_path):
    manifest = load_manifest(manifest_path)
    tasks = generate_tasks(manifest, m29_manifest_path, m30_manifest_path)
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(task) + "\n" for task in tasks))
    return manifest, tasks


def frozen_m30_classifier(m30_manifest_path, m30_labels_path,
                          m30_telemetry_path, m30_evaluation_path):
    """Refit the M30 full_telemetry model deterministically and verify it
    reproduces the published M30 holdout confusion matrix exactly."""
    m30_manifest = M30.load_manifest(m30_manifest_path)
    split, _ = M30.load_dataset(m30_manifest, m30_labels_path,
                                m30_telemetry_path)
    features = m30_manifest["frozen_feature_sets"]["full_telemetry"]
    classifier = M27.FrozenDictCentroid.fit(
        [row for _, row in split["train"]],
        [label_row["label"] for label_row, _ in split["train"]],
        features)
    published = json.loads(Path(m30_evaluation_path).read_text())
    expected = published["evaluations"]["full_telemetry"]["confusion_matrix"]
    confusion = {true: {pred: 0 for pred in ("fail", "pass")}
                 for true in ("fail", "pass")}
    for label_row, row in split["holdout"]:
        confusion[label_row["label"]][classifier.predict(row)] += 1
    if confusion != expected:
        raise ValueError(
            "M31 frozen-score verification failed: refit M30 model does not "
            "reproduce the published holdout confusion matrix")
    return classifier


def _success_delta_bootstrap(success_a, success_b, seed, iterations=2000):
    rng = random.Random(seed)
    n = len(success_a)
    deltas = []
    for _ in range(iterations):
        indices = [rng.randrange(n) for _ in range(n)]
        deltas.append((sum(success_a[i] for i in indices)
                       - sum(success_b[i] for i in indices)) / n)
    deltas.sort()
    return [deltas[int(0.025 * (iterations - 1))],
            deltas[int(0.975 * (iterations - 1))]]


def run_policies(manifest, rows):
    """rows: per task {task_id, band, original_pass, retry_pass, p_fail}."""
    threshold = manifest["frozen_score"]["threshold_fail_probability"]
    triggered = {row["task_id"] for row in rows
                 if row["p_fail"] >= threshold}
    rng = random.Random("m31:random-retry")
    random_set = set(rng.sample(sorted(row["task_id"] for row in rows),
                                len(triggered)))
    retried_by_policy = {
        "no_retry": set(),
        "always_retry": {row["task_id"] for row in rows},
        "random_retry": random_set,
        "telemetry_triggered": triggered,
    }

    success = {}
    metrics = {}
    for policy, retried in retried_by_policy.items():
        outcomes = []
        false_alarms = rescued = introduced = 0
        for row in rows:
            use_retry = row["task_id"] in retried
            final = row["retry_pass"] if use_retry else row["original_pass"]
            outcomes.append(1 if final else 0)
            if use_retry:
                if row["original_pass"]:
                    false_alarms += 1
                    if not row["retry_pass"]:
                        introduced += 1
                elif row["retry_pass"]:
                    rescued += 1
        success[policy] = outcomes
        metrics[policy] = {
            "verified_success_rate": sum(outcomes) / len(outcomes),
            "retries_used": len(retried),
            "false_alarm_count": false_alarms,
            "errors_rescued": rescued,
            "errors_introduced": introduced,
        }

    deltas = {}
    for name_a, name_b in DELTAS:
        point = (metrics[name_a]["verified_success_rate"]
                 - metrics[name_b]["verified_success_rate"])
        interval = _success_delta_bootstrap(
            success[name_a], success[name_b],
            f"m31:delta:{name_a}-vs-{name_b}")
        deltas[f"{name_a}_vs_{name_b}"] = {
            "delta_success_rate": point,
            "delta_success_bootstrap_95pct": interval,
            "bootstrap_iterations": 2000,
            "paired": True,
        }

    over_none = deltas["telemetry_triggered_vs_no_retry"][
        "delta_success_bootstrap_95pct"]
    over_random = deltas["telemetry_triggered_vs_random_retry"][
        "delta_success_bootstrap_95pct"]
    if over_none[0] > 0 and over_random[0] > 0:
        verdict = "useful"
    elif over_none[1] < 0:
        verdict = "harmful"
    else:
        verdict = "not_established"
    return {
        "trigger_count": len(triggered),
        "trigger_rate": len(triggered) / len(rows),
        "policy_metrics": metrics,
        "paired_success_deltas": deltas,
        "telemetry_policy_classification": verdict,
    }, triggered


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest",
                    default="data/prompts/m31_intervention_manifest.json")
    ap.add_argument("--m29-manifest", default="data/prompts/m29_power_manifest.json")
    ap.add_argument("--m30-manifest", default="data/prompts/m30_decisive_manifest.json")
    ap.add_argument("--m30-labels",
                    default="reports/shadow/private/m30_error_labels_local.jsonl")
    ap.add_argument("--m30-telemetry",
                    default="reports/shadow/private/m30_hf_telemetry_records_local.jsonl")
    ap.add_argument("--m30-evaluation",
                    default="reports/telemetry/hf_m30_decisive_increment_evaluation.json")
    ap.add_argument("--tasks-out",
                    default="reports/shadow/private/m31_hf_prompts_local.jsonl")
    ap.add_argument("--captures", default="data/captures/m31_qwen15_moe")
    ap.add_argument("--retry-captures", default="data/captures/m31_qwen15_moe_retry")
    ap.add_argument("--model-ref")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--telemetry-out",
                    default="reports/shadow/private/m31_hf_telemetry_records_local.jsonl")
    ap.add_argument("--rows-out",
                    default="reports/shadow/private/m31_intervention_rows_local.jsonl")
    ap.add_argument("--traces-out",
                    default="reports/shadow/private/m31_recovery_traces_local.jsonl")
    ap.add_argument("--summary-out",
                    default="reports/telemetry/hf_m31_intervention_run_summary.json")
    ap.add_argument("--evaluation-out",
                    default="reports/telemetry/hf_m31_intervention_evaluation.json")
    args = ap.parse_args(argv)

    manifest, tasks = prepare_private_tasks(
        args.manifest, args.m29_manifest, args.m30_manifest, args.tasks_out)
    if args.prepare_only:
        completion = M23.capture_completion(args.captures, tasks)
        retry_completion = M23.capture_completion(args.retry_captures, tasks)
        print(f"[jlens] M31 predeclared tasks: {len(tasks)}; "
              f"original existing={len(completion['complete'])}, "
              f"retry existing={len(retry_completion['complete'])}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required for M31 real capture processing")

    classifier = frozen_m30_classifier(
        args.m30_manifest, args.m30_labels, args.m30_telemetry,
        args.m30_evaluation)

    import torch
    from jsonschema import Draft7Validator
    telemetry_schema = Draft7Validator(json.loads(Path(
        "schema/hf_telemetry_record_v1.json").read_text()))
    backend = HFTelemetryBackend(
        model_ref=args.model_ref, source_kind="local_path", top_k=5)
    adapter = EXEC.FixtureRetrievalAdapter({
        "*": {"source_kind": "public_fixture",
              "context": "M31 controlled local fixture context",
              "confidence": 0.8}
    })
    cfg = M23._qwen_config()
    bands_manifest = {"bands": manifest["bands"]}

    telemetry_rows, rows, traces = [], [], []
    original_actions = []
    excluded = Counter()
    original_capped = retry_capped = 0
    for task in tasks:
        original_path = Path(args.captures) / f"{task['prompt_id']}.pt"
        retry_path = Path(args.retry_captures) / f"{task['prompt_id']}.pt"
        for path in (original_path, retry_path):
            if not path.exists():
                raise FileNotFoundError(f"missing M31 capture: {path.name}")
        original = torch.load(original_path, map_location="cpu",
                              weights_only=False)
        retry = torch.load(retry_path, map_location="cpu", weights_only=False)

        telemetry, runtime, action, result = M23.process_same_capture(
            task, original, backend, cfg=cfg, retrieval_adapter=adapter)
        del runtime
        errors = list(telemetry_schema.iter_errors(telemetry))
        if errors:
            raise ValueError(
                f"invalid telemetry for {task['prompt_id']}: {errors[0].message}")
        if action["action_type"] != "checker_needed":
            raise ValueError(
                "M31 action applicability drifted: "
                f"{task['prompt_id']} -> {action['action_type']}")
        original_actions.append(action)
        telemetry_rows.append(telemetry)
        original_capped += telemetry["decode_step_count"] == M26.DECODE_CAP_TOKENS
        retry_steps = retry.get("decode_steps") or []
        retry_capped += len(retry_steps) == M26.DECODE_CAP_TOKENS

        original_verdict = M26.label_from_result(result)
        retry_check = VZ.math_checker(
            retry.get("generated_output") or "",
            known_answer=task["known_answer"], expression=task["expression"])
        retry_verdict = (retry_check["verdict"]
                         if retry_check["verdict"] in ("pass", "fail")
                         else "undecided")
        if original_verdict == "undecided" or retry_verdict == "undecided":
            key = ("original" if original_verdict == "undecided" else "retry")
            excluded[key] += 1
            continue

        label_row = {"task_id": task["prompt_id"], "band": task["m31_band"]}
        features = M29.feature_row(bands_manifest, label_row, telemetry)
        p_fail = M28.fail_probability(classifier, features)
        rows.append({
            "task_id": task["prompt_id"],
            "band": task["m31_band"],
            "original_pass": original_verdict == "pass",
            "retry_pass": retry_verdict == "pass",
            "p_fail": p_fail,
        })
        threshold = manifest["frozen_score"]["threshold_fail_probability"]
        if (p_fail >= threshold and original_verdict == "fail"
                and retry_verdict == "pass"):
            traces.append({
                "trace_kind": "m31_verified_recovery",
                "task_id": task["prompt_id"],
                "band": task["m31_band"],
                "prompt": task["prompt"],
                "expression": task["expression"],
                "known_answer": task["known_answer"],
                "original_output": original.get("generated_output"),
                "original_verdict": original_verdict,
                "retry_output": retry.get("generated_output"),
                "retry_verdict": retry_verdict,
                "trigger_p_fail": p_fail,
                "retry_temperature": 0.7,
                "verifier": "math_checker",
            })

    M23.write_jsonl(args.telemetry_out, telemetry_rows)
    M23.write_jsonl(args.rows_out, rows)
    M23.write_jsonl(args.traces_out, traces)

    policy_report, triggered = run_policies(manifest, rows)
    original_pass = sum(row["original_pass"] for row in rows)
    retry_pass = sum(row["retry_pass"] for row in rows)
    summary = {
        "schema_version": 1,
        "run_kind": "m31_intervention_dataset",
        "task_category": manifest["task_category"],
        "n_tasks": len(tasks),
        "n_rows_evaluated": len(rows),
        "undecided_excluded_counts": dict(sorted(excluded.items())),
        "actual_action_type_distribution": dict(sorted(Counter(
            row["action_type"] for row in original_actions).items())),
        "action_applicability_constant": True,
        "original_label_distribution": {
            "pass": original_pass, "fail": len(rows) - original_pass},
        "retry_label_distribution": {
            "pass": retry_pass, "fail": len(rows) - retry_pass},
        "decode_cap_tokens": M26.DECODE_CAP_TOKENS,
        "original_decode_cap_reached_count": original_capped,
        "retry_decode_cap_reached_count": retry_capped,
        "retry_temperature": 0.7,
        "operands_disjoint_from_m29_and_m30": True,
        "no_posthoc_selection": True,
        "per_task_labels_or_predictions_persisted_publicly": False,
        "raw_text_token_tensor_or_path_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only intervention run summary",
    }
    evaluation = {
        "schema_version": 1,
        "run_kind": "m31_intervention_evaluation",
        "task_category": manifest["task_category"],
        "frozen_score_source": "M30 full_telemetry (refit-verified, no tuning)",
        "frozen_threshold_fail_probability":
            manifest["frozen_score"]["threshold_fail_probability"],
        "n_rows_evaluated": len(rows),
        "policy_semantics": "replace-on-retry; no policy consults labels",
        **policy_report,
        "classification_rule": dict(
            manifest["metrics_protocol"]["classification_rule"]),
        "recovery_traces": {
            "criterion": "verified wrong-to-right rescues under "
                         "telemetry_triggered only",
            "count": len(traces),
            "storage": "private gitignored JSONL",
            "schema_fields": ["trace_kind", "task_id", "band", "prompt",
                              "expression", "known_answer", "original_output",
                              "original_verdict", "retry_output",
                              "retry_verdict", "trigger_p_fail",
                              "retry_temperature", "verifier"],
        },
        "threshold_status": "candidate-only",
        "production_policy_set": False,
        "per_task_predictions_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate policy metrics only; no ids/text/paths",
    }
    for path, payload in ((args.summary_out, summary),
                          (args.evaluation_out, evaluation)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M31: {len(rows)} rows; trigger rate "
          f"{policy_report['trigger_rate']:.3f}; verdict="
          f"{policy_report['telemetry_policy_classification']}; "
          f"recovery traces={len(traces)} (private)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
