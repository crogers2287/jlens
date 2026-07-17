"""Q35Q source<->artifact module reconciliation tests (CPU-only, no model/network).

Synthetic 2-layer / 2-expert sets modeled on the REAL artifact naming
(model.language_model.* prefix, numbered split experts, model.visual.* + mtp.*
omitted) prove the frozen packed<->numbered map yields exact source equality and
fails closed on a wrong expert range, missing sub-modules, an out-of-partition
module, and a genuine source/artifact mismatch.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_module_reconcile import reconcile_source_vs_artifact, rewrite_artifact_to_textonly

NE = 2  # experts per layer in the synthetic sets


def source_set():
    """Packed/fused source (2 layers)."""
    s = {"model.embed_tokens", "model.norm", "lm_head"}
    for i in range(2):
        s |= {f"model.layers.{i}.input_layernorm", f"model.layers.{i}.post_attention_layernorm",
              f"model.layers.{i}.mlp.gate", f"model.layers.{i}.mlp.shared_expert.gate_proj",
              f"model.layers.{i}.mlp.shared_expert.up_proj", f"model.layers.{i}.mlp.shared_expert.down_proj",
              f"model.layers.{i}.mlp.shared_expert_gate",
              f"model.layers.{i}.mlp.experts.gate_up_proj", f"model.layers.{i}.mlp.experts.down_proj",
              f"model.layers.{i}.linear_attn.in_proj_qkv", f"model.layers.{i}.linear_attn.out_proj"}
    return s


def artifact_set(*, drop=None, add=None, break_expert=False):
    """Numbered/split artifact under model.language_model.* + vision/mtp noise."""
    a = {"model.language_model.embed_tokens", "model.language_model.norm", "lm_head"}
    a |= {"model.visual.blocks.0.attn.qkv", "model.visual.patch_embed.proj"}         # vision
    a |= {"mtp.fc", "mtp.layers.0.input_layernorm", "mtp.norm"}                        # mtp
    for i in range(2):
        a |= {f"model.language_model.layers.{i}.input_layernorm",
              f"model.language_model.layers.{i}.post_attention_layernorm",
              f"model.language_model.layers.{i}.mlp.gate",
              f"model.language_model.layers.{i}.mlp.shared_expert.gate_proj",
              f"model.language_model.layers.{i}.mlp.shared_expert.up_proj",
              f"model.language_model.layers.{i}.mlp.shared_expert.down_proj",
              f"model.language_model.layers.{i}.mlp.shared_expert_gate",
              f"model.language_model.layers.{i}.linear_attn.in_proj_qkv",
              f"model.language_model.layers.{i}.linear_attn.out_proj"}
        for e in range(NE):
            subs = ["gate_proj", "up_proj", "down_proj"]
            if break_expert and i == 0 and e == 0:
                subs = ["gate_proj", "down_proj"]  # missing up_proj
            for sub in subs:
                a.add(f"model.language_model.layers.{i}.mlp.experts.{e}.{sub}")
    if drop:
        a = {m for m in a if drop not in m}
    if add:
        a |= set(add)
    return a


def test_reconcile_equal():
    out = reconcile_source_vs_artifact(source_set(), artifact_set(), NE)
    assert out["equal"] is True and out["missing_count"] == 0 and out["extra_count"] == 0
    assert out["vision_omitted"] == 2 and out["mtp_omitted"] == 3 and out["expert_layers"] == 2


def test_vision_mtp_are_omitted_not_extra():
    out = reconcile_source_vs_artifact(source_set(), artifact_set(), NE)
    assert out["equal"] is True  # vision/mtp excluded, not counted as extra


def test_wrong_expert_count_fails():
    # only 1 expert present where 2 are required
    a = artifact_set(drop="mlp.experts.1.")
    with pytest.raises(Q35QStageBlock, match="expert ids are not exactly"):
        reconcile_source_vs_artifact(source_set(), a, NE)


def test_missing_expert_submodule_fails():
    with pytest.raises(Q35QStageBlock, match="missing one of"):
        reconcile_source_vs_artifact(source_set(), artifact_set(break_expert=True), NE)


def test_out_of_partition_module_fails():
    a = artifact_set(add=["model.rogue.module"])
    with pytest.raises(Q35QStageBlock, match="outside frozen text-only"):
        reconcile_source_vs_artifact(source_set(), a, NE)


def test_source_extra_module_not_equal():
    src = source_set() | {"model.layers.0.linear_attn.phantom"}
    out = reconcile_source_vs_artifact(src, artifact_set(), NE)
    assert out["equal"] is False and out["missing_count"] == 1


def test_artifact_extra_textonly_module_not_equal():
    a = artifact_set(add=["model.language_model.layers.0.linear_attn.phantom"])
    out = reconcile_source_vs_artifact(source_set(), a, NE)
    assert out["equal"] is False and out["extra_count"] == 1


def test_fused_experts_collapse():
    rw = rewrite_artifact_to_textonly(artifact_set(), NE)
    assert "model.layers.0.mlp.experts.gate_up_proj" in rw["textonly"]
    assert "model.layers.0.mlp.experts.down_proj" in rw["textonly"]


def test_empty_source_fails():
    with pytest.raises(Q35QStageBlock, match="empty source"):
        reconcile_source_vs_artifact(set(), artifact_set(), NE)
