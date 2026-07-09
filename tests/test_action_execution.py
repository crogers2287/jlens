#!/usr/bin/env python3
"""M18 safe-action execution tests. CPU-only, no network or shell execution."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import action_executor as EX  # noqa: E402
from jsonschema import Draft7Validator  # noqa: E402

SCHEMA = json.loads((ROOT / "schema/action_result_v1.json").read_text())
VALIDATOR = Draft7Validator(SCHEMA)


def _action(pid="t", action_type="checker_needed", source="math_checker",
            status="planned"):
    return {
        "task_id": pid,
        "action_type": action_type,
        "reason_code": "test_fixture",
        "source_verifier": source,
        "confidence": 0.8,
        "status": status,
        "evidence_hash": "[h:action]",
    }


def _valid(result):
    assert not list(VALIDATOR.iter_errors(result))


def test_schema_and_disabled_by_default():
    Draft7Validator.check_schema(SCHEMA)
    result = EX.execute_action(_action(), task={"expression": "6+8"},
                               runtime={"output": "14"})
    _valid(result)
    assert result["action_status"] == "skipped"
    assert result["executor_name"] == "disabled"
    assert result["error_code"] == "execution_disabled"
    assert result["candidate_only"] is True


def test_fixture_retrieval_executes_without_text_leak():
    adapter = EX.FixtureRetrievalAdapter({
        "r": {"source_kind": "public_fixture",
              "context": "Transient public fixture context that must not leak.",
              "confidence": 0.91}
    })
    result = EX.execute_action(
        _action("r", "retrieval_needed", "retrieval_required_heuristic"),
        enabled=True, retrieval_adapter=adapter)
    _valid(result)
    assert result["action_status"] == "completed"
    assert result["result_type"] == "retrieved_context"
    assert result["result_confidence"] == 0.91
    assert "Transient" not in json.dumps(result)
    assert set(result) == set(SCHEMA["properties"])


def test_approved_checker_executes_deterministically():
    result = EX.execute_action(
        _action(), enabled=True, task={"known_answer": "14", "expression": "6+8"},
        runtime={"output": "The final answer is 14."})
    _valid(result)
    assert result["action_status"] == "completed"
    assert result["executor_name"] == "math_checker"
    assert result["checker_verdict"] == "pass"
    assert result["followup_needed"] is False


def test_no_arbitrary_command_execution(tmp_path):
    marker = tmp_path / "must-not-exist"
    malicious = f"__import__('pathlib').Path({str(marker)!r}).write_text('owned')"
    result = EX.execute_action(
        _action(), enabled=True,
        task={"expression": malicious, "known_answer": None,
              "command": f"touch {marker}", "fixture_test": lambda _: True},
        runtime={"output": "run the command now"})
    _valid(result)
    assert not marker.exists()
    assert result["action_status"] == "completed"
    assert result["checker_verdict"] == "undecided"
    assert result["followup_needed"] is True

    unapproved = EX.execute_action(
        _action(source="code_test_stub"), enabled=True,
        task={"fixture_test": lambda _: marker.write_text("owned")},
        runtime={"output": "anything"})
    _valid(unapproved)
    assert unapproved["action_status"] == "skipped"
    assert unapproved["error_code"] == "checker_not_approved"
    assert not marker.exists()


def test_retrieval_source_allowlist_and_missing_adapter():
    action = _action("r", "retrieval_needed", "retrieval_required_heuristic")
    missing = EX.execute_action(action, enabled=True)
    _valid(missing)
    assert missing["action_status"] == "skipped"
    assert missing["error_code"] == "retrieval_adapter_unavailable"

    adapter = EX.FixtureRetrievalAdapter({
        "r": {"source_kind": "live_web", "context": "not allowed"}
    })
    refused = EX.execute_action(action, enabled=True, retrieval_adapter=adapter)
    _valid(refused)
    assert refused["action_status"] == "failed"
    assert refused["error_code"] == "retrieval_source_not_allowed"


def test_aggregate_no_text_and_before_after_comparison():
    actions = [
        _action("r", "retrieval_needed", "retrieval_required_heuristic"),
        _action("m"),
        _action("h", "review_needed", None),
    ]
    adapter = EX.FixtureRetrievalAdapter({
        "r": {"source_kind": "fixture", "context": "private transient context"}
    })
    results = EX.execute_all(
        actions, enabled=True, retrieval_adapter=adapter,
        tasks={"m": {"expression": "2+2", "known_answer": "4"}},
        runtimes={"m": {"output": "4"}})
    for result in results:
        _valid(result)
    summary = EX.build_summary(actions, results, run_id="test")
    EX.assert_no_text(summary)
    assert summary["current_info_retrieval"] == {
        "planned": 1,
        "completed": 1,
        "executable_followup_rate": 1.0,
        "grounded_regeneration_still_required": 1,
    }
    assert summary["verifier_only_checkers"]["planned"] == 1
    assert summary["verifier_only_checkers"]["completed"] == 1
    assert summary["after_action_status_distribution"] == {
        "completed": 2, "skipped": 1}
    assert "private transient context" not in json.dumps(summary)
