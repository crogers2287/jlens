"""Q35Q Phase-0 pinned-source + text-only load-manifest admission (CPU-only, pure).

Second-repair defect 4, corrected per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_SOURCE_BINDING_AND_LOAD_MANIFEST_CORRECTION.md.

The first attempt was too weak: the source hash was shape-checked not equality-
bound; the module qualname only had to be non-empty; parameter shapes were
optional; projection admission used loose `substring in name` matching (a decoy
module could satisfy it); shared/routed-expert checks were global rather than
per-layer; and vision/MTP omission relied on a deny-list rather than a positive
allow-list. This version:

- binds observed source identity to an independently derived expected identity by
  equality (outer class, text-only class, module qualname, immutable source hash);
- takes the complete frozen text-only allow-list (derived live from the pinned
  class + weight index) and requires the admitted module set to equal it exactly
  (no missing, no unapproved extra) — a positive allow-list, not a deny-list;
- verifies per-layer coverage over the agreed set: the exact projection segment
  set on every linear-/full-attention layer and shared+routed expert construction
  on every MoE layer, using exact dot-delimited segment admission (no substrings);
- makes parameter-shape evidence mandatory in the conjunction;
- keeps vision/MTP deny-list checks only as defense in depth.

Purity note: the complete expected allow-list, expected source identity, and
parameter shapes are derived by the live orchestration from the pinned immutable
implementation source and `model.safetensors.index.json`; that derivation is the
open live-composition step. Only module names and shapes are inspected — never
tensor values — and only booleans/counts leave via the verdict.
"""
from __future__ import annotations

import re

from q35q_stage import Q35QStageBlock, expected_layer_types

_HEX = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
_OUTER_CLASS = "Qwen3_5MoeForConditionalGeneration"
_TEXT_ONLY_CLASS = "Qwen3_5MoeForCausalLM"
_DELTANET_PROJ = ("in_proj_qkv", "in_proj_z", "in_proj_b", "in_proj_a", "out_proj")
_FULL_ATTN_PROJ = ("q_proj", "k_proj", "v_proj", "o_proj")
_VISION_RE = re.compile(r"(^|\.)(visual|vision|vit|image|patch_embed)(\.|$)")
_MTP_RE = re.compile(r"(^|\.)(mtp|multi_token|nextn|next_token_pred)(\.|$)")
# tensor-leaf suffixes stripped to reduce a parameter name to its owning module
_TENSOR_LEAVES = ("weight", "bias", "qweight", "qzeros", "scales", "g_idx",
                  "weight_scale", "weight_scale_inv", "act_scale")


def canonical_module_path(param_name: str) -> str:
    """Reduce a parameter tensor name to its owning module path by stripping a
    known tensor-leaf suffix. `a.b.c.weight` -> `a.b.c`; unknown leaves are kept."""
    segs = param_name.split(".")
    if len(segs) > 1 and segs[-1] in _TENSOR_LEAVES:
        return ".".join(segs[:-1])
    return param_name


def validate_source_identity(observed: dict, expected: dict) -> dict:
    """Bind observed pinned-source identity to an independently derived expected
    identity by equality. The expected values must come from the pinned immutable
    implementation source, not from the same object used to form `observed`."""
    if not isinstance(observed, dict) or not isinstance(expected, dict):
        raise Q35QStageBlock("source identities must be dicts")
    exp_sha = expected.get("source_sha")
    if not exp_sha or not _HEX.match(exp_sha):
        raise Q35QStageBlock("expected source_sha must be an immutable 40/64-hex identity")
    if expected.get("outer_class") != _OUTER_CLASS or expected.get("text_only_class") != _TEXT_ONLY_CLASS:
        raise Q35QStageBlock("expected class identities are not the admitted Qwen3.5-MoE classes")
    obs_sha = observed.get("source_sha")
    checks = {
        "outer_class_equal": observed.get("outer_class") == expected.get("outer_class"),
        "text_only_class_equal": observed.get("text_only_class") == expected.get("text_only_class"),
        "module_qualname_equal":
            bool(expected.get("module_qualname"))
            and observed.get("module_qualname") == expected.get("module_qualname"),
        "source_hash_equal":
            bool(obs_sha) and bool(_HEX.match(obs_sha or "")) and obs_sha == exp_sha,
    }
    checks["all_required_pass"] = all(v for k, v in checks.items() if k != "all_required_pass")
    return checks


