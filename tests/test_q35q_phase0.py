"""Q35Q Phase 0 CPU-only validator tests: fail-closed admission, architecture,
layer, device-map, quantization, privacy, and artifact-schema behavior.

No model loading, no GPU, no network, no private data — synthetic fixtures only.
"""
import math
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
REQUIRED_MODULES = (
    "model.embed",
    "model.layers.0",
    "model.layers.39",
    "lm_head",
)


# ---------- revision ----------

def test_immutable_revision_accepted():
    assert validate_revision(GOOD_REV) == GOOD_REV


@pytest.mark.parametrize("bad", ["main", "v1.0", "A" * 40, "a" * 39, "", 123, None])
def test_mutable_or_malformed_revision_blocked(bad):
    with pytest.raises(Q35QBlock):
        validate_revision(bad)


# ---------- file manifest ----------

def test_manifest_pass_and_mismatch(tmp_path):
    artifact = tmp_path / "model.safetensors"
    artifact.write_bytes(b"synthetic-weights")
    manifest = {"model.safetensors": sha256_file(str(artifact))}
    assert verify_file_manifest(str(tmp_path), manifest)["result"] == "pass"

    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path), {"model.safetensors": "0" * 64})
    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path), {"missing.bin": "0" * 64})
    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path), {})


@pytest.mark.parametrize("rel", ["../outside.bin", "..", ".", "", "/tmp/outside.bin"])
def test_manifest_path_escape_blocked(tmp_path, rel):
    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path), {rel: "0" * 64})


@pytest.mark.parametrize("digest", ["A" * 64, "0" * 63, "g" * 64, 123, None])
def test_manifest_malformed_digest_blocked(tmp_path, digest):
    artifact = tmp_path / "model.safetensors"
    artifact.write_bytes(b"synthetic-weights")
    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path), {"model.safetensors": digest})


