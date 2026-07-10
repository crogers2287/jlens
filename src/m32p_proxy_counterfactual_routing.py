#!/usr/bin/env python3
"""M32P Qwen-proxy counterfactual expert-routing feasibility and causal screen.

All claims are scoped to the local Qwen1.5-MoE-A2.7B-Chat research proxy.
"""
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
import capture_router_logits as CAP  # noqa: E402
from hf_telemetry_backend import HFTelemetryBackend  # noqa: E402
import m22_real_telemetry as M22  # noqa: E402
import m23_within_model as M23  # noqa: E402
import m28_ablation_calibration as M28  # noqa: E402
import m29_scaled_error_power as M29  # noqa: E402
import m30_decisive_increment as M30  # noqa: E402
import m31_intervention_study as M31  # noqa: E402
import m32_structured_repair as M32  # noqa: E402
from qwen2_moe_route_override import (  # noqa: E402
    PenaltyPlan, RouteController, SwapPlan, clone_cache)
import verifiers as VZ  # noqa: E402

ARCH = {"model_type": "qwen2_moe", "layers": 24, "experts": 60, "top_k": 4}
HEURISTIC_FAMILIES = ("each_selected_to_rank5", "selected_to_rank6",
                      "diversity_swap")
DECODE_CAP = 64
SPLITS = ("discovery", "validation", "holdout")


# ---------------------------------------------------------------------------
# Model-calibrated multiplication cells (Phase 0B)
# ---------------------------------------------------------------------------

def _draw_plain(rng, digits):
    lo = 10 ** (digits - 1) if digits > 1 else 2
    hi = 10 ** digits - 1 if digits > 1 else 9
    return rng.randint(lo, hi)


def _draw_digits(rng, digits, lead_choices, rest_choices):
    value = rng.choice(lead_choices)
    for _ in range(digits - 1):
        value = value * 10 + rng.choice(rest_choices)
    return value


def draw_cell_tuple(rng, cell):
    """One (a, b) draw for a frozen sweep/benchmark cell definition."""
    structure = cell["structure"]
    da, db = cell["digits_a"], cell["digits_b"]
    if structure == "plain":
        return _draw_plain(rng, da), _draw_plain(rng, db)
    if structure == "low_carry":
        return (_draw_digits(rng, da, (1, 2, 3), (0, 1, 2, 3)),
                _draw_digits(rng, db, (1, 2, 3), (0, 1, 2, 3)))
    if structure == "carry_heavy":
        return (_draw_digits(rng, da, (6, 7, 8, 9), (6, 7, 8, 9)),
                _draw_digits(rng, db, (6, 7, 8, 9), (6, 7, 8, 9)))
    if structure == "middle_zero":
        lead, last = rng.randint(1, 9), rng.randint(0, 9)
        return lead * 100 + last, _draw_plain(rng, db)
    if structure == "near_power_of_ten":
        return rng.choice((101, 102, 998, 999)), _draw_plain(rng, 2)
    raise ValueError(f"unknown cell structure: {structure}")


def generate_cell_tuples(config_cell, seed, count, prior, max_attempts=20000):
    rng = random.Random(f"{seed}:{config_cell['cell_id']}")
    seen, tuples, attempts = set(prior), [], 0
    while len(tuples) < count and attempts < max_attempts:
        attempts += 1
        pair = draw_cell_tuple(rng, config_cell)
        if pair in seen:
            continue
        seen.add(pair)
        tuples.append(pair)
    return tuples


def flat_prior_tuples(m29_path, m30_path, m31_path, m32_path):
    prior = prior_tuples_with_m32(m29_path, m30_path, m31_path, m32_path)
    return set().union(*prior.values())


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("selection_status") != "predeclared_before_m32p_task_generation":
        raise ValueError("M32P manifest is not predeclared before generation")
    cells = manifest.get("cells") or []
    tasks = manifest.get("tasks") or []
    if not tasks or manifest.get("n_tasks") != len(tasks):
        raise ValueError("M32P manifest task count mismatch")
    if manifest["n_tasks"] not in (192, 240, 288):
        raise ValueError("M32P task count must come from the frozen power table")
    if len({task["task_id"] for task in tasks}) != len(tasks):
        raise ValueError("M32P task ids must be unique")
    counts = Counter((task["cell"], task["split"]) for task in tasks)
    for cell in cells:
        n = cell["n_tasks"]
        if n % 4 != 0:
            raise ValueError(f"cell count not a multiple of 4: {cell['cell_id']}")
        if counts[(cell["cell_id"], "discovery")] != n // 2 \
                or counts[(cell["cell_id"], "validation")] != n // 4 \
                or counts[(cell["cell_id"], "holdout")] != n // 4:
            raise ValueError(f"M32P split mismatch: {cell['cell_id']}")
    if sum(cell["n_tasks"] for cell in cells) != manifest["n_tasks"]:
        raise ValueError("M32P cell counts do not sum to n_tasks")
    if manifest["frozen_trigger"].get("threshold_fail_probability") != 0.5:
        raise ValueError("M32P frozen trigger threshold changed")
    rules = manifest["causal_screen"]
    if rules["fragile_steps_per_task"] != 2 or rules["layers_per_step"] != 4:
        raise ValueError("M32P fragile-site budgets changed")
    if rules["full_continuations_per_arm"] != 4:
        raise ValueError("M32P full-continuation budget changed")
    return manifest


def prior_tuples_with_m32(m29_path, m30_path, m31_path, m32_path):
    """Prior operand tuples from M29, M30, M31, and the abandoned M32 set."""
    prior = M32.prior_tuples_all(m29_path, m30_path, m31_path)
    m32_manifest = M32.load_manifest(m32_path)
    seed = m32_manifest["generation"]["seed"]
    for band in m32_manifest["bands"]:
        rng = random.Random(f"{seed}:{band['band_id']}")
        seen = set(prior[band["band_id"]])
        tuples = M30._draw_tuples(rng, band, band["n_tasks"], seen)
        prior[band["band_id"]] |= set(tuples)
    return prior


def sweep_tuples_for_config(config, prior_flat):
    """Deterministic calibration-sweep tuples per cell (private)."""
    seed = config["sweep_seed"]
    count = config["samples_per_cell"]
    seen = set(prior_flat)
    result = {}
    for cell in config["cells"]:
        tuples = generate_cell_tuples(cell, seed, count, seen)
        seen |= set(tuples)
        result[cell["cell_id"]] = tuples
    return result


