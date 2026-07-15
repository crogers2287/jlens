"""Q35Q artifact-admission builder tests: pass path + fail-closed on every
missing/mutable/contradictory field. Synthetic metadata only; no model,
no GPU, no network, no private data.
"""
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
        weight_manifest={"model-00001-of-00002.safetensors": H,
                         "model-00002-of-00002.safetensors": "c" * 64},
        param_count_text_only=35_000_000_000,
        omitted_modules=["visual.encoder", "mtp.head"],
        toolchain={"transformers": "4.99", "accelerate": "1.0", "torch": "2.5",
                   "cuda": "12.4", "driver": "550.x", "backend": "gptqmodel",
                   "kernel": "eager"},
        quant={"quant_type": "gptq", "group_size": 128,
               "compute_dtype": "float16", "storage_dtype": "int4"},
        device_map={"model.embed_tokens": 0, "model.layers.0": 0,
                    "model.layers.39": 1, "lm_head": 1},
        transport="explicit-nccl-p2p",
        tokenization_fixture={"seq": [1, 2, 3], "len": 32},
        driver_files={"src/q35q_phase0.py": H, "src/q35q_admission.py": "d" * 64},
        commit_safe=True,
    )
    meta.update(over)
    return meta


def test_admission_pass():
    rec = build_admission_record(good_meta())
    assert rec["outcome"] == ADMISSION_READY
    assert rec["revision"] == GOOD_REV
    assert rec["weight_file_count"] == 2
    assert rec["device_set"] == [0, 1]
    assert "vision" not in rec  # only aggregate identity fields
    scan_aggregate_only(rec)  # public-safe


def test_admission_outcome_helper():
    rec, outcome = admission_outcome(good_meta())
    assert outcome == ADMISSION_READY and rec is not None
    rec2, outcome2 = admission_outcome(good_meta(revision="main"))
    assert outcome2 == ADMISSION_BLOCKED and rec2 is None


@pytest.mark.parametrize("field", [
    "repo_id", "revision", "license", "lineage", "config", "tokenizer_id",
    "weight_manifest", "toolchain", "quant", "device_map", "transport",
    "driver_files", "omitted_modules",
])
def test_missing_field_blocked(field):
    meta = good_meta()
    del meta[field]
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(meta)


def test_mutable_revision_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(revision="main"))


def test_architecture_mismatch_blocked():
    cfg = dict(QWEN35_35B_A3B_ARCH)
    cfg["num_routed_experts"] = 64
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(config=cfg))


def test_device_map_auto_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(device_map="auto"))


def test_offload_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(device_map={"model.layers.0": "cpu"}))


def test_commit_unsafe_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(commit_safe=False))


def test_incomplete_toolchain_blocked():
    tc = {"transformers": "4.99"}  # missing the rest
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(toolchain=tc))


def test_incomplete_quant_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(quant={"quant_type": "gptq"}))


def test_vision_not_omitted_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(omitted_modules=["mtp.head"]))


def test_bad_param_count_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(param_count_text_only=0))
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(param_count_text_only=True))


def test_bad_manifest_hash_blocked():
    with pytest.raises(Q35QAdmissionBlock):
        build_admission_record(good_meta(weight_manifest={"a.safetensors": "xyz"}))


def test_manifest_digest_verifiable():
    m = {"model-00002-of-00002.safetensors": "c" * 64,
         "model-00001-of-00002.safetensors": H}
    rec = build_admission_record(good_meta())
    assert verify_manifest_digest(m, rec["weight_manifest_digest"])
    # tampered manifest fails
    m2 = dict(m)
    m2["model-00001-of-00002.safetensors"] = "e" * 64
    assert not verify_manifest_digest(m2, rec["weight_manifest_digest"])
