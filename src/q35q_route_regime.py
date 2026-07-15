"""Q35Q route-regime diagnostic artifact schema (CPU-only, aggregate-only).

This module binds the pre-registered route-regime evidence required before the
Phase-2 micro-fit. It accepts only the committed aggregate schema, rejects
unknown fields, and emits no raw router logits, expert identities, token-level
routes, or per-example margins. The artifact is diagnostic and never replaces
the exact-VJP gate.
"""
from __future__ import annotations

import hashlib
import json
import math
import re

from q35q_phase0 import (
    MEM_GIB_PER_GPU,
    MEM_GIB_TOTAL,
    QWEN35_35B_A3B_ARCH,
    Q35QBlock,
    scan_aggregate_only,
)

BIAS_CONVENTIONS = ("pre_bias", "post_bias")
SOFTMAX_CONVENTIONS = ("pre_softmax", "post_softmax")
ROUTE_REGIME_READY = "q35q_route_regime_ready"
REQUIRED_MARGIN_QUANTILES = (0.0, 0.1, 0.5, 0.9, 1.0)
ROUTE_LOAD_KEYS = ("mean_load", "max_load", "load_cv", "zero_load_fraction")
ROUTE_TRANSITION_KEYS = ("mean_route_changes", "fraction_with_any_change")

REQUIRED_FIELDS = (
    "router_module_ids", "router_tensor_ids", "observed_layers",
    "top_k", "num_routed_experts", "num_shared_experts",
    "bias_convention", "softmax_convention", "route_parity_repeated",
    "near_boundary_threshold", "threshold_manifest_sha256",
    "margin_quantiles", "fraction_below_threshold",
    "route_load_summary", "route_transition_summary",
    "token_parity_exact", "logit_parity_within_tol", "no_offload",
    "hook_overhead_s", "peak_gib_per_gpu", "peak_gib_total", "source_hashes",
)

