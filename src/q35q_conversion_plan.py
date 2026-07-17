"""Q35Q Phase-0 runtime conversion-plan audit (CPU-only source inspection, pure).

Order item 2 (partial) of
docs/STEER_ADDENDUM_2026-07-17_Q35Q_DYNAMIC_GPTQ_LOADER_AND_REPOSITORY_VISIBILITY_CORRECTION.md:
document the exact numbered->packed conversion the installed runtime applies, and
delimit precisely what it does and does NOT cover for the GPTQ artifact.

Frozen expected transformers conversion for `qwen3_5_moe_text` (from
`conversion_mapping.py`), inherited as `qwen3_5_text` + `qwen2_moe`:

- PrefixChange: strip `language_model` -> `model`;
- expert gate/up merge: `mlp.experts.*.gate_proj.weight` + `mlp.experts.*.up_proj.weight`
  -> `mlp.experts.gate_up_proj` via [MergeModulelist(dim=0), Concatenate(dim=1)];
- expert down merge: `mlp.experts.*.down_proj.weight` -> `mlp.experts.down_proj`
  via [MergeModulelist(dim=0)].

Critical scope fact: these WeightConverter `source_patterns` target `.weight`
tensors. The GPTQ artifact stores `.qweight/.qzeros/.scales/.g_idx` per numbered
expert, which these converters do NOT match. So the transformers global conversion
handles a STANDARD (bf16/fp16) numbered->packed merge but NOT the quantized tensors;
the GPTQ route requires a separate loader stack (Optimum QuantLinear replacement,
which cannot apply to packed nn.Parameter experts, or GPTQModel+Defuser which
defuses the model to numbered experts to match the numbered quantized checkpoint).

`verify_conversion_plan_present` checks the frozen entries are present in the
installed conversion-mapping source text so a Transformers version drift is caught.
Pure over the source text (injected) for testability.
"""
from __future__ import annotations

CONVERSION_PLAN = {
    "prefix_change": {"prefix_to_remove": "language_model", "model_prefix": "model"},
    "expert_gate_up_merge": {
        "source_patterns": ["mlp.experts.*.gate_proj.weight", "mlp.experts.*.up_proj.weight"],
        "target": "mlp.experts.gate_up_proj",
        "operations": ["MergeModulelist(dim=0)", "Concatenate(dim=1)"],
    },
    "expert_down_merge": {
        "source_patterns": ["mlp.experts.*.down_proj.weight"],
        "target": "mlp.experts.down_proj",
        "operations": ["MergeModulelist(dim=0)"],
    },
    "gptq_coverage": {
        "covers_standard_weight_experts": True,
        "covers_gptq_quant_tensors": False,
        "reason": "converter source_patterns target `.weight`, not `.qweight/.qzeros/.scales/.g_idx`",
    },
}


def verify_conversion_plan_present(conversion_source_text: str) -> dict:
    """Confirm the frozen qwen3_5_moe conversion entries are present in the installed
    Transformers conversion-mapping source (version-drift guard)."""
    t = conversion_source_text or ""
    checks = {
        "prefix_change_present":
            'PrefixChange(prefix_to_remove="language_model", model_prefix="model")' in t,
        "gate_up_source_patterns_present":
            "mlp.experts.*.gate_proj.weight" in t and "mlp.experts.*.up_proj.weight" in t,
        "gate_up_target_present": 'target_patterns="mlp.experts.gate_up_proj"' in t,
        "gate_up_operations_present": "MergeModulelist(dim=0)" in t and "Concatenate(dim=1)" in t,
        "down_source_pattern_present": "mlp.experts.*.down_proj.weight" in t,
        "down_target_present": 'target_patterns="mlp.experts.down_proj"' in t,
        "qwen3_5_moe_text_mapping_present": '"qwen3_5_moe_text"' in t and '"qwen2_moe"' in t,
    }
    checks["standard_numbered_to_packed_present"] = all(
        v for k, v in checks.items() if k != "standard_numbered_to_packed_present")
    return checks
