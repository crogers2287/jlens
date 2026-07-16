"""Q35Q Phase-0 pinned-source + text-only load-manifest admission (CPU-only, pure).

Second-repair defect 4 per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_PHASE0_SECOND_CORRECTION_AND_M39_PREGEN_PROBE.md.

Configuration agreement (already covered by `q35q_stage.validate_text_architecture`)
is necessary but not sufficient. This module adds the source-and-load-manifest
proofs the correction requires: the admitted text-only `Qwen3_5MoeForCausalLM`
class/source mapping, Gated DeltaNet projection identities on each linear-attention
layer, standard attention projections on each full-attention layer, shared-expert
construction, final RMS norm, an untied 248320-wide LM head, and — the checks a
config alone cannot make — that vision modules and MTP modules present in the
repository are *omitted from the admitted load manifest* (the set of modules the
text-only load path actually instantiates).

Purity note: the validators compare an already-derived load manifest and source
identity against frozen expectations. The live orchestration is responsible for
deriving the admitted module set from the pinned `model.safetensors.index.json`
weight map and the pinned implementation source; that live derivation remains the
open live-CLI wiring step. Module names only — never tensor values — are inspected,
and only booleans/counts leave via the returned verdict.
"""
from __future__ import annotations

import re

from q35q_stage import Q35QStageBlock, expected_layer_types

_HEX = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
_OUTER_CLASS = "Qwen3_5MoeForConditionalGeneration"
_TEXT_ONLY_CLASS = "Qwen3_5MoeForCausalLM"
_DELTANET_PROJ = ("in_proj_qkv", "in_proj_z", "in_proj_b", "in_proj_a", "out_proj")
_FULL_ATTN_PROJ = ("q_proj", "k_proj", "v_proj", "o_proj")
# Any admitted module name matching these means vision/MTP leaked into the
# text-only load manifest.
_VISION_RE = re.compile(r"(^|\.)(visual|vision|vit|image|patch_embed)(\.|$)")
_MTP_RE = re.compile(r"(^|\.)(mtp|multi_token|nextn|next_token_pred)(\.|$)")


def validate_source_identity(source: dict) -> dict:
    """Bind the pinned implementation-source class mapping. `source` carries the
    outer class, the admitted text-only class, its module qualname, and an
    immutable source hash (commit sha1 or file sha256)."""
    if not isinstance(source, dict):
        raise Q35QStageBlock("source identity must be a dict")
    checks = {
        "outer_class_admitted": source.get("outer_class") == _OUTER_CLASS,
        "text_only_class_admitted": source.get("text_only_class") == _TEXT_ONLY_CLASS,
        "module_qualname_present": bool(source.get("module_qualname")),
        "source_hash_immutable":
            bool(source.get("source_sha")) and bool(_HEX.match(source.get("source_sha") or "")),
    }
    checks["all_required_pass"] = all(v for k, v in checks.items() if k != "all_required_pass")
    return checks


def _layer_module(names, layer, leaf):
    prefix = f"model.layers.{layer}."
    return any(n.startswith(prefix) and leaf in n for n in names)


def validate_load_manifest(
    admitted_module_names,
    *,
    tie_word_embeddings: bool,
    num_layers: int = 40,
    full_attention_interval: int = 4,
    param_shapes: dict | None = None,
    expected_hidden: int = 2048,
    expected_vocab: int = 248320,
    expected_moe_intermediate: int = 512,
) -> dict:
    """Validate that the admitted text-only load manifest instantiates exactly the
    admitted modules and omits vision/MTP. `admitted_module_names` is the set of
    module (parameter-owning) names the text-only load path admits."""
    names = list(admitted_module_names)
    if not names:
        raise Q35QStageBlock("empty admitted load manifest")
    schedule = expected_layer_types(num_layers, full_attention_interval)

    vision_leak = [n for n in names if _VISION_RE.search(n)]
    mtp_leak = [n for n in names if _MTP_RE.search(n)]

    # per-layer projection identities according to the hybrid schedule
    deltanet_ok = full_attn_ok = True
    for i, kind in enumerate(schedule):
        if kind == "linear_attention":
            if not all(_layer_module(names, i, p) for p in _DELTANET_PROJ):
                deltanet_ok = False
        else:  # full_attention
            if not all(_layer_module(names, i, p) for p in _FULL_ATTN_PROJ):
                full_attn_ok = False

    shapes = param_shapes or {}

    def _shape(key_substr, idx, val):
        for k, shp in shapes.items():
            if key_substr in k and len(shp) > idx and shp[idx] == val:
                return True
        return False

    checks = {
        "embed_tokens_present": any("embed_tokens" in n for n in names),
        "final_norm_present": any(n == "model.norm" or n.endswith(".model.norm")
                                  or n == "model.norm.weight" for n in names),
        "lm_head_present": any("lm_head" in n for n in names),
        "untied_lm_head": tie_word_embeddings is False and any("lm_head" in n for n in names),
        "shared_expert_present": any("shared_expert" in n for n in names),
        "routed_experts_present": any(re.search(r"experts\.\d+\.", n) for n in names),
        "gated_deltanet_projections_present": deltanet_ok,
        "full_attention_projections_present": full_attn_ok,
        "vision_omitted_from_load": not vision_leak,
        "mtp_omitted_from_load": not mtp_leak,
    }
    if shapes:
        checks["embed_width_bound"] = _shape("embed_tokens", 0, expected_vocab) and _shape("embed_tokens", 1, expected_hidden)
        checks["lm_head_width_bound"] = _shape("lm_head", 0, expected_vocab)
        checks["expert_width_bound"] = _shape("experts.", 0, expected_moe_intermediate) or _shape("experts.", 1, expected_moe_intermediate)
    checks["all_required_pass"] = all(v for k, v in checks.items()
                                      if isinstance(v, bool) and k != "all_required_pass")
    return checks
