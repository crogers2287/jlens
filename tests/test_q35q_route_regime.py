"""Q35Q route-regime artifact schema tests (CPU-only, aggregate-only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_phase0 import Q35QBlock, scan_aggregate_only
from q35q_route_regime import (
    REQUIRED_MARGIN_QUANTILES,
    ROUTE_REGIME_READY,
    build_route_regime_artifact,
)

H = "a" * 64


def good_meta(**over):
    meta = dict(
        router_module_ids=[
            "model.layers.3.mlp.gate",
            "model.layers.7.mlp.gate",
            "model.layers.20.mlp.gate",
        ],
        router_tensor_ids=[
            "model.layers.3.mlp.gate.output",
            "model.layers.7.mlp.gate.output",
            "model.layers.20.mlp.gate.output",
        ],
        observed_layers=[3, 7, 20],
        top_k=8,
        num_routed_experts=256,
        num_shared_experts=1,
        bias_convention="post_bias",
        softmax_convention="post_softmax",
        route_parity_repeated=True,
        near_boundary_threshold=1e-3,
        threshold_manifest_sha256=H,
        margin_quantiles={0.0: 0.001, 0.1: 0.02, 0.5: 0.15, 0.9: 0.6, 1.0: 1.4},
        fraction_below_threshold=0.05,
        route_load_summary={
            "mean_load": 0.03125,
            "max_load": 0.13,
            "load_cv": 0.4,
            "zero_load_fraction": 0.0,
        },
        route_transition_summary={
            "mean_route_changes": 1.2,
            "fraction_with_any_change": 0.8,
        },
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
    assert art["router_binding_count"] == 3
    assert len(art["router_binding_sha256"]) == 64
    assert art["fraction_below_threshold"] == 0.05
    assert tuple(float(key) for key in art["margin_quantiles"]) == REQUIRED_MARGIN_QUANTILES
    assert "router_module_ids" not in art and "observed_layers" not in art
    scan_aggregate_only(art)


@pytest.mark.parametrize("field", [
    "router_module_ids", "router_tensor_ids", "observed_layers", "top_k",
    "bias_convention", "margin_quantiles", "route_load_summary",
    "source_hashes", "near_boundary_threshold", "threshold_manifest_sha256",
])
def test_missing_field_blocked(field):
    meta = good_meta()
    del meta[field]
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(meta)


def test_unknown_field_blocked_even_if_private():
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(router_logits=[1.0, 2.0]))


@pytest.mark.parametrize("over", [
    {"router_module_ids": ["a", "b"]},
    {"router_tensor_ids": ["a", "b"]},
    {"router_module_ids": ["a", "a", "b"]},
    {"router_tensor_ids": ["a", "a", "b"]},
    {"observed_layers": [3, 3, 20]},
    {"observed_layers": [7, 3, 20]},
])
def test_router_bindings_must_be_one_to_one_and_ordered(over):
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(**over))


@pytest.mark.parametrize("over", [
    {"top_k": 8.0},
    {"top_k": True},
    {"top_k": 4},
    {"num_routed_experts": 256.0},
    {"num_routed_experts": 128},
    {"num_shared_experts": 0},
])
def test_architecture_identity_is_strict(over):
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(**over))


@pytest.mark.parametrize("field", ["route_parity_repeated", "token_parity_exact",
                                    "logit_parity_within_tol", "no_offload"])
def test_true_gates_are_strict(field):
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(**{field: False}))
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(**{field: 1}))


def test_threshold_manifest_and_source_hashes_are_strict():
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(threshold_manifest_sha256="A" * 64))
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(source_hashes={"x": "short"}))


def test_quantile_schema_and_monotonicity_are_frozen():
    bad = good_meta()["margin_quantiles"].copy()
    del bad[0.0]
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(margin_quantiles=bad))

    bad = good_meta()["margin_quantiles"].copy()
    bad[0.5] = -0.1
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(margin_quantiles=bad))

    bad = good_meta()["margin_quantiles"].copy()
    bad[0.9] = 0.1
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(margin_quantiles=bad))


def test_summary_keys_and_ranges_are_frozen():
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(route_load_summary={"max_load": 0.1}))
    load = good_meta()["route_load_summary"].copy()
    load["max_load"] = 0.01
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(route_load_summary=load))
    transitions = good_meta()["route_transition_summary"].copy()
    transitions["fraction_with_any_change"] = 1.1
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(route_transition_summary=transitions))


@pytest.mark.parametrize("over", [
    {"fraction_below_threshold": -0.01},
    {"fraction_below_threshold": 1.01},
    {"near_boundary_threshold": 0.0},
    {"peak_gib_per_gpu": 23.1},
    {"peak_gib_total": 46.1},
    {"observed_layers": [3, 41]},
])
def test_numeric_bounds_blocked(over):
    with pytest.raises(Q35QBlock):
        build_route_regime_artifact(good_meta(**over))
