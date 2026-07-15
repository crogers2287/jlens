"""Q35Q deterministic fp32 merge of independent prompt shards.

Horizontal prompt sharding is estimator-preserving because the reference
``anthropics/jacobian-lens`` fit returns one average Jacobian matrix for every
selected source layer and ``JacobianLens.merge`` forms an ``n_prompts``-
weighted mean. Each worker therefore emits a complete mapping from source layer
to the fp32 SUM of that layer's per-prompt transports, plus its prompt count.

Every frozen identity, source-layer key, shape, dtype, and finite-value gate is
verified before merging. Accumulation uses a fixed worker-id and source-layer
order. Raw matrices remain private; only aggregate numerical health and a
canonical content hash are suitable for public status artifacts.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

import numpy as np

from q35q_phase0 import Q35QBlock

FP32 = np.float32
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass
class ShardPartial:
    """One worker's complete multi-layer partial-sum artifact."""
    worker_id: int
    partial_sums: dict[int, np.ndarray]
    n_prompts: int
    source_layers: tuple[int, ...]
    d_model: int
    identity: str


def _validate_source_layers(source_layers) -> tuple[int, ...]:
    if not isinstance(source_layers, tuple) or not source_layers:
        raise Q35QBlock("source_layers must be a non-empty tuple")
    if any(type(layer) is not int or layer < 0 for layer in source_layers):
        raise Q35QBlock("source_layers must contain non-negative ints")
    if tuple(sorted(set(source_layers))) != source_layers:
        raise Q35QBlock("source_layers must be unique and strictly increasing")
    return source_layers


def _validate_matrix(a, d_model: int, name: str) -> np.ndarray:
    if not isinstance(a, np.ndarray) or a.dtype != FP32:
        raise Q35QBlock(f"{name} must be a float32 ndarray")
    if a.shape != (d_model, d_model):
        raise Q35QBlock(f"{name} shape mismatch")
    if not np.isfinite(a).all():
        raise Q35QBlock(f"non-finite values in {name}")
    return a


def _check_partial(p: ShardPartial, ref: dict) -> None:
    if not isinstance(p, ShardPartial):
        raise Q35QBlock("every shard must be a ShardPartial")
    if type(p.worker_id) is not int or p.worker_id < 0:
        raise Q35QBlock("worker_id must be a non-negative int")
    if type(p.n_prompts) is not int or p.n_prompts <= 0:
        raise Q35QBlock("n_prompts must be a positive int")
    if type(p.d_model) is not int or p.d_model <= 0:
        raise Q35QBlock("d_model must be a positive int")
    if not isinstance(p.identity, str) or not _SHA256.fullmatch(p.identity):
        raise Q35QBlock("identity must be a lowercase SHA-256 digest")
    layers = _validate_source_layers(p.source_layers)
    if p.identity != ref["identity"]:
        raise Q35QBlock("frozen identity mismatch across shards")
    if layers != ref["source_layers"]:
        raise Q35QBlock("source-layer set mismatch across shards")
    if p.d_model != ref["d_model"]:
        raise Q35QBlock("d_model mismatch across shards")
    if not isinstance(p.partial_sums, dict):
        raise Q35QBlock("partial_sums must be a dict")
    if set(p.partial_sums) != set(layers) or len(p.partial_sums) != len(layers):
        raise Q35QBlock("partial_sums keys must exactly match source_layers")
    for layer in layers:
        _validate_matrix(p.partial_sums[layer], p.d_model, f"partial_sums[{layer}]")