_NUM_LAYERS = QWEN35_35B_A3B_ARCH["num_hidden_layers"]
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _num(value, name, lo=None, hi=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Q35QBlock(f"{name} must be a finite number")
    try:
        finite = math.isfinite(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise Q35QBlock(f"{name} must be a finite number") from exc
    if not finite:
        raise Q35QBlock(f"{name} must be a finite number")
    if lo is not None and value < lo:
        raise Q35QBlock(f"{name} below {lo}")
    if hi is not None and value > hi:
        raise Q35QBlock(f"{name} above {hi}")
    return value


def _strict_arch_int(meta, name, expected):
    value = meta[name]
    if type(value) is not int or value != expected:
        raise Q35QBlock(f"{name} mismatch vs frozen architecture")
    return value


def _true(value, name):
    if type(value) is not bool or value is not True:
        raise Q35QBlock(f"{name} must be True")
    return True


def _sha256(value, name):
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise Q35QBlock(f"{name} must be a lowercase SHA-256 digest")
    return value


def _identity_list(value, name, count):
    if not isinstance(value, (list, tuple)) or len(value) != count:
        raise Q35QBlock(f"{name} must contain exactly one identity per observed layer")
    if any(not isinstance(item, str) or not item for item in value):
        raise Q35QBlock(f"{name} must contain non-empty strings")
    if len(set(value)) != len(value):
        raise Q35QBlock(f"{name} contains duplicates")
    return tuple(value)


def _summary(meta, name, expected_keys, ranges):
    value = meta[name]
    if not isinstance(value, dict) or set(value) != set(expected_keys):
        raise Q35QBlock(f"{name} keys do not match the committed schema")
    out = {}
    for key in expected_keys:
        lo, hi = ranges[key]
        out[key] = float(_num(value[key], f"{name}.{key}", lo=lo, hi=hi))
    return out


def build_route_regime_artifact(meta: dict) -> dict:
    """Validate and emit the public aggregate-only route-regime artifact."""
    if not isinstance(meta, dict):
        raise Q35QBlock("route-regime metadata must be a dict")
    missing = sorted(set(REQUIRED_FIELDS).difference(meta))
    extra = sorted(set(meta).difference(REQUIRED_FIELDS))
    if missing:
        raise Q35QBlock(f"missing route-regime fields: {','.join(missing)}")
    if extra:
        raise Q35QBlock(f"unknown route-regime fields: {','.join(extra)}")

    layers_value = meta["observed_layers"]
    if not isinstance(layers_value, (list, tuple)) or not layers_value:
        raise Q35QBlock("observed_layers must be a non-empty ordered sequence")
    layers = tuple(layers_value)
    if any(type(layer) is not int or not (0 <= layer < _NUM_LAYERS) for layer in layers):
        raise Q35QBlock("observed_layers out of range")
    if tuple(sorted(set(layers))) != layers:
        raise Q35QBlock("observed_layers must be unique and strictly increasing")

    module_ids = _identity_list(meta["router_module_ids"], "router_module_ids", len(layers))
    tensor_ids = _identity_list(meta["router_tensor_ids"], "router_tensor_ids", len(layers))

    _strict_arch_int(meta, "top_k", QWEN35_35B_A3B_ARCH["num_experts_per_tok"])
    _strict_arch_int(meta, "num_routed_experts", QWEN35_35B_A3B_ARCH["num_routed_experts"])
    _strict_arch_int(meta, "num_shared_experts", QWEN35_35B_A3B_ARCH["num_shared_experts"])

    if type(meta["bias_convention"]) is not str or meta["bias_convention"] not in BIAS_CONVENTIONS:
        raise Q35QBlock("unknown bias convention")
    if type(meta["softmax_convention"]) is not str or meta["softmax_convention"] not in SOFTMAX_CONVENTIONS:
        raise Q35QBlock("unknown softmax convention")

    _true(meta["route_parity_repeated"], "route_parity_repeated")
    threshold = float(_num(meta["near_boundary_threshold"], "near_boundary_threshold", lo=0))
    if threshold <= 0:
        raise Q35QBlock("near_boundary_threshold must be positive")
    threshold_manifest = _sha256(meta["threshold_manifest_sha256"],
                                 "threshold_manifest_sha256")
    fraction_below = float(_num(meta["fraction_below_threshold"],
                                "fraction_below_threshold", lo=0.0, hi=1.0))

    quantiles = meta["margin_quantiles"]
    if not isinstance(quantiles, dict) or set(quantiles) != set(REQUIRED_MARGIN_QUANTILES):
        raise Q35QBlock("margin_quantiles keys do not match the committed schema")
    quantile_values = []
    for probability in REQUIRED_MARGIN_QUANTILES:
        quantile_values.append(float(_num(
            quantiles[probability], f"margin_quantiles[{probability}]", lo=0.0
        )))
    if any(right < left for left, right in zip(quantile_values, quantile_values[1:])):
        raise Q35QBlock("margin_quantiles must be non-decreasing")

    load = _summary(
        meta, "route_load_summary", ROUTE_LOAD_KEYS,
        {
            "mean_load": (0.0, 1.0),
            "max_load": (0.0, 1.0),
            "load_cv": (0.0, None),
            "zero_load_fraction": (0.0, 1.0),
        },
    )
    if load["max_load"] < load["mean_load"]:
        raise Q35QBlock("max_load may not be below mean_load")
    transitions = _summary(
        meta, "route_transition_summary", ROUTE_TRANSITION_KEYS,
        {
            "mean_route_changes": (0.0, float(max(len(layers) - 1, 0))),
            "fraction_with_any_change": (0.0, 1.0),
        },
    )

    _true(meta["token_parity_exact"], "token_parity_exact")
    _true(meta["logit_parity_within_tol"], "logit_parity_within_tol")
    _true(meta["no_offload"], "no_offload")
    hook_overhead = float(_num(meta["hook_overhead_s"], "hook_overhead_s", lo=0.0))
    peak_per_gpu = float(_num(meta["peak_gib_per_gpu"], "peak_gib_per_gpu",
                              lo=0.0, hi=MEM_GIB_PER_GPU))
    peak_total = float(_num(meta["peak_gib_total"], "peak_gib_total",
                            lo=0.0, hi=MEM_GIB_TOTAL))

    source_hashes = meta["source_hashes"]
    if not isinstance(source_hashes, dict) or not source_hashes:
        raise Q35QBlock("source_hashes must be a non-empty dict")
    if any(not isinstance(name, str) or not name for name in source_hashes):
        raise Q35QBlock("source_hashes keys must be non-empty strings")
    for name, digest in source_hashes.items():
        _sha256(digest, f"source_hashes[{name}]")

    binding_payload = [
        {"layer": layer, "module": module_id, "tensor": tensor_id}
        for layer, module_id, tensor_id in zip(layers, module_ids, tensor_ids, strict=True)
    ]
    binding_digest = hashlib.sha256(json.dumps(
        binding_payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()

    artifact = {
        "outcome": ROUTE_REGIME_READY,
        "observed_layer_count": len(layers),
        "router_binding_count": len(binding_payload),
        "router_binding_sha256": binding_digest,
        "top_k": meta["top_k"],
        "num_routed_experts": meta["num_routed_experts"],
        "num_shared_experts": meta["num_shared_experts"],
        "bias_convention": meta["bias_convention"],
        "softmax_convention": meta["softmax_convention"],
        "route_parity_repeated": True,
        "near_boundary_threshold": threshold,
        "threshold_manifest_sha256": threshold_manifest,
        "fraction_below_threshold": fraction_below,
        "margin_quantiles": {
            str(probability): value
            for probability, value in zip(REQUIRED_MARGIN_QUANTILES, quantile_values, strict=True)
        },
        "route_load_summary": load,
        "route_transition_summary": transitions,
        "token_parity_exact": True,
        "logit_parity_within_tol": True,
        "no_offload": True,
        "hook_overhead_s": hook_overhead,
        "peak_gib_per_gpu": peak_per_gpu,
        "peak_gib_total": peak_total,
        "source_hash_count": len(source_hashes),
    }
    scan_aggregate_only(artifact)
    return artifact
