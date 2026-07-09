#!/usr/bin/env python3
"""M20 grounded-regeneration safety/report tests. CPU-only, no network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import action_executor as EXEC  # noqa: E402
import grounded_regenerator as GR  # noqa: E402
import verifiers as VZ  # noqa: E402
from jsonschema import Draft7Validator  # noqa: E402

SCHEMA = json.loads((ROOT / "schema/grounded_result_v1.json").read_text())
VALIDATOR = Draft7Validator(SCHEMA)


def _task(pid="c", category="current_info"):
    return {"prompt_id": pid, "prompt": "What is the answer?",
            "task_category": category}


def _action(pid="c"):
    return {"task_id": pid, "action_type": "retrieval_needed",
            "action_status": "completed", "result_type": "retrieved_context",
            "action_evidence_hash": "[h:action]"}


def _adapter(source="public_fixture"):
    return EXEC.FixtureRetrievalAdapter({
        "*": {"source_kind": source, "context": "secret fixture context",
              "expected_answer": "EXPECTED-TOKEN", "confidence": 0.8}
    })


def _valid(result):
    assert not list(VALIDATOR.iter_errors(result))


def test_schema_and_default_off():
    Draft7Validator.check_schema(SCHEMA)
    called = {"n": 0}
    result = GR.regenerate(
        _task(), _action(), {"output_preview": "old"},
        lambda _: called.__setitem__("n", called["n"] + 1),
        retrieval_adapter=_adapter(), model_name="fixture")
    _valid(result)
    assert called["n"] == 0
    assert result["grounded_status"] == "skipped"
    assert result["error_code"] == "execution_disabled"


def test_fixture_context_reaches_model_but_never_result():
    seen = {}

    def model(prompt):
        seen["prompt"] = prompt
        return "The grounded answer is EXPECTED-TOKEN."

    result = GR.regenerate(
        _task(), _action(), {"output_preview": "ungrounded old answer"}, model,
        enabled=True, retrieval_adapter=_adapter(), model_name="fixture-model")
    _valid(result)
    assert "secret fixture context" in seen["prompt"]
    assert result["grounded_status"] == "completed"
    assert result["verifier_verdicts"] == ["pass"]
    assert result["answer_changed"] is True
    serialized = json.dumps(result)
    assert "secret fixture context" not in serialized
    assert "EXPECTED-TOKEN" not in serialized
    assert "ungrounded old answer" not in serialized


def test_non_current_false_positive_never_calls_model():
    called = {"n": 0}

    def model(_):
        called["n"] += 1
        return "EXPECTED-TOKEN"

    result = GR.regenerate(
        _task(category="numeric"), _action(), {"output_preview": "old"}, model,
        enabled=True, retrieval_adapter=_adapter(), model_name="fixture")
    _valid(result)
    assert called["n"] == 0
    assert result["error_code"] == "not_current_info"


def test_grounded_summary_distinguishes_completion_and_quality():
    completed = GR.regenerate(
        _task(), _action(), {"output_preview": "old"},
        lambda _: "EXPECTED-TOKEN", enabled=True,
        retrieval_adapter=_adapter(), model_name="fixture")
    skipped = GR.regenerate(
        _task("n", "numeric"), _action("n"), {"output_preview": "old"},
        lambda _: "must-not-run", enabled=True,
        retrieval_adapter=_adapter(), model_name="fixture")
    summary = GR.build_summary([completed, skipped])
    EXEC.assert_no_text(summary)
    assert summary["grounded_answer_produced"] == 1
    assert summary["deterministically_checked"] == 1
    assert summary["verifier_verdict_distribution"] == {"pass": 1}
    assert summary["retrieval_completion_is_answer_correctness"] is False
    assert summary["fixture_verification_is_real_world_truth"] is False


def test_review_summary_for_four_misses_and_three_false_positives():
    tasks, runtime, actions = [], [], []
    for i in range(4):
        pid = f"m{i}"
        tasks.append({"prompt_id": pid, "task_category": "math",
                      "known_answer": "4", "expression": "2+2"})
        runtime.append({"prompt_id": pid, "output_preview": "5"})
        actions.append({"task_id": pid, "action_type": "checker_needed",
                        "checker_verdict": "fail"})
    for i, category in enumerate(("explain", "explain", "numeric")):
        pid = f"r{i}"
        tasks.append({"prompt_id": pid, "task_category": category})
        actions.append({"task_id": pid, "action_type": "retrieval_needed",
                        "checker_verdict": None})
    review = GR.build_review_summary(tasks, runtime, actions)
    EXEC.assert_no_text(review)
    assert review["m19_arithmetic_miss_candidates"]["reviewed"] == 4
    assert review["m19_arithmetic_miss_candidates"]["confirmed_wrong_candidates"] == 4
    assert review["retrieval_heuristic_false_positives"]["reviewed"] == 3
    assert review["retrieval_heuristic_false_positives"]["category_distribution"] == {
        "explain": 2, "numeric": 1}


def test_retrieval_heuristic_refinement_preserves_explicit_current_info():
    weather = VZ.retrieval_required_heuristic(
        "", prompt="Explain the difference between weather and climate.",
        task_category="explain")
    price = VZ.retrieval_required_heuristic(
        "", prompt="A $120 item has a price discount.", task_category="numeric")
    current = VZ.retrieval_required_heuristic(
        "", prompt="What is the price?", task_category="current_info")
    assert weather["verdict"] == VZ.VERDICT_PASS
    assert price["verdict"] == VZ.VERDICT_PASS
    assert current["verdict"] == VZ.VERDICT_FAIL
