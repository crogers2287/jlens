"""Q35Q deterministic multi-layer weighted-merge tests."""
import hashlib
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
IDENT = hashlib.sha256(b"rev|quant|tok|layers").hexdigest()
LAYERS = (4, 20)


def prompt(layer4, layer20):
    return {4: np.asarray(layer4, dtype=FP32),
            20: np.asarray(layer20, dtype=FP32)}


def partial(worker_id, prompt_maps):
    sums = {layer: np.zeros((D, D), dtype=FP32) for layer in LAYERS}
    for per_prompt in prompt_maps:
        for layer in LAYERS:
            sums[layer] += per_prompt[layer]
    return ShardPartial(worker_id=worker_id, partial_sums=sums,
                        n_prompts=len(prompt_maps), source_layers=LAYERS,
                        d_model=D, identity=IDENT)


def test_synthetic_exact_merge_equals_global_mean_for_every_layer():
    rng = np.random.default_rng(0)
    prompts = [prompt(rng.integers(-5, 6, size=(D, D)),
                      rng.integers(-5, 6, size=(D, D))) for _ in range(9)]
    shards = [partial(0, prompts[0:4]), partial(1, prompts[4:7]),
              partial(2, prompts[7:9])]
    merged, total = weighted_merge(shards)
    assert total == 9
    assert tuple(merged) == LAYERS
    for layer in LAYERS:
        ref = np.sum(np.stack([p[layer] for p in prompts]), axis=0).astype(FP32)
        ref = (ref / FP32(9)).astype(FP32)
        assert np.array_equal(merged[layer], ref)


def test_merge_order_independent():
    one = np.ones((D, D), dtype=FP32)
    two = np.full((D, D), 2, dtype=FP32)
    prompts = [prompt(one, two) for _ in range(6)]
    a = [partial(0, prompts[0:3]), partial(1, prompts[3:6])]
    b = [partial(1, prompts[3:6]), partial(0, prompts[0:3])]
    ma, _ = weighted_merge(a)
    mb, _ = weighted_merge(b)
    for layer in LAYERS:
        assert np.array_equal(ma[layer], mb[layer])


def test_merge_health_binds_layers_and_content():
    one = np.ones((D, D), dtype=FP32)
    two = np.full((D, D), 2, dtype=FP32)
    merged, total = weighted_merge([partial(0, [prompt(one, two)])])
    health = merge_health(merged, total)
    assert health["total_prompts"] == 1
    assert health["d_model"] == D
    assert health["source_layer_count"] == 2
    assert health["source_layers"] == [4, 20]
    assert health["finite"] is True
    assert len(health["merged_transport_sha256"]) == 64
    scan_aggregate_only(health)


def test_cross_worker_agreement_checks_every_layer():
    rng = np.random.default_rng(2)
    a = {layer: rng.integers(-9, 10, size=(D, D)).astype(FP32)
         for layer in LAYERS}
    b = {layer: matrix.copy() for layer, matrix in a.items()}
    assert cross_worker_agreement(a, b) is True
    b[20][0, 0] += FP32(1)
    assert cross_worker_agreement(a, b) is False
    assert cross_worker_agreement(a, b, tol=1.0) is True


def test_empty_and_non_shard_partials_blocked():
    with pytest.raises(Q35QBlock):
        weighted_merge([])
    with pytest.raises(Q35QBlock):
        weighted_merge([object()])


def test_duplicate_worker_blocked():
    one = np.ones((D, D), dtype=FP32)
    p = [prompt(one, one)]
    with pytest.raises(Q35QBlock):
        weighted_merge([partial(0, p), partial(0, p)])


def test_identity_mismatch_and_malformed_identity_blocked():
    one = np.ones((D, D), dtype=FP32)
    s0 = partial(0, [prompt(one, one)])
    s1 = partial(1, [prompt(one, one)])
    s1.identity = hashlib.sha256(b"different").hexdigest()
    with pytest.raises(Q35QBlock):
        weighted_merge([s0, s1])
    s0.identity = "not-a-digest"
    with pytest.raises(Q35QBlock):
        weighted_merge([s0])


def test_layer_set_and_partial_keys_must_match_exactly():
    one = np.ones((D, D), dtype=FP32)
    s = partial(0, [prompt(one, one)])
    s.source_layers = (20, 4)
    with pytest.raises(Q35QBlock):
        weighted_merge([s])
    s = partial(0, [prompt(one, one)])
    del s.partial_sums[20]
    with pytest.raises(Q35QBlock):
        weighted_merge([s])


@pytest.mark.parametrize("mutator", [
    lambda s: setattr(s, "worker_id", True),
    lambda s: setattr(s, "n_prompts", 0),
    lambda s: setattr(s, "d_model", True),
    lambda s: setattr(s, "d_model", 0),
])
def test_strict_scalar_types_blocked(mutator):
    one = np.ones((D, D), dtype=FP32)
    s = partial(0, [prompt(one, one)])
    mutator(s)
    with pytest.raises(Q35QBlock):
        weighted_merge([s])


def test_dtype_shape_nonfinite_and_accumulation_overflow_blocked():
    one = np.ones((D, D), dtype=FP32)
    s = partial(0, [prompt(one, one)])
    s.partial_sums[4] = s.partial_sums[4].astype(np.float64)
    with pytest.raises(Q35QBlock):
        weighted_merge([s])

    s = partial(0, [prompt(one, one)])
    s.partial_sums[4] = np.ones((D, D + 1), dtype=FP32)
    with pytest.raises(Q35QBlock):
        weighted_merge([s])

    s = partial(0, [prompt(one, one)])
    s.partial_sums[4][0, 0] = np.inf
    with pytest.raises(Q35QBlock):
        weighted_merge([s])

    huge = np.full((D, D), np.finfo(FP32).max, dtype=FP32)
    s0 = partial(0, [prompt(huge, one)])
    s1 = partial(1, [prompt(huge, one)])
    with pytest.raises(Q35QBlock):
        weighted_merge([s0, s1])


@pytest.mark.parametrize("tol", [-1.0, True, float("nan"), float("inf")])
def test_cross_worker_bad_tolerance_blocked(tol):
    one = np.ones((D, D), dtype=FP32)
    maps = {4: one, 20: one.copy()}
    with pytest.raises(Q35QBlock):
        cross_worker_agreement(maps, maps, tol=tol)


def test_merge_health_fail_closed():
    one = np.ones((D, D), dtype=FP32)
    with pytest.raises(Q35QBlock):
        merge_health({}, 1)
    with pytest.raises(Q35QBlock):
        merge_health({4: one}, 0)
    with pytest.raises(Q35QBlock):
        merge_health({4: np.ones((D, D + 1), dtype=FP32)}, 1)
