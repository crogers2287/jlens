"""CPU-only tests for the M35 track A hierarchical router."""
import json
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m35_track_a as TA  # noqa: E402
import m35_track_b as TB  # noqa: E402


def _row(family, split, fail, f1, task):
    return {"task_id": task, "family": family, "split": split,
            "original_pass": not fail, "tool_pass": True,
            "features": {"f1": f1, "f2": 0.0}}


def _campaign(seed=11):
    rng = random.Random(seed)
    rows = []
    for split, n in (("D", 40), ("R", 20), ("A_test", 20)):
        for i in range(n):
            fail = i % 2 == 0
            rows.append(_row("mul_carry", split, fail,
                             2 + rng.random() if fail else -2 - rng.random(),
                             f"mc_{split}_{i}"))
        for i in range(n):
            rows.append(_row("mul_add", split, i != 0, rng.random(),
                             f"ma_{split}_{i}"))
        for i in range(n):
            rows.append(_row("add_carry", split, i == 0, rng.random(),
                             f"ac_{split}_{i}"))
    return rows


def test_route_family_thresholds():
    assert TA.route_family(0.02, 0.1, 0.8) == "no_tool"
    assert TA.route_family(0.95, 0.1, 0.8) == "tool_on_every_task"
    assert TA.route_family(0.4, 0.1, 0.8) == "telemetry_gated_tool"


def test_calibrate_router_respects_budget():
    rows = _campaign()
    d_rows = [r for r in rows if r["split"] == "D"]
    r_rows = [r for r in rows if r["split"] == "R"]
    variants = TB.fit_variants(d_rows)
    router = TA.calibrate_router(r_rows, variants)
    assert router["r_invocation_fraction"] <= TA.BUDGET_FRACTION
    assert router["t_low"] in TA.LOW_GRID
    assert router["t_high"] in TA.HIGH_GRID


def test_evaluate_a_test_verdicts_and_verifier_first():
    rows = _campaign()
    d_rows = [r for r in rows if r["split"] == "D"]
    r_rows = [r for r in rows if r["split"] == "R"]
    a_rows = [r for r in rows if r["split"] == "A_test"]
    variants = TB.fit_variants(d_rows)
    router = TA.calibrate_router(r_rows, variants)
    out = TA.evaluate_a_test(a_rows, router["priors"], variants, router)
    metrics = out["policy_metrics"]
    # router routes mul_add to tool-everywhere, add_carry to no-tool
    counts = out["router"]["action_row_counts"]
    assert counts.get("tool_on_every_task", 0) >= 20
    assert counts.get("no_tool", 0) >= 20
    # verifier-first: every arm >= no_repair
    floor = metrics["no_repair"]["verified_success_rate_task_level"]
    for name, m in metrics.items():
        assert m["verified_success_rate_task_level"] >= floor
    assert out["a_h2_non_inferiority"]["tool_calls_saved"] > 0
    assert out["a_h1_fixed_budget"]["verdict"] in (
        "useful", "not_established")


def test_router_config_hash_sensitive_to_thresholds():
    base = {"t_low": 0.05, "t_high": 0.8, "priors": {"x": 0.5},
            "r_invocation_fraction": 0.4, "r_verified_success": 0.9}
    other = dict(base, t_low=0.15)
    assert TA.router_config_hash(base, "abc") != \
        TA.router_config_hash(other, "abc")


def test_a_test_reread_refused(tmp_path):
    rows = _campaign()
    rows_path = tmp_path / "rows.jsonl"
    rows_path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    d_rows = [r for r in rows if r["split"] == "D"]
    det_freeze = tmp_path / "det.json"
    det_freeze.write_text(json.dumps(
        {"config_hash": TB.config_hash(TB.fit_variants(d_rows))}))
    freeze_path = tmp_path / "router.json"
    eval_path = tmp_path / "eval.json"
    TA.main(["--rows", str(rows_path), "--stage", "fit",
             "--detector-freeze", str(det_freeze),
             "--freeze-out", str(freeze_path)])
    TA.main(["--rows", str(rows_path), "--stage", "a_test",
             "--detector-freeze", str(det_freeze),
             "--freeze-out", str(freeze_path),
             "--evaluation-out", str(eval_path)])
    with pytest.raises(ValueError, match="already been read"):
        TA.main(["--rows", str(rows_path), "--stage", "a_test",
                 "--detector-freeze", str(det_freeze),
                 "--freeze-out", str(freeze_path),
                 "--evaluation-out", str(eval_path)])
