#!/usr/bin/env python3
"""M32P proxy-routing tests are CPU-only and no-network."""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m32p_proxy_counterfactual_routing as M32P  # noqa: E402

SWEEP_CONFIG = json.loads(
    (ROOT / "data/prompts/m32p_frontier_sweep_config.json").read_text())


def _fake_manifest():
    return {
        "task_category": "integer_multiplication_model_calibrated",
        "frozen_trigger": {"threshold_fail_probability": 0.5},
        "causal_screen": {"fragile_steps_per_task": 2, "layers_per_step": 4,
                          "full_continuations_per_arm": 4},
        "soft_penalty_rule": {"discovery_min_support": 5,
                              "discovery_min_net_rescues": 2,
                              "validation_min_support": 2,
                              "penalty_delta": 2.0, "alpha": 0.05},
    }


def _branch(task_id, step, layer, family, arm, *, changed=1, gain=0.1,
            full=False, verdict=None, swap_out=None):
    return {"task_id": task_id, "step": step, "layer": layer, "arm": arm,
            "family": family, "swap_out": swap_out, "swap_in": 9,
            "screen_changed_token": changed, "screen_margin_gain": gain,
            "full_run": full, "verdict": verdict, "output": None,
            "tokens_generated": 8 if full else 0}


def _rows_and_branches(*, heuristic_wins=True):
    rows, branches = [], {}
    for index in range(96):
        split = ("discovery" if index < 48 else
                 "validation" if index < 72 else "holdout")
        original_pass = index % 2 == 0
        triggered = not original_pass or index % 12 == 0
        rows.append({"task_id": f"t{index:03d}", "cell": "c_3x2_heavy",
                     "split": split, "original_pass": original_pass,
                     "p_fail": 0.9 if triggered else 0.1,
                     "triggered": triggered})
        if not triggered:
            continue
        task_branches = []
        for i in range(4):
            rescued = heuristic_wins and not original_pass and i == 0 \
                and index % 3 != 2
            # Heuristic branches on originally-passing tasks keep passing, so
            # the deployable policy has rescues without regressions.
            branch_passes = rescued or (original_pass and heuristic_wins)
            task_branches.append(_branch(
                f"t{index:03d}", 2, 5 + i, "each_selected_to_rank5",
                "heuristic", changed=1, gain=0.2 - 0.01 * i, full=True,
                verdict="pass" if branch_passes else "fail", swap_out=10 + i))
            task_branches.append(_branch(
                f"t{index:03d}", 2, 5 + i, "matched_random_swap", "random",
                changed=1, gain=0.15 - 0.01 * i, full=True,
                verdict="fail", swap_out=20 + i))
        branches[f"t{index:03d}"] = task_branches
    return rows, branches


def test_cell_generators_are_deterministic_and_structured():
    prior = set()
    for cell in SWEEP_CONFIG["cells"]:
        tuples = M32P.generate_cell_tuples(cell, "test-seed", 12, prior)
        again = M32P.generate_cell_tuples(cell, "test-seed", 12, prior)
        assert tuples == again
        assert len(set(tuples)) == len(tuples) == 12
        for a, b in tuples:
            assert len(str(a)) == cell["digits_a"]
            if cell["structure"] == "low_carry":
                assert all(d in "0123" for d in f"{a}{b}")
            if cell["structure"] == "carry_heavy":
                assert all(d in "6789" for d in f"{a}{b}")
            if cell["structure"] == "middle_zero":
                assert str(a)[1] == "0"
            if cell["structure"] == "near_power_of_ten":
                assert a in (101, 102, 998, 999)


def test_frontier_selection_composition_and_power_table():
    results = [
        {"cell_id": "c_2x1", "n": 24, "feasible": True, "pass_rate": 1.0},
        {"cell_id": "c_2x2_low", "n": 24, "feasible": True, "pass_rate": 0.95},
        {"cell_id": "c_2x2_heavy", "n": 24, "feasible": True, "pass_rate": 0.6},
        {"cell_id": "c_3x2_low", "n": 24, "feasible": True, "pass_rate": 0.7},
        {"cell_id": "c_3x2_heavy", "n": 24, "feasible": True, "pass_rate": 0.3},
        {"cell_id": "c_4x2_low", "n": 24, "feasible": True, "pass_rate": 0.5},
        {"cell_id": "c_3x3", "n": 24, "feasible": True, "pass_rate": 0.05},
    ]
    frontier = M32P.select_frontier(SWEEP_CONFIG, results)
    assert frontier["frontier_found"] is True
    counts = frontier["composition"]
    total = frontier["task_count"]
    assert total in (192, 240, 288)
    assert sum(counts.values()) == total
    assert all(count % 4 == 0 for count in counts.values())
    assert all(count / total <= 0.35 + 1e-9 for count in counts.values())
    boundary_cells = {"c_2x2_heavy", "c_3x2_low", "c_3x2_heavy", "c_4x2_low"}
    assert boundary_cells <= set(counts)
    assert frontier["expected_failures"] >= 88


