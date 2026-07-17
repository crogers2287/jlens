"""Q35Q structural (AST) conversion-plan verification tests (CPU-only, no network).

Proves the AST verifier passes on the real composed mapping and FAILS when the
expected strings appear only in comments/dead code, when operations are reordered,
when the merge lives under an unrelated model key, and when a duplicate shadow
mapping is present -- the failure modes a substring check cannot catch.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from q35q_conversion_ast import structurally_verify_conversion

GOOD = '''
mapping = {
    "qwen3_5_text": [PrefixChange(prefix_to_remove="language_model", model_prefix="model")],
    "qwen2_moe": [
        WeightConverter(
            source_patterns=["mlp.experts.*.gate_proj.weight", "mlp.experts.*.up_proj.weight"],
            target_patterns="mlp.experts.gate_up_proj",
            operations=[MergeModulelist(dim=0), Concatenate(dim=1)]),
        WeightConverter(
            source_patterns="mlp.experts.*.down_proj.weight",
            target_patterns="mlp.experts.down_proj",
            operations=[MergeModulelist(dim=0)]),
    ],
}
mapping["qwen3_5_moe_text"] = mapping["qwen3_5_text"].copy()
mapping["qwen3_5_moe_text"] += mapping["qwen2_moe"].copy()
'''


def test_structural_pass():
    out = structurally_verify_conversion(GOOD)
    assert out["structural_pass"] is True


def test_strings_only_in_comments_fail():
    src = '''
mapping = {
    # qwen3_5_text: PrefixChange(prefix_to_remove="language_model", model_prefix="model")
    # qwen2_moe: WeightConverter(target_patterns="mlp.experts.gate_up_proj",
    #   operations=[MergeModulelist(dim=0), Concatenate(dim=1)])
    "other_model": [],
}
'''
    out = structurally_verify_conversion(src)
    assert out["structural_pass"] is False
    assert out["qwen2_moe_expert_merge"] is False and out["qwen3_5_text_prefix_change"] is False


def test_reordered_operations_fail():
    bad = GOOD.replace("[MergeModulelist(dim=0), Concatenate(dim=1)]",
                       "[Concatenate(dim=1), MergeModulelist(dim=0)]")
    out = structurally_verify_conversion(bad)
    assert out["qwen2_moe_expert_merge"] is False and out["structural_pass"] is False


def test_merge_under_unrelated_key_fails():
    bad = GOOD.replace('"qwen2_moe": [', '"unrelated_moe": [')
    out = structurally_verify_conversion(bad)
    assert out["qwen2_moe_expert_merge"] is False and out["structural_pass"] is False


def test_duplicate_shadow_mapping_fails():
    bad = GOOD.replace(
        '"qwen2_moe": [',
        '"qwen2_moe": [WeightConverter(source_patterns="x", target_patterns="y", operations=[])],\n    "qwen2_moe": [',
        1)
    out = structurally_verify_conversion(bad)
    assert out["no_duplicate_shadow_mapping"] is False and out["structural_pass"] is False


def test_missing_prefix_fails():
    bad = GOOD.replace('PrefixChange(prefix_to_remove="language_model", model_prefix="model")',
                       'PrefixChange(prefix_to_remove="wrong", model_prefix="model")')
    out = structurally_verify_conversion(bad)
    assert out["qwen3_5_text_prefix_change"] is False and out["structural_pass"] is False


def test_missing_composition_fails():
    bad = GOOD.split('mapping["qwen3_5_moe_text"]')[0]  # drop the composition statements
    out = structurally_verify_conversion(bad)
    assert out["qwen3_5_moe_text_composed"] is False and out["structural_pass"] is False
