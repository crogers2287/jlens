"""Q35Q exact-cost projection tests (CPU-only, pure arithmetic)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_phase0 import Q35QBlock, scan_aggregate_only
from q35q_cost import (
    D_MODEL,
    WALL_CLOCK_CEILING_S,
    Phase1Timing,
    backward_passes_per_prompt,
    project_fit,
    project_prompt_seconds,
    project_storage_bytes,
    single_worker_feasible,
)


def timing(**over):
    base = dict(forward_s=1.0, first_backward_s=0.5, steady_backward_s=0.4,
                cleanup_s=0.1)
    base.update(over)
    return Phase1Timing(**base)


def test_backward_passes_exact_model():
    assert backward_passes_per_prompt() == D_MODEL
    assert backward_passes_per_prompt(2048, 8) == 256
    assert backward_passes_per_prompt(2050, 8) == 257


@pytest.mark.parametrize("d,db", [(0, 1), (-1, 1), (2048, 0), (2048, -2),
                                   (2048, True), (2.0, 1)])
def test_backward_passes_bad_args_blocked(d, db):
    with pytest.raises(Q35QBlock):
        backward_passes_per_prompt(d, db)


@pytest.mark.parametrize("field", ["forward_s", "first_backward_s",
                                    "steady_backward_s", "cleanup_s"])
def test_timing_rejects_negative_and_nonfinite(field):
    with pytest.raises(Q35QBlock):
        timing(**{field: -1.0}).validate()
    with pytest.raises(Q35QBlock):
        timing(**{field: float("inf")}).validate()


def test_timing_rejects_bool_and_wrong_object():
    with pytest.raises(Q35QBlock):
        timing(forward_s=True).validate()
    with pytest.raises(Q35QBlock):
        project_prompt_seconds(object())


def test_project_prompt_seconds_formula():
    got = project_prompt_seconds(timing(), dim_batch=8)
    assert abs(got - (1.0 + 0.5 + 255 * 0.4 + 0.1)) < 1e-9


def test_project_storage_counts_every_source_layer():
    out = project_storage_bytes(d_model=2048, n_source_layers=5,
                                bytes_per_elem=4, n_checkpoints=1)
    matrix = 2048 * 2048 * 4
    assert out["matrix_bytes"] == matrix
    assert out["lens_set_bytes"] == matrix * 5
    assert out["projected_storage_bytes"] == matrix * 5 * 3
    scan_aggregate_only(out)


@pytest.mark.parametrize("kwargs", [
    {"d_model": 0},
    {"n_source_layers": 0},
    {"n_source_layers": True},
    {"bytes_per_elem": 0},
    {"n_checkpoints": -1},
    {"n_checkpoints": True},
])
def test_project_storage_bad_args_blocked(kwargs):
    with pytest.raises(Q35QBlock):
        project_storage_bytes(**kwargs)


def test_project_fit_aggregate_and_ceiling():
    proj = project_fit(120, timing(), dim_batch=8, workers=1, uncertainty=0.2)
    assert proj["backward_passes_per_prompt"] == 256
    assert proj["max_prompts_per_worker"] == 120
    assert proj["projected_total_compute_seconds"] == proj["projected_wall_seconds"]
    assert proj["within_ceiling_per_worker"] is True
    assert proj["single_worker"] is True
    assert proj["ceiling_seconds"] == WALL_CLOCK_CEILING_S
    scan_aggregate_only(proj)


def test_project_fit_exceeds_ceiling():
    assert single_worker_feasible(120, timing(), dim_batch=1) is False


def test_project_fit_sharding_uses_most_loaded_worker_not_average():
    proj = project_fit(10, timing(), dim_batch=8, workers=3, uncertainty=0.0)
    per = project_prompt_seconds(timing(), dim_batch=8)
    assert proj["max_prompts_per_worker"] == 4
    assert proj["idle_prompt_slots"] == 2
    assert proj["projected_wall_seconds"] == per * 4
    assert proj["projected_total_compute_seconds"] == per * 10
    assert proj["projected_wall_seconds"] > per * (10 / 3)


def test_project_fit_sharding_helps():
    proj = project_fit(120, timing(), dim_batch=1, workers=4, uncertainty=0.2)
    assert proj["within_ceiling_per_worker"] is True
    assert proj["single_worker"] is False


@pytest.mark.parametrize("over", [
    {"n_prompts": 0},
    {"workers": 0},
    {"workers": 121},
    {"workers": True},
    {"uncertainty": -0.1},
    {"uncertainty": float("nan")},
])
def test_project_fit_bad_args_blocked(over):
    kw = dict(n_prompts=120, workers=1, uncertainty=0.2)
    kw.update(over)
    with pytest.raises(Q35QBlock):
        project_fit(kw["n_prompts"], timing(), workers=kw["workers"],
                    uncertainty=kw["uncertainty"])
