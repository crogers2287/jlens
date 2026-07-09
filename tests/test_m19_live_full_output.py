#!/usr/bin/env python3
"""M19 transient full-output action-run tests. CPU-only, no network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import action_executor as EXEC  # noqa: E402
import gen_m19_batch as GEN  # noqa: E402
import m19_reports as REPORT  # noqa: E402
import run_agents_a1_shadow_batch as RUN  # noqa: E402
import validate_task_metadata as META  # noqa: E402
from jsonschema import Draft7Validator  # noqa: E402

AUTO_SCHEMA = json.loads((ROOT / "schema/auto_outcome_v1.json").read_text())
ACTION_SCHEMA = json.loads((ROOT / "schema/action_result_v1.json").read_text())


def _cfg(task_path):
    return {
        "endpoint": {"model": "fixture", "alias": "fixture"},
        "task_sources": [{"path": str(task_path), "kind": "public_fixture"}],
        "batch": {"size": 1, "cap": 500},
        "verifiers": {"self_consistency_samples": 1},
        "escalation": {},
        "actions": {"enabled": True},
        "resume": {"enabled": True},
        "run": {"deterministic": True, "mode": "dry-run"},
    }


def test_m19_batch_is_deterministic_500_and_metadata_clean():
    a, b = GEN.build(), GEN.build()
    assert a == b and len(a) == 500
    assert len({r["prompt_id"] for r in a}) == 500
    assert META.validate(a) == {}
    assert sum(r["task_category"] == "current_info" for r in a) == 20
    assert sum(r["task_category"] == "math" for r in a) == 360


def test_transient_full_output_checker_no_raw_persistence_and_resume(tmp_path):
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(json.dumps({
        "prompt_id": "m", "prompt": "Compute 6+8", "task_category": "math",
        "known_answer": "14", "expression": "6+8"}) + "\n")
    runtime, actions, meta = (tmp_path / "runtime.jsonl", tmp_path / "actions.jsonl",
                              tmp_path / "meta.json")
    calls = {"n": 0}
    secret_tail = "FULL-OUTPUT-ONLY final answer 14"

    def model(_):
        calls["n"] += 1
        return "x" * 300 + secret_tail

    first = RUN.run_batch(
        _cfg(tasks), model, runtime, meta, source_path=str(tasks),
        validator=Draft7Validator(AUTO_SCHEMA), action_out_path=actions,
        action_validator=Draft7Validator(ACTION_SCHEMA))
    assert calls["n"] == 1 and first["n_action_completed_this_run"] == 1
    rec = json.loads(runtime.read_text())
    result = json.loads(actions.read_text())
    assert secret_tail not in runtime.read_text() + actions.read_text()
    assert len(rec["output_preview"]) <= 161
    assert result["checker_verdict"] == "pass"
    assert result["executor_name"] == "math_checker"

    second = RUN.run_batch(
        _cfg(tasks), model, runtime, meta, source_path=str(tasks),
        validator=Draft7Validator(AUTO_SCHEMA), action_out_path=actions,
        action_validator=Draft7Validator(ACTION_SCHEMA))
    assert calls["n"] == 1
    assert second["n_already_done_skipped"] == 1
    assert len(runtime.read_text().splitlines()) == 1
    assert len(actions.read_text().splitlines()) == 1


def test_action_execution_is_explicit_opt_in(tmp_path):
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(json.dumps({"prompt_id": "x", "prompt": "hello"}) + "\n")
    cfg = _cfg(tasks); cfg["actions"]["enabled"] = False
    runtime = tmp_path / "runtime.jsonl"
    meta = RUN.run_batch(cfg, lambda _: "output", runtime,
                         source_path=str(tasks))
    assert meta["action_execution_enabled"] is False
    assert meta["n_action_completed_this_run"] == 0
    assert runtime.exists()


def test_retrieval_stays_fixture_only_with_wildcard():
    adapter = EXEC.FixtureRetrievalAdapter({
        "*": {"source_kind": "public_fixture", "context": "transient"}
    })
    action = {"task_id": "any", "action_type": "retrieval_needed",
              "status": "planned", "evidence_hash": "[h:a]"}
    result = EXEC.execute_action(action, enabled=True, retrieval_adapter=adapter)
    assert result["action_status"] == "completed"
    assert result["executor_name"] == "fixture_retrieval"
    assert "transient" not in json.dumps(result)


def test_aggregate_reports_no_text_and_compare_baselines():
    record = {"prompt_id": "m", "auto_outcome": {
        "auto_needed_retrieval": False, "auto_needed_checker": True,
        "verifier_names": ["math_checker"], "verifier_confidence": 0.9,
        "escalate_for_review": False}}
    action = {"task_id": "m", "action_type": "checker_needed",
              "status": "planned", "source_verifier": "math_checker",
              "evidence_hash": "[h:a]"}
    result = EXEC.execute_action(action, enabled=True,
                                 task={"expression": "2+2"},
                                 runtime={"output": "4"})
    act = REPORT.action_summary([record], [result], "test")
    assert act["verifier_only_checkers"]["checker_input_mode"] == \
        "full_transient_output"
    assert act["transient_full_output_persisted"] is False
    run = {"n_completed": 1, "n_tasks": 1, "escalation_rate": 0.0}
    old_run = {"n_completed": 261, "escalation_rate": 0.073}
    old_act = {"n_actions": 261,
               "after_action_status_distribution": {"completed": 172},
               "verifier_only_checkers": {"verdict_distribution": {"fail": 90}},
               "current_info_retrieval": {"completed": 12}}
    comp = REPORT.baseline_comparison(run, act, old_run, old_act)
    EXEC.assert_no_text(act); EXEC.assert_no_text(comp)
    assert comp["checker_verdicts"]["m18_interpretation"] == \
        "invalid_from_truncated_previews"
    assert comp["checker_verdicts"]["m19_interpretation"] == \
        "valid_for_full_transient_execution_input"


def test_report_separates_current_info_from_retrieval_false_positives():
    records = [
        {"prompt_id": "c", "task_category": "current_info", "auto_outcome": {
            "auto_needed_retrieval": True, "auto_needed_checker": False,
            "verifier_names": ["retrieval_required_heuristic"],
            "verifier_confidence": 0.7, "escalate_for_review": False}},
        {"prompt_id": "n", "task_category": "numeric", "auto_outcome": {
            "auto_needed_retrieval": True, "auto_needed_checker": False,
            "verifier_names": ["retrieval_required_heuristic"],
            "verifier_confidence": 0.7, "escalate_for_review": False}},
    ]
    adapter = EXEC.FixtureRetrievalAdapter({
        "*": {"source_kind": "fixture", "context": "transient"}
    })
    actions = [{"task_id": pid, "action_type": "retrieval_needed",
                "status": "planned", "evidence_hash": "[h:a]"}
               for pid in ("c", "n")]
    results = [EXEC.execute_action(a, enabled=True, retrieval_adapter=adapter)
               for a in actions]
    summary = REPORT.action_summary(records, results, "test")
    assert summary["current_info_retrieval"]["planned"] == 1
    assert summary["retrieval_non_current_info"]["planned"] == 1
    assert summary["retrieval_non_current_info"]["category_distribution"] == {
        "numeric": 1}
