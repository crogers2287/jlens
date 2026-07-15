"""Q35Q artifact-admission builder tests.

Synthetic metadata only; no model, GPU, network, or private data.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_phase0 import QWEN35_35B_A3B_ARCH, scan_aggregate_only
from q35q_admission import (
    ADMISSION_BLOCKED,
    ADMISSION_READY,
    Q35QAdmissionBlock,
    admission_outcome,
    build_admission_record,
    verify_manifest_digest,
)

H = "a" * 64
GOOD_REV = "b" * 40
REQUIRED_MODULES = (
    "model.embed_tokens",
    "model.layers.0",
    "model.layers.39",
    "lm_head",
)


def good_meta(**over):
    meta = dict(
        repo_id="Org/Model-GPTQ-Int4",
        revision=GOOD_REV,
        license="apache-2.0",
        lineage="qwen3.5-35b-a3b-base",
        config=dict(QWEN35_35B_A3B_ARCH),
        tokenizer_id="tok:" + H,
        generation_id="gen:" + H,
        custom_code_id="code:" + H,
        weight_manifest={
            "model-00001-of-00002.safetensors": H,
            "model-00002-of-00002.safetensors": "c" * 64,
        },
        param_count_text_only=35_000_000_000,
        omitted_modules=["visual.encoder", "mtp.head"],
        toolchain={
            "transformers": "4.99",
            "accelerate": "1.0",
            "torch": "2.5",
            "cuda": "12.4",
            "driver": "550.x",
            "backend": "gptqmodel",
            "kernel": "eager",
        },
        quant={
            "quant_type": "gptq",
            "group_size": 128,
            "compute_dtype": "float16",
            "storage_dtype": "int4",
        },
        device_map={
            "model.embed_tokens": 0,
            "model.layers.0": 0,
            "model.layers.39": 1,
            "lm_head": 1,
        },
        required_modules=REQUIRED_MODULES,
        transport="explicit-nccl-p2p",
        tokenization_fixture={"seq": [1, 2, 3], "len": 32},
        driver_files={
            "src/q35q_phase0.py": H,
            "src/q35q_admission.py": "d" * 64,
        },
        commit_safe=True,
    )
    meta.update(over)
    return meta


def test_admission_pass():
    record = build_admission_record(good_meta())
    assert record["outcome"] == ADMISSION_READY
    assert record["revision"] == GOOD_REV
    assert record["weight_file_count"] == 2
    assert record["device_set"] == [0, 1]
    assert record["required_module_count"] == len(REQUIRED_MODULES)
    assert "vision" not in record
    scan_aggregate_only(record)


def test_admission_outcome_helper():
    record, outcome = admission_outcome(good_meta())
    assert outcome == ADMISSION_READY and record is not None
    blocked_record, blocked = admission_outcome(good_meta(revision="main"))
    assert blocked == ADMISSION_BLOCKED and blocked_record is None


@pytest.mark.parametrize("field", [
    "repo_id", "revision", "license", "lineage", "config", "tokenizer_id",
    "generation_id", "custom_code_id", "weight_manifest", "toolchain", "quant",
    "device_map", "required_modules", "transport", "tokenization_fixture",
    "driver_files", "omitted_modules",
])
def test_missing_field_blocked(field):
    meta = good_meta()
    del meta[field]
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(meta)


@pytest.mark.parametrize("bad", [None, [], "metadata"])
def test_non_dict_metadata_blocked(bad):
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(bad)


@pytest.mark.parametrize("field", [
    "repo_id", "license", "lineage", "tokenizer_id", "generation_id",
    "custom_code_id", "transport",
])
@pytest.mark.parametrize("bad", [123, ["x"], "   "])
def test_string_identity_fields_strict(field, bad):
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(**{field: bad}))


def test_mutable_revision_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(revision="main"))


def test_architecture_mismatch_blocked():
    config = dict(QWEN35_35B_A3B_ARCH)
    config["num_routed_experts"] = 64
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(config=config))


def test_device_map_auto_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(device_map="auto"))


def test_incomplete_device_map_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(
            good_meta(device_map={"model.layers.0": 0})
        )


def test_required_module_inventory_mismatch_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(
            good_meta(required_modules=REQUIRED_MODULES + ("model.layers.20",))
        )


def test_offload_blocked():
    device_map = good_meta()["device_map"].copy()
    device_map["model.layers.0"] = "cpu"
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(device_map=device_map))


def test_commit_unsafe_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(commit_safe=False))


def test_incomplete_toolchain_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(toolchain={"transformers": "4.99"}))


def test_non_string_toolchain_identity_blocked():
    toolchain = good_meta()["toolchain"].copy()
    toolchain["kernel"] = 123
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(toolchain=toolchain))


def test_incomplete_quant_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(quant={"quant_type": "gptq"}))


def test_nonfinite_quant_blocked():
    quant = good_meta()["quant"].copy()
    quant["scale"] = math.nan
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(quant=quant))


def test_vision_not_omitted_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(omitted_modules=["mtp.head"]))


@pytest.mark.parametrize("bad", [None, "visual.encoder", [123], []])
def test_malformed_omitted_modules_blocked(bad):
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(omitted_modules=bad))


def test_bad_param_count_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(param_count_text_only=0))
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(param_count_text_only=True))


@pytest.mark.parametrize("manifest", [
    {"a.safetensors": "xyz"},
    {"../a.safetensors": H},
    {"/tmp/a.safetensors": H},
    {"dir//a.safetensors": H},
    {"dir\\a.safetensors": H},
])
def test_bad_manifest_blocked(manifest):
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(weight_manifest=manifest))


def test_noncanonical_tokenization_fixture_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(
            good_meta(tokenization_fixture={"value": math.nan})
        )


def test_manifest_digest_verifiable():
    manifest = {
        "model-00002-of-00002.safetensors": "c" * 64,
        "model-00001-of-00002.safetensors": H,
    }
    record = build_admission_record(good_meta())
    assert verify_manifest_digest(manifest, record["weight_manifest_digest"])

    tampered = dict(manifest)
    tampered["model-00001-of-00002.safetensors"] = "e" * 64
    assert not verify_manifest_digest(tampered, record["weight_manifest_digest"])
    assert not verify_manifest_digest({"../escape": H}, record["weight_manifest_digest"])
    assert not verify_manifest_digest(manifest, "not-a-digest")