def test_manifest_symlink_escape_blocked(tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.bin"
    outside.write_bytes(b"outside")
    link = tmp_path / "linked.bin"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    with pytest.raises(Q35QBlock):
        verify_file_manifest(
            str(tmp_path), {"linked.bin": sha256_file(str(outside))}
        )


def test_manifest_invalid_root_blocked(tmp_path):
    with pytest.raises(Q35QBlock):
        verify_file_manifest(str(tmp_path / "missing"), {"x": "0" * 64})


# ---------- architecture ----------

def test_architecture_exact_match():
    assert validate_architecture(dict(QWEN35_35B_A3B_ARCH))["result"] == "pass"


def test_architecture_mismatch_blocked():
    cfg = dict(QWEN35_35B_A3B_ARCH)
    cfg["num_routed_experts"] = 128
    with pytest.raises(Q35QBlock):
        validate_architecture(cfg)


def test_architecture_non_dict_blocked():
    with pytest.raises(Q35QBlock):
        validate_architecture(None)


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

def test_device_map_explicit_complete_pass():
    device_map = {
        "model.embed": 0,
        "model.layers.0": 0,
        "model.layers.39": 1,
        "lm_head": 1,
    }
    out = validate_device_map(device_map, required_modules=REQUIRED_MODULES)
    assert out["result"] == "pass"
    assert out["devices"] == [0, 1]
    assert out["required_modules_checked"] == len(REQUIRED_MODULES)


def test_device_map_auto_blocked():
    with pytest.raises(Q35QBlock):
        validate_device_map("auto", required_modules=REQUIRED_MODULES)


def test_device_map_required_inventory_mandatory():
    with pytest.raises(Q35QBlock):
        validate_device_map({"model.layers.0": 0})


def test_device_map_missing_required_module_blocked():
    with pytest.raises(Q35QBlock):
        validate_device_map(
            {"model.embed": 0, "model.layers.0": 0},
            required_modules=REQUIRED_MODULES,
        )


def test_device_map_offload_blocked():
    for target in ("cpu", "disk", "meta"):
        with pytest.raises(Q35QBlock):
            validate_device_map(
                {
                    "model.embed": 0,
                    "model.layers.0": target,
                    "model.layers.39": 1,
                    "lm_head": 1,
                },
                required_modules=REQUIRED_MODULES,
            )


@pytest.mark.parametrize("bad_device", [2, True, "cuda:0", None])
def test_device_map_bad_gpu_blocked(bad_device):
    with pytest.raises(Q35QBlock):
        validate_device_map(
            {
                "model.embed": 0,
                "model.layers.0": bad_device,
                "model.layers.39": 1,
                "lm_head": 1,
            },
            required_modules=REQUIRED_MODULES,
        )


def test_device_map_invalid_allowed_devices_blocked():
    with pytest.raises(Q35QBlock):
        validate_device_map(
            {module: 0 for module in REQUIRED_MODULES},
            allowed_devices=(0, True),
            required_modules=REQUIRED_MODULES,
        )


# ---------- quantization config ----------

def test_quant_config_canonical_and_equality():
    first = {"bits": 4, "group_size": 128, "sym": True}
    second = {"sym": True, "group_size": 128, "bits": 4}
    assert canonical_quant_config(first) == canonical_quant_config(second)
    assert quant_configs_equal(first, second)
    assert not quant_configs_equal(first, {**first, "group_size": 64})


@pytest.mark.parametrize("bad", [None, [], {"scale": math.nan}, {"scale": math.inf}])
def test_quant_config_invalid_blocked(bad):
    with pytest.raises(Q35QBlock):
        canonical_quant_config(bad)


def test_detect_inference_only():
    assert detect_inference_only(["moe_wna16", "eager"]) == ["moe_wna16"]
    assert detect_inference_only(["vLLM/0.24", "SGLang"]) == ["sglang", "vllm"]
    assert detect_inference_only(["eager", "transformers"]) == []


@pytest.mark.parametrize("bad", ["vllm", None, [1, "eager"]])
def test_detect_inference_only_invalid_input_blocked(bad):
    with pytest.raises(Q35QBlock):
        detect_inference_only(bad)


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
    assert scan_aggregate_only({"metric": list(range(8))})


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_scan_aggregate_only_nonfinite_blocked(value):
    with pytest.raises(Q35QBlock):
        scan_aggregate_only({"metric": value})


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
    gate = _good_gate()
    assert gate.passed()
    assert gate.outcome() == "q35q_gptq_exact_vjp_passed"
    assert scan_aggregate_only(gate.gates())


@pytest.mark.parametrize("field", [
    "vjp_non_none", "vjp_nonzero", "vjp_finite", "repeat_stable",
    "weight_grads_absent", "token_parity_exact", "logit_parity_within_tol",
    "no_offload", "identities_match",
])
def test_vjp_gate_any_false_fails(field):
    gate = replace(_good_gate(), **{field: False})
    assert not gate.passed()
    assert gate.outcome() is None


@pytest.mark.parametrize("field", [
    "vjp_non_none", "vjp_nonzero", "vjp_finite", "repeat_stable",
    "weight_grads_absent", "token_parity_exact", "logit_parity_within_tol",
    "no_offload", "identities_match",
])
@pytest.mark.parametrize("bad_value", ["false", 1, 0, None])
def test_vjp_gate_truthy_or_nonboolean_blocked(field, bad_value):
    with pytest.raises(Q35QBlock):
        _good_gate(**{field: bad_value})


def test_vjp_gate_memory_ceilings():
    assert not _good_gate(peak_gib_per_gpu=23.1).passed()
    assert not _good_gate(peak_gib_total=46.1).passed()
    assert _good_gate(peak_gib_per_gpu=23.0, peak_gib_total=46.0).passed()


@pytest.mark.parametrize("field", ["peak_gib_per_gpu", "peak_gib_total"])
@pytest.mark.parametrize("bad_value", [-0.1, math.nan, math.inf, -math.inf, True, "21"])
def test_vjp_gate_invalid_memory_blocked(field, bad_value):
    with pytest.raises(Q35QBlock):
        _good_gate(**{field: bad_value})


def test_vjp_gate_nf4_outcome():
    assert _good_gate(path_name="nf4").outcome() == "q35q_nf4_exact_vjp_passed"


def test_vjp_gate_unknown_path_blocked():
    with pytest.raises(Q35QBlock):
        _good_gate(path_name="awq")


# ---------- atomic checkpoint ----------

def test_atomic_write_json_roundtrip(tmp_path):
    import json
    path = tmp_path / "ckpt" / "state.json"
    atomic_write_json(str(path), {"seq": 3, "result": "pass"})
    assert json.loads(path.read_text())["seq"] == 3
    assert [item.name for item in (tmp_path / "ckpt").iterdir()] == ["state.json"]


def test_atomic_write_json_rejects_private(tmp_path):
    path = tmp_path / "state.json"
    with pytest.raises(Q35QBlock):
        atomic_write_json(str(path), {"hidden": [0.1, 0.2, 0.3]})
    assert not path.exists()


def test_atomic_write_json_rejects_nonfinite(tmp_path):
    path = tmp_path / "state.json"
    with pytest.raises(Q35QBlock):
        atomic_write_json(str(path), {"metric": math.nan})
    assert not path.exists()
