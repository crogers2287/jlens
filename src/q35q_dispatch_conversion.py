"""Q35Q Phase-0 dispatch-bound conversion verification (CPU-only, pure + injected).

Corrects the AST verifier per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_AST_DISPATCH_AND_SOURCE_PIN_COMPOSITION_CORRECTION.md.
Parsing arbitrary dict literals could not (1) bind to the exact dispatch-selected
mapping object, (3) check constructor dimensions, (4) require exact source-pattern
equality, (5) require exact converter multiplicity, or (6) prove no later overwrite.

The fix inspects the LIVE composed mapping the loader dispatch actually returns
(`transformers.conversion_mapping.get_checkpoint_conversion_mapping(model_type)`),
which is the final post-composition object — immune to later overwrite/mutation and
bound to the exact model_type. Each converter is checked for exact target patterns,
exact source-pattern lists, exact operation ordering AND dimensions, and exact
converter multiplicity (no extra converter targeting the packed expert tensors).

Pure over an already-extracted structured list so the exact-equality logic is
unit-testable; `extract_mapping` reads the live converter objects' attributes.
"""
from __future__ import annotations

from q35q_stage import Q35QStageBlock

EXPECTED_PREFIX = {"prefix_to_remove": "language_model", "model_prefix": "model"}
EXPECTED_GATE_UP = {
    "target": ["mlp.experts.gate_up_proj"],
    "source": ["mlp.experts.*.gate_proj.weight", "mlp.experts.*.up_proj.weight"],
    "ops": [("MergeModulelist", 0), ("Concatenate", 1)],
}
EXPECTED_DOWN = {
    "target": ["mlp.experts.down_proj"],
    "source": ["mlp.experts.*.down_proj.weight"],
    "ops": [("MergeModulelist", 0)],
}
_PACKED_TARGETS = (EXPECTED_GATE_UP["target"], EXPECTED_DOWN["target"])


def _as_list(x):
    if x is None:
        return []
    return [x] if isinstance(x, str) else list(x)


def extract_converter(conv) -> dict:
    """Structured extraction of one live converter object (attributes, not source)."""
    kind = type(conv).__name__
    if kind == "PrefixChange":
        return {"kind": "PrefixChange",
                "prefix_to_remove": getattr(conv, "prefix_to_remove", None),
                "model_prefix": getattr(conv, "model_prefix", None)}
    return {"kind": kind,
            "target": _as_list(getattr(conv, "target_patterns", None)),
            "source": _as_list(getattr(conv, "source_patterns", None)),
            "ops": [(type(o).__name__, getattr(o, "dim", None))
                    for o in (getattr(conv, "operations", None) or [])]}


def extract_mapping(mapping_list) -> list:
    return [extract_converter(c) for c in mapping_list]


def verify_dispatch_conversion(extracted) -> dict:
    """Exact verification of the dispatch-selected qwen3_5_moe_text conversion."""
    if not extracted:
        raise Q35QStageBlock("empty dispatch conversion mapping")
    prefixes = [e for e in extracted if e.get("kind") == "PrefixChange"]
    gate_up = [e for e in extracted if e.get("target") == EXPECTED_GATE_UP["target"]]
    down = [e for e in extracted if e.get("target") == EXPECTED_DOWN["target"]]
    packed_targeting = [e for e in extracted if e.get("target") in _PACKED_TARGETS]
    checks = {
        "prefix_change_exact": any(
            p.get("prefix_to_remove") == EXPECTED_PREFIX["prefix_to_remove"]
            and p.get("model_prefix") == EXPECTED_PREFIX["model_prefix"] for p in prefixes),
        "exactly_one_gate_up_converter": len(gate_up) == 1,
        "exactly_one_down_converter": len(down) == 1,
        "gate_up_source_exact": len(gate_up) == 1 and gate_up[0]["source"] == EXPECTED_GATE_UP["source"],
        "gate_up_ops_exact": len(gate_up) == 1 and gate_up[0]["ops"] == EXPECTED_GATE_UP["ops"],
        "down_source_exact": len(down) == 1 and down[0]["source"] == EXPECTED_DOWN["source"],
        "down_ops_exact": len(down) == 1 and down[0]["ops"] == EXPECTED_DOWN["ops"],
        "no_extra_packed_expert_converters": len(packed_targeting) == 2,
    }
    checks["dispatch_conversion_pass"] = all(
        v for k, v in checks.items() if k != "dispatch_conversion_pass")
    return checks
