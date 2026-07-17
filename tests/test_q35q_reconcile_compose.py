"""Q35Q source<->artifact reconciliation composition tests (CPU-only, no network/model).

Drives the committed composition with synthetic source parameter names + a synthetic
strict weight index, proving the independent source/artifact providers reconcile to
exact equality and that a source/artifact mismatch or a bad index identity fails.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_reconcile_compose import run_reconciliation

NE = 2


def source_param_names():
    """Reduced (4-layer) meta-style parameter names with .weight leaves."""
    from q35q_stage import expected_layer_types
    top = ["model.embed_tokens.weight", "model.norm.weight", "lm_head.weight"]
    names = list(top)
    for i, kind in enumerate(expected_layer_types(4, 4)):
        attn = ["linear_attn.in_proj_qkv", "linear_attn.out_proj"] if kind == "linear_attention" \
            else ["self_attn.q_proj", "self_attn.o_proj"]
        for rel in (attn + ["input_layernorm", "post_attention_layernorm", "mlp.gate",
                            "mlp.shared_expert.gate_proj", "mlp.shared_expert.up_proj",
                            "mlp.shared_expert.down_proj", "mlp.shared_expert_gate",
                            "mlp.experts.gate_up_proj", "mlp.experts.down_proj"]):
            names.append(f"model.layers.{i}.{rel}.weight")
    return names


def artifact_index_bytes(*, break_equal=False):
    """Numbered/split artifact under model.language_model.* + vision/mtp noise."""
    from q35q_stage import expected_layer_types
    wm = {"model.language_model.embed_tokens.weight": "m0.safetensors",
          "model.language_model.norm.weight": "m0.safetensors", "lm_head.weight": "m0.safetensors",
          "model.visual.blocks.0.attn.qkv.weight": "m1.safetensors",
          "mtp.fc.weight": "m1.safetensors"}
    for i, kind in enumerate(expected_layer_types(40, 4)):
        attn = ["linear_attn.in_proj_qkv", "linear_attn.out_proj"] if kind == "linear_attention" \
            else ["self_attn.q_proj", "self_attn.o_proj"]
        for rel in (attn + ["input_layernorm", "post_attention_layernorm", "mlp.gate",
                            "mlp.shared_expert.gate_proj", "mlp.shared_expert.up_proj",
                            "mlp.shared_expert.down_proj", "mlp.shared_expert_gate"]):
            wm[f"model.language_model.layers.{i}.{rel}.weight"] = "m0.safetensors"
        for e in range(NE):
            for sub in ("gate_proj", "up_proj", "down_proj"):
                wm[f"model.language_model.layers.{i}.mlp.experts.{e}.{sub}.qweight"] = "m0.safetensors"
    if break_equal:
        wm["model.language_model.layers.0.linear_attn.phantom.weight"] = "m0.safetensors"
    return json.dumps({"weight_map": wm}).encode("utf-8")


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def test_reconciliation_equal():
    idx = artifact_index_bytes()
    out = run_reconciliation(source_param_names=source_param_names(), index_bytes=idx,
                             index_expected_sha256=_sha(idx), num_experts=NE)
    assert out["equal"] is True
    assert out["outcome"] == "q35q_phase0_source_artifact_module_equality_established"
    assert out["artifact_admission_status"] == "q35q_artifact_admission_blocked"
    assert out["vision_omitted"] == 1 and out["mtp_omitted"] == 1 and out["expert_layers"] == 40


def test_reconciliation_mismatch_blocks_outcome():
    idx = artifact_index_bytes(break_equal=True)
    out = run_reconciliation(source_param_names=source_param_names(), index_bytes=idx,
                             index_expected_sha256=_sha(idx), num_experts=NE)
    assert out["equal"] is False and out["outcome"] == "q35q_artifact_admission_blocked"
    assert out["extra_count"] == 1


def test_bad_index_identity_fails():
    idx = artifact_index_bytes()
    with pytest.raises(Q35QStageBlock, match="frozen remote identity"):
        run_reconciliation(source_param_names=source_param_names(), index_bytes=idx,
                           index_expected_sha256="0" * 64, num_experts=NE)