def generate_tasks(manifest, m29_path, m30_path, m31_path, m32_path,
                   sweep_config_path):
    """Decision tasks per frozen manifest cell, disjoint from every prior
    tuple set including the calibration sweep."""
    seed = manifest["generation"]["seed"]
    template = manifest["prompt_template"]
    prior = flat_prior_tuples(m29_path, m30_path, m31_path, m32_path)
    sweep_config = json.loads(Path(sweep_config_path).read_text())
    for tuples in sweep_tuples_for_config(sweep_config, prior).values():
        prior |= set(tuples)
    slots = defaultdict(list)
    for task in manifest["tasks"]:
        slots[task["cell"]].append(task)
    tasks = []
    seen = set(prior)
    for cell in manifest["cells"]:
        cell_id = cell["cell_id"]
        tuples = generate_cell_tuples(cell, seed, cell["n_tasks"], seen)
        if len(tuples) < cell["n_tasks"]:
            raise ValueError(f"M32P cell tuple space exhausted: {cell_id}")
        seen |= set(tuples)
        for slot, (a, b) in zip(slots[cell_id], tuples):
            tasks.append({
                "prompt_id": slot["task_id"],
                "m32p_cell": cell_id,
                "m32p_split": slot["split"],
                "task_category": "math",
                "expression": f"{a}*{b}",
                "known_answer": str(a * b),
                "prompt": template.format(a=a, op="*", b=b),
            })
    expected = manifest["n_tasks"]
    if len(tasks) != expected or len({t["prompt_id"] for t in tasks}) != expected:
        raise ValueError("M32P generation did not produce the frozen task count")
    order = {task["task_id"]: i for i, task in enumerate(manifest["tasks"])}
    tasks.sort(key=lambda task: order[task["prompt_id"]])
    return tasks


def prepare_private_tasks(args):
    manifest = load_manifest(args.manifest)
    tasks = generate_tasks(manifest, args.m29_manifest, args.m30_manifest,
                           args.m31_manifest, args.m32_manifest,
                           args.sweep_config)
    out = Path(args.tasks_out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(task) + "\n" for task in tasks))
    return manifest, tasks


def verdict_for(output, task):
    result = VZ.math_checker(output or "", known_answer=task["known_answer"],
                             expression=task["expression"])
    return result["verdict"] if result["verdict"] in ("pass", "fail") \
        else "undecided"


# ---------------------------------------------------------------------------
# Fragile-site selection (original telemetry only; no labels, no answers)
# ---------------------------------------------------------------------------

def fragile_steps(capture, top_n=2):
    """Top generated steps by selection entropy; ties break to earlier step."""
    steps = capture.get("decode_steps") or []
    scored = [(-(step.get("entropy_final_logits") or 0.0), index)
              for index, step in enumerate(steps)]
    scored.sort()
    return [index for _, index in scored[:top_n]]


def _row_entropy(row):
    import math as _math
    total = sum(_math.exp(v) for v in row)
    probs = [max(_math.exp(v) / total, 1e-12) for v in row]
    return -sum(p * _math.log(p) for p in probs)


def _layer_rows(capture, step_index):
    if step_index == 0:
        return [layer.float()[-1].tolist()
                for layer in capture["router_logits"]]
    step = capture["decode_steps"][step_index - 1]
    rows = []
    for layer in step["router_logits"]:
        layer = layer.float()
        rows.append(layer.reshape(-1, layer.shape[-1])[-1].tolist())
    return rows


def _top4(row):
    import math as _math
    ranked = sorted(range(len(row)), key=lambda i: -row[i])
    total = sum(_math.exp(v) for v in row)
    probs = [_math.exp(v) / total for v in row]
    return ranked[:ARCH["top_k"]], ranked, probs


def implicated_layers(capture, step_index, top_n=4):
    """Frozen combined layer score at the forward that SELECTED token
    step_index: router entropy minus the top4/rank5 probability margin plus
    the trajectory deviation of the current top-4 from earlier steps'
    selections at the same layer. Original telemetry only."""
    rows = _layer_rows(capture, step_index)
    earlier = [_layer_rows(capture, earlier_step)
               for earlier_step in range(step_index)]
    scored = []
    for index, row in enumerate(rows):
        selected, ranked, probs = _top4(row)
        margin45 = probs[ranked[3]] - probs[ranked[4]]
        history = set()
        for step_rows in earlier:
            history.update(_top4(step_rows[index])[0])
        deviation = (sum(1 for expert in selected if expert not in history)
                     / ARCH["top_k"]) if history else 0.0
        score = _row_entropy(row) - margin45 + deviation
        scored.append((-score, index))
    scored.sort()
    return [index for _, index in scored[:top_n]]


def coactivation_table(captures):
    """Discovery-only per-layer expert co-selection counts (private)."""
    table = defaultdict(Counter)
    for capture in captures:
        for step in capture.get("decode_steps") or []:
            for layer_index, layer in enumerate(step["router_logits"]):
                layer = layer.float()
                row = layer.reshape(-1, layer.shape[-1])[-1]
                import torch
                selected = torch.topk(row, ARCH["top_k"]).indices.tolist()
                for i, a in enumerate(selected):
                    for b in selected[i + 1:]:
                        table[layer_index][(min(a, b), max(a, b))] += 1
    return table


def branch_plans(row_logits, layer_index, coact, task_id, step_index,
                 rank6_count=1):
    """Frozen heuristic + matched-random swap plans for one fragile site."""
    import torch
    row = row_logits
    ranked = torch.argsort(row, descending=True).tolist()
    selected = ranked[:ARCH["top_k"]]
    rank5, rank6 = ranked[ARCH["top_k"]], ranked[ARCH["top_k"] + 1]
    weights = {expert: float(row[expert]) for expert in selected}
    lowest = min(selected, key=lambda expert: (weights[expert], expert))
    plans = []
    for expert in selected:
        family = ("lowest_weight_to_rank5" if expert == lowest
                  else "each_selected_to_rank5")
        plans.append((family, SwapPlan(layer_index, expert, rank5)))
    plans.append(("selected_to_rank6", SwapPlan(layer_index, lowest, rank6)))
    coacts = coact.get(layer_index, Counter())

    def redundancy(expert):
        return sum(coacts.get((min(expert, other), max(expert, other)), 0)
                   for other in selected if other != expert)

    redundant = max(selected, key=lambda expert: (redundancy(expert), -expert))
    plans.append(("diversity_swap", SwapPlan(layer_index, redundant, rank5)))

    unselected = [expert for expert in ranked[ARCH["top_k"]:]]
    random_plans = []
    for i in range(len(plans)):
        rng = random.Random(f"m32p:random:{task_id}:{step_index}:{layer_index}:{i}")
        swap_out = rng.choice(selected)
        swap_in = rng.choice(unselected)
        random_plans.append(("matched_random_swap",
                             SwapPlan(layer_index, swap_out, swap_in)))
    return plans, random_plans


# ---------------------------------------------------------------------------
# Aggregate evaluation (CPU) over private branch/row records
# ---------------------------------------------------------------------------

def _delta_bootstrap(success_a, success_b, seed, iterations=2000):
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


POLICY_CANDIDATES = ("p1_top_screen", "p2_each_selected_only",
                     "p3_margin_only")


def policy_choice(policy, branches):
    """Pick one full-continued heuristic branch without any label access."""
    full = [b for b in branches
            if b["full_run"] and b["arm"] == "heuristic"]
    if not full:
        return None
    if policy == "p2_each_selected_only":
        restricted = [b for b in full if b["family"] in
                      ("each_selected_to_rank5", "lowest_weight_to_rank5")]
        full = restricted or full
    if policy == "p3_margin_only":
        key = lambda b: (-b["screen_margin_gain"], b["step"], b["layer"])
    else:
        key = lambda b: (-b["screen_changed_token"], -b["screen_margin_gain"],
                         b["step"], b["layer"])
    return sorted(full, key=key)[0]


