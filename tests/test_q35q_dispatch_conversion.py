"""Q35Q dispatch-bound conversion verification tests (CPU-only, no network).

Uses structured extractions modeled on the live qwen3_5_moe_text mapping and proves
exact-equality failure on wrong merge/concat dimensions, extra/duplicate source
patterns, duplicate relevant converters, an extra converter targeting the packed
tensors, and a missing prefix change -- the failure modes the AST verifier missed.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_dispatch_conversion import verify_dispatch_conversion


def good():
    return [
        {"kind": "PrefixChange", "prefix_to_remove": "language_model", "model_prefix": "model"},
        {"kind": "WeightConverter", "target": ["mlp.experts.gate_up_proj"],
         "source": ["mlp.experts.*.gate_proj.weight", "mlp.experts.*.up_proj.weight"],
         "ops": [("MergeModulelist", 0), ("Concatenate", 1)]},
        {"kind": "WeightConverter", "target": ["mlp.experts.down_proj"],
         "source": ["mlp.experts.*.down_proj.weight"], "ops": [("MergeModulelist", 0)]},
    ]


def test_pass():
    out = verify_dispatch_conversion(good())
    assert out["dispatch_conversion_pass"] is True


def test_wrong_concat_dim_fails():
    m = good(); m[1]["ops"] = [("MergeModulelist", 0), ("Concatenate", 0)]
    out = verify_dispatch_conversion(m)
    assert out["gate_up_ops_exact"] is False and out["dispatch_conversion_pass"] is False


def test_wrong_merge_dim_fails():
    m = good(); m[2]["ops"] = [("MergeModulelist", 1)]
    out = verify_dispatch_conversion(m)
    assert out["down_ops_exact"] is False and out["dispatch_conversion_pass"] is False


def test_reordered_ops_fails():
    m = good(); m[1]["ops"] = [("Concatenate", 1), ("MergeModulelist", 0)]
    out = verify_dispatch_conversion(m)
    assert out["gate_up_ops_exact"] is False and out["dispatch_conversion_pass"] is False


def test_extra_source_pattern_fails():
    m = good(); m[1]["source"].append("mlp.experts.*.bias")
    out = verify_dispatch_conversion(m)
    assert out["gate_up_source_exact"] is False and out["dispatch_conversion_pass"] is False


def test_duplicate_gate_up_converter_fails():
    m = good(); m.append(copy.deepcopy(m[1]))
    out = verify_dispatch_conversion(m)
    assert out["exactly_one_gate_up_converter"] is False
    assert out["no_extra_packed_expert_converters"] is False and out["dispatch_conversion_pass"] is False


def test_extra_packed_converter_fails():
    m = good()
    m.append({"kind": "WeightConverter", "target": ["mlp.experts.gate_up_proj"],
              "source": ["decoy.weight"], "ops": [("Transpose", 1)]})
    out = verify_dispatch_conversion(m)
    assert out["no_extra_packed_expert_converters"] is False and out["dispatch_conversion_pass"] is False


def test_missing_prefix_fails():
    m = [e for e in good() if e["kind"] != "PrefixChange"]
    out = verify_dispatch_conversion(m)
    assert out["prefix_change_exact"] is False and out["dispatch_conversion_pass"] is False


def test_wrong_prefix_value_fails():
    m = good(); m[0]["prefix_to_remove"] = "wrong"
    out = verify_dispatch_conversion(m)
    assert out["prefix_change_exact"] is False and out["dispatch_conversion_pass"] is False


def test_extra_prefix_converter_fails():
    m = good(); m.insert(0, {"kind": "PrefixChange", "prefix_to_remove": "language_model", "model_prefix": "model"})
    out = verify_dispatch_conversion(m)
    assert out["exactly_one_prefix_change"] is False and out["exact_total_object_count"] is False
    assert out["dispatch_conversion_pass"] is False


def test_exact_total_count_enforced():
    m = good(); m.append({"kind": "WeightConverter", "target": ["other.thing"],
                          "source": ["x"], "ops": [("Transpose", 1)]})
    out = verify_dispatch_conversion(m)
    assert out["exact_total_object_count"] is False and out["dispatch_conversion_pass"] is False


def test_empty_fails():
    with pytest.raises(Q35QStageBlock, match="empty dispatch"):
        verify_dispatch_conversion([])
