"""Q35Q deterministic fp32 weighted merge of independent per-shard partial
Jacobian/transport sums (CPU-only; no GPU, no model, no capture).

Horizontal prompt sharding is exact because the reference estimator forms an
`n_prompts`-weighted mean over independent prompt Jacobians (anthropics/
jacobian-lens `JacobianLens.merge`). Each worker emits a partial SUM of its
prompt transports plus its prompt count; the merged transport is
`sum(partials) / sum(n_prompts)`. Every frozen identity (source-layer set,
d_model, dtype, shape, identity digest) is verified before merging, and
accumulation runs in a fixed deterministic worker order.

Callers keep raw transports private; only aggregate numerical-health and a
content hash are committed. See
docs/STEER_ADDENDUM_2026-07-15_Q35Q_ROUTE_REGIME_AND_EXACT_SHARDING.md
("Exact horizontal prompt sharding").
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import numpy as np

from q35q_phase0 import Q35QBlock

FP32 = np.float32


@dataclass
class ShardPartial:
    """One worker's partial: a fp32 SUM of prompt transports and its count."""
    worker_id: int
    partial_sum: np.ndarray          # (d_model, d_model) float32
    n_prompts: int
    source_layers: tuple
    d_model: int
    identity: str                    # frozen-identity digest shared by all shards


def _check_partial(p: ShardPartial, ref: dict) -> None:
    if type(p.worker_id) is not int or isinstance(p.worker_id, bool) or p.worker_id < 0:
        raise Q35QBlock("worker_id must be a non-negative int")
    if type(p.n_prompts) is not int or isinstance(p.n_prompts, bool) or p.n_prompts <= 0:
        raise Q35QBlock("n_prompts must be a positive int")
    if p.identity != ref["identity"]:
        raise Q35QBlock("frozen identity mismatch across shards")
    if tuple(p.source_layers) != ref["source_layers"]:
        raise Q35QBlock("source-layer set mismatch across shards")
    if p.d_model != ref["d_model"]:
        raise Q35QBlock("d_model mismatch across shards")
    a = p.partial_sum
    if not isinstance(a, np.ndarray) or a.dtype != FP32:
        raise Q35QBlock("partial_sum must be a float32 ndarray")
    if a.shape != (ref["d_model"], ref["d_model"]):
        raise Q35QBlock("partial_sum shape mismatch")
    if not np.isfinite(a).all():
        raise Q35QBlock("non-finite values in partial_sum")


def weighted_merge(partials):
    """Deterministic fp32 weighted merge -> (merged_transport fp32, total_prompts).

    Fixed accumulation order (by worker_id); rejects duplicate worker ids and any
    frozen-identity / shape / dtype / finiteness mismatch."""
    if not partials:
        raise Q35QBlock("no shard partials")
    order = sorted(partials, key=lambda p: p.worker_id)
    ids = [p.worker_id for p in order]
    if len(set(ids)) != len(ids):
        raise Q35QBlock("duplicate worker_id in shard set")
    ref = {"identity": order[0].identity,
           "source_layers": tuple(order[0].source_layers),
           "d_model": order[0].d_model}
    for p in order:
        _check_partial(p, ref)
    d = ref["d_model"]
    acc = np.zeros((d, d), dtype=FP32)
    total = 0
    for p in order:
        acc = (acc + p.partial_sum).astype(FP32)   # fixed-order fp32 accumulation
        total += p.n_prompts
    if total <= 0:
        raise Q35QBlock("total prompt count non-positive")
    merged = (acc / FP32(total)).astype(FP32)
    return merged, total


def merge_health(merged: np.ndarray, total: int) -> dict:
    """Aggregate-only numerical-health + content hash (public-safe)."""
    if not isinstance(merged, np.ndarray) or merged.ndim != 2:
        raise Q35QBlock("merged transport must be a 2-D ndarray")
    return {
        "total_prompts": int(total),
        "d_model": int(merged.shape[0]),
        "finite": bool(np.isfinite(merged).all()),
        "frobenius": float(np.linalg.norm(merged.astype(np.float64))),
        "merged_transport_sha256": hashlib.sha256(merged.tobytes()).hexdigest(),
    }


def cross_worker_agreement(partial_a: np.ndarray, partial_b: np.ndarray,
                           tol: float = 0.0) -> bool:
    """Duplicated-neutral-prompt smoke: two workers given the SAME prompt under
    identical runtime must produce identical single-prompt partials (bitwise
    when tol=0)."""
    if not (isinstance(partial_a, np.ndarray) and isinstance(partial_b, np.ndarray)):
        raise Q35QBlock("partials must be ndarrays")
    if partial_a.shape != partial_b.shape or partial_a.dtype != partial_b.dtype:
        raise Q35QBlock("shape/dtype mismatch")
    if partial_a.size == 0:
        raise Q35QBlock("empty partial")
    diff = float(np.abs(partial_a.astype(np.float64) - partial_b.astype(np.float64)).max())
    return diff <= tol
