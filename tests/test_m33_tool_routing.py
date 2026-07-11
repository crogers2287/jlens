"""CPU-only tests for M33 telemetry-gated tool routing."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m33_tool_routing as M33  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m33_tool_routing_manifest.json"


@pytest.fixture(scope="module")
def manifest():
    return M33.load_manifest(MANIFEST_PATH)


def _manifest_with(**overrides):
    data = json.loads(MANIFEST_PATH.read_text())
    data.update(overrides)
    return data


def test_load_manifest_validates(manifest, tmp_path):
    assert manifest["n_tasks"] == 384
    bad = _manifest_with(selection_status="post_hoc")
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        M33.load_manifest(path)


def test_tool_answer_is_exact():
    task = {"a": 4321, "b": 987, "expression": "4321*987",
            "known_answer": str(4321 * 987)}
    assert M33.tool_answer(task) == str(4321 * 987)


def _rows(n_fail_triggered=5, n_fail_missed=2, n_pass_triggered=1,
          n_pass=8):
    rows, i = [], 0
    for _ in range(n_fail_triggered):
        rows.append({"task_id": f"t{i}", "band": "band_4", "p_fail": 0.9,
                     "original_pass": False, "tool_pass": True}); i += 1
    for _ in range(n_fail_missed):
        rows.append({"task_id": f"t{i}", "band": "band_2", "p_fail": 0.1,
                     "original_pass": False, "tool_pass": True}); i += 1
    for _ in range(n_pass_triggered):
        rows.append({"task_id": f"t{i}", "band": "band_4", "p_fail": 0.9,
                     "original_pass": True, "tool_pass": True}); i += 1
    for _ in range(n_pass):
        rows.append({"task_id": f"t{i}", "band": "band_1", "p_fail": 0.1,
                     "original_pass": True, "tool_pass": True}); i += 1
    return rows


def test_evaluate_policies_and_gate(manifest):
    rows = _rows()
    out = M33.evaluate(manifest, rows)
    trig = out["frozen_trigger"]
    assert trig["trigger_count"] == 6
    assert trig["trigger_precision"] == pytest.approx(5 / 6)
    assert trig["trigger_recall"] == pytest.approx(5 / 7)
    # recall 5/7 < .75 -> reproduction gate fails, no H1/H2 claims
    assert not trig["reproduction_gate"]["passed"]
    assert out["h1_routing_usefulness"]["verdict"] == "gate_failed_no_claim"
    assert out["h2_routing_efficiency"]["verdict"] == "gate_failed_no_claim"
    # tool_on_every_task rescues every failure; originals never replaced
    tool = out["policy_metrics"]["tool_on_every_task"]
    assert tool["verified_success_rate"] == 1.0
    assert tool["errors_introduced"] == 0
    tel = out["policy_metrics"]["telemetry_trigger_tool"]
    assert tel["errors_rescued"] == 5
    assert tel["tool_invocations"] == 6


def test_evaluate_gate_pass_verdicts(manifest):
    rows = _rows(n_fail_triggered=9, n_fail_missed=1, n_pass_triggered=1,
                 n_pass=20)
    out = M33.evaluate(manifest, rows)
    assert out["frozen_trigger"]["reproduction_gate"]["passed"]
    assert out["h1_routing_usefulness"]["verdict"] in (
        "useful", "not_established")
    h2 = out["h2_routing_efficiency"]
    assert h2["uplift_retention"] == pytest.approx(0.9)
    assert h2["invocation_fraction"] == pytest.approx(10 / 31)
    assert h2["verdict"] == "efficient"
    bands = {b["band"]: b for b in
             out["per_band_descriptives_secondary"]["bands"]}
    assert bands["band_4"]["telemetry_rescues"] == 9


def test_verifier_first_never_replaces_passing_original(manifest):
    rows = _rows()
    # even a task whose tool output would fail cannot harm a passing original
    rows.append({"task_id": "tx", "band": "band_1", "p_fail": 0.9,
                 "original_pass": True, "tool_pass": False})
    out = M33.evaluate(manifest, rows)
    for metrics in out["policy_metrics"].values():
        assert metrics["errors_introduced"] == 0


def test_generation_disjoint_from_m32(manifest):
    import m32_structured_repair as M32
    base = Path(__file__).resolve().parent.parent
    args = [str(base / "data/prompts" / name) for name in (
        "m29_power_manifest.json", "m30_decisive_manifest.json",
        "m31_intervention_manifest.json")]
    m33_tasks = M33.generate_tasks(
        manifest, *args, str(base / "data/prompts/m32_repair_manifest.json"))
    m32_manifest = M32.load_manifest(
        base / "data/prompts/m32_repair_manifest.json")
    m32_tasks = M32.generate_tasks(m32_manifest, *args)
    m33_tuples = {(t["a"], t["b"]) for t in m33_tasks}
    m32_tuples = {(t["a"], t["b"]) for t in m32_tasks}
    assert len(m33_tasks) == 384
    assert not m33_tuples & m32_tuples
