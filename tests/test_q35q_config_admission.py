"""Q35Q config admission tests (CPU-only, no network/model).

Proves the config is admitted via its immutable git-blob identity + the full
architecture and GPTQ conjunctions, failing closed on identity mismatch, a wrong
architecture field, a wrong GPTQ field, and duplicate JSON keys.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock, expected_layer_types
from q35q_index_admission import git_blob_sha1
from q35q_config_admission import admit_config, verify_config_identity


def good_config_obj():
    txt = {"model_type": "qwen3_5_moe_text", "hidden_size": 2048, "num_hidden_layers": 40,
           "vocab_size": 248320, "num_experts": 256, "num_experts_per_tok": 8,
           "moe_intermediate_size": 512, "shared_expert_intermediate_size": 512,
           "full_attention_interval": 4, "layer_types": expected_layer_types(40, 4),
           "mtp_num_hidden_layers": 1}
    return {"architectures": ["Qwen3_5MoeForConditionalGeneration"], "model_type": "qwen3_5_moe",
            "tie_word_embeddings": False, "vision_config": {"depth": 32}, "text_config": txt,
            "quantization_config": {"bits": 4, "group_size": 128, "quant_method": "gptq", "sym": True,
                                    "dynamic": {"-:.*attn.*": True, "-:.*mtp.*": True,
                                                "-:.*shared_expert.*": True, "-:.*visual.*": True,
                                                "lm_head": True}}}


def good_bytes(**textover):
    obj = good_config_obj()
    obj["text_config"].update(textover)
    return json.dumps(obj).encode("utf-8")


def test_admit_ok():
    b = good_bytes()
    out = admit_config(b, git_blob_sha1(b))
    assert out["architecture_pass"] and out["gptq_pass"]
    assert out["num_experts"] == 256 and out["num_hidden_layers"] == 40


def test_identity_mismatch_fails():
    with pytest.raises(Q35QStageBlock, match="do not match the frozen git blob"):
        admit_config(good_bytes(), "0" * 40)


def test_identity_bad_shape_fails():
    with pytest.raises(Q35QStageBlock, match="not a 40-hex git blob"):
        verify_config_identity(good_bytes(), "deadbeef")


def test_wrong_architecture_field_fails():
    b = good_bytes(hidden_size=4096)
    with pytest.raises(Q35QStageBlock, match="architecture conjunction failed"):
        admit_config(b, git_blob_sha1(b))


def test_wrong_num_experts_fails():
    b = good_bytes(num_experts=128)
    with pytest.raises(Q35QStageBlock, match="architecture conjunction failed"):
        admit_config(b, git_blob_sha1(b))


def test_wrong_gptq_field_fails():
    obj = good_config_obj()
    obj["quantization_config"]["bits"] = 8
    b = json.dumps(obj).encode()
    with pytest.raises(Q35QStageBlock, match="gptq conjunction failed"):
        admit_config(b, git_blob_sha1(b))


def test_duplicate_key_fails():
    body = b'{"model_type": "qwen3_5_moe", "model_type": "x"}'
    with pytest.raises(Q35QStageBlock, match="duplicate JSON key"):
        admit_config(body, git_blob_sha1(body))
