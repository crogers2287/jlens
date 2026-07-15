"""Q35Q Phase 0 CPU-only validator tests: fail-closed admission, architecture,
layer, device-map, quantization, privacy, and artifact-schema behavior.

No model loading, no GPU, no network, no private data — synthetic fixtures only.
"""
import os
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_phase0 import (
    QWEN35_35B_A3B_ARCH,
    FINAL_RESIDUAL_LAYER,
    Q35QBlock,
    VJPGateArtifact,
    atomic_write_json,
    canonical_quant_config,
    detect_inference_only,
    quant_configs_equal,
    scan_aggregate_only,
    sha256_file,
    validate_architecture,
    validate_device_map,
    validate_layers,
    validate_revision,
    verify_file_manifest,
)

GOOD_REV = "a" * 40


# ---------- revision ----------

def test_immutable_revision_accepted():
    assert validate_revision(GOOD_REV) == GOOD_REV


@pytest.mark.parametrize("bad", ["main", "v1.0", "A" * 40, "a" * 39, "", 123, None])
def test_mutable_or_malformed_revision_blocked(bad):
    with pytest.raises(Q35QBlock):
        validate_revision(bad)


# ---------- file manifest ----------

def test_manifest_pass_and_mismatch(tmp_path):
    f = tmp_path / "model.safetensors"
    f.write_bytes(b"synthetic-weights")
    manifest = {"model.safetensors": sha256_file(str(f))}
    assert verify_file_manifest(str(tmp_path), manifest)["result"] == "pass"

    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path), {"model.safetensors": "0" * 64})
    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path), {"missing.bin": "0" * 64})
    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path), {})


# ---------- architecture ----------

def test_architecture_exact_match():
    assert validate_architecture(dict(QWEN35_35B_A3B_ARCH))["result"] == "pass"


def test_architecture_mismatch_blocked():
    cfg = dict(QWEN35_35B_A3B_ARCH)
    cfg["num_routed_experts"] = 128
    with pytest.raises(Q35QBlock):
        validate_architecture(cfg)


def test_vision_encoder_blocked():
    cfg = dict(QWEN35_35B_A3B_ARCH)
    cfg["vision_config"] = {"depth": 32}
    with pytest.raises(Q35QBlock):
        validate_architecture(cfg)


# ---------- layers ----------

def test_layers_default_pass():
    out = validate_layers(20)
    assert out["source"] == 20 and out["target"] == FINAL_RESIDUAL_LAYER


@pytest.mark.parametrize("src,tgt", [(39, 39), (40, 39), (-1, 39), (20, 38)])
def test_layers_blocked(src, tgt):
    with pytest.raises(Q35QBlock):
        validate_layers(src, tgt)


def test_layers_reject_bool():
    with pytest.raises(Q35QBlock):
        validate_layers(True)


# ---------- device map ----------

def test_device_map_explicit_pass():
    dm = {"model.embed": 0, "model.layers.0": 0, "model.layers.39": 1, "lm_head": 1}
    out = validate_device_map(dm)
    assert out["result"] == "pass" and out["devices"] == [0, 1]


def test_device_map_auto_blocked():
    with pytest.raises(Q35QBlock):
        validate_device_map("auto")


def test_device_map_offload_blocked():
    with pytest.raises(Q35QBlock):
        validate_device_map({"model.layers.0": "cpu"})
    with pytest.raises(Q35QBlock):
        validate_device_map({"model.layers.0": "disk"})


def test_device_map_bad_gpu_blocked():
    with pytest.raises(Q35QBlock):
        validate_device_map({"model.layers.0": 2})


# ---------- quantization config ----------

def test_quant_config_canonical_and_equality():
    a = {"bits": 4, "group_size": 128, "sym": True}
    b = {"sym": True, "group_size": 128, "bits": 4}
    assert canonical_quant_config(a) == canonical_quant_config(b)
    assert quant_configs_equal(a, b)
    assert not quant_configs_equal(a, {**a, "group_size": 64})


def test_detect_inference_only():
    assert detect_inference_only(["moe_wna16", "eager"]) == ["moe_wna16"]
    assert detect_inference_only(["vLLM/0.24", "SGLang"]) == ["sglang", "vllm"]
    assert detect_inference_only(["eager", "transformers"]) == []


# ---------- privacy scan ----------

def test_scan_aggregate_only_pass():
    assert scan_aggregate_only({"result": "pass", "count": 8, "flags": [True, False]})


@pytest.mark.parametrize("bad", [
    {"prompts": ["hi"]},
    {"nested": {"hidden": [0.1, 0.2]}},
    {"vjp_values": [1.0, 2.0]},
    {"path": "/mnt/thor/x"},
])
def test_scan_aggregate_only_forbidden_key(bad):
    with pytest.raises(Q35QBlock):
        scan_aggregate_only(bad)


def test_scan_aggregate_only_raw_array_blocked():
    with pytest.raises(Q35QBlock):
        scan_aggregate_only({"metric": list(range(65))})
    # small lists are fine
    assert scan_aggregate_only({"metric": list(range(8))})


# ---------- VJP gate artifact ----------

def _good_gate(**kw):
    base = dict(
        path_name="gptq", vjp_non_none=True, vjp_nonzero=True, vjp_finite=True,
        repeat_stable=True, weight_grads_absent=True, token_parity_exact=True,
        logit_parity_within_tol=True, no_offload=True, identities_match=True,
        peak_gib_per_gpu=21.0, peak_gib_total=42.0,
    )
    base.update(kw)
    return VJPGateArtifact(**base)


def test_vjp_gate_pass_outcome():
    g = _good_gate()
    assert g.passed()
    assert g.outcome() == "q35q_gptq_exact_vjp_passed"
    assert scan_aggregate_only(g.gates())


@pytest.mark.parametrize("field", [
    "vjp_non_none", "vjp_nonzero", "vjp_finite", "repeat_stable",
    "weight_grads_absent", "token_parity_exact", "logit_parity_within_tol",
    "no_offload", "identities_match",
])
def test_vjp_gate_any_false_fails(field):
    g = replace(_good_gate(), **{field: False})
    assert not g.passed()
    assert g.outcome() is None


def test_vjp_gate_memory_ceilings():
    assert not _good_gate(peak_gib_per_gpu=23.1).passed()
    assert not _good_gate(peak_gib_total=46.1).passed()
    assert _good_gate(peak_gib_per_gpu=23.0, peak_gib_total=46.0).passed()


def test_vjp_gate_nf4_outcome():
    assert _good_gate(path_name="nf4").outcome() == "q35q_nf4_exact_vjp_passed"


def test_vjp_gate_unknown_path_blocked():
    with pytest.raises(Q35QBlock):
        _good_gate(path_name="awq").outcome()


# ---------- atomic checkpoint ----------

def test_atomic_write_json_roundtrip(tmp_path):
    import json
    p = tmp_path / "ckpt" / "state.json"
    atomic_write_json(str(p), {"seq": 3, "result": "pass"})
    assert json.loads(p.read_text())["seq"] == 3
    # no leftover temp files
    assert [x.name for x in (tmp_path / "ckpt").iterdir()] == ["state.json"]


def test_atomic_write_json_rejects_private(tmp_path):
    p = tmp_path / "state.json"
    with pytest.raises(Q35QBlock):
        atomic_write_json(str(p), {"hidden": [0.1, 0.2, 0.3]})
    assert not p.exists()