def random_policy_choice(branches):
    full = [b for b in branches if b["full_run"] and b["arm"] == "random"]
    if not full:
        return None
    key = lambda b: (-b["screen_changed_token"], -b["screen_margin_gain"],
                     b["step"], b["layer"])
    return sorted(full, key=key)[0]


def evaluate(manifest, rows, branches_by_task):
    threshold = manifest["frozen_trigger"]["threshold_fail_probability"]
    by_split = defaultdict(list)
    for row in rows:
        by_split[row["split"]].append(row)

    def oracle(branches, arm):
        full = [b for b in branches if b["full_run"] and b["arm"] == arm]
        return any(b["verdict"] == "pass" for b in full)

    # --- policy freeze on discovery + validation --------------------------
    def policy_success(policy, split_rows):
        outcomes = []
        for row in split_rows:
            if row["triggered"]:
                chosen = policy_choice(policy,
                                       branches_by_task.get(row["task_id"], []))
                outcomes.append(1 if chosen is not None
                                and chosen["verdict"] == "pass"
                                else (1 if chosen is None and row["original_pass"]
                                      else 0))
            else:
                outcomes.append(1 if row["original_pass"] else 0)
        return outcomes

    validation_scores = {
        policy: sum(policy_success(policy, by_split["validation"]))
        for policy in POLICY_CANDIDATES}
    frozen_policy = sorted(
        POLICY_CANDIDATES,
        key=lambda p: (-validation_scores[p],
                       POLICY_CANDIDATES.index(p)))[0]

    # --- sealed holdout ----------------------------------------------------
    holdout = by_split["holdout"]
    h1_rows = [row for row in holdout
               if row["triggered"] and not row["original_pass"]]
    h1_heuristic = [1 if oracle(branches_by_task.get(r["task_id"], []),
                                "heuristic") else 0 for r in h1_rows]
    h1_random = [1 if oracle(branches_by_task.get(r["task_id"], []),
                             "random") else 0 for r in h1_rows]
    h1_ci = _delta_bootstrap(h1_heuristic, h1_random, "m32p:h1") \
        if h1_rows else [0.0, 0.0]
    if h1_rows and h1_ci[0] > 0:
        h1_verdict = "route_recoverability_established"
    elif h1_rows and h1_ci[1] < 0:
        h1_verdict = "route_recoverability_negative"
    else:
        h1_verdict = "route_recoverability_not_established"

    def holdout_success(chooser):
        outcomes = []
        for row in holdout:
            if row["triggered"]:
                chosen = chooser(row)
                outcomes.append(
                    1 if chosen is not None and chosen["verdict"] == "pass"
                    else (1 if chosen is None and row["original_pass"] else 0))
            else:
                outcomes.append(1 if row["original_pass"] else 0)
        return outcomes

    policy_outcomes = holdout_success(
        lambda row: policy_choice(frozen_policy,
                                  branches_by_task.get(row["task_id"], [])))
    normal_outcomes = [1 if row["original_pass"] else 0 for row in holdout]
    random_outcomes = holdout_success(
        lambda row: random_policy_choice(
            branches_by_task.get(row["task_id"], [])))
    h2_vs_normal = _delta_bootstrap(policy_outcomes, normal_outcomes,
                                    "m32p:h2:policy-vs-normal")
    h2_vs_random = _delta_bootstrap(policy_outcomes, random_outcomes,
                                    "m32p:h2:policy-vs-random")
    if h2_vs_normal[0] > 0 and h2_vs_random[0] > 0:
        h2_verdict = "deployable_rerouting_established"
    elif h2_vs_normal[1] < 0:
        h2_verdict = "deployable_rerouting_harmful"
    else:
        h2_verdict = "deployable_rerouting_not_established"

    # --- family-level aggregates (all splits, descriptive) -----------------
    family_stats = defaultdict(lambda: Counter())
    for row in rows:
        for branch in branches_by_task.get(row["task_id"], []):
            if not branch["full_run"]:
                continue
            stats = family_stats[branch["family"]]
            stats["full_continuations"] += 1
            if not row["original_pass"] and branch["verdict"] == "pass":
                stats["rescues"] += 1
            if row["original_pass"] and branch["verdict"] == "fail":
                stats["regressions"] += 1

    triggered = [row for row in rows if row["triggered"]]
    fails = [row for row in rows if not row["original_pass"]]
    trigger_hits = sum(1 for row in triggered if not row["original_pass"])
    screens = sum(1 for branches in branches_by_task.values()
                  for b in branches)
    fulls = sum(1 for branches in branches_by_task.values()
                for b in branches if b["full_run"])

    oracle_all = [row for row in rows
                  if row["triggered"] and not row["original_pass"]]
    oracle_recovered = sum(
        1 for row in oracle_all
        if oracle(branches_by_task.get(row["task_id"], []), "heuristic")
        or oracle(branches_by_task.get(row["task_id"], []), "random"))

    return {
        "schema_version": 1,
        "run_kind": "m32p_proxy_counterfactual_routing_evaluation",
        "model_scope": "qwen2_moe research proxy only; not Agents-A1",
        "task_category": manifest["task_category"],
        "n_rows_evaluated": len(rows),
        "split_sizes": {name: len(by_split[name])
                        for name in ("discovery", "validation", "holdout")},
        "original_label_distribution": {
            "pass": len(rows) - len(fails), "fail": len(fails)},
        "frozen_trigger": {
            "threshold_fail_probability": threshold,
            "trigger_count": len(triggered),
            "trigger_rate": len(triggered) / len(rows) if rows else None,
            "trigger_precision": (trigger_hits / len(triggered)
                                  if triggered else None),
            "trigger_recall": (trigger_hits / len(fails) if fails else None),
        },
        "causal_screen_volume": {
            "one_step_screens": screens,
            "full_continuations": fulls,
        },
        "route_family_stats": {family: dict(stats) for family, stats
                               in sorted(family_stats.items())},
        "oracle_recoverable_fraction_triggered_failures": (
            oracle_recovered / len(oracle_all) if oracle_all else None),
        "h1_route_recoverability": {
            "population": "sealed holdout triggered true failures",
            "n": len(h1_rows),
            "heuristic_oracle_rescue_rate": (
                statistics.fmean(h1_heuristic) if h1_rows else None),
            "random_oracle_rescue_rate": (
                statistics.fmean(h1_random) if h1_rows else None),
            "delta_bootstrap_95pct": h1_ci,
            "verdict": h1_verdict,
        },
        "h2_deployable_rerouting": {
            "frozen_policy": frozen_policy,
            "validation_scores": validation_scores,
            "holdout_success": {
                "policy": statistics.fmean(policy_outcomes),
                "normal": statistics.fmean(normal_outcomes),
                "matched_random": statistics.fmean(random_outcomes),
            },
            "delta_vs_normal_bootstrap_95pct": h2_vs_normal,
            "delta_vs_random_bootstrap_95pct": h2_vs_random,
            "verdict": h2_verdict,
        },
        "h3_soft_penalty": {
            "status": "reported separately in the evaluation payload",
        },
        "per_task_routes_or_expert_tables_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate metrics/intervals only; no ids/routes",
    }


