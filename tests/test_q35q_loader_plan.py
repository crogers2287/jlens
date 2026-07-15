"""Q35Q loader-spec + device-placement planner tests (CPU-only, no model)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_phase0 import Q35QBlock, QWEN35_35B_A3B_ARCH, validate_device_map
from q35q_loader_plan import LoaderSpec, build_device_plan, transport_boundary

N = QWEN35_35B_A3B_ARCH["num_hidden_layers"]  # 40


def good_spec(**over):
    base = dict(
        path_name="gptq",
        use_cache=False,
        mtp_disabled=True,
        speculative_disabled=True,
        frozen_weights=True,
        eager=True,
        attn_impl="eager",
        serving_markers=(),
    )
    base.update(over)
    return LoaderSpec(**base)


# ---------- loader spec ----------


def test_loader_spec_pass():
    assert good_spec().validate()["result"] == "pass"
    assert good_spec(path_name="nf4").validate()["result"] == "pass"


@pytest.mark.parametrize(
    "over",
    [
        {"use_cache": True},
        {"mtp_disabled": False},
        {"speculative_disabled": False},
        {"frozen_weights": False},
        {"eager": False},
        {"attn_impl": "sdpa"},
        {"path_name": "awq"},
        {"serving_markers": ("moe_wna16",)},
        {"serving_markers": ("vllm-0.24",)},
    ],
)
def test_loader_spec_blocked(over):
    with pytest.raises(Q35QBlock):
        good_spec(**over).validate()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("use_cache", 0),
        ("use_cache", "false"),
        ("mtp_disabled", 1),
        ("mtp_disabled", "true"),
        ("speculative_disabled", 1),
        ("frozen_weights", "true"),
        ("eager", 1),
    ],
)
def test_loader_spec_rejects_non_boolean_gate_values(field, value):
    with pytest.raises(Q35QBlock):
        good_spec(**{field: value}).validate()


def test_loader_spec_rejects_non_string_identity_fields():
    with pytest.raises(Q35QBlock):
        good_spec(path_name=1).validate()
    with pytest.raises(Q35QBlock):
        good_spec(attn_impl=True).validate()


def test_loader_spec_rejects_invalid_marker_container():
    with pytest.raises(Q35QBlock):
        good_spec(serving_markers="eager").validate()
    with pytest.raises(Q35QBlock):
        good_spec(serving_markers=("eager", 1)).validate()


# ---------- device plan ----------


def test_device_plan_default_split():
    dm = build_device_plan()
    assert len(dm) == N + 3
    assert dm["model.embed_tokens"] == 0
    assert dm["model.layers.0"] == 0
    assert dm["model.layers.19"] == 0
    assert dm["model.layers.20"] == 1
    assert dm["model.layers.39"] == 1
    assert dm["model.norm"] == 1 and dm["lm_head"] == 1
    assert all(f"model.layers.{i}" in dm for i in range(N))
    assert validate_device_map(dm, required_modules=tuple(dm.keys()))["result"] == "pass"


def test_device_plan_custom_split_boundary():
    dm = build_device_plan(split_after=28)
    assert dm["model.layers.27"] == 0 and dm["model.layers.28"] == 1
    assert transport_boundary(dm) == 28


def test_device_plan_default_boundary():
    assert transport_boundary(build_device_plan()) == 20


@pytest.mark.parametrize("bad", [0, N, -1, N + 5, True, 20.0, "20"])
def test_device_plan_bad_split_blocked(bad):
    with pytest.raises(Q35QBlock):
        build_device_plan(split_after=bad)


@pytest.mark.parametrize(
    "gpus",
    [
        (0, 0),
        (0, 1, 2),
        (0, True),
        (0, "1"),
        "01",
        None,
    ],
)
def test_device_plan_requires_two_distinct_integer_gpus(gpus):
    with pytest.raises(Q35QBlock):
        build_device_plan(gpus=gpus)


@pytest.mark.parametrize("bad", [39, 41, True, 40.0, "40"])
def test_device_plan_requires_frozen_layer_count(bad):
    with pytest.raises(Q35QBlock):
        build_device_plan(num_layers=bad)


# ---------- transport boundary ----------


def test_transport_boundary_multi_crossing_blocked():
    dm = build_device_plan()
    dm["model.layers.21"] = 0
    with pytest.raises(Q35QBlock):
        transport_boundary(dm)


def test_transport_boundary_no_layers_blocked():
    with pytest.raises(Q35QBlock):
        transport_boundary({"model.embed_tokens": 0})


def test_transport_boundary_single_gpu_no_crossing_blocked():
    dm = build_device_plan()
    for key in dm:
        dm[key] = 0
    with pytest.raises(Q35QBlock):
        transport_boundary(dm)


def test_transport_boundary_missing_layer_blocked():
    dm = build_device_plan()
    del dm["model.layers.17"]
    with pytest.raises(Q35QBlock):
        transport_boundary(dm)


def test_transport_boundary_extra_module_blocked():
    dm = build_device_plan()
    dm["model.layers.0.self_attn"] = 0
    with pytest.raises(Q35QBlock):
        transport_boundary(dm)


def test_transport_boundary_embedding_endpoint_mismatch_blocked():
    dm = build_device_plan()
    dm["model.embed_tokens"] = 1
    with pytest.raises(Q35QBlock):
        transport_boundary(dm)


def test_transport_boundary_final_endpoint_mismatch_blocked():
    dm = build_device_plan()
    dm["lm_head"] = 0
    with pytest.raises(Q35QBlock):
        transport_boundary(dm)


def test_transport_boundary_non_integer_device_blocked():
    dm = build_device_plan()
    dm["model.layers.20"] = "cuda:1"
    with pytest.raises(Q35QBlock):
        transport_boundary(dm)
