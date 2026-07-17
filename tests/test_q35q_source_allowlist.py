"""Q35Q source-derived allow-list tests (CPU-only, no model/network).

Uses synthetic reduced-layer module name sets modeled on the REAL meta-device
templates of Qwen3_5MoeForCausalLM (DeltaNet under linear_attn.*, QK-norm on full
layers, packed experts mlp.experts.gate_up_proj/down_proj) to prove template
extraction, per-kind classification, and full-schedule expansion.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock, expected_layer_types
from q35q_source_allowlist import (
    classify_layer_templates,
    derive_source_allowlist_from_modules,
    expand_source_allowlist,
    extract_templates,
)

# real linear-attn layer template (relative), from meta construction
LINEAR = ["input_layernorm", "post_attention_layernorm", "mlp.gate",
          "mlp.experts.gate_up_proj", "mlp.experts.down_proj",
          "mlp.shared_expert.gate_proj", "mlp.shared_expert.up_proj",
          "mlp.shared_expert.down_proj", "mlp.shared_expert_gate",
          "linear_attn.in_proj_qkv", "linear_attn.in_proj_z", "linear_attn.in_proj_a",
          "linear_attn.in_proj_b", "linear_attn.out_proj", "linear_attn.conv1d",
          "linear_attn.A_log", "linear_attn.dt_bias", "linear_attn.norm"]
FULL = ["input_layernorm", "post_attention_layernorm", "mlp.gate",
        "mlp.experts.gate_up_proj", "mlp.experts.down_proj",
        "mlp.shared_expert.gate_proj", "mlp.shared_expert.up_proj",
        "mlp.shared_expert.down_proj", "mlp.shared_expert_gate",
        "self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj",
        "self_attn.q_norm", "self_attn.k_norm"]
TOP = ["model.embed_tokens", "model.norm", "lm_head"]


def reduced_param_names(interval=4):
    """4-layer reduced construction: layers 0-2 linear, layer 3 full (+ .weight leaf)."""
    names = [f"{t}.weight" for t in TOP]
    sched = expected_layer_types(4, interval)
    for i, kind in enumerate(sched):
        tmpl = LINEAR if kind == "linear_attention" else FULL
        for rel in tmpl:
            names.append(f"model.layers.{i}.{rel}.weight")
    return names


def test_extract_templates_splits_top_and_layers():
    from q35q_source_allowlist import canonical_source_modules
    mods = canonical_source_modules(reduced_param_names())
    t = extract_templates(mods, 4)
    assert set(t["top_level"]) == set(TOP)
    assert set(t["per_layer"][0]) == set(LINEAR)
    assert set(t["per_layer"][3]) == set(FULL)


def test_classify_kinds():
    from q35q_source_allowlist import canonical_source_modules
    mods = canonical_source_modules(reduced_param_names())
    by_kind = classify_layer_templates(extract_templates(mods, 4), 4, 4)
    assert set(by_kind["linear_attention"]) == set(LINEAR)
    assert set(by_kind["full_attention"]) == set(FULL)


def test_full_derivation_40_layers():
    out = derive_source_allowlist_from_modules(reduced_param_names(), num_layers=40, interval=4)
    allow = out["allowlist"]
    # top-level + 40 layers; DeltaNet path is linear_attn (NOT self_attn)
    assert "model.layers.0.linear_attn.in_proj_qkv" in allow
    assert "model.layers.0.self_attn.q_proj" not in allow  # layer 0 is linear
    assert "model.layers.3.self_attn.q_proj" in allow      # layer 3 is full
    assert "model.layers.3.self_attn.q_norm" in allow
    assert "model.layers.39.mlp.experts.gate_up_proj" in allow  # packed experts
    # 40 layers: 10 full (every 4th), 30 linear
    n_full = sum(1 for k in expected_layer_types(40, 4) if k == "full_attention")
    assert n_full == 10
    assert out["allowlist_size"] == len(TOP) + 30 * len(LINEAR) + 10 * len(FULL)


def test_inconsistent_same_kind_template_fails():
    from q35q_source_allowlist import canonical_source_modules
    names = reduced_param_names()
    names.append("model.layers.1.linear_attn.rogue_extra.weight")  # layer 1 differs from 0
    mods = canonical_source_modules(names)
    with pytest.raises(Q35QStageBlock, match="inconsistent"):
        classify_layer_templates(extract_templates(mods, 4), 4, 4)


def test_missing_attention_kind_fails():
    # only linear layers present -> no full template
    names = [f"{t}.weight" for t in TOP]
    for i in range(3):
        for rel in LINEAR:
            names.append(f"model.layers.{i}.{rel}.weight")
    from q35q_source_allowlist import canonical_source_modules
    mods = canonical_source_modules(names)
    with pytest.raises(Q35QStageBlock, match="both attention kinds"):
        classify_layer_templates(extract_templates(mods, 3), 3, 4)


def test_empty_modules_fail():
    from q35q_source_allowlist import canonical_source_modules
    with pytest.raises(Q35QStageBlock, match="no source modules"):
        canonical_source_modules([])


def test_no_layers_fail():
    from q35q_source_allowlist import canonical_source_modules
    with pytest.raises(Q35QStageBlock, match="no per-layer modules"):
        extract_templates(canonical_source_modules(["model.embed_tokens.weight"]), 40)
