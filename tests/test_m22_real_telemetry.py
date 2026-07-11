#!/usr/bin/env python3
"""M22 conversion/report tests use tiny CPU tensors and perform no downloads."""
import json
import sys
from pathlib import Path

import torch
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import hf_telemetry_backend as HF  # noqa: E402
import m22_real_telemetry as M22  # noqa: E402

SCHEMA = json.loads((ROOT / "schema/hf_telemetry_record_v1.json").read_text())
VALIDATOR = Draft7Validator(SCHEMA)


def _capture(task_id="m19_m_000"):
    return {
        "prompt_id": task_id,
        "input_ids": torch.tensor([1, 2, 3]),
        "decode_steps": [
            {"generated_token_id": 7, "generated_token_text": "private",
             "entropy_final_logits": 1.5, "selected_token_prob": 0.4,
             "top_k": 5, "top_k_mass": 0.8, "top_k_margin": 0.2,
             "router_logits": [torch.tensor([[3.0, 1.0, 0.0]]),
                               torch.tensor([[0.0, 2.0, 1.0]])]},
            {"generated_token_id": 8, "generated_token_text": "private2",
             "entropy_final_logits": 0.5, "selected_token_prob": 0.7,
             "top_k": 5, "top_k_mass": 0.9, "top_k_margin": 0.5,
             "router_logits": [torch.tensor([[0.0, 1.0, 3.0]]),
                               torch.tensor([[0.0, 2.0, 1.0]])]},
        ],
    }


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def test_precomputed_real_capture_is_schema_valid_and_aggregate_only():
    backend = HF.HFTelemetryBackend(
        model_ref="/private/model/path", source_kind="local_path")
    record = M22.record_from_capture(
        _capture(), backend,
        {"auto_outcome": True, "action_result": True})
    assert not list(VALIDATOR.iter_errors(record))
    assert record["logits"]["status"] == "available"
    assert record["logits"]["window"]["step_count"] == 2
    assert record["logits"]["top_k_mass"] == 0.9
    assert record["hidden"]["status"] == "disabled"
    assert record["router"]["status"] == "available"
    assert record["router"]["layer_count"] == 2
    assert record["router"]["windowed_expert_shift"] == 0.5
    keys = set(_walk_keys(record))
    assert not ({"prompt", "text", "output", "generated_token_text",
                 "router_logits", "model_path", "input_ids"} & keys)
    assert "/private/model/path" not in json.dumps(record)


def test_precomputed_missing_and_router_degraded_states_are_honest():
    backend = HF.HFTelemetryBackend(model_ref="x", source_kind="local_path")
    missing = backend.capture_precomputed("x", [], model_kind="moe")
    assert missing["capture_status"] == "failed"
    assert missing["logits"]["status"] == "missing"
    assert missing["router"]["status"] == "missing"
    unsupported = backend.capture_precomputed(
        "x", M22.aggregate_steps(_capture()), model_kind="moe",
        router_supported=False)
    assert unsupported["logits"]["status"] == "available"
    assert unsupported["router"]["status"] == "unsupported"


def test_selected_batch_is_fixed_shared_eight(tmp_path):
    source = tmp_path / "source.jsonl"
    rows = [{"prompt_id": task_id, "prompt": f"private-{i}",
             "task_category": "math"}
            for i, task_id in enumerate(reversed(M22.SELECTED_TASK_IDS))]
    source.write_text("".join(json.dumps(row) + "\n" for row in rows))
    out = tmp_path / "selected.jsonl"
    selected = M22.prepare_selected_batch(source, out)
    assert [row["prompt_id"] for row in selected] == list(M22.SELECTED_TASK_IDS)
    assert len(read := out.read_text().splitlines()) == 8
    assert all("private-" in line for line in read)


def test_alignment_flags_use_existing_candidate_records():
    alignment_for, labels = M22.build_alignment(
        [{"prompt_id": "a", "auto_outcome": {"auto_judged": True}}],
        [{"task_id": "a", "action_type": "checker_needed"}],
        [{"task_id": "a", "grounded_status": "completed"}],
        [{"prompt_id": "a", "review_meta": {"reviewer": "operator"}}])
    assert alignment_for("a") == {
        "auto_outcome": True, "action_result": True,
        "grounded_result": True, "reviewed_outcome": True}
    assert labels["a"] == "checker_needed"


def test_public_reports_have_groups_but_no_ids_text_paths_or_tensors():
    backend = HF.HFTelemetryBackend(model_ref="/secret", source_kind="local_path")
    records = []
    labels = {}
    meta = {}
    for i, action in enumerate(("checker_needed", "retrieval_needed",
                                "review_needed", "no_action")):
        task_id = f"task-{i}"
        records.append(M22.record_from_capture(
            _capture(task_id), backend, {"auto_outcome": True}))
        labels[task_id] = action
        meta[task_id] = {"task_category": "fixture_category"}
    summary, comparison = M22.build_public_reports(records, meta, labels)
    assert summary["weights_loaded"] == 1
    assert summary["cross_model_alignment"] is True
    assert summary["router_status_distribution"] == {"available": 4}
    assert comparison["need_comparisons"]["checker"]["needed"]["n"] == 1
    assert comparison["predictive_value_claimed"] is False
    assert comparison["within_model_error_prediction_tested"] is False
    public = json.dumps([summary, comparison])
    assert not any(task_id in public for task_id in meta)
    assert "/secret" not in public
    keys = set(_walk_keys([summary, comparison]))
    assert not ({"prompt", "output", "task_id", "model_path",
                 "router_logits", "hidden_states"} & keys)


def test_aggregate_steps_clamps_top_k_mass():
    from m22_real_telemetry import aggregate_steps
    # captures written before the capture-side clamp can carry float32
    # rounding above 1.0; the read side must clamp so frozen-schema
    # validation holds without recapturing (M34 fix)
    capture = {"decode_steps": [
        {"generated_token_id": 1, "top_k_mass": 1.0000001192092896},
        {"generated_token_id": 2, "top_k_mass": None},
    ]}
    steps = aggregate_steps(capture)
    assert steps[0]["top_k_mass"] == 1.0
    assert steps[1]["top_k_mass"] is None
