"""Q35Q route-regime diagnostic artifact schema (CPU-only, aggregate-only).

The route-regime/exact-sharding addendum requires that, before the Phase-2
micro-fit, the Phase-1-passing path produce an aggregate-only route-regime
artifact whose formulas are committed before collection. This module validates
and emits that artifact and fails closed on missing/ill-formed evidence or any
privacy leak. It is diagnostic — it does not replace the exact-VJP gate.

Binds: router module/tensor identities per observed MoE layer; top-k and
routed/shared/bias/softmax conventions; repeated-forward route parity; a
PRE-registered near-boundary threshold (set before margins) plus the aggregate
fraction below it; selected-boundary margin quantiles; route-load/transition
summaries; token/logit parity, hook overhead, memory, offload, and source
hashes. Raw router logits, expert identities, token-level routes, and
per-example margins remain private and are NOT accepted here.

See docs/STEER_ADDENDUM_2026-07-15_Q35Q_ROUTE_REGIME_AND_EXACT_SHARDING.md.
"""
from __future__ import annotations

import math

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

REQUIRED_FIELDS = (
    "router_module_ids", "observed_layers", "top_k", "num_routed_experts",
    "num_shared_experts", "bias_convention", "softmax_convention",
    "route_parity_repeated", "near_boundary_threshold",
    "threshold_committed_before_margins", "margin_quantiles",
    "fraction_below_threshold", "route_load_summary", "route_transition_summary",
    "token_parity_exact", "logit_parity_within_tol", "no_offload",
    "hook_overhead_s", "peak_gib_per_gpu", "peak_gib_total", "source_hashes",
)

_NUM_LAYERS = QWEN35_35B_A3B_ARCH["num_hidden_layers"]


def _num(v, name, lo=None, hi=None):
    if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
        raise Q35QBlock(f"{name} must be a finite number")
    if lo is not None and v < lo:
        raise Q35QBlock(f"{name} below {lo}")
    if hi is not None and v > hi:
        raise Q35QBlock(f"{name} above {hi}")
    return v


def _true(v, name):
    if v is not True:
        raise Q35QBlock(f"{name} must be True")
    return True


def build_route_regime_artifact(meta: dict) -> dict:
    """Validate route-regime metadata and return the aggregate-only artifact.
    Fails closed (Q35QBlock) on any missing/ill-formed field or privacy leak."""
    missing = [f for f in REQUIRED_FIELDS
               if f not in meta or meta[f] in (None, "", [], {})]
    if missing:
        raise Q35QBlock(f"missing route-regime fields: {','.join(sorted(missing))}")

    router_ids = list(meta["router_module_ids"])
    if not router_ids or any(not isinstance(x, str) or not x for x in router_ids):
        raise Q35QBlock("router_module_ids must be non-empty strings")

    layers = list(meta["observed_layers"])
    if not layers or any(type(i) is not int or not (0 <= i < _NUM_LAYERS) for i in layers):
        raise Q35QBlock("observed_layers out of range")

    if meta["top_k"] != QWEN35_35B_A3B_ARCH["num_experts_per_tok"]:
        raise Q35QBlock("top_k mismatch vs frozen architecture")
    if meta["num_routed_experts"] != QWEN35_35B_A3B_ARCH["num_routed_experts"]:
        raise Q35QBlock("routed expert count mismatch")
    if meta["num_shared_experts"] != QWEN35_35B_A3B_ARCH["num_shared_experts"]:
        raise Q35QBlock("shared expert count mismatch")

    if meta["bias_convention"] not in BIAS_CONVENTIONS:
        raise Q35QBlock("unknown bias convention")
    if meta["softmax_convention"] not in SOFTMAX_CONVENTIONS:
        raise Q35QBlock("unknown softmax convention")

    _true(meta["route_parity_repeated"], "route_parity_repeated")
    _true(meta["threshold_committed_before_margins"], "threshold_committed_before_margins")
    _num(meta["near_boundary_threshold"], "near_boundary_threshold", lo=0)
    if meta["near_boundary_threshold"] <= 0:
        raise Q35QBlock("near_boundary_threshold must be positive")
    _num(meta["fraction_below_threshold"], "fraction_below_threshold", lo=0.0, hi=1.0)

    mq = meta["margin_quantiles"]
    if not isinstance(mq, dict) or not mq:
        raise Q35QBlock("margin_quantiles must be a non-empty dict")
    for q, val in mq.items():
        _num(float(q), "quantile key", lo=0.0, hi=1.0)
        _num(val, "quantile value")

    for name in ("route_load_summary", "route_transition_summary"):
        if not isinstance(meta[name], dict) or not meta[name]:
            raise Q35QBlock(f"{name} must be a non-empty aggregate dict")
        for k, v in meta[name].items():
            _num(v, f"{name}.{k}")

    _true(meta["token_parity_exact"], "token_parity_exact")
    _true(meta["logit_parity_within_tol"], "logit_parity_within_tol")
    _true(meta["no_offload"], "no_offload")
    _num(meta["hook_overhead_s"], "hook_overhead_s", lo=0)
    _num(meta["peak_gib_per_gpu"], "peak_gib_per_gpu", lo=0, hi=MEM_GIB_PER_GPU)
    _num(meta["peak_gib_total"], "peak_gib_total", lo=0, hi=MEM_GIB_TOTAL)

    sh = meta["source_hashes"]
    if not isinstance(sh, dict) or not sh:
        raise Q35QBlock("source_hashes must be a non-empty dict")
    for k, h in sh.items():
        if not (isinstance(h, str) and len(h) == 64):
            raise Q35QBlock(f"bad source hash for {k}")

    artifact = {
        "outcome": ROUTE_REGIME_READY,
        "observed_layer_count": len(layers),
        "router_module_count": len(router_ids),
        "top_k": meta["top_k"],
        "num_routed_experts": meta["num_routed_experts"],
        "num_shared_experts": meta["num_shared_experts"],
        "bias_convention": meta["bias_convention"],
        "softmax_convention": meta["softmax_convention"],
        "route_parity_repeated": True,
        "near_boundary_threshold": float(meta["near_boundary_threshold"]),
        "threshold_committed_before_margins": True,
        "fraction_below_threshold": float(meta["fraction_below_threshold"]),
        "margin_quantiles": {str(q): float(v) for q, v in mq.items()},
        "route_load_summary": {k: float(v) for k, v in meta["route_load_summary"].items()},
        "route_transition_summary": {k: float(v) for k, v in meta["route_transition_summary"].items()},
        "token_parity_exact": True,
        "logit_parity_within_tol": True,
        "no_offload": True,
        "hook_overhead_s": float(meta["hook_overhead_s"]),
        "peak_gib_per_gpu": float(meta["peak_gib_per_gpu"]),
        "peak_gib_total": float(meta["peak_gib_total"]),
        "source_hash_count": len(sh),
    }
    scan_aggregate_only(artifact)  # guarantee no raw routes/logits/margins leak
    return artifact