# ---------------------------------------------------------------------------
# H3 soft-penalty fitting (discovery -> validation -> frozen for holdout)
# ---------------------------------------------------------------------------

def _pair_effects(rows, branches_by_task, split):
    effects = defaultdict(lambda: Counter())
    by_id = {row["task_id"]: row for row in rows}
    for task_id, branches in branches_by_task.items():
        row = by_id.get(task_id)
        if row is None or row["split"] != split:
            continue
        for branch in branches:
            if not branch["full_run"] or branch["arm"] != "heuristic":
                continue
            key = (branch["layer"], branch["swap_out"])
            effects[key]["support"] += 1
            if not row["original_pass"] and branch["verdict"] == "pass":
                effects[key]["rescues"] += 1
            if row["original_pass"] and branch["verdict"] == "fail":
                effects[key]["regressions"] += 1
    return effects


def fit_soft_penalties(manifest, rows, branches_by_task):
    rules = manifest["soft_penalty_rule"]
    discovery = _pair_effects(rows, branches_by_task, "discovery")
    validation = _pair_effects(rows, branches_by_task, "validation")
    candidates = []
    for key, stats in sorted(discovery.items()):
        if stats["support"] < rules["discovery_min_support"]:
            continue
        if stats["rescues"] - stats["regressions"] < rules[
                "discovery_min_net_rescues"]:
            continue
        val = validation.get(key, Counter())
        if val["support"] < rules["validation_min_support"]:
            continue
        if val["rescues"] <= val["regressions"]:
            continue
        candidates.append({"layer": key[0], "expert": key[1],
                           "delta": rules["penalty_delta"]})
    return candidates


def _binomial_p_one_sided(successes, trials):
    import math as _math
    if trials == 0:
        return 1.0
    return sum(_math.comb(trials, k) for k in range(successes, trials + 1)) \
        / (2 ** trials)


def h3_verdicts(manifest, penalties, rows, branches_by_task):
    rules = manifest["soft_penalty_rule"]
    if not penalties:
        return {"candidates_frozen": 0, "verdict": "no_candidate_survived",
                "pairs": []}
    by_id = {row["task_id"]: row for row in rows}
    pairs = []
    for penalty in penalties:
        rescues = regressions = support = 0
        for task_id, branches in branches_by_task.items():
            row = by_id.get(task_id)
            if row is None or row["split"] != "holdout":
                continue
            for branch in branches:
                if branch["family"] != "soft_penalty_route":
                    continue
                if branch["layer"] != penalty["layer"]:
                    continue
                support += 1
                if not row["original_pass"] and branch["verdict"] == "pass":
                    rescues += 1
                if row["original_pass"] and branch["verdict"] == "fail":
                    regressions += 1
        decisive = rescues + regressions
        p_value = _binomial_p_one_sided(rescues, decisive)
        corrected_alpha = rules["alpha"] / max(len(penalties), 1)
        pairs.append({
            "layer": penalty["layer"],
            "holdout_support": support,
            "rescues": rescues,
            "regressions": regressions,
            "one_sided_binomial_p": p_value,
            "bonferroni_alpha": corrected_alpha,
            "generalizes": bool(decisive and p_value < corrected_alpha
                                and regressions <= rescues),
        })
    verdict = ("candidate_soft_penalty" if any(p["generalizes"] for p in pairs)
               else "exploratory_only")
    return {"candidates_frozen": len(penalties), "verdict": verdict,
            "pairs": pairs}


# ---------------------------------------------------------------------------
# GPU driver: smoke, originals, causal screen
# ---------------------------------------------------------------------------

def _load_model(model_ref):
    args = argparse.Namespace(model=model_ref, dtype="bf16",
                              device_map="auto", max_gpu_mem_gib=20.0,
                              trust_remote_code=False)
    tok, model, cfg = CAP.load_model(args)
    if (cfg.model_type != ARCH["model_type"]
            or cfg.num_hidden_layers != ARCH["layers"]
            or cfg.num_experts != ARCH["experts"]
            or cfg.num_experts_per_tok != ARCH["top_k"]):
        raise ValueError("M32P architecture verification failed")
    controller = RouteController(model, ARCH["experts"], ARCH["top_k"])
    return tok, model, cfg, controller


def _templated_ids(tok, model, prompt):
    text = tok.apply_chat_template(
        [{"role": "user", "content": prompt}], tokenize=False,
        add_generation_prompt=True)
    ids = tok(text, return_tensors="pt", truncation=True, max_length=4096)
    return {k: v.to(model.device) for k, v in ids.items()}


def _greedy_continue(model, next_logits, past, remaining, eos):
    import torch
    tokens = []
    for _ in range(remaining):
        token = int(next_logits.argmax(-1).item())
        tokens.append(token)
        if eos is not None and token == eos:
            break
        with torch.inference_mode():
            out = model(input_ids=torch.tensor([[token]], device=model.device),
                        past_key_values=past, use_cache=True)
        past = out.past_key_values
        next_logits = out.logits[:, -1, :]
    return tokens


def _margin(next_logits):
    import torch
    probs = torch.softmax(next_logits.float().reshape(-1), dim=-1)
    top = torch.topk(probs, 2).values
    return float(top[0] - top[1])


