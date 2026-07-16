"""Q35Q Phase-0 admission-logic tests (CPU-only, no network/model).

Proves the corrected admission fails closed on incomplete architecture, cache/
metadata contamination, extra/missing files, path escape, hash mismatch, and
substring-only or nondeterministic tokenizer behavior.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import (
    EXPECTED,
    GPTQ_EXPECTED,
    Q35QStageBlock,
    admitted_public_manifest,
    expected_layer_types,
    tokenizer_roundtrip_verdict,
    validate_gptq_quant,
    validate_text_architecture,
)

H = "a" * 64


def good_config(**over):
    txt = {
        "model_type": "qwen3_5_moe_text", "hidden_size": 2048,
        "num_hidden_layers": 40, "vocab_size": 248320, "num_experts": 256,
        "num_experts_per_tok": 8, "moe_intermediate_size": 512,
        "shared_expert_intermediate_size": 512, "full_attention_interval": 4,
        "layer_types": expected_layer_types(40, 4), "mtp_num_hidden_layers": 1,
    }
    cfg = {
        "architectures": ["Qwen3_5MoeForConditionalGeneration"],
        "model_type": "qwen3_5_moe", "tie_word_embeddings": False,
        "vision_config": {"depth": 32}, "text_config": txt,
    }
    cfg.update(over)
    if "text_over" in over:
        cfg["text_config"] = {**txt, **over.pop("text_over")}
    return cfg


# ---------- architecture ----------

def test_layer_types_schedule():
    lt = expected_layer_types(40, 4)
    assert len(lt) == 40 and lt[3] == "full_attention" and lt[0] == "linear_attention"
    assert lt.count("full_attention") == 10


def test_architecture_full_pass():
    out = validate_text_architecture(good_config())
    assert out["all_required_pass"] is True
    assert all(out[k] for k in out if k != "all_required_pass")


def test_architecture_missing_text_config_blocked():
    with pytest.raises(Q35QStageBlock):
        validate_text_architecture({"model_type": "qwen3_5_moe"})


@pytest.mark.parametrize("field,bad", [
    ("num_experts", 128), ("num_experts_per_tok", 4),
    ("moe_intermediate_size", 256), ("shared_expert_intermediate_size", 0),
    ("hidden_size", 4096), ("num_hidden_layers", 48), ("vocab_size", 200000),
    ("full_attention_interval", 8),
])
def test_architecture_each_field_can_fail(field, bad):
    cfg = good_config()
    cfg["text_config"][field] = bad
    out = validate_text_architecture(cfg)
    assert out[field] is False and out["all_required_pass"] is False


def test_architecture_wrong_layer_schedule_fails():
    cfg = good_config()
    cfg["text_config"]["layer_types"] = ["full_attention"] * 40
    out = validate_text_architecture(cfg)
    assert out["layer_types_hybrid_schedule"] is False and out["all_required_pass"] is False


def test_architecture_tied_head_fails():
    out = validate_text_architecture(good_config(tie_word_embeddings=True))
    assert out["untied_output_head"] is False and out["all_required_pass"] is False


def test_architecture_missing_vision_fails():
    cfg = good_config(); cfg.pop("vision_config")
    out = validate_text_architecture(cfg)
    assert out["vision_present_in_repo"] is False and out["all_required_pass"] is False


# ---------- gptq ----------

def good_qcfg(**over):
    q = {"bits": 4, "group_size": 128, "quant_method": "gptq", "sym": True,
         "dynamic": {"-:.*attn.*": True, "-:.*mtp.*": True,
                     "-:.*shared_expert.*": True, "-:.*visual.*": True,
                     "lm_head": True, "model.language_model.embed_tokens": True}}
    q.update(over)
    return q


def test_gptq_full_pass():
    assert validate_gptq_quant(good_qcfg())["all_required_pass"] is True


@pytest.mark.parametrize("over", [{"bits": 8}, {"group_size": 64},
                                   {"quant_method": "awq"}, {"sym": False}])
def test_gptq_field_fails(over):
    assert validate_gptq_quant(good_qcfg(**over))["all_required_pass"] is False


def test_gptq_missing_skip_rules_fails():
    q = good_qcfg(dynamic={"lm_head": True})
    out = validate_gptq_quant(q)
    assert out["skips_attention"] is False and out["all_required_pass"] is False


# ---------- manifest ----------

def test_manifest_pass():
    admitted = {"config.json": H, "tokenizer.json": "b" * 64}
    present = dict(admitted)
    out = admitted_public_manifest(admitted, present)
    assert out["file_count"] == 2 and len(out["manifest_sha256"]) == 64


def test_manifest_missing_blocked():
    with pytest.raises(Q35QStageBlock):
        admitted_public_manifest({"config.json": H}, {})


def test_manifest_hash_mismatch_blocked():
    with pytest.raises(Q35QStageBlock):
        admitted_public_manifest({"config.json": H}, {"config.json": "c" * 64})


def test_manifest_extra_unapproved_blocked():
    with pytest.raises(Q35QStageBlock):
        admitted_public_manifest({"config.json": H},
                                 {"config.json": H, "rogue.py": "d" * 64})


def test_manifest_cache_metadata_not_extra_but_ignored():
    # cache/metadata present in staging is excluded, not counted as extra
    out = admitted_public_manifest(
        {"config.json": H},
        {"config.json": H, ".cache/huggingface/x": "e" * 64, "config.json.lock": "f" * 64})
    assert out["file_count"] == 1


def test_manifest_path_escape_blocked():
    with pytest.raises(Q35QStageBlock):
        admitted_public_manifest({"../escape.json": H}, {"../escape.json": H})


def test_manifest_cache_in_admitted_set_blocked():
    with pytest.raises(Q35QStageBlock):
        admitted_public_manifest({".cache/x": H}, {".cache/x": H})


# ---------- tokenizer roundtrip ----------

def test_tokenizer_roundtrip_pass():
    v = tokenizer_roundtrip_verdict([1, 2, 3], [1, 2, 3], [1, 2, 3], add_special_tokens=False)
    assert v["roundtrip_pass"] is True


def test_tokenizer_nondeterministic_fails():
    v = tokenizer_roundtrip_verdict([1, 2, 3], [1, 2, 4], [1, 2, 3], add_special_tokens=False)
    assert v["deterministic_encode"] is False and v["roundtrip_pass"] is False


def test_tokenizer_decode_reencode_mismatch_fails():
    v = tokenizer_roundtrip_verdict([1, 2, 3], [1, 2, 3], [1, 2, 3, 9], add_special_tokens=False)
    assert v["exact_decode_reencode"] is False and v["roundtrip_pass"] is False


def test_tokenizer_special_tokens_requested_fails():
    v = tokenizer_roundtrip_verdict([1, 2, 3], [1, 2, 3], [1, 2, 3], add_special_tokens=True)
    assert v["no_special_tokens_requested"] is False and v["roundtrip_pass"] is False


def test_tokenizer_empty_fails():
    v = tokenizer_roundtrip_verdict([], [], [], add_special_tokens=False)
    assert v["roundtrip_pass"] is False
