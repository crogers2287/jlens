"""Q35Q route-regime artifact schema tests (CPU-only, aggregate-only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_phase0 import Q35QBlock, scan_aggregate_only
from q35q_route_regime import (
    ROUTE_REGIME_READY,
    build_route_regime_artifact,
)

H = "a" * 64


def good_meta(**over):
    meta = dict(
        router_module_ids=["model.layers.3.mlp.gate", "model.layers.7.mlp.gate"],
        observed_layers=[3, 7, 20],
        top_k=8,
        num_routed_experts=256,
        num_shared_experts=1,
        bias_convention="post_bias",
        softmax_convention="post_softmax",
        route_parity_repeated=True,
        near_boundary_threshold=1e-3,
        threshold_committed_before_margins=True,
        margin_quantiles={0.1: 0.02, 0.5: 0.15, 0.9: 0.6},
        fraction_below_threshold=0.05,
        route_load_summary={"max_load": 0.13, "cv": 0.4},
        route_transition_summary={"mean_transitions": 2.1},
        token_parity_exact=True,
        logit_parity_within_tol=True,
        no_offload=True,
        hook_overhead_s=0.02,
        peak_gib_per_gpu=21.0,
        peak_gib_total=42.0,
        source_hashes={"src/q35q_route_regime.py": H},
    )
    meta.update(over)
    return meta


def test_route_regime_pass():
    art = build_route_regime_artifact(good_meta())
    assert art["outcome"] == ROUTE_REGIME_READY
    assert art["observed_layer_count"] == 3
    assert art["router_module_count"] == 2
    assert art["fraction_below_threshold"] == 0.05
    # aggregate-only: no raw routes/logits/margins keys
    assert "router_module_ids" not in art and "observed_layers" not in art
    scan_aggregate_only(art)


@pytest.mark.parametrize("field", [
    "router_module_ids", "observed_layers", "top_k", "bias_convention",
    "margin_quantiles", "route_load_summary", "source_hashes",
    "near_boundary_threshold",
])
def test_missing_field_blocked(field):
    meta = good_meta()
    del meta[field]
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(meta)


def test_threshold_not_preregistered_blocked():
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(threshold_committed_before_margins=False))


def test_route_parity_required():
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(route_parity_repeated=False))


@pytest.mark.parametrize("conv", [{"bias_convention": "mid_bias"},
                                   {"softmax_convention": "no_softmax"}])
def test_bad_convention_blocked(conv):
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(**conv))


@pytest.mark.parametrize("over", [{"top_k": 4}, {"num_routed_experts": 128},
                                   {"num_shared_experts": 0}])
def test_architecture_mismatch_blocked(over):
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(**over))


@pytest.mark.parametrize("frac", [-0.01, 1.01])
def test_fraction_out_of_range_blocked(frac):
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(fraction_below_threshold=frac))


def test_memory_ceilings_blocked():
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(peak_gib_per_gpu=23.1))
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(peak_gib_total=46.1))


def test_layer_out_of_range_blocked():
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(observed_layers=[3, 41]))


def test_bad_source_hash_blocked():
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(source_hashes={"x": "short"}))


def test_parity_flags_required():
    for flag in ("token_parity_exact", "logit_parity_within_tol", "no_offload"):
        with pytest.raises(Q35QBlock):
            build_route_regime_artifact(good_meta(**{flag: False}))
