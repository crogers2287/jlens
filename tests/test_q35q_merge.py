"""Q35Q deterministic fp32 weighted-merge tests: synthetic exact-merge,
cross-worker agreement smoke, and fail-closed identity/shape checks.

Small integer-valued fp32 matrices keep the merge bitwise-exact. No GPU,
no model, no private data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
import pytest

from q35q_phase0 import Q35QBlock, scan_aggregate_only
from q35q_merge import (
    FP32,
    ShardPartial,
    cross_worker_agreement,
    merge_health,
    weighted_merge,
)

D = 4
IDENT = "rev|quant|tok|layers"
LAYERS = (20,)


def partial(worker_id, prompt_mats):
    """Build a ShardPartial as the fp32 sum over its prompt transports."""
    s = np.zeros((D, D), dtype=FP32)
    for m in prompt_mats:
        s = s + np.asarray(m, dtype=FP32)
    return ShardPartial(worker_id=worker_id, partial_sum=s.astype(FP32),
                        n_prompts=len(prompt_mats), source_layers=LAYERS,
                        d_model=D, identity=IDENT)


def test_synthetic_exact_merge_equals_global_mean():
    rng = np.random.default_rng(0)
    # integer-valued matrices -> exact in fp32
    prompts = [rng.integers(-5, 6, size=(D, D)).astype(FP32) for _ in range(9)]
    # shard 9 prompts as 4 + 3 + 2 across 3 workers
    shards = [partial(0, prompts[0:4]), partial(1, prompts[4:7]),
              partial(2, prompts[7:9])]
    merged, total = weighted_merge(shards)
    assert total == 9
    # reference: direct global mean
    ref = np.sum(np.stack(prompts), axis=0).astype(FP32) / FP32(9)
    assert np.array_equal(merged, ref.astype(FP32))


def test_merge_order_independent():
    rng = np.random.default_rng(1)
    prompts = [rng.integers(-3, 4, size=(D, D)).astype(FP32) for _ in range(6)]
    a = [partial(0, prompts[0:3]), partial(1, prompts[3:6])]
    b = [partial(1, prompts[3:6]), partial(0, prompts[0:3])]  # reversed input order
    ma, _ = weighted_merge(a)
    mb, _ = weighted_merge(b)
    assert np.array_equal(ma, mb)  # deterministic (sorted by worker_id)


def test_merge_health_public_safe():
    prompts = [np.ones((D, D), dtype=FP32)]
    merged, total = weighted_merge([partial(0, prompts)])
    h = merge_health(merged, total)
    assert h["total_prompts"] == 1 and h["d_model"] == D and h["finite"] is True
    assert len(h["merged_transport_sha256"]) == 64
    scan_aggregate_only(h)  # no forbidden keys / raw arrays


def test_cross_worker_agreement_bitwise():
    rng = np.random.default_rng(2)
    m = rng.integers(-9, 10, size=(D, D)).astype(FP32)
    assert cross_worker_agreement(m.copy(), m.copy()) is True
    m2 = m.copy()
    m2[0, 0] += FP32(1)
    assert cross_worker_agreement(m, m2) is False


# ---------- fail-closed ----------

def test_empty_partials_blocked():
    with pytest.raises(Q35QBlock):
        weighted_merge([])


def test_duplicate_worker_blocked():
    p = [np.ones((D, D), dtype=FP32)]
    with pytest.raises(Q35QBlock):
        weighted_merge([partial(0, p), partial(0, p)])


def test_identity_mismatch_blocked():
    s0 = partial(0, [np.ones((D, D), dtype=FP32)])
    s1 = partial(1, [np.ones((D, D), dtype=FP32)])
    s1.identity = "different"
    with pytest.raises(Q35QBlock):
        weighted_merge([s0, s1])


def test_layer_set_mismatch_blocked():
    s0 = partial(0, [np.ones((D, D), dtype=FP32)])
    s1 = partial(1, [np.ones((D, D), dtype=FP32)])
    s1.source_layers = (28,)
    with pytest.raises(Q35QBlock):
        weighted_merge([s0, s1])


def test_dtype_mismatch_blocked():
    s = partial(0, [np.ones((D, D), dtype=FP32)])
    s.partial_sum = s.partial_sum.astype(np.float64)
    with pytest.raises(Q35QBlock):
        weighted_merge([s])


def test_shape_mismatch_blocked():
    s = partial(0, [np.ones((D, D), dtype=FP32)])
    s.partial_sum = np.ones((D, D + 1), dtype=FP32)
    with pytest.raises(Q35QBlock):
        weighted_merge([s])


def test_nonfinite_blocked():
    s = partial(0, [np.ones((D, D), dtype=FP32)])
    s.partial_sum[0, 0] = np.inf
    with pytest.raises(Q35QBlock):
        weighted_merge([s])


def test_bad_n_prompts_blocked():
    s = partial(0, [np.ones((D, D), dtype=FP32)])
    s.n_prompts = 0
    with pytest.raises(Q35QBlock):
        weighted_merge([s])
