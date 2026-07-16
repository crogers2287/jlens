"""Q35Q Phase-0 source + load-manifest admission tests (CPU-only, no model/network).

Proves the corrected conjunction (source-binding correction): source identity is
bound to an independently derived expected identity by equality; the admitted
module set must equal a frozen positive allow-list exactly; per-layer projection
and expert coverage use exact segment admission (decoys fail); parameter shapes
are mandatory; vision/MTP remain excluded as defense in depth.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock, expected_layer_types
from q35q_source_admission import (
    canonical_module_path,
    validate_load_manifest,
    validate_source_identity,
)

REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"
QUALNAME = "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe"


# ---------- source identity ----------

def good_source(**over):
    s = {"outer_class": "Qwen3_5MoeForConditionalGeneration",
         "text_only_class": "Qwen3_5MoeForCausalLM",
         "module_qualname": QUALNAME, "source_sha": REV}
    s.update(over)
    return s


def test_source_identity_pass():
    assert validate_source_identity(good_source(), good_source())["all_required_pass"] is True


def test_source_hash_valid_shape_but_wrong_fails():
    out = validate_source_identity(good_source(source_sha="b" * 40), good_source())
    assert out["source_hash_equal"] is False and out["all_required_pass"] is False


def test_source_qualname_nonempty_but_wrong_fails():
    out = validate_source_identity(good_source(module_qualname="some.other.module"), good_source())
    assert out["module_qualname_equal"] is False and out["all_required_pass"] is False


def test_source_wrong_text_only_class_fails():
    out = validate_source_identity(good_source(text_only_class="Qwen2ForCausalLM"), good_source())
    assert out["text_only_class_equal"] is False and out["all_required_pass"] is False


def test_expected_bad_source_sha_raises():
    with pytest.raises(Q35QStageBlock, match="immutable 40/64-hex"):
        validate_source_identity(good_source(), good_source(source_sha="not-hex"))


def test_expected_wrong_class_raises():
    with pytest.raises(Q35QStageBlock, match="admitted Qwen3.5-MoE classes"):
        validate_source_identity(good_source(), good_source(outer_class="X"))


# ---------- canonicalization ----------

def test_canonical_strips_tensor_leaves():
    assert canonical_module_path("model.layers.0.self_attn.in_proj_qkv.qweight") == "model.layers.0.self_attn.in_proj_qkv"
    assert canonical_module_path("lm_head.weight") == "lm_head"
    assert canonical_module_path("model.norm.weight") == "model.norm"


# ---------- load manifest allow-list ----------

def build_allowlist(num_layers=40, interval=4, n_experts=2, layout="unpacked",
                    drop=None, replace=None, add=None):
    paths = {"model.embed_tokens", "model.norm", "lm_head"}
    for i, kind in enumerate(expected_layer_types(num_layers, interval)):
        projs = ("in_proj_qkv", "in_proj_z", "in_proj_b", "in_proj_a", "out_proj") \
            if kind == "linear_attention" else ("q_proj", "k_proj", "v_proj", "o_proj")
        for p in projs:
            paths.add(f"model.layers.{i}.self_attn.{p}")
        paths.add(f"model.layers.{i}.mlp.gate")
        for sub in ("gate_proj", "up_proj", "down_proj"):
            paths.add(f"model.layers.{i}.mlp.shared_expert.{sub}")
        if layout == "unpacked":
            for e in range(n_experts):
                paths.add(f"model.layers.{i}.mlp.experts.{e}.gate_proj")
        else:
            paths.add(f"model.layers.{i}.mlp.experts")
        paths.add(f"model.layers.{i}.input_layernorm")
        paths.add(f"model.layers.{i}.post_attention_layernorm")
    if drop:
        paths = {p for p in paths if drop not in p}
    if replace:
        old, new = replace
        paths = {(new if p == old else p) for p in paths}
    if add:
        paths |= set(add)
    return paths


def good_shapes():
    return {"model.embed_tokens.weight": (248320, 2048), "lm_head.weight": (248320, 2048),
            "model.layers.0.mlp.experts.0.gate_proj.qweight": (512, 2048)}


def test_load_manifest_pass():
    allow = build_allowlist()
    out = validate_load_manifest(allow, allow, param_shapes=good_shapes())
    assert out["all_required_pass"] is True
    assert out["admitted_equals_allowlist"] and out["per_layer_projections_present"]
    assert out["per_layer_experts_present"]


def test_packed_layout_pass():
    allow = build_allowlist(layout="packed")
    out = validate_load_manifest(allow, allow, expert_layout="packed", param_shapes=good_shapes())
    assert out["all_required_pass"] is True


# defect 3: shapes mandatory
def test_omitted_shapes_raises():
    allow = build_allowlist()
    with pytest.raises(Q35QStageBlock, match="parameter-shape evidence is mandatory"):
        validate_load_manifest(allow, allow, param_shapes=None)


def test_wrong_embed_shape_fails():
    allow = build_allowlist()
    shapes = dict(good_shapes()); shapes["model.embed_tokens.weight"] = (200000, 2048)
    out = validate_load_manifest(allow, allow, param_shapes=shapes)
    assert out["embed_width_bound"] is False and out["all_required_pass"] is False


# defect 4: decoy projection substring fails exact segment admission
def test_decoy_projection_substring_fails():
    allow = build_allowlist(replace=("model.layers.0.self_attn.in_proj_qkv",
                                     "model.layers.0.self_attn.backup_in_proj_qkv"))
    out = validate_load_manifest(allow, allow, param_shapes=good_shapes())
    assert out["per_layer_projections_present"] is False and out["all_required_pass"] is False


# defect 5: expert evidence missing on one layer fails
def test_expert_missing_on_one_layer_fails():
    allow = build_allowlist(drop="model.layers.1.mlp.experts")
    out = validate_load_manifest(allow, allow, param_shapes=good_shapes())
    assert out["per_layer_experts_present"] is False and out["all_required_pass"] is False


def test_shared_expert_missing_on_one_layer_fails():
    allow = build_allowlist(drop="model.layers.2.mlp.shared_expert")
    out = validate_load_manifest(allow, allow, param_shapes=good_shapes())
    assert out["per_layer_experts_present"] is False and out["all_required_pass"] is False


# defect 6: unapproved extra module rejected by positive allow-list
def test_unapproved_module_rejected(tmp_path=None):
    allow = build_allowlist()
    admitted = set(allow) | {"model.mystery.module"}
    out = validate_load_manifest(admitted, allow, param_shapes=good_shapes())
    assert out["no_unapproved_modules"] is False and out["all_required_pass"] is False


def test_missing_module_rejected():
    allow = build_allowlist()
    admitted = set(allow) - {"model.norm"}
    out = validate_load_manifest(admitted, allow, param_shapes=good_shapes())
    assert out["no_missing_modules"] is False and out["final_norm_present"] is True
    assert out["all_required_pass"] is False


# vision/MTP defense in depth (even if on the allow-list)
def test_vision_module_flagged_even_if_allowlisted():
    allow = build_allowlist(add=["model.visual.blocks.0.attn.qkv"])
    out = validate_load_manifest(allow, allow, param_shapes=good_shapes())
    assert out["vision_omitted_from_load"] is False and out["all_required_pass"] is False


def test_mtp_module_flagged_even_if_allowlisted():
    allow = build_allowlist(add=["model.mtp.layers.0"])
    out = validate_load_manifest(allow, allow, param_shapes=good_shapes())
    assert out["mtp_omitted_from_load"] is False and out["all_required_pass"] is False


def test_empty_sets_raise():
    with pytest.raises(Q35QStageBlock, match="empty admitted or expected"):
        validate_load_manifest(set(), build_allowlist(), param_shapes=good_shapes())


def test_unknown_expert_layout_raises():
    allow = build_allowlist()
    with pytest.raises(Q35QStageBlock, match="unknown expert_layout"):
        validate_load_manifest(allow, allow, expert_layout="weird", param_shapes=good_shapes())
