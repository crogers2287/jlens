"""CPU-only tests for M34 second-category detector transfer."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m34_detector_transfer as M34  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m34_transfer_manifest.json"


@pytest.fixture(scope="module")
def manifest():
    return M34.load_manifest(MANIFEST_PATH)


def test_load_manifest_validates(manifest, tmp_path):
    assert manifest["n_tasks"] == 384
    bad = json.loads(MANIFEST_PATH.read_text())
    bad["generation"]["additive_term_range"] = [2, 999]
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        M34.load_manifest(path)


def test_tool_answer_is_exact():
    task = {"a": 4321, "b": 987, "c": 55, "expression": "4321*987+55"}
    assert M34.tool_answer(task) == str(4321 * 987 + 55)


def _rows(n_fail_triggered, n_fail_missed, n_pass_triggered, n_pass):
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


def test_t1_transfer_maintained(manifest):
    out = M34.evaluate(manifest, _rows(9, 1, 1, 20))
    trig = out["frozen_trigger"]
    assert trig["trigger_precision"] == pytest.approx(0.9)
    assert trig["trigger_recall"] == pytest.approx(0.9)
    assert out["t1_transfer_classification"]["verdict"] == \
        "transfer_maintained"
    assert out["h2_routing_efficiency"]["verdict"] == "efficient"


def test_t1_transfer_degraded_when_weak_but_useful(manifest):
    # precision .5 (below .80) but routing still rescues many failures
    out = M34.evaluate(manifest, _rows(40, 0, 40, 120))
    assert out["frozen_trigger"]["trigger_precision"] == pytest.approx(0.5)
    assert out["h1_routing_usefulness"]["verdict"] == "useful"
    assert out["t1_transfer_classification"]["verdict"] == "transfer_degraded"


def test_t1_transfer_failed_when_no_signal(manifest):
    # trigger fires only on passing tasks: no rescues, H1 cannot be useful
    rows = _rows(0, 6, 8, 30)
    out = M34.evaluate(manifest, rows)
    assert out["frozen_trigger"]["trigger_precision"] == 0.0
    assert out["t1_transfer_classification"]["verdict"] == "transfer_failed"


def test_verifier_first_never_replaces_passing_original(manifest):
    rows = _rows(5, 2, 1, 8)
    rows.append({"task_id": "tx", "band": "band_1", "p_fail": 0.9,
                 "original_pass": True, "tool_pass": False})
    out = M34.evaluate(manifest, rows)
    for metrics in out["policy_metrics"].values():
        assert metrics["errors_introduced"] == 0


def test_generation_disjoint_from_m33_and_c_range(manifest):
    import m33_tool_routing as M33
    base = ROOT / "data/prompts"
    args = [str(base / name) for name in (
        "m29_power_manifest.json", "m30_decisive_manifest.json",
        "m31_intervention_manifest.json", "m32_repair_manifest.json")]
    m34_tasks = M34.generate_tasks(
        manifest, *args, str(base / "m33_tool_routing_manifest.json"))
    m33_manifest = M33.load_manifest(base / "m33_tool_routing_manifest.json")
    m33_tasks = M33.generate_tasks(m33_manifest, *args)
    m34_tuples = {(t["a"], t["b"]) for t in m34_tasks}
    m33_tuples = {(t["a"], t["b"]) for t in m33_tasks}
    assert len(m34_tasks) == 384
    assert not m34_tuples & m33_tuples
    assert all(2 <= t["c"] <= 99 for t in m34_tasks)
    assert all(t["known_answer"] == str(t["a"] * t["b"] + t["c"])
               for t in m34_tasks)
