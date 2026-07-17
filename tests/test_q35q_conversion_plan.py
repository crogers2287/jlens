"""Q35Q conversion-plan verifier tests (CPU-only, no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from q35q_conversion_plan import CONVERSION_PLAN, verify_conversion_plan_present

# minimal source text modeled on the real transformers conversion_mapping.py entries
GOOD = '''
"qwen3_5_text": [PrefixChange(prefix_to_remove="language_model", model_prefix="model")],
"qwen2_moe": [
  WeightConverter(source_patterns=["mlp.experts.*.gate_proj.weight","mlp.experts.*.up_proj.weight"],
                  target_patterns="mlp.experts.gate_up_proj",
                  operations=[MergeModulelist(dim=0), Concatenate(dim=1)]),
  WeightConverter(source_patterns="mlp.experts.*.down_proj.weight",
                  target_patterns="mlp.experts.down_proj", operations=[MergeModulelist(dim=0)]),
],
mapping["qwen3_5_moe_text"] = mapping["qwen3_5_text"].copy()
mapping["qwen3_5_moe_text"] += mapping["qwen2_moe"].copy()
'''


def test_plan_present():
    out = verify_conversion_plan_present(GOOD)
    assert out["standard_numbered_to_packed_present"] is True
    assert out["prefix_change_present"] and out["gate_up_operations_present"]


def test_missing_prefix_change_fails():
    out = verify_conversion_plan_present(GOOD.replace(
        'PrefixChange(prefix_to_remove="language_model", model_prefix="model")', ""))
    assert out["prefix_change_present"] is False
    assert out["standard_numbered_to_packed_present"] is False


def test_missing_merge_ops_fails():
    out = verify_conversion_plan_present(GOOD.replace("MergeModulelist(dim=0)", ""))
    assert out["gate_up_operations_present"] is False
    assert out["standard_numbered_to_packed_present"] is False


def test_empty_source_fails():
    out = verify_conversion_plan_present("")
    assert out["standard_numbered_to_packed_present"] is False


def test_plan_documents_gptq_gap():
    assert CONVERSION_PLAN["gptq_coverage"]["covers_standard_weight_experts"] is True
    assert CONVERSION_PLAN["gptq_coverage"]["covers_gptq_quant_tensors"] is False
