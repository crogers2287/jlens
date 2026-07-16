"""Q35Q Phase-0 source + load-manifest admission tests (CPU-only, no model/network).

Proves the load-manifest conjunction fails closed on a wrong/missing class source,
a vision or MTP module leaking into the admitted text-only load path, a missing
Gated DeltaNet projection, a tied head, and missing text modules — the source and
load-manifest proofs config metadata alone cannot make (defect 4).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock, expected_layer_types
from q35q_source_admission import validate_load_manifest, validate_source_identity

REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"


def good_source(**over):
    s = {"outer_class": "Qwen3_5MoeForConditionalGeneration",
         "text_only_class": "Qwen3_5MoeForCausalLM",
         "module_qualname": "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe",
         "source_sha": REV}
    s.update(over)
    return s


def good_manifest(num_layers=40, interval=4, drop=None, add=None):
    names = ["model.embed_tokens.weight", "model.norm.weight", "lm_head.weight"]
    for i, kind in enumerate(expected_layer_types(num_layers, interval)):
        if kind == "linear_attention":
            for p in ("in_proj_qkv", "in_proj_z", "in_proj_b", "in_proj_a", "out_proj"):
                names.append(f"model.layers.{i}.self_attn.{p}.weight")
        else:
            for p in ("q_proj", "k_proj", "v_proj", "o_proj"):
                names.append(f"model.layers.{i}.self_attn.{p}.weight")
        names.append(f"model.layers.{i}.mlp.shared_expert.gate_proj.weight")
        names.append(f"model.layers.{i}.mlp.experts.0.gate_proj.weight")
    if drop:
        names = [n for n in names if drop not in n]
    if add:
        names += list(add)
    return names


# ---------- source identity ----------

def test_source_identity_pass():
    assert validate_source_identity(good_source())["all_required_pass"] is True


@pytest.mark.parametrize("over", [
    {"outer_class": "SomethingElse"},
    {"text_only_class": "Qwen2ForCausalLM"},
    {"module_qualname": ""},
    {"source_sha": "not-a-hash"},
    {"source_sha": ""},
])
def test_source_identity_each_field_fails(over):
    assert validate_source_identity(good_source(**over))["all_required_pass"] is False


def test_source_identity_bad_type_raises():
    with pytest.raises(Q35QStageBlock):
        validate_source_identity("not-a-dict")


# ---------- load manifest happy path ----------

def test_load_manifest_pass():
    out = validate_load_manifest(good_manifest(), tie_word_embeddings=False)
    assert out["all_required_pass"] is True
    assert out["vision_omitted_from_load"] and out["mtp_omitted_from_load"]
    assert out["gated_deltanet_projections_present"] and out["full_attention_projections_present"]


# ---------- vision / MTP must be omitted from the admitted load path ----------

@pytest.mark.parametrize("leak", [
    "model.visual.blocks.0.attn.qkv.weight",
    "model.vision_tower.patch_embed.proj.weight",
])
def test_vision_leak_fails(leak):
    out = validate_load_manifest(good_manifest(add=[leak]), tie_word_embeddings=False)
    assert out["vision_omitted_from_load"] is False and out["all_required_pass"] is False


@pytest.mark.parametrize("leak", [
    "model.mtp.layers.0.weight",
    "model.nextn.head.weight",
])
def test_mtp_leak_fails(leak):
    out = validate_load_manifest(good_manifest(add=[leak]), tie_word_embeddings=False)
    assert out["mtp_omitted_from_load"] is False and out["all_required_pass"] is False


# ---------- structural failures ----------

def test_missing_deltanet_projection_fails():
    out = validate_load_manifest(good_manifest(drop="in_proj_z"), tie_word_embeddings=False)
    assert out["gated_deltanet_projections_present"] is False and out["all_required_pass"] is False


def test_missing_full_attention_projection_fails():
    out = validate_load_manifest(good_manifest(drop="k_proj"), tie_word_embeddings=False)
    assert out["full_attention_projections_present"] is False and out["all_required_pass"] is False


def test_tied_head_fails():
    out = validate_load_manifest(good_manifest(), tie_word_embeddings=True)
    assert out["untied_lm_head"] is False and out["all_required_pass"] is False


def test_missing_lm_head_fails():
    out = validate_load_manifest(good_manifest(drop="lm_head"), tie_word_embeddings=False)
    assert out["lm_head_present"] is False and out["all_required_pass"] is False


def test_missing_shared_expert_fails():
    out = validate_load_manifest(good_manifest(drop="shared_expert"), tie_word_embeddings=False)
    assert out["shared_expert_present"] is False and out["all_required_pass"] is False


def test_missing_embed_fails():
    out = validate_load_manifest(good_manifest(drop="embed_tokens"), tie_word_embeddings=False)
    assert out["embed_tokens_present"] is False and out["all_required_pass"] is False


def test_empty_manifest_raises():
    with pytest.raises(Q35QStageBlock, match="empty admitted load manifest"):
        validate_load_manifest([], tie_word_embeddings=False)


# ---------- optional shape binding ----------

def test_shape_binding_pass():
    shapes = {"model.embed_tokens.weight": (248320, 2048),
              "lm_head.weight": (248320, 2048),
              "model.layers.0.mlp.experts.0.gate_proj.weight": (512, 2048)}
    out = validate_load_manifest(good_manifest(), tie_word_embeddings=False, param_shapes=shapes)
    assert out["embed_width_bound"] and out["lm_head_width_bound"] and out["expert_width_bound"]
    assert out["all_required_pass"] is True


def test_shape_binding_wrong_vocab_fails():
    shapes = {"model.embed_tokens.weight": (200000, 2048), "lm_head.weight": (200000, 2048),
              "model.layers.0.mlp.experts.0.gate_proj.weight": (512, 2048)}
    out = validate_load_manifest(good_manifest(), tie_word_embeddings=False, param_shapes=shapes)
    assert out["embed_width_bound"] is False and out["all_required_pass"] is False