def test_frontier_not_found_with_too_few_boundary_cells():
    results = [
        {"cell_id": "c_2x1", "n": 24, "feasible": True, "pass_rate": 1.0},
        {"cell_id": "c_2x2_heavy", "n": 24, "feasible": True, "pass_rate": 0.5},
        {"cell_id": "c_3x3", "n": 24, "feasible": True, "pass_rate": 0.02},
    ]
    frontier = M32P.select_frontier(SWEEP_CONFIG, results)
    assert frontier["frontier_found"] is False


def test_fragile_steps_and_layers_use_original_telemetry_only():
    import torch
    steps = []
    for index in range(6):
        steps.append({
            "generated_token_id": index,
            "entropy_final_logits": 2.0 if index in (1, 4) else 0.2,
            "top_k_margin": 0.5,
            "router_logits": [torch.randn(1, 60) for _ in range(24)],
        })
    capture = {"decode_steps": steps,
               "router_logits": [torch.randn(3, 60) for _ in range(24)]}
    fragile = M32P.fragile_steps(capture)
    assert fragile == [1, 4]
    layers = M32P.implicated_layers(capture, 1)
    assert len(layers) == 4 and len(set(layers)) == 4
    assert all(0 <= layer < 24 for layer in layers)
    layers_at_zero = M32P.implicated_layers(capture, 0)
    assert len(layers_at_zero) == 4


def test_branch_plans_respect_frozen_families_and_budgets():
    import torch
    torch.manual_seed(3)
    row = torch.randn(60)
    plans, randoms = M32P.branch_plans(row, 7, {}, "task_x", 2)
    families = [family for family, _ in plans]
    assert families.count("each_selected_to_rank5") == 3
    assert families.count("lowest_weight_to_rank5") == 1
    assert families.count("selected_to_rank6") == 1
    assert families.count("diversity_swap") == 1
    assert len(randoms) == len(plans) == 6
    selected = set(torch.topk(row, 4).indices.tolist())
    for _, plan in plans:
        assert plan.swap_out in selected
        assert plan.swap_in not in selected
    again, _ = M32P.branch_plans(row, 7, {}, "task_x", 2)
    assert [(f, p.swap_out, p.swap_in) for f, p in plans] == \
        [(f, p.swap_out, p.swap_in) for f, p in again]


def test_evaluate_h1_h2_verdicts_on_synthetic_branches():
    manifest = _fake_manifest()
    rows, branches = _rows_and_branches(heuristic_wins=True)
    report = M32P.evaluate(manifest, rows, branches)
    h1 = report["h1_route_recoverability"]
    assert h1["heuristic_oracle_rescue_rate"] > h1["random_oracle_rescue_rate"]
    assert h1["verdict"] == "route_recoverability_established"
    h2 = report["h2_deployable_rerouting"]
    assert h2["frozen_policy"] in M32P.POLICY_CANDIDATES
    assert h2["verdict"] == "deployable_rerouting_established"
    assert report["frozen_trigger"]["trigger_recall"] == 1.0


def test_evaluate_not_established_when_routes_never_help():
    manifest = _fake_manifest()
    rows, branches = _rows_and_branches(heuristic_wins=False)
    report = M32P.evaluate(manifest, rows, branches)
    assert report["h1_route_recoverability"]["verdict"] == \
        "route_recoverability_not_established"
    assert report["h2_deployable_rerouting"]["verdict"] != \
        "deployable_rerouting_established"


def test_soft_penalty_pipeline_and_h3():
    manifest = _fake_manifest()
    rows, branches = _rows_and_branches(heuristic_wins=True)
    penalties = M32P.fit_soft_penalties(manifest, rows, branches)
    for penalty in penalties:
        assert penalty["delta"] == 2.0
    verdict = M32P.h3_verdicts(manifest, penalties, rows, branches)
    if not penalties:
        assert verdict["verdict"] == "no_candidate_survived"
    else:
        assert verdict["verdict"] in ("candidate_soft_penalty",
                                      "exploratory_only")


def test_public_evaluation_has_no_routes_ids_or_text():
    manifest = _fake_manifest()
    rows, branches = _rows_and_branches(heuristic_wins=True)
    report = M32P.evaluate(manifest, rows, branches)
    public = json.dumps(report)
    assert "t00" not in public and "swap_out" not in public
    assert "expression" not in public and "prompt" not in public
    assert report["per_task_routes_or_expert_tables_persisted_publicly"] is False