def weighted_merge(partials):
    """Merge complete multi-layer shard sums.

    Returns ``(merged_by_layer, total_prompts)`` where ``merged_by_layer`` maps
    every frozen source layer to one fp32 mean matrix.
    """
    if isinstance(partials, (str, bytes)) or partials is None:
        raise Q35QBlock("partials must be a non-empty iterable")
    try:
        order = sorted(list(partials), key=lambda p: p.worker_id)
    except (TypeError, AttributeError) as exc:
        raise Q35QBlock("partials must contain ShardPartial objects") from exc
    if not order:
        raise Q35QBlock("no shard partials")
    ids = [p.worker_id for p in order]
    if len(set(ids)) != len(ids):
        raise Q35QBlock("duplicate worker_id in shard set")

    first = order[0]
    if not isinstance(first, ShardPartial):
        raise Q35QBlock("every shard must be a ShardPartial")
    ref = {
        "identity": first.identity,
        "source_layers": _validate_source_layers(first.source_layers),
        "d_model": first.d_model,
    }
    for p in order:
        _check_partial(p, ref)

    acc = {
        layer: np.zeros((ref["d_model"], ref["d_model"]), dtype=FP32)
        for layer in ref["source_layers"]
    }
    total = 0
    for p in order:
        for layer in ref["source_layers"]:
            with np.errstate(over="ignore", invalid="ignore"):
                np.add(acc[layer], p.partial_sums[layer], out=acc[layer], casting="no")
            if not np.isfinite(acc[layer]).all():
                raise Q35QBlock("non-finite values produced during fp32 accumulation")
        total += p.n_prompts
    if total <= 0:
        raise Q35QBlock("total prompt count non-positive")

    merged = {}
    for layer in ref["source_layers"]:
        merged[layer] = (acc[layer] / FP32(total)).astype(FP32)
        if not np.isfinite(merged[layer]).all():
            raise Q35QBlock("non-finite values produced during fp32 normalization")
    return merged, total


def merge_health(merged_by_layer, total: int) -> dict:
    """Aggregate-only multi-layer numerical health and canonical content hash."""
    if type(total) is not int or total <= 0:
        raise Q35QBlock("total must be a positive int")
    if not isinstance(merged_by_layer, dict) or not merged_by_layer:
        raise Q35QBlock("merged_by_layer must be a non-empty dict")
    layers = tuple(sorted(merged_by_layer))
    _validate_source_layers(layers)

    d_model = None
    digest = hashlib.sha256()
    frobenius_sum = 0.0
    max_abs = 0.0
    for layer in layers:
        matrix = merged_by_layer[layer]
        if d_model is None:
            if not isinstance(matrix, np.ndarray) or matrix.ndim != 2:
                raise Q35QBlock("merged matrices must be 2-D ndarrays")
            if matrix.shape[0] != matrix.shape[1]:
                raise Q35QBlock("merged matrices must be square")
            d_model = matrix.shape[0]
        _validate_matrix(matrix, d_model, f"merged_by_layer[{layer}]")
        matrix64 = matrix.astype(np.float64)
        frobenius_sum += float(np.linalg.norm(matrix64))
        max_abs = max(max_abs, float(np.abs(matrix64).max()))
        digest.update(layer.to_bytes(4, "big", signed=False))
        digest.update(d_model.to_bytes(8, "big", signed=False))
        digest.update(matrix.tobytes(order="C"))

    if not math.isfinite(frobenius_sum) or not math.isfinite(max_abs):
        raise Q35QBlock("non-finite aggregate health")
    return {
        "total_prompts": total,
        "d_model": d_model,
        "source_layer_count": len(layers),
        "source_layers": list(layers),
        "finite": True,
        "frobenius_sum": frobenius_sum,
        "max_abs": max_abs,
        "merged_transport_sha256": digest.hexdigest(),
    }


def cross_worker_agreement(partials_a, partials_b, tol: float = 0.0) -> bool:
    """Duplicated-neutral-prompt smoke across complete multi-layer artifacts."""
    if isinstance(tol, bool) or not isinstance(tol, (int, float)):
        raise Q35QBlock("tol must be a finite non-negative number")
    try:
        finite_tol = math.isfinite(tol)
    except (TypeError, ValueError, OverflowError) as exc:
        raise Q35QBlock("tol must be a finite non-negative number") from exc
    if not finite_tol or tol < 0:
        raise Q35QBlock("tol must be a finite non-negative number")
    if not isinstance(partials_a, dict) or not isinstance(partials_b, dict):
        raise Q35QBlock("worker partials must be dicts")
    if not partials_a or set(partials_a) != set(partials_b):
        raise Q35QBlock("worker source-layer sets mismatch")
    layers = tuple(sorted(partials_a))
    _validate_source_layers(layers)

    d_model = None
    for layer in layers:
        a = partials_a[layer]
        b = partials_b[layer]
        if d_model is None:
            if not isinstance(a, np.ndarray) or a.ndim != 2 or a.shape[0] != a.shape[1]:
                raise Q35QBlock("worker matrices must be square 2-D ndarrays")
            d_model = a.shape[0]
        _validate_matrix(a, d_model, f"partials_a[{layer}]")
        _validate_matrix(b, d_model, f"partials_b[{layer}]")
        diff = float(np.abs(a.astype(np.float64) - b.astype(np.float64)).max())
        if not math.isfinite(diff) or diff > tol:
            return False
    return True