def run_smoke(model_ref, report_path, preloaded=None):
    """Phase-0 real smoke gate; returns the feasibility payload."""
    import torch
    tok, model, cfg, controller = preloaded or _load_model(model_ref)
    smoke_prompts = ["What is 6 + 7? Reply with the final number only.",
                     "What is 12 * 3? Reply with the final number only."]
    parity = []
    for prompt in smoke_prompts:
        runs = []
        for _ in range(2):
            _ids, _router, _hidden, steps = CAP.capture_one(
                tok, model, prompt, 4096, max_new_tokens=16,
                router_only=True, chat_template=True)
            runs.append([s["generated_token_id"] for s in steps])
        parity.append(runs[0] == runs[1])
    ids = _templated_ids(tok, model, smoke_prompts[0])
    with torch.inference_mode():
        out = model(**ids, use_cache=True, output_router_logits=True)
    baseline_next = int(out.logits[:, -1, :].argmax(-1))
    layer = 12
    row = out.router_logits[layer].float()[-1]
    selected = torch.topk(row, ARCH["top_k"]).indices.tolist()
    ranked = torch.argsort(row, descending=True).tolist()
    plan = SwapPlan(layer, selected[0], ranked[ARCH["top_k"]])
    spy = {}

    def spy_hook(_m, _i, output):
        spy["scores"] = output[1].detach().float().clone()[-1]

    handle = model.model.layers[layer].mlp.gate.register_forward_hook(spy_hook)
    with torch.inference_mode():
        base_out = model(**ids, use_cache=False)
    base_scores = spy["scores"].clone()
    with controller.active(plan):
        with torch.inference_mode():
            swap_out = model(**ids, use_cache=False)
    swap_scores = spy["scores"].clone()
    handle.remove()
    routing_changed = not torch.equal(base_scores, swap_scores)
    output_can_differ = (baseline_next != int(swap_out.logits[:, -1, :]
                                              .argmax(-1))) or routing_changed
    peak = sum(torch.cuda.max_memory_allocated(i)
               for i in range(torch.cuda.device_count())) / 1024 ** 3
    payload = {
        "schema_version": 1,
        "run_kind": "m32p_phase0_feasibility",
        "model_scope": "qwen2_moe research proxy only; not Agents-A1",
        "architecture_verified": {
            "model_type": cfg.model_type,
            "layers": cfg.num_hidden_layers,
            "experts": cfg.num_experts,
            "top_k": cfg.num_experts_per_tok,
            "norm_topk_prob": bool(cfg.norm_topk_prob),
        },
        "disabled_override_greedy_parity": all(parity),
        "forced_swap_routing_changed": routing_changed,
        "forced_swap_output_can_differ": output_can_differ,
        "controller_applications": controller.applications,
        "peak_gpu_memory_gib": round(peak, 2),
        "memory_gate_44gib": peak <= 44.0,
        "hidden_capture": "disabled",
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate smoke facts only; no paths/prompts",
    }
    out_path = Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=1) + "\n")
    if not (all(parity) and routing_changed):
        raise ValueError("M32P Phase-0 smoke gate failed; stopping")
    return payload


def _branch_records_for_task(tok, model, controller, task, capture, coact,
                             penalties=None):
    """Screen + full-continue counterfactual branches for one triggered task."""
    import torch
    manifest_cap = DECODE_CAP
    eos = getattr(tok, "eos_token_id", None)
    original_tokens = [s["generated_token_id"] for s in capture["decode_steps"]]
    ids = _templated_ids(tok, model, task["prompt"])
    records = []
    ks = fragile_steps(capture)
    for k in ks:
        layers = implicated_layers(capture, k)
        if k == 0:
            snapshot = None
        else:
            with torch.inference_mode():
                out = model(**ids, use_cache=True)
            past = out.past_key_values
            for token in original_tokens[:k - 1]:
                with torch.inference_mode():
                    out = model(input_ids=torch.tensor([[token]],
                                                       device=model.device),
                                past_key_values=past, use_cache=True)
                past = out.past_key_values
            snapshot = past
        original_margin = capture["decode_steps"][k]["top_k_margin"]

        def _forward_with(plan):
            if k == 0:
                context = controller.active(plan)
                with context:
                    with torch.inference_mode():
                        out = model(**ids, use_cache=True)
                return out
            branch_past = clone_cache(snapshot)
            with controller.active(plan):
                with torch.inference_mode():
                    out = model(input_ids=torch.tensor(
                        [[original_tokens[k - 1]]], device=model.device),
                        past_key_values=branch_past, use_cache=True)
            return out

        for layer in layers:
            if k == 0:
                row = capture["router_logits"][layer].float()[-1]
            else:
                layer_tensor = capture["decode_steps"][k - 1][
                    "router_logits"][layer].float()
                row = layer_tensor.reshape(-1, layer_tensor.shape[-1])[-1]
            heuristic, randoms = branch_plans(
                row, layer, coact, task["prompt_id"], k)
            plan_sets = ([("heuristic", family, plan)
                          for family, plan in heuristic]
                         + [("random", family, plan)
                            for family, plan in randoms])
            if penalties:
                relevant = tuple((p["expert"], p["delta"]) for p in penalties
                                 if p["layer"] == layer)
                if relevant:
                    plan_sets.append(("heuristic", "soft_penalty_route",
                                      PenaltyPlan(layer, relevant)))
            for arm, family, plan in plan_sets:
                try:
                    out = _forward_with(plan)
                except ValueError:
                    continue  # invalid swap for this row (e.g. random dup)
                next_logits = out.logits[:, -1, :]
                new_token = int(next_logits.argmax(-1).item())
                records.append({
                    "task_id": task["prompt_id"],
                    "step": k, "layer": layer,
                    "arm": arm, "family": family,
                    "swap_out": getattr(plan, "swap_out", None),
                    "swap_in": getattr(plan, "swap_in", None),
                    "screen_changed_token": int(
                        new_token != original_tokens[k]),
                    "screen_margin_gain": _margin(next_logits)
                    - float(original_margin),
                    "full_run": False, "verdict": None, "output": None,
                    "tokens_generated": 0,
                    "_plan": plan, "_next": next_logits, "_out": out,
                })
    # Select per-arm top-N for full continuation.
    budget = 4
    for arm in ("heuristic", "random"):
        pool = [r for r in records if r["arm"] == arm
                and r["family"] != "soft_penalty_route"]
        pool.sort(key=lambda r: (-r["screen_changed_token"],
                                 -r["screen_margin_gain"],
                                 r["step"], r["layer"]))
        chosen = pool[:budget]
        for record in chosen:
            record["full_run"] = True
    for record in records:
        if record["family"] == "soft_penalty_route":
            record["full_run"] = True
    for record in records:
        if not record["full_run"]:
            for key in ("_plan", "_next", "_out"):
                record.pop(key, None)
            continue
        k = record["step"]
        out = record.pop("_out")
        next_logits = record.pop("_next")
        record.pop("_plan")
        continuation = _greedy_continue(
            model, next_logits, out.past_key_values,
            manifest_cap - k, eos)
        full_tokens = original_tokens[:k] + continuation
        output = tok.decode(full_tokens, skip_special_tokens=True)
        record["output"] = output
        record["verdict"] = verdict_for(output, task)
        record["tokens_generated"] = len(continuation)
    return records




# ---------------------------------------------------------------------------
# Phase 0B: calibration sweep, frontier selection, manifest construction
# ---------------------------------------------------------------------------

