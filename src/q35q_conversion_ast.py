"""Q35Q Phase-0 structural (AST) conversion-plan verification (CPU-only, pure).

Per docs/STEER_ADDENDUM_2026-07-17_Q35Q_DIFFERENTIABLE_GPTQ_TORCH_BACKEND_PRIORITY.md:
a substring check over the conversion-mapping source can pass when the expected
strings appear in comments, dead code, unrelated model mappings, or reordered/
duplicate shadow objects. It is a drift hint only. This module parses the source
with `ast` and verifies the EXACT selected `qwen3_5_moe_text` conversion objects:

- `qwen3_5_text` is a list with a single `PrefixChange(prefix_to_remove="language_model",
  model_prefix="model")`;
- `qwen2_moe` is a list whose `WeightConverter` calls include the gate/up merge to
  `mlp.experts.gate_up_proj` with operations `[MergeModulelist, Concatenate]` IN ORDER
  and the down merge to `mlp.experts.down_proj` with `[MergeModulelist]`;
- `qwen3_5_moe_text` is composed from `qwen3_5_text` and `qwen2_moe`.

Comments and docstrings are not AST nodes, so they cannot satisfy the checks;
operation order is preserved by the AST, so a reordering is detected; a duplicate
shadow entry for a relevant key fails closed.
"""
from __future__ import annotations

import ast

_RELEVANT_KEYS = ("qwen3_5_text", "qwen2_moe")


def _call_name(node):
    if isinstance(node, ast.Call):
        f = node.func
        return f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
    return None


def _kw(call, name):
    for k in call.keywords:
        if k.arg == name:
            return k.value
    return None


def _str(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _str_list(node):
    if isinstance(node, ast.List):
        return [_str(e) for e in node.elts]
    s = _str(node)
    return [s] if s is not None else []


def _op_names(node):
    if not isinstance(node, ast.List):
        return []
    return [_call_name(e) for e in node.elts]


def _verify_prefix(value):
    if not isinstance(value, ast.List) or len(value.elts) != 1:
        return False
    c = value.elts[0]
    if _call_name(c) != "PrefixChange":
        return False
    return _str(_kw(c, "prefix_to_remove")) == "language_model" and _str(_kw(c, "model_prefix")) == "model"


def _verify_expert_merge(value):
    if not isinstance(value, ast.List):
        return False
    converters = [e for e in value.elts if _call_name(e) == "WeightConverter"]
    gate_up_ok = down_ok = False
    for c in converters:
        target = _str(_kw(c, "target_patterns"))
        ops = _op_names(_kw(c, "operations"))
        srcs = _str_list(_kw(c, "source_patterns"))
        if target == "mlp.experts.gate_up_proj":
            gate_up_ok = (ops == ["MergeModulelist", "Concatenate"]
                          and "mlp.experts.*.gate_proj.weight" in srcs
                          and "mlp.experts.*.up_proj.weight" in srcs)
        elif target == "mlp.experts.down_proj":
            down_ok = (ops == ["MergeModulelist"] and "mlp.experts.*.down_proj.weight" in srcs)
    return gate_up_ok and down_ok


def _verify_composition(tree):
    """qwen3_5_moe_text must be built by referencing qwen3_5_text and qwen2_moe."""
    refs = set()
    for n in ast.walk(tree):
        # mapping["qwen3_5_moe_text"] = ... / += ...
        targets = ([n.target] if isinstance(n, ast.AugAssign)
                   else n.targets if isinstance(n, ast.Assign) else [])
        for t in targets:
            if isinstance(t, ast.Subscript) and _str(t.slice) == "qwen3_5_moe_text":
                for sub in ast.walk(n.value):
                    if isinstance(sub, ast.Subscript):
                        k = _str(sub.slice)
                        if k in _RELEVANT_KEYS:
                            refs.add(k)
    return refs == set(_RELEVANT_KEYS)


def structurally_verify_conversion(source_text: str) -> dict:
    tree = ast.parse(source_text)
    # collect string-keyed dict entries; detect duplicate shadow entries of relevant keys
    entries, dup = {}, set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                ks = _str(k) if k is not None else None
                if ks in _RELEVANT_KEYS:
                    if ks in entries:
                        dup.add(ks)
                    entries[ks] = v
    checks = {
        "no_duplicate_shadow_mapping": not dup,
        "qwen3_5_text_prefix_change": _verify_prefix(entries.get("qwen3_5_text")),
        "qwen2_moe_expert_merge": _verify_expert_merge(entries.get("qwen2_moe")),
        "qwen3_5_moe_text_composed": _verify_composition(tree),
    }
    checks["structural_pass"] = all(v for k, v in checks.items() if k != "structural_pass")
    return checks