def _covers_segment(paths, prefix: str) -> bool:
    """Exact dot-delimited segment admission: a path equals `prefix` or begins
    with `prefix.`. Rejects decoys where the token is only a substring."""
    return any(p == prefix or p.startswith(prefix + ".") for p in paths)


def validate_load_manifest(
    admitted_module_paths,
    expected_module_paths,
    *,
    num_layers: int = 40,
    full_attention_interval: int = 4,
    expert_layout: str = "unpacked",
    param_shapes: dict | None = None,
    expected_hidden: int = 2048,
    expected_vocab: int = 248320,
    expected_moe_intermediate: int = 512,
) -> dict:
    """Exact positive-allow-list admission of the text-only load manifest.
    `admitted_module_paths` (canonical) must equal the frozen `expected_module_paths`
    allow-list, with per-layer projection/expert coverage and mandatory shapes."""
    admitted = set(admitted_module_paths)
    expected = set(expected_module_paths)
    if not admitted or not expected:
        raise Q35QStageBlock("empty admitted or expected module set")
    if expert_layout not in ("unpacked", "packed"):
        raise Q35QStageBlock(f"unknown expert_layout: {expert_layout!r}")
    if not param_shapes:
        raise Q35QStageBlock("parameter-shape evidence is mandatory")

    unapproved = sorted(admitted - expected)
    missing = sorted(expected - admitted)
    schedule = expected_layer_types(num_layers, full_attention_interval)

    proj_ok = expert_ok = True
    for i, kind in enumerate(schedule):
        projs = _DELTANET_PROJ if kind == "linear_attention" else _FULL_ATTN_PROJ
        for p in projs:
            if not _covers_segment(expected, f"model.layers.{i}.self_attn.{p}"):
                proj_ok = False
        if not _covers_segment(expected, f"model.layers.{i}.mlp.shared_expert"):
            expert_ok = False
        routed_prefix = f"model.layers.{i}.mlp.experts"
        if expert_layout == "unpacked":
            if not any(re.match(rf"^model\.layers\.{i}\.mlp\.experts\.\d+(\.|$)", p) for p in expected):
                expert_ok = False
        else:
            if not _covers_segment(expected, routed_prefix):
                expert_ok = False

    vision_leak = [p for p in admitted if _VISION_RE.search(p)]
    mtp_leak = [p for p in admitted if _MTP_RE.search(p)]

    def _shape(key_substr, idx, val):
        for k, shp in param_shapes.items():
            if key_substr in k and len(shp) > idx and shp[idx] == val:
                return True
        return False

    checks = {
        "admitted_equals_allowlist": not unapproved and not missing,
        "no_unapproved_modules": not unapproved,
        "no_missing_modules": not missing,
        "embed_tokens_present": _covers_segment(expected, "model.embed_tokens"),
        "final_norm_present": "model.norm" in expected,
        # a distinct lm_head module in the load manifest is the untied-head evidence
        "untied_lm_head_present": "lm_head" in expected and "lm_head" in admitted,
        "per_layer_projections_present": proj_ok,
        "per_layer_experts_present": expert_ok,
        "vision_omitted_from_load": not vision_leak,
        "mtp_omitted_from_load": not mtp_leak,
        "embed_width_bound": _shape("embed_tokens", 0, expected_vocab) and _shape("embed_tokens", 1, expected_hidden),
        "lm_head_width_bound": _shape("lm_head", 0, expected_vocab),
        "expert_width_bound": _shape("experts", 0, expected_moe_intermediate) or _shape("experts", 1, expected_moe_intermediate),
    }
    checks["all_required_pass"] = all(v for k, v in checks.items() if k != "all_required_pass")
    return checks