def run_sweep(args):
    """Smoke gate, then the private capability-frontier sweep (one load)."""
    import torch
    config = json.loads(Path(args.sweep_config).read_text())
    if config.get("selection_status") != "predeclared_before_frontier_sweep":
        raise ValueError("sweep config is not predeclared")
    prior = flat_prior_tuples(args.m29_manifest, args.m30_manifest,
                              args.m31_manifest, args.m32_manifest)
    tuples_by_cell = sweep_tuples_for_config(config, prior)

    tok, model, cfg, controller = _load_model(args.model_ref)
    payload = run_smoke(args.model_ref, args.feasibility_out,
                        preloaded=(tok, model, cfg, controller))
    print(f"[jlens] M32P smoke passed; peak={payload['peak_gpu_memory_gib']} GiB",
          flush=True)
    template = config["prompt_template"]
    results = []
    for cell in config["cells"]:
        cell_id = cell["cell_id"]
        tuples = tuples_by_cell[cell_id]
        outcomes = []
        for a, b in tuples:
            task = {"expression": f"{a}*{b}", "known_answer": str(a * b)}
            _ids, _router, _hidden, steps = CAP.capture_one(
                tok, model, template.format(a=a, op="*", b=b), 4096,
                max_new_tokens=DECODE_CAP, router_only=True,
                chat_template=True)
            output = tok.decode([s["generated_token_id"] for s in steps],
                                skip_special_tokens=True)
            outcomes.append(verdict_for(output, task))
        counts = Counter(outcomes)
        results.append({
            "cell_id": cell_id,
            "n": len(tuples),
            "feasible": len(tuples) == config["samples_per_cell"],
            "pass": counts.get("pass", 0),
            "fail": counts.get("fail", 0),
            "undecided": counts.get("undecided", 0),
            "pass_rate": (counts.get("pass", 0) / len(tuples)
                          if tuples else None),
        })
        print(f"[jlens] sweep {cell_id}: pass_rate="
              f"{results[-1]['pass_rate']:.3f} (n={len(tuples)})", flush=True)
    out = Path(args.sweep_results_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r) + "\n" for r in results))
    frontier = select_frontier(config, results)
    public = {
        "schema_version": 1,
        "run_kind": "m32p_proxy_benchmark_frontier",
        "model_scope": "qwen2_moe research proxy only; not Agents-A1",
        "sweep_samples_per_cell": config["samples_per_cell"],
        "cell_pass_rates": {r["cell_id"]: round(r["pass_rate"], 4)
                            for r in results},
        "cell_classes": frontier["cell_classes"],
        "frontier_found": frontier["frontier_found"],
        "chosen_task_count": frontier.get("task_count"),
        "chosen_composition": frontier.get("composition"),
        "expected_original_failures": frontier.get("expected_failures"),
        "selection_inputs": "original greedy pass rates and frozen structural "
                            "diversity rules only",
        "calibration_rows_are_decision_data": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate cell counts/pass rates only",
    }
    out = Path(args.frontier_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(public, indent=1) + "\n")
    if not frontier["frontier_found"]:
        print("[jlens] M32P STOP: benchmark_frontier_not_found")
        return 1
    print(f"[jlens] M32P frontier: N={frontier['task_count']} "
          f"composition={frontier['composition']}")
    return 0


def select_frontier(config, results):
    """Deterministic benchmark composition from sweep pass rates only."""
    rules = config["frontier_selection_rules"]
    lo, hi = rules["cell_classes"]["boundary"]
    easy_min = rules["cell_classes"]["easy_min"]
    hard_max = rules["cell_classes"]["hard_max"]
    classes = {}
    for row in results:
        if not row["feasible"] or row["pass_rate"] is None:
            classes[row["cell_id"]] = "infeasible"
        elif lo <= row["pass_rate"] <= hi:
            classes[row["cell_id"]] = "boundary"
        elif row["pass_rate"] > easy_min:
            classes[row["cell_id"]] = "easy"
        elif row["pass_rate"] < hard_max:
            classes[row["cell_id"]] = "hard"
        else:
            classes[row["cell_id"]] = "unused_gap"
    comp = rules["composition"]
    boundary = [r for r in results if classes[r["cell_id"]] == "boundary"]
    if len(boundary) < comp["min_boundary_cells"]:
        return {"frontier_found": False, "cell_classes": classes}
    easy = sorted((r for r in results if classes[r["cell_id"]] == "easy"),
                  key=lambda r: -r["pass_rate"])[:comp["max_easy_cells"]]
    hard = sorted((r for r in results if classes[r["cell_id"]] == "hard"),
                  key=lambda r: r["pass_rate"])[:comp["max_hard_cells"]]

    def allocate(n_total):
        def per_cell(fraction, cells):
            if not cells:
                return {}
            share = fraction * n_total / len(cells)
            base = int(share // 4) * 4
            counts = {r["cell_id"]: base for r in cells}
            remainder = int(fraction * n_total) - base * len(cells)
            for r in cells:
                if remainder >= 4:
                    counts[r["cell_id"]] += 4
                    remainder -= 4
            return counts
        counts = {}
        counts.update(per_cell(comp["boundary_fraction"], boundary))
        counts.update(per_cell(comp["easy_fraction"], easy))
        counts.update(per_cell(comp["hard_fraction"], hard))
        # Top up to n_total in cell order with multiples of 4 (boundary first).
        ordered = [r["cell_id"] for r in boundary + easy + hard]
        index = 0
        while sum(counts.values()) < n_total and ordered:
            cell_id = ordered[index % len(ordered)]
            if counts[cell_id] + 4 <= comp["max_single_cell_fraction"] * n_total:
                counts[cell_id] += 4
            index += 1
            if index > 400:
                break
        return counts

    pass_rate = {r["cell_id"]: r["pass_rate"] for r in results}
    chosen = None
    for n_total in rules["task_count_power_table"]["options"]:
        counts = allocate(n_total)
        if sum(counts.values()) != n_total:
            continue
        if any(count / n_total > comp["max_single_cell_fraction"] + 1e-9
               for count in counts.values()):
            continue
        expected = sum(count * (1 - pass_rate[cell_id])
                       for cell_id, count in counts.items())
        chosen = {"task_count": n_total, "counts": counts,
                  "expected_failures": round(expected, 1)}
        if expected >= rules["task_count_power_table"][
                "expected_failure_minimum"]:
            break
    if chosen is None:
        return {"frontier_found": False, "cell_classes": classes}
    return {
        "frontier_found": True,
        "cell_classes": classes,
        "task_count": chosen["task_count"],
        "composition": chosen["counts"],
        "expected_failures": chosen["expected_failures"],
    }


def build_manifest(args):
    """Construct the preregistration manifest from the frontier report."""
    config = json.loads(Path(args.sweep_config).read_text())
    frontier = json.loads(Path(args.frontier_out).read_text())
    if not frontier.get("frontier_found"):
        raise ValueError("cannot build manifest: frontier not found")
    cells_by_id = {cell["cell_id"]: cell for cell in config["cells"]}
    cells, tasks = [], []
    for cell_id, count in sorted(frontier["chosen_composition"].items()):
        cell = dict(cells_by_id[cell_id])
        cell["n_tasks"] = count
        cell["sweep_pass_rate"] = frontier["cell_pass_rates"][cell_id]
        cell["cell_class"] = frontier["cell_classes"][cell_id]
        cells.append(cell)
        for i in range(count):
            split = ("discovery" if i < count // 2 else
                     "validation" if i < count // 2 + count // 4 else
                     "holdout")
            tasks.append({"task_id": f"m32p_{cell_id[2:]}_{i:03d}",
                          "cell": cell_id, "split": split})
    manifest = {
        "milestone": "M32P",
        "schema_version": 1,
        "selection_status": "predeclared_before_m32p_task_generation",
        "protocol_source": "docs/M32P_QWEN_PROXY_COUNTERFACTUAL_ROUTING_AUTOLOOP.md",
        "model_scope": "qwen2_moe research proxy only; not Agents-A1",
        "benchmark_source": ("model-calibrated capability frontier; cells and "
                             "counts chosen from sweep pass rates and frozen "
                             "structural rules only"),
        "task_category": "integer_multiplication_model_calibrated",
        "prompt_template": config["prompt_template"],
        "generation": {
            "seed": "m32p-decision-v1",
            "algorithm": ("per manifest cell, draw unique tuples with the "
                          "frozen cell generators, rejecting every "
                          "M29/M30/M31/abandoned-M32 tuple and every "
                          "calibration-sweep tuple"),
            "no_posthoc_selection": True,
            "all_generated_tasks_retained": True,
        },
        "cells": cells,
        "n_tasks": frontier["chosen_task_count"],
        "split_rule": "per cell by index: first half discovery, next quarter "
                      "validation, final quarter sealed holdout",
        "tasks": tasks,
        "frozen_trigger": {
            "source": "M30 full_telemetry nearest centroid",
            "reinstantiation": ("deterministic refit from private M30 train "
                                "records; must reproduce the published M30 "
                                "holdout confusion matrix exactly"),
            "threshold_fail_probability": 0.5,
            "scored_input": "original greedy decode telemetry only",
        },
        "decode_protocol": {"decode": "greedy", "decode_cap_tokens": DECODE_CAP,
                            "chat_template": True, "router_only_capture": True,
                            "dtype": "bf16"},
        "causal_screen": {
            "fragile_steps_per_task": 2,
            "fragile_step_rule": ("top generated steps by selection entropy "
                                  "of the step's predictive distribution; "
                                  "ties break to the earlier step"),
            "layers_per_step": 4,
            "layer_rule": ("frozen combined score: router entropy minus the "
                           "top4/rank5 probability margin plus the trajectory "
                           "deviation of the current top-4 from earlier "
                           "steps' selections at the same layer"),
            "route_families": ["each_selected_to_rank5 (4 swaps, includes "
                               "lowest_weight_to_rank5)",
                               "selected_to_rank6 (1 swap)",
                               "diversity_swap (1 swap, discovery-only "
                               "co-selection table)",
                               "matched_random_swap (6 swaps, fixed seeds)",
                               "soft_penalty_route (validation-frozen)",
                               "oracle_best_tested (ceiling only)"],
            "one_step_screen": ("rank branches by (next-token changed, "
                                "probability-margin gain), identical for "
                                "heuristic and random arms"),
            "full_continuations_per_arm": 4,
            "random_seed_rule": "m32p:random:<task>:<step>:<layer>:<i>",
        },
        "policy_candidates": list(POLICY_CANDIDATES),
        "policy_freeze_rule": ("choose among frozen candidates by validation "
                               "success only; freeze before holdout"),
        "soft_penalty_rule": {
            "discovery_min_support": 5,
            "discovery_min_net_rescues": 2,
            "validation_min_support": 2,
            "penalty_delta": 2.0,
            "alpha": 0.05,
            "correction": "Bonferroni over frozen candidates",
        },
        "hypotheses": {
            "h1": "oracle heuristic-family rescue rate vs matched-random on "
                  "sealed holdout; paired bootstrap seed m32p:h1",
            "h2": "validation-frozen non-oracle policy vs normal and "
                  "matched-random on sealed holdout; seeds m32p:h2:*",
            "h3": "soft penalties must generalize discovery->validation->"
                  "holdout under Bonferroni",
            "bootstrap_iterations": 2000,
        },
        "minimum_realized_failures": {"discovery": 30, "validation": 15,
                                      "holdout": 15,
                                      "on_shortfall": "classify underpowered; "
                                                      "never regenerate"},
        "privacy": {"public": "aggregate metrics/intervals only",
                    "private": "operands/prompts/outputs/routes/expert tables "
                               "stay gitignored"},
        "candidate_only": True,
        "production_gated": True,
    }
    out = Path(args.manifest)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"[jlens] M32P manifest built: N={manifest['n_tasks']} "
          f"cells={len(cells)} -> {out}")
    return 0


