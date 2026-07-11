#!/usr/bin/env python3
"""M35 track A: hierarchical competence router (R calibration, sealed A-test)."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import m35_track_b as TB  # noqa: E402

BUDGET_FRACTION = 0.5          # predeclared in the M35 manifest (A-H1)
NON_INFERIORITY_MARGIN = 0.05  # predeclared in the M35 manifest (A-H2)
RANDOM_COMPARATOR_SEED = "m35:a-random-trigger"
H1_SEED_PREFIX = "m35:a-h1"
H2_SEED = "m35:a-h2"
BOOTSTRAP_ITERATIONS = 2000
# Router calibration grid, fixed before the R fit is run.
LOW_GRID = (0.05, 0.10, 0.15)
HIGH_GRID = (0.70, 0.80, 0.90)
ACTIONS = ("no_tool", "telemetry_gated_tool", "tool_on_every_task")


def route_family(prior, t_low, t_high):
    if prior <= t_low:
        return "no_tool"
    if prior >= t_high:
        return "tool_on_every_task"
    return "telemetry_gated_tool"


def family_priors(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["family"]].append(row)
    return {family: sum(1 for r in group if not r["original_pass"])
            / len(group) for family, group in grouped.items()}


def router_decisions(rows, priors, variants, t_low, t_high):
    """Per-row (invoke_tool, final_pass) under verifier-first semantics."""
    decisions = []
    for row in rows:
        action = route_family(priors.get(row["family"], 0.5), t_low, t_high)
        if action == "no_tool":
            invoke = False
        elif action == "tool_on_every_task":
            invoke = True
        else:
            invoke = TB.p_fail(variants, "global", row) >= TB.THRESHOLD
        final_pass = row["original_pass"] or (invoke and row["tool_pass"])
        decisions.append({"task_id": row["task_id"], "family": row["family"],
                          "invoke": invoke, "final_pass": final_pass,
                          "action": action})
    return decisions


def calibrate_router(r_rows, variants):
    """Grid-search thresholds on R under the predeclared budget."""
    priors = family_priors(r_rows)
    best = None
    for t_low in LOW_GRID:
        for t_high in HIGH_GRID:
            decisions = router_decisions(r_rows, priors, variants,
                                         t_low, t_high)
            fraction = sum(d["invoke"] for d in decisions) / len(decisions)
            success = sum(d["final_pass"] for d in decisions) / len(decisions)
            if fraction > BUDGET_FRACTION:
                continue
            key = (success, -fraction)
            if best is None or key > best[0]:
                best = (key, t_low, t_high, fraction, success)
    if best is None:
        raise ValueError("M35 router: no grid point meets the budget on R")
    _, t_low, t_high, fraction, success = best
    return {"t_low": t_low, "t_high": t_high,
            "r_invocation_fraction": fraction, "r_verified_success": success,
            "priors": dict(sorted(priors.items()))}


def router_config_hash(router, detector_hash):
    payload = {"router": router, "detector_config_hash": detector_hash,
               "budget_fraction": BUDGET_FRACTION,
               "non_inferiority_margin": NON_INFERIORITY_MARGIN,
               "random_seed": RANDOM_COMPARATOR_SEED,
               "grids": [LOW_GRID, HIGH_GRID]}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def _family_weighted_rate(rows, flags):
    grouped = defaultdict(list)
    for row, flag in zip(rows, flags):
        grouped[row["family"]].append(flag)
    return sum(sum(group) / len(group) for group in grouped.values()) \
        / len(grouped)


def _stratified_bootstrap_delta(rows, flags_a, flags_b, seed):
    by_family = defaultdict(list)
    for index, row in enumerate(rows):
        by_family[row["family"]].append(index)
    rng = random.Random(seed)
    deltas = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        rate_a = rate_b = 0.0
        for indices in by_family.values():
            sample = [indices[rng.randrange(len(indices))]
                      for _ in indices]
            rate_a += sum(flags_a[i] for i in sample) / len(sample)
            rate_b += sum(flags_b[i] for i in sample) / len(sample)
        deltas.append((rate_a - rate_b) / len(by_family))
    deltas.sort()
    return [deltas[int(0.025 * (BOOTSTRAP_ITERATIONS - 1))],
            deltas[int(0.975 * (BOOTSTRAP_ITERATIONS - 1))]]


def evaluate_a_test(a_rows, priors, variants, router):
    decisions = router_decisions(a_rows, priors, variants,
                                 router["t_low"], router["t_high"])
    k = sum(d["invoke"] for d in decisions)
    router_flags = [1 if d["final_pass"] else 0 for d in decisions]

    def verifier_first(invoked_ids):
        return [1 if (row["original_pass"]
                      or (row["task_id"] in invoked_ids and row["tool_pass"]))
                else 0 for row in a_rows]

    ids_sorted = sorted(row["task_id"] for row in a_rows)
    rng = random.Random(RANDOM_COMPARATOR_SEED)
    random_ids = set(rng.sample(ids_sorted, k))
    ranked = sorted(a_rows,
                    key=lambda row: (-TB.p_fail(variants, "global", row),
                                     row["task_id"]))
    threshold_ids = {row["task_id"] for row in ranked[:k]}
    arms = {
        "hierarchical_router": router_flags,
        "count_matched_random": verifier_first(random_ids),
        "global_threshold_same_budget": verifier_first(threshold_ids),
        "no_repair": [1 if row["original_pass"] else 0 for row in a_rows],
        "tool_on_every_task": verifier_first(
            {row["task_id"] for row in a_rows}),
    }
    for name, flags in arms.items():
        if any(f < o for f, o in zip(
                flags, arms["no_repair"])):
            raise ValueError(f"M35 stop: {name} replaced a passing original")

    metrics = {name: {
        "verified_success_rate_family_weighted":
            _family_weighted_rate(a_rows, flags),
        "verified_success_rate_task_level": sum(flags) / len(flags),
        "tool_invocations": (k if name == "hierarchical_router"
                             else 0 if name == "no_repair"
                             else len(a_rows) if name == "tool_on_every_task"
                             else k),
    } for name, flags in arms.items()}

    h1 = {}
    for comparator in ("count_matched_random",
                       "global_threshold_same_budget"):
        interval = _stratified_bootstrap_delta(
            a_rows, arms["hierarchical_router"], arms[comparator],
            f"{H1_SEED_PREFIX}:router-vs-{comparator}")
        h1[f"router_vs_{comparator}"] = {
            "delta_family_weighted": (
                metrics["hierarchical_router"][
                    "verified_success_rate_family_weighted"]
                - metrics[comparator][
                    "verified_success_rate_family_weighted"]),
            "delta_bootstrap_95pct": interval,
        }
    lows = [entry["delta_bootstrap_95pct"][0] for entry in h1.values()]
    highs = [entry["delta_bootstrap_95pct"][1] for entry in h1.values()]
    if all(low > 0 for low in lows):
        h1_verdict = "useful"
    elif any(high < 0 for high in highs):
        h1_verdict = "harmful"
    else:
        h1_verdict = "not_established"

    success_interval = _stratified_bootstrap_delta(
        a_rows, arms["hierarchical_router"], arms["tool_on_every_task"],
        f"{H2_SEED}:success")
    call_reduction = len(a_rows) - k
    h2_verdict = ("efficient"
                  if success_interval[0] + NON_INFERIORITY_MARGIN > 0
                  and call_reduction > 0
                  else "not_established")
    action_counts = defaultdict(int)
    for d in decisions:
        action_counts[d["action"]] += 1

    return {
        "schema_version": 1,
        "run_kind": "m35_track_a_evaluation",
        "a_test_row_count": len(a_rows),
        "router": {"t_low": router["t_low"], "t_high": router["t_high"],
                   "action_row_counts": dict(action_counts),
                   "invocation_count": k,
                   "invocation_fraction": k / len(a_rows),
                   "budget_fraction": BUDGET_FRACTION},
        "policy_metrics": metrics,
        "a_h1_fixed_budget": {"comparisons": h1, "verdict": h1_verdict},
        "a_h2_non_inferiority": {
            "success_delta_vs_tool_everywhere_bootstrap_95pct":
                success_interval,
            "non_inferiority_margin": NON_INFERIORITY_MARGIN,
            "tool_calls_saved": call_reduction,
            "verdict": h2_verdict,
        },
        "per_task_predictions_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate metrics/intervals only",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rows",
                    default="reports/shadow/private/m35_campaign_rows_local.jsonl")
    ap.add_argument("--stage", choices=("fit", "a_test"), required=True)
    ap.add_argument("--detector-freeze",
                    default="reports/telemetry/hf_m35_track_b_freeze.json")
    ap.add_argument("--freeze-out",
                    default="reports/telemetry/hf_m35_track_a_freeze.json")
    ap.add_argument("--evaluation-out",
                    default="reports/telemetry/hf_m35_track_a_evaluation.json")
    args = ap.parse_args(argv)

    rows = [json.loads(line) for line in
            Path(args.rows).read_text().splitlines() if line]
    d_rows = [row for row in rows if row["split"] == "D"]
    detector_freeze = json.loads(Path(args.detector_freeze).read_text())
    variants = TB.fit_variants(d_rows)
    if TB.config_hash(variants) != detector_freeze["config_hash"]:
        raise ValueError("M35 track A: detector refit does not match freeze")

    if args.stage == "fit":
        r_rows = [row for row in rows if row["split"] == "R"]
        router = calibrate_router(r_rows, variants)
        freeze = {
            "schema_version": 1,
            "run_kind": "m35_track_a_freeze",
            "calibration_split": "R",
            "r_row_count": len(r_rows),
            "detector_config_hash": detector_freeze["config_hash"],
            "router_config_hash": router_config_hash(
                router, detector_freeze["config_hash"]),
            "router_thresholds": {"t_low": router["t_low"],
                                  "t_high": router["t_high"]},
            "r_invocation_fraction": router["r_invocation_fraction"],
            "r_verified_success": router["r_verified_success"],
            "budget_fraction": BUDGET_FRACTION,
            "non_inferiority_margin": NON_INFERIORITY_MARGIN,
            "comparator_seed": RANDOM_COMPARATOR_SEED,
            "sealed_reads_performed": [],
            "per_task_predictions_persisted_publicly": False,
            "privacy_check_status": "aggregate metrics only",
        }
        Path(args.freeze_out).write_text(json.dumps(freeze, indent=1) + "\n")
        print(f"[jlens] M35 track A frozen: router_hash="
              f"{freeze['router_config_hash']} thresholds="
              f"({router['t_low']}, {router['t_high']}) "
              f"R fraction={router['r_invocation_fraction']:.3f} "
              f"success={router['r_verified_success']:.3f}", flush=True)
        return 0

    freeze = json.loads(Path(args.freeze_out).read_text())
    if freeze.get("sealed_reads_performed"):
        raise ValueError("M35 A-test has already been read; refusing reread")
    r_rows = [row for row in rows if row["split"] == "R"]
    router = calibrate_router(r_rows, variants)
    router_hash = router_config_hash(router,
                                     detector_freeze["config_hash"])
    if router_hash != freeze["router_config_hash"]:
        raise ValueError("M35 track A: router recalibration does not match "
                         "frozen hash")
    a_rows = [row for row in rows if row["split"] == "A_test"]
    evaluation = evaluate_a_test(a_rows, router["priors"], variants, router)
    evaluation["router_config_hash"] = router_hash
    Path(args.evaluation_out).write_text(
        json.dumps(evaluation, indent=1) + "\n")
    freeze["sealed_reads_performed"] = ["A_test"]
    Path(args.freeze_out).write_text(json.dumps(freeze, indent=1) + "\n")
    print(f"[jlens] M35 A-test read complete: "
          f"H1={evaluation['a_h1_fixed_budget']['verdict']} "
          f"H2={evaluation['a_h2_non_inferiority']['verdict']} "
          f"router={evaluation['policy_metrics']['hierarchical_router']} ",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
