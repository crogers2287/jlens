"""Q35Q Phase-0 source-derived text-only allow-list (CPU-only, pure + injected ctor).

Corrected-composition item 2 per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_LIVE_COMPOSITION_SELF_BINDING_AND_HEADER_GATE.md:
"Derive the complete expected text-only module allow-list from the pinned
implementation source or a deterministic meta-device construction that does not
inspect the weight index; independently derive the admitted set from the pinned
weight index; require exact equality."

A bounded meta-device construction of the admitted text-only `Qwen3_5MoeForCausalLM`
class (no weights, no GPU, no memory: `with torch.device('meta')`) yields the real
per-layer module templates. Because the source represents routed experts as a
single PACKED module per layer (`mlp.experts.gate_up_proj` / `mlp.experts.down_proj`)
whose module count does not scale with `num_experts`, a reduced-layer construction
is structurally faithful and can be expanded to the full layer schedule.

These functions are pure over already-enumerated module names so they unit-test
without constructing a model; the thin live derivation supplies real names from a
meta model. This is the SOURCE side; the artifact side comes from the weight index
(`q35q_safetensors_header` / index weight_map). The two must be reconciled under a
frozen packed<->numbered expert representation map before an equality pass — that
reconciliation is the explicit remaining gate.
"""
from __future__ import annotations

import re

from q35q_stage import Q35QStageBlock, expected_layer_types
from q35q_source_admission import canonical_module_path

_LAYER_RE = re.compile(r"^model\.layers\.(\d+)\.(.+)$")


def canonical_source_modules(param_names) -> set:
    """Canonical module-path set from a constructed model's parameter names."""
    mods = {canonical_module_path(n) for n in param_names}
    if not mods:
        raise Q35QStageBlock("no source modules enumerated")
    return mods


def extract_templates(module_set, num_layers: int) -> dict:
    """Split a source module set into top-level modules and per-layer relative
    templates keyed by the layer index actually present (reduced construction)."""
    top, per_layer = set(), {}
    for m in module_set:
        mo = _LAYER_RE.match(m)
        if mo:
            idx, rel = int(mo.group(1)), mo.group(2)
            per_layer.setdefault(idx, set()).add(rel)
        else:
            top.add(m)
    if not per_layer:
        raise Q35QStageBlock("no per-layer modules found in source set")
    return {"top_level": top, "per_layer": per_layer}


def classify_layer_templates(templates: dict, num_layers: int, interval: int) -> dict:
    """Assign the reduced per-layer templates to linear/full attention kinds using
    the frozen hybrid schedule, and require one representative template per kind."""
    schedule = expected_layer_types(num_layers, interval)
    by_kind = {}
    for idx, rel in templates["per_layer"].items():
        kind = schedule[idx] if idx < len(schedule) else None
        if kind is None:
            raise Q35QStageBlock(f"reduced layer index {idx} outside schedule")
        # keep each kind's template as the exact set from the first seen layer of
        # that kind; require identical templates across same-kind layers
        if kind in by_kind and by_kind[kind] != rel:
            raise Q35QStageBlock(f"inconsistent {kind} templates across layers")
        by_kind[kind] = rel
    if "linear_attention" not in by_kind or "full_attention" not in by_kind:
        raise Q35QStageBlock("reduced construction must cover both attention kinds")
    return by_kind


def expand_source_allowlist(top_level, templates_by_kind, num_layers: int, interval: int) -> set:
    """Expand the per-kind templates over the full frozen layer schedule into the
    complete source-derived text-only module allow-list."""
    schedule = expected_layer_types(num_layers, interval)
    allow = set(top_level)
    for i, kind in enumerate(schedule):
        tmpl = templates_by_kind.get(kind)
        if not tmpl:
            raise Q35QStageBlock(f"no template for layer kind {kind}")
        for rel in tmpl:
            allow.add(f"model.layers.{i}.{rel}")
    return allow


def derive_source_allowlist_from_modules(param_names, num_layers: int = 40, interval: int = 4) -> dict:
    """End-to-end pure derivation: canonical modules -> templates -> classify ->
    expand. Returns the full allow-list + the per-kind templates (aggregate)."""
    mods = canonical_source_modules(param_names)
    templates = extract_templates(mods, num_layers)
    by_kind = classify_layer_templates(templates, num_layers, interval)
    allow = expand_source_allowlist(templates["top_level"], by_kind, num_layers, interval)
    return {
        "allowlist": allow,
        "allowlist_size": len(allow),
        "top_level": sorted(templates["top_level"]),
        "linear_template_size": len(by_kind["linear_attention"]),
        "full_template_size": len(by_kind["full_attention"]),
    }