def run_study(args):
    """Single-load driver: originals, trigger, causal screen, evaluation."""
    import time
    import torch
    manifest, tasks = prepare_private_tasks(args)
    started = time.time()
    tok, model, cfg, controller = _load_model(args.model_ref)

    captures_dir = Path(args.captures)
    captures_dir.mkdir(parents=True, exist_ok=True)
    print(f"[jlens] M32P originals ({len(tasks)})", flush=True)
    for task in tasks:
        dest = captures_dir / f"{task['prompt_id']}.pt"
        if CAP._valid_capture(dest):
            continue
        input_ids, router, hidden, steps = CAP.capture_one(
            tok, model, task["prompt"], 4096, max_new_tokens=DECODE_CAP,
            router_only=True, chat_template=True)
        torch.save({"prompt_id": task["prompt_id"], "input_ids": input_ids,
                    "router_logits": router, "hidden_states": hidden,
                    "model_type": cfg.model_type,
                    "model_path": str(args.model_ref),
                    "decode_steps": steps,
                    "generated_output": tok.decode(
                        [s["generated_token_id"] for s in steps],
                        skip_special_tokens=True)}, dest)

    classifier = M31.frozen_m30_classifier(
        args.m30_manifest, args.m30_labels, args.m30_telemetry,
        args.m30_evaluation)
    backend = HFTelemetryBackend(
        model_ref=args.model_ref, source_kind="local_path", top_k=5)
    threshold = manifest["frozen_trigger"]["threshold_fail_probability"]

    import m26_objective_error as M26
    rows, undecided, captures = [], Counter(), {}
    for task in tasks:
        payload = torch.load(captures_dir / f"{task['prompt_id']}.pt",
                             map_location="cpu", weights_only=False)
        captures[task["prompt_id"]] = payload
        verdict = verdict_for(payload.get("generated_output"), task)
        if verdict == "undecided":
            undecided[task["m32p_split"]] += 1
            continue
        record = M22.record_from_capture(payload, backend, {})
        features = {name: getter(record)
                    for name, getter in M26.FEATURES.items()}
        p_fail = M28.fail_probability(classifier, features)
        rows.append({
            "task_id": task["prompt_id"], "cell": task["m32p_cell"],
            "split": task["m32p_split"],
            "original_pass": verdict == "pass",
            "p_fail": p_fail, "triggered": p_fail >= threshold,
        })

    coact = coactivation_table(
        [captures[row["task_id"]] for row in rows
         if row["split"] == "discovery"])
    task_by_id = {task["prompt_id"]: task for task in tasks}

    branches_by_task = {}

    def screen_split(split, penalties=None):
        todo = [row for row in rows if row["split"] == split
                and row["triggered"]]
        print(f"[jlens] M32P causal screen: {split} ({len(todo)} triggered)",
              flush=True)
        for index, row in enumerate(todo):
            task = task_by_id[row["task_id"]]
            branches_by_task[row["task_id"]] = _branch_records_for_task(
                tok, model, controller, task, captures[row["task_id"]],
                coact, penalties=penalties)
            if (index + 1) % 10 == 0:
                print(f"[jlens]   {split}: {index + 1}/{len(todo)}",
                      flush=True)

    screen_split("discovery")
    screen_split("validation")
    penalties = fit_soft_penalties(manifest, rows, branches_by_task)
    print(f"[jlens] M32P frozen soft-penalty candidates: {len(penalties)}",
          flush=True)
    screen_split("holdout", penalties=penalties)

    peak = sum(torch.cuda.max_memory_allocated(i)
               for i in range(torch.cuda.device_count())) / 1024 ** 3
    wall_minutes = (time.time() - started) / 60

    M23.write_jsonl(args.rows_out, rows)
    flat = [dict(branch, task_id=task_id) for task_id, branches
            in branches_by_task.items() for branch in branches]
    M23.write_jsonl(args.branches_out, flat)

    evaluation = evaluate(manifest, rows, branches_by_task)
    evaluation["h3_soft_penalty"] = h3_verdicts(
        manifest, penalties, rows, branches_by_task)
    rescue_traces = sum(
        1 for row in rows if not row["original_pass"]
        for branch in branches_by_task.get(row["task_id"], [])
        if branch["full_run"] and branch["verdict"] == "pass")
    evaluation["private_counterfactual_records"] = {
        "branch_records": len(flat),
        "verified_rescue_branches": rescue_traces,
        "storage": "private gitignored JSONL",
    }
    summary = {
        "schema_version": 1,
        "run_kind": "m32p_proxy_routing_dataset",
        "model_scope": "qwen2_moe research proxy only; not Agents-A1",
        "task_category": manifest["task_category"],
        "n_tasks": len(tasks),
        "n_rows_evaluated": len(rows),
        "undecided_excluded_counts": dict(sorted(undecided.items())),
        "label_distribution_by_split": {
            split: dict(sorted(Counter(
                "pass" if row["original_pass"] else "fail"
                for row in rows if row["split"] == split).items()))
            for split in SPLITS},
        "label_distribution_by_cell": {
            cell["cell_id"]: dict(sorted(Counter(
                "pass" if row["original_pass"] else "fail"
                for row in rows if row["cell"] == cell["cell_id"]).items()))
            for cell in manifest["cells"]},
        "decode_cap_tokens": DECODE_CAP,
        "peak_gpu_memory_gib": round(peak, 2),
        "memory_gate_44gib": peak <= 44.0,
        "wall_minutes": round(wall_minutes, 1),
        "operands_disjoint_from_prior_milestones": True,
        "no_posthoc_selection": True,
        "per_task_routes_or_expert_tables_persisted_publicly": False,
        "raw_text_token_tensor_or_path_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only proxy routing summary",
    }
    for path, payload in ((args.summary_out, summary),
                          (args.evaluation_out, evaluation)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n")
    h1 = evaluation["h1_route_recoverability"]
    h2 = evaluation["h2_deployable_rerouting"]
    print(f"[jlens] M32P: rows={len(rows)}; H1={h1['verdict']} "
          f"(heur {h1['heuristic_oracle_rescue_rate']} vs rand "
          f"{h1['random_oracle_rescue_rate']}); H2={h2['verdict']} "
          f"(policy {h2['frozen_policy']}); "
          f"H3={evaluation['h3_soft_penalty']['verdict']}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest",
                    default="data/prompts/m32p_proxy_routing_manifest.json")
    ap.add_argument("--m29-manifest", default="data/prompts/m29_power_manifest.json")
    ap.add_argument("--m30-manifest", default="data/prompts/m30_decisive_manifest.json")
    ap.add_argument("--m31-manifest",
                    default="data/prompts/m31_intervention_manifest.json")
    ap.add_argument("--m32-manifest", default="data/prompts/m32_repair_manifest.json")
    ap.add_argument("--m30-labels",
                    default="reports/shadow/private/m30_error_labels_local.jsonl")
    ap.add_argument("--m30-telemetry",
                    default="reports/shadow/private/m30_hf_telemetry_records_local.jsonl")
    ap.add_argument("--m30-evaluation",
                    default="reports/telemetry/hf_m30_decisive_increment_evaluation.json")
    ap.add_argument("--tasks-out",
                    default="reports/shadow/private/m32p_hf_prompts_local.jsonl")
    ap.add_argument("--captures", default="data/captures/m32p_qwen15_moe")
    ap.add_argument("--rows-out",
                    default="reports/shadow/private/m32p_rows_local.jsonl")
    ap.add_argument("--branches-out",
                    default="reports/shadow/private/m32p_branches_local.jsonl")
    ap.add_argument("--model-ref")
    ap.add_argument("--sweep-config",
                    default="data/prompts/m32p_frontier_sweep_config.json")
    ap.add_argument("--sweep-results-out",
                    default="reports/shadow/private/m32p_sweep_results_local.jsonl")
    ap.add_argument("--frontier-out",
                    default="reports/telemetry/hf_m32p_proxy_benchmark_frontier.json")
    ap.add_argument("--sweep", action="store_true",
                    help="run the smoke gate then the calibration sweep (GPU)")
    ap.add_argument("--build-manifest", action="store_true",
                    help="construct the preregistration manifest from the "
                         "frontier report (CPU)")
    ap.add_argument("--smoke", action="store_true",
                    help="run the Phase-0 real smoke gate only")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--run", action="store_true",
                    help="run the full study driver (GPU)")
    ap.add_argument("--feasibility-out",
                    default="reports/telemetry/hf_m32p_proxy_routing_feasibility.json")
    ap.add_argument("--summary-out",
                    default="reports/telemetry/hf_m32p_proxy_routing_run_summary.json")
    ap.add_argument("--evaluation-out",
                    default="reports/telemetry/hf_m32p_proxy_routing_evaluation.json")
    args = ap.parse_args(argv)

    if args.sweep:
        if not args.model_ref:
            raise ValueError("--model-ref is required for the sweep")
        return run_sweep(args)
    if args.build_manifest:
        return build_manifest(args)
    if args.smoke:
        if not args.model_ref:
            raise ValueError("--model-ref is required for the smoke gate")
        payload = run_smoke(args.model_ref, args.feasibility_out)
        print(f"[jlens] M32P smoke: parity="
              f"{payload['disabled_override_greedy_parity']} "
              f"swap_changes_routing={payload['forced_swap_routing_changed']} "
              f"peak={payload['peak_gpu_memory_gib']} GiB")
        return 0
    if args.prepare_only:
        manifest, tasks = prepare_private_tasks(args)
        done = sum((Path(args.captures) / f"{t['prompt_id']}.pt").exists()
                   for t in tasks)
        print(f"[jlens] M32P predeclared tasks: {len(tasks)}; "
              f"original captures existing={done}")
        return 0
    if args.run:
        if not args.model_ref:
            raise ValueError("--model-ref is required for the study driver")
        return run_study(args)
    ap.error("choose one of --sweep, --build-manifest, --smoke, --prepare-only, --run")


if __name__ == "__main__":
    raise SystemExit(main())
