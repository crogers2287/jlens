#!/usr/bin/env python3
"""M21 HF/safetensors telemetry backend tests. No downloads or real weights."""
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import hf_telemetry_backend as HF  # noqa: E402

SCHEMA = json.loads((ROOT / "schema/hf_telemetry_record_v1.json").read_text())
VALIDATOR = Draft7Validator(SCHEMA)


def _validate(record):
    assert not list(VALIDATOR.iter_errors(record))


def _walk_keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from _walk_keys(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _walk_keys(value)


def test_schema_and_logits_window_metrics():
    Draft7Validator.check_schema(SCHEMA)
    backend = HF.HFTelemetryBackend(top_k=2, high_entropy=0.5, low_confidence=0.8)
    rec = backend.capture(
        "t", [{"logits": [0.0, 1.0, 2.0]},
              {"logits": [2.0, 0.0, 1.0], "selected_token_id": 0}],
        model_kind="dense", input_token_count=4,
        alignment={"auto_outcome": True})
    _validate(rec)
    assert rec["logits"]["status"] == "available"
    assert rec["logits"]["selected_token_id"] == 0
    assert 0 < rec["logits"]["selected_token_probability"] < 1
    assert 0 < rec["logits"]["top_k_mass"] <= 1
    assert 0 <= rec["logits"]["top_k_margin"] <= 1
    assert rec["logits"]["window"]["step_count"] == 2
    assert rec["logits"]["window"]["high_entropy_count"] == 2
    assert rec["logits"]["window"]["low_confidence_count"] == 2
    assert rec["decode_step_count"] == 2
    assert rec["outcome_alignment"]["auto_outcome"] is True


def test_missing_logits_and_hidden_states_are_honest():
    backend = HF.HFTelemetryBackend()
    missing = backend.capture(
        "missing", [{"logits": None}], model_kind="unknown",
        capture_hidden=True)
    _validate(missing)
    assert missing["capture_status"] == "failed"
    assert missing["logits"]["status"] == "missing"
    assert missing["logits"]["entropy"] is None
    assert missing["hidden"] == {
        "status": "missing", "layer_count": None, "vector_norm_mean": None}
    disabled = backend.capture(
        "disabled", [{"logits": [1.0, 0.0], "hidden_states": [[3.0, 4.0]]}],
        model_kind="dense", capture_hidden=False)
    assert disabled["hidden"]["status"] == "disabled"
    enabled = backend.capture(
        "enabled", [{"logits": [1.0, 0.0], "hidden_states": [[3.0, 4.0]]}],
        model_kind="dense", capture_hidden=True)
    assert enabled["hidden"]["status"] == "available"
    assert enabled["hidden"]["layer_count"] == 1
    assert enabled["hidden"]["vector_norm_mean"] == 5.0


def test_dense_not_moe_and_moe_router_features():
    backend = HF.HFTelemetryBackend()
    dense = backend.capture("d", [{"logits": [1.0, 0.0]}], model_kind="dense")
    _validate(dense)
    assert dense["router"]["status"] == "not_moe"
    assert dense["router"]["top_expert_ids"] == []

    moe = backend.capture(
        "m", [
            {"logits": [1.0, 0.0],
             "router_logits": [[4.0, 1.0, 0.0], [0.0, 3.0, 1.0]]},
            {"logits": [0.0, 2.0],
             "router_logits": [[0.0, 1.0, 4.0], [0.0, 3.0, 1.0]]},
        ], model_kind="moe")
    _validate(moe)
    assert moe["router"]["status"] == "available"
    assert moe["router"]["layer_count"] == 2
    assert moe["router"]["top_expert_ids"] == [2, 1]
    assert moe["router"]["windowed_expert_shift"] == 0.5
    assert moe["router"]["router_entropy_mean"] > 0
    assert 0 < moe["router"]["expert_concentration_mean"] <= 1


def test_moe_router_unsupported_is_not_fabricated():
    rec = HF.HFTelemetryBackend().capture(
        "m", [{"logits": [1.0, 0.0]}], model_kind="moe",
        router_supported=False)
    _validate(rec)
    assert rec["router"]["status"] == "unsupported"
    assert rec["router"]["layer_count"] is None
    assert rec["router"]["router_entropy_mean"] is None


def test_loader_refuses_unapproved_or_non_safetensors(tmp_path):
    with pytest.raises(HF.ModelApprovalRequired):
        HF.HFSafetensorsLoader().resolve()
    with pytest.raises(HF.ModelApprovalRequired):
        HF.HFSafetensorsLoader("org/unapproved").resolve()
    empty = tmp_path / "empty-model"; empty.mkdir()
    with pytest.raises(HF.SafetensorsNotFound):
        HF.HFSafetensorsLoader(str(empty)).resolve()
    (empty / "model.safetensors").write_bytes(b"fixture marker, not loaded")
    spec = HF.HFSafetensorsLoader(str(empty)).resolve()
    assert spec.source_kind == "local_path"
    assert spec.local_files_only is True and spec.trust_remote_code is False
    approved = HF.HFSafetensorsLoader(
        "org/approved", approved_model_ids={"org/approved"}).resolve()
    assert approved.source_kind == "approved_model_id"
    assert approved.local_files_only is True


def test_loader_passes_no_download_flags(monkeypatch):
    calls = []

    class Stub:
        @classmethod
        def from_pretrained(cls, ref, **kwargs):
            calls.append((ref, kwargs))
            return cls()

        def eval(self):
            calls.append(("eval", {}))

    monkeypatch.setitem(sys.modules, "transformers", types.SimpleNamespace(
        AutoModelForCausalLM=Stub, AutoTokenizer=Stub))
    loader = HF.HFSafetensorsLoader(
        "org/cached", approved_model_ids={"org/cached"})
    _, _, spec = loader.load()
    assert spec.source_kind == "approved_model_id"
    pretrained = [item for item in calls if item[0] == "org/cached"]
    assert len(pretrained) == 2
    assert all(kwargs == {"local_files_only": True, "trust_remote_code": False}
               for _, kwargs in pretrained)


def test_fixture_summary_schema_no_text_and_backend_separation():
    records = HF.fixture_records()
    assert len(records) == 3
    for record in records:
        _validate(record)
        keys = set(_walk_keys(record))
        assert not ({"prompt", "text", "output", "generated_token_text",
                     "raw_logits", "hidden_states", "router_logits",
                     "model_path"} & keys)
    summary = HF.summarize(records)
    assert summary["weights_loaded"] == 0
    assert summary["logits_status_distribution"] == {"available": 2, "missing": 1}
    assert summary["router_status_distribution"] == {
        "available": 1, "missing": 1, "not_moe": 1}
    assert summary["raw_prompt_output_or_tensor_persisted"] is False
    assert HF.GGUFBackendDescriptor().telemetry_access == "missing"
    assert HF.GGUFBackendDescriptor().record_kind == "auto_outcome_v1"
    assert HF.HFSafetensorsBackendDescriptor().record_kind == \
        "hf_telemetry_record_v1"


def test_repository_tracks_no_model_weights_or_cache_files():
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True,
        text=True).stdout.splitlines()
    forbidden_suffixes = (".safetensors", ".gguf", ".ckpt", ".pt", ".pth")
    forbidden_names = {"pytorch_model.bin", "tf_model.h5", "flax_model.msgpack"}
    bad = [path for path in tracked
           if path.lower().endswith(forbidden_suffixes)
           or Path(path).name.lower() in forbidden_names]
    assert bad == []


def test_top_k_mass_clamped_to_one():
    from hf_telemetry_backend import _logit_stats
    # float32-style rounding can make the top-k probability sum exceed 1.0;
    # the schema caps probabilities at 1, so the stat must clamp (M34 fix)
    probs = [0.5000001, 0.5000001]
    stats = _logit_stats(probs, selected_token_id=0, top_k=2)
    assert stats["top_k_mass"] <= 1.0
