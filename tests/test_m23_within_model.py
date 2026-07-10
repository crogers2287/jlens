#!/usr/bin/env python3
"""M23 same-run tests use CPU fixtures only and perform no network/model load."""
import json
import sys
from pathlib import Path

import torch
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import action_executor as EXEC  # noqa: E402
import hf_telemetry_backend as HF  # noqa: E402
import m23_within_model as M23  # noqa: E402


def _capture(task_id="m19_m_000", output="14"):
    return {
        "prompt_id": task_id,
        "input_ids": torch.tensor([1, 2, 3]),
        "generated_output": output,
        "router_logits": [torch.tensor([[1.0, 0.0]])],
        "decode_steps": [
            {"generated_token_id": 7, "generated_token_text": "private",
             "entropy_final_logits": 1.5, "selected_token_prob": 0.4,
             "top_k": 5, "top_k_mass": 0.8, "top_k_margin": 0.2,
             "router_logits": [torch.tensor([3.0, 1.0, 0.0])]},
            {"generated_token_id": 8, "generated_token_text": "private2",
             "entropy_final_logits": 0.5, "selected_token_prob": 0.7,
             "top_k": 5, "top_k_mass": 0.9, "top_k_margin": 0.5,
             "router_logits": [torch.tensor([0.0, 1.0, 3.0])]},
        ],
    }


def _backend():
    return HF.HFTelemetryBackend(model_ref="/private/model", source_kind="local_path")


def _walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_manifest_is_predeclared_balanced_and_resolves_public_ids(tmp_path):
    manifest, mapping = M23.load_manifest(ROOT / "data/prompts/m23_manifest.json")
    assert manifest["n_tasks"] == 32 and len(mapping) == 32
    assert {group: list(mapping.values()).count(group) for group in set(mapping.values())} == {
        "checker_candidate": 8, "retrieval_candidate": 8,
        "review_candidate": 8, "no_action_control": 8}
    selected = M23.prepare_selected_batch(
        ROOT / "data/prompts/m23_manifest.json",
        ROOT / "data/prompts/agents_a1_m19_batch.jsonl",
        tmp_path / "private.jsonl")
    assert len(selected) == 32
    assert all(row["m23_predeclared_group"] == mapping[row["prompt_id"]]
               for row in selected)


def test_same_capture_drives_qwen_telemetry_and_full_output_checker():
    secret_tail = "FULL-OUTPUT-ONLY final answer 14"
    output = "x" * 300 + secret_tail
    task = {"prompt_id": "m", "prompt": "Compute 6+8",
            "task_category": "math", "known_answer": "14",
            "expression": "6+8"}
    rows = M23.process_same_capture(
        task, _capture("m", output), _backend(),
        retrieval_adapter=EXEC.FixtureRetrievalAdapter({
            "*": {"source_kind": "fixture", "context": "private"}}))
    telemetry, runtime, action, result = rows
    assert telemetry["task_id"] == runtime["prompt_id"] == action["task_id"] == \
        result["task_id"] == "m"
    assert runtime["telemetry_missing"] is False
    assert runtime["feature_source"] == "hf_telemetry_record_v1"
    assert secret_tail not in json.dumps([runtime, action, result, telemetry])
    assert result["checker_verdict"] == "pass"
    assert result["executor_name"] == "math_checker"
    assert telemetry["logits"]["status"] == "available"
    assert telemetry["router"]["status"] == "available"
    for name, row in zip(("telemetry", "runtime", "action", "result"), rows):
        schema_name = {
            "telemetry": "hf_telemetry_record_v1.json",
            "runtime": "auto_outcome_v1.json",
            "action": "action_record_v1.json",
            "result": "action_result_v1.json"}[name]
        schema = json.loads((ROOT / "schema" / schema_name).read_text())
        assert not list(Draft7Validator(schema).iter_errors(row))


def test_capture_completion_supports_resume_and_invalid_detection(tmp_path):
    tasks = [{"prompt_id": "good"}, {"prompt_id": "bad"},
             {"prompt_id": "missing"}]
    torch.save({"router_logits": [torch.tensor([1.0])]}, tmp_path / "good.pt")
    (tmp_path / "bad.pt").write_bytes(b"corrupt")
    status = M23.capture_completion(tmp_path, tasks)
    assert status == {"complete": ["good"],
                      "missing_or_invalid": ["bad", "missing"]}


def test_missing_decode_telemetry_is_honestly_failed():
    record = _backend().capture_precomputed(
        "missing", [], model_kind="moe", alignment={"auto_outcome": True})
    assert record["capture_status"] == "failed"
    assert record["logits"]["status"] == "missing"
    assert record["router"]["status"] == "missing"


def test_public_same_run_reports_effects_and_no_private_fields():
    backend = _backend()
    telemetry, runtimes, actions, results, tasks = [], [], [], [], []
    action_types = (["checker_needed"] * 8 + ["retrieval_needed"] * 8
                    + ["review_needed"] * 8 + ["no_action"] * 8)
    groups = (["checker_candidate"] * 8 + ["retrieval_candidate"] * 8
              + ["review_candidate"] * 8 + ["no_action_control"] * 8)
    for i, (action_type, group) in enumerate(zip(action_types, groups)):
        task_id = f"private-id-{i}"
        capture = _capture(task_id)
        for step in capture["decode_steps"]:
            step["entropy_final_logits"] += i / 100
        telemetry.append(M23.record_from_capture(
            capture, backend, {"auto_outcome": True, "action_result": True}))
        runtimes.append({"prompt_id": task_id, "auto_outcome": {
            "auto_was_wrong": i % 2 == 0}})
        actions.append({"task_id": task_id, "action_type": action_type})
        verdict = ("fail" if i < 4 else "pass") if i < 8 else None
        results.append({"task_id": task_id, "action_status": "completed",
                        "checker_verdict": verdict})
        tasks.append({"prompt_id": task_id, "m23_predeclared_group": group})
    summary, alignment = M23.build_public_reports(
        telemetry, runtimes, actions, results, tasks)
    assert summary["within_model_alignment"] is True
    assert summary["cross_model_alignment"] is False
    assert summary["n_records"] == 32
    assert summary["decode_cap_tokens"] == 64
    assert summary["decode_cap_reached_count"] == 0
    assert summary["checker_outputs_reached_eos_before_cap"] is True
    effect = alignment["actual_need_comparisons"]["checker"]["effects"][
        "decode_window_entropy"]
    assert effect["status"] == "descriptive_only"
    assert len(effect["bootstrap_mean_difference_95pct"]) == 2
    checker = alignment["checker_pass_vs_fail"]["effects"]["router_entropy"]
    assert checker["status"] == "descriptive_only"
    public = json.dumps([summary, alignment])
    assert "private-id-" not in public and "/private/model" not in public
    assert not ({"task_id", "prompt", "output", "generated_output",
                 "generated_token_text", "router_logits", "model_path"}
                & set(_walk([summary, alignment])))
