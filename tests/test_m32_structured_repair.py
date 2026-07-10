#!/usr/bin/env python3
"""M32 structured-repair tests are CPU-only and no-network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m32_structured_repair as M32  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m32_repair_manifest.json"
M29_PATH = ROOT / "data/prompts/m29_power_manifest.json"
M30_PATH = ROOT / "data/prompts/m30_decisive_manifest.json"
M31_PATH = ROOT / "data/prompts/m31_intervention_manifest.json"


def _candidate(passes, tokens=50, p_fail=0.3, output="Answer: 1"):
    return {"output": output, "pass": passes,
            "verdict": "pass" if passes else "fail",
            "tokens": tokens, "p_fail": p_fail}


def _rows(*, bundle_strength=0.5, resample_strength=0.05):
    """60 synthetic rows: 30 pass / 30 fail with an informative trigger."""
    rows = []
    for index in range(60):
        original_pass = index < 30
        candidates = {"resample_t07": _candidate(
            (not original_pass) and index % int(1 / max(resample_strength, .01))
            == 30 % 3 if not original_pass and resample_strength > 0 else False)}
        if not original_pass:
            candidates["resample_t07"] = _candidate(
                resample_strength > 0 and index % 20 == 10)
            candidates["independent_deliberate"] = _candidate(
                bundle_strength > 0 and index % 2 == 0, tokens=100)
            candidates["checker_guided_repair"] = _candidate(
                bundle_strength > 0 and index % 4 == 1, tokens=90)
            candidates["diagnose_then_repair"] = _candidate(
                False, tokens=120)
        rows.append({
            "task_id": f"row_{index:03d}",
            "band": "band_4",
            "expression": "111*111",
            "known_answer": "12321",
            "original_pass": original_pass,
            "p_fail": 0.1 if original_pass else 0.9,
            "candidates": candidates,
        })
    return rows


def _walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_generation_is_deterministic_and_disjoint_from_prior_milestones():
    manifest = M32.load_manifest(MANIFEST_PATH)
    tasks = M32.generate_tasks(manifest, M29_PATH, M30_PATH, M31_PATH)
    assert tasks == M32.generate_tasks(manifest, M29_PATH, M30_PATH, M31_PATH)
    assert len(tasks) == 384
    prior = M32.prior_tuples_all(M29_PATH, M30_PATH, M31_PATH)
    counts = {}
    for task in tasks:
        assert (task["a"], task["b"]) not in prior[task["m32_band"]]
        assert task["known_answer"] == str(task["a"] * task["b"])
        counts[task["m32_band"]] = counts.get(task["m32_band"], 0) + 1
    assert all(count == 64 for count in counts.values())


def test_repair_prompts_never_reveal_the_true_answer():
    manifest = M32.load_manifest(MANIFEST_PATH)
    task = {"a": 47, "b": 83, "known_answer": "3901", "expression": "47*83"}
    prompts = M32.repair_prompts(manifest, task, "3801",
                                 diagnosis="check the carry in tens column")
    assert set(prompts) == {"independent_deliberate", "checker_guided_repair",
                            "diagnose_stage_a", "diagnose_stage_b"}
    for name, prompt in prompts.items():
        assert "3901" not in prompt, name
    assert "3801" in prompts["checker_guided_repair"]
    assert "3801" not in prompts["independent_deliberate"]
    assert "carry in tens column" in prompts["diagnose_stage_b"]


def test_verdict_mapping():
    task = {"known_answer": "12", "expression": "3*4"}
    assert M32.verdict_for("Answer: 12", task) == "pass"
    assert M32.verdict_for("Answer: 13", task) == "fail"
    assert M32.verdict_for("no digits here", task) == "undecided"


def test_evaluate_bundle_never_harms_and_counts_sequential_tokens():
    manifest = M32.load_manifest(MANIFEST_PATH)
    report = M32.evaluate(manifest, _rows())
    metrics = report["policy_metrics"]
    assert metrics["no_repair"]["errors_rescued"] == 0
    for policy in ("always_structured_bundle",
                   "telemetry_trigger_structured_bundle",
                   "random_trigger_structured_bundle"):
        assert metrics[policy]["errors_introduced"] == 0
        assert (metrics[policy]["verified_success_rate"]
                >= metrics["no_repair"]["verified_success_rate"])
    # Perfect trigger: telemetry bundle attempts exactly the 30 fails.
    assert metrics["telemetry_trigger_structured_bundle"][
        "tasks_attempted"] == 30
    assert report["frozen_trigger"]["trigger_precision"] == 1.0
    assert report["frozen_trigger"]["trigger_recall"] == 1.0
    # Sequential consumption: when the first candidate wins, later
    # candidates are not consumed, so tokens < sum of all candidates.
    bundle = metrics["telemetry_trigger_structured_bundle"]
    assert bundle["candidate_decode_tokens"] < 30 * (100 + 90 + 120)
    assert bundle["errors_rescued"] > 0
    assert report["tool_upper_bound_success_rate"] == 1.0


def test_h1_improved_when_bundle_beats_resample_and_h2_useful():
    manifest = M32.load_manifest(MANIFEST_PATH)
    report = M32.evaluate(manifest, _rows())
    h1 = report["h1_repair_operator"]
    assert h1["n"] == 30
    assert h1["bundle_rescue_rate"] > h1["resample_rescue_rate"]
    assert h1["verdict"] == "repair_improved"
    assert report["h2_policy_usefulness"]["verdict"] == "useful"


def test_h1_not_established_when_bundle_matches_resample():
    manifest = M32.load_manifest(MANIFEST_PATH)
    rows = _rows(bundle_strength=0.0, resample_strength=0.0)
    report = M32.evaluate(manifest, rows)
    assert report["h1_repair_operator"]["verdict"] == "repair_not_established"
    assert report["h2_policy_usefulness"]["verdict"] != "useful"


def test_majority_answer_tie_breaks_to_frozen_order():
    candidates = {
        "independent_deliberate": {"output": "Answer: 10"},
        "checker_guided_repair": {"output": "Answer: 20"},
        "diagnose_then_repair": {"output": "Answer: 20"},
        "resample_t07": {"output": "Answer: 10"},
    }
    assert M32._majority_answer(candidates, list(M32.ALL_OPERATORS)) == "10"
    candidates["resample_t07"]["output"] = "Answer: 20"
    assert M32._majority_answer(candidates, list(M32.ALL_OPERATORS)) == "20"


def test_public_evaluation_is_aggregate_only():
    manifest = M32.load_manifest(MANIFEST_PATH)
    report = M32.evaluate(manifest, _rows())
    public = json.dumps(report)
    assert "row_0" not in public and "m32_b" not in public
    assert "12321" not in public and "Answer:" not in public
    assert not ({"task_id", "prompt", "expression", "known_answer",
                 "output", "candidates", "diagnosis"} & set(_walk(report)))
    assert report["per_task_predictions_persisted_publicly"] is False
