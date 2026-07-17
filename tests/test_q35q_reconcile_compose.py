"""Q35Q source<->artifact reconciliation composition tests (CPU-only, no network/model).

Drives the committed composition with a synthetic admitted config, a synthetic FULL
40-layer source parameter enumeration, and a synthetic strict weight index, proving:
exact equality; a source module that appears only OUTSIDE the reduced window is
caught (full enumeration, no extrapolation); config identity + architecture
admission gates; and incomplete source enumeration fails.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock, expected_layer_types
from q35q_index_admission import git_blob_sha1
from q35q_reconcile_compose import run_reconciliation

NE = 256  # architecture admission requires the real routed-expert count
NL = 40


def config_bytes(**textover):
    txt = {"model_type": "qwen3_5_moe_text", "hidden_size": 2048, "num_hidden_layers": NL,
           "vocab_size": 248320, "num_experts": NE, "num_experts_per_tok": 8,
           "moe_intermediate_size": 512, "shared_expert_intermediate_size": 512,
           "full_attention_interval": 4, "layer_types": expected_layer_types(NL, 4),
           "mtp_num_hidden_layers": 1}
    txt.update(textover)
    obj = {"architectures": ["Qwen3_5MoeForConditionalGeneration"], "model_type": "qwen3_5_moe",
           "tie_word_embeddings": False, "vision_config": {"depth": 32}, "text_config": txt,
           "quantization_config": {"bits": 4, "group_size": 128, "quant_method": "gptq", "sym": True,
                                   "dynamic": {"-:.*attn.*": True, "-:.*mtp.*": True,
                                               "-:.*shared_expert.*": True, "-:.*visual.*": True,
                                               "lm_head": True}}}
    return json.dumps(obj).encode("utf-8")


def _layer_rel(kind):
    attn = ["linear_attn.in_proj_qkv", "linear_attn.out_proj"] if kind == "linear_attention" \
        else ["self_attn.q_proj", "self_attn.o_proj"]
    return attn + ["input_layernorm", "post_attention_layernorm", "mlp.gate",
                   "mlp.shared_expert.gate_proj", "mlp.shared_expert.up_proj",
                   "mlp.shared_expert.down_proj", "mlp.shared_expert_gate"]


def source_param_names(*, extra_on_layer=None):
    """FULL 40-layer source enumeration (packed experts)."""
    names = ["model.embed_tokens.weight", "model.norm.weight", "lm_head.weight"]
    for i, kind in enumerate(expected_layer_types(NL, 4)):
        rels = _layer_rel(kind) + ["mlp.experts.gate_up_proj", "mlp.experts.down_proj"]
        if extra_on_layer == i:
            rels = rels + ["linear_attn.phantom"]
        for rel in rels:
            names.append(f"model.layers.{i}.{rel}.weight")
    return names


def index_bytes(*, extra_on_layer=None):
    wm = {"model.language_model.embed_tokens.weight": "m0.safetensors",
          "model.language_model.norm.weight": "m0.safetensors", "lm_head.weight": "m0.safetensors",
          "model.visual.blocks.0.attn.qkv.weight": "m1.safetensors", "mtp.fc.weight": "m1.safetensors"}
    for i, kind in enumerate(expected_layer_types(NL, 4)):
        for rel in _layer_rel(kind):
            wm[f"model.language_model.layers.{i}.{rel}.weight"] = "m0.safetensors"
        if extra_on_layer == i:
            wm[f"model.language_model.layers.{i}.linear_attn.phantom.weight"] = "m0.safetensors"
        for e in range(NE):
            for sub in ("gate_proj", "up_proj", "down_proj"):
                wm[f"model.language_model.layers.{i}.mlp.experts.{e}.{sub}.qweight"] = "m0.safetensors"
    return json.dumps({"weight_map": wm}).encode("utf-8")


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _run(*, src=None, idx=None, cfg=None):
    cfg = cfg if cfg is not None else config_bytes()
    idx = idx if idx is not None else index_bytes()
    src = src if src is not None else source_param_names()
    return run_reconciliation(config_bytes=cfg, config_expected_git_sha1=git_blob_sha1(cfg),
                              source_param_names=src, index_bytes=idx, index_expected_sha256=_sha(idx))


def test_reconciliation_equal():
    out = _run()
    assert out["equal"] is True
    assert out["outcome"] == "q35q_phase0_source_artifact_module_equality_established"
    assert out["config_admitted"] and out["full_source_enumeration"]
    assert out["admitted_num_layers"] == 40 and out["admitted_num_experts"] == NE
    assert out["vision_omitted"] == 1 and out["mtp_omitted"] == 1 and out["expert_layers"] == 40


def test_extra_module_only_outside_reduced_window_is_caught():
    # a phantom source+artifact module on layer 37 (outside layers 0-3): full
    # enumeration reconciles it; if either side lacks it, equality fails.
    out = _run(src=source_param_names(extra_on_layer=37), idx=index_bytes(extra_on_layer=37))
    assert out["equal"] is True  # both sides have it -> still equal under full enum
    out2 = _run(src=source_param_names(extra_on_layer=37))  # source-only phantom on L37
    assert out2["equal"] is False and out2["missing_count"] == 1


def test_incomplete_source_enumeration_fails():
    # drop all of layer 20 from the source -> not the complete 40-layer manifest
    src = [n for n in source_param_names() if not n.startswith("model.layers.20.")]
    with pytest.raises(Q35QStageBlock, match="complete 40-layer manifest"):
        _run(src=src)


def test_bad_config_identity_fails():
    cfg = config_bytes()
    with pytest.raises(Q35QStageBlock, match="frozen git blob identity"):
        run_reconciliation(config_bytes=cfg, config_expected_git_sha1="0" * 40,
                           source_param_names=source_param_names(),
                           index_bytes=index_bytes(), index_expected_sha256=_sha(index_bytes()))


def test_bad_config_architecture_fails():
    with pytest.raises(Q35QStageBlock, match="architecture conjunction failed"):
        _run(cfg=config_bytes(hidden_size=4096))


def test_bad_index_identity_fails():
    idx = index_bytes()
    with pytest.raises(Q35QStageBlock, match="frozen remote identity"):
        run_reconciliation(config_bytes=config_bytes(),
                           config_expected_git_sha1=git_blob_sha1(config_bytes()),
                           source_param_names=source_param_names(),
                           index_bytes=idx, index_expected_sha256="0" * 64)
