"""Q35Q exact-cost projection (CPU-only, pure arithmetic; no GPU, no model).

Projects the bounded fit cost from Phase-1 aggregate timings using the exact
cost model the protocol/addendum pin: exact fitting is one forward plus
``ceil(d_model / dim_batch)`` backward passes per prompt
(anthropics/jacobian-lens). Produces an aggregate-only projection and a
fail-closed 24-hour single-worker wall-clock gate so the program never starts a
knowingly-impossible single-worker fit and retunes it after partial results.

See docs/STEER_ADDENDUM_2026-07-15_Q35Q_ROUTE_REGIME_AND_EXACT_SHARDING.md
("Mandatory exact-cost projection after Phase 1"). Storage projection covers
the d_model x d_model transport running-sum, checkpoints, and final lens.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from q35q_phase0 import QWEN35_35B_A3B_ARCH, Q35QBlock, scan_aggregate_only

# 24-hour Phase-3 single-worker wall-clock ceiling (seconds).
WALL_CLOCK_CEILING_S = 24 * 3600
D_MODEL = QWEN35_35B_A3B_ARCH["hidden_size"]  # 2048


def _pos_int(value, name):
    if type(value) is not int or value <= 0:
        raise Q35QBlock(f"{name} must be a positive int")
    return value


def _nonneg_number(value, name):
    if not isinstance(value, (int, float)) or isinstance(value, bool) \
            or not math.isfinite(value) or value < 0:
        raise Q35QBlock(f"{name} must be a finite non-negative number")
    return value


def backward_passes_per_prompt(d_model: int = D_MODEL, dim_batch: int = 1) -> int:
    """Exact backward passes per prompt = ceil(d_model / dim_batch)."""
    _pos_int(d_model, "d_model")
    _pos_int(dim_batch, "dim_batch")
    return math.ceil(d_model / dim_batch)


@dataclass
class Phase1Timing:
    """Measured aggregate seconds from the one-sequence Phase-1 gate."""
    forward_s: float
    first_backward_s: float
    steady_backward_s: float
    cleanup_s: float

    def validate(self) -> bool:
        for name in ("forward_s", "first_backward_s", "steady_backward_s", "cleanup_s"):
            _nonneg_number(getattr(self, name), name)
        return True


def project_prompt_seconds(timing: Phase1Timing, d_model: int = D_MODEL,
                           dim_batch: int = 1) -> float:
    """Projected seconds for one prompt: forward + first backward +
    (passes-1) steady backwards + cleanup."""
    timing.validate()
    nb = backward_passes_per_prompt(d_model, dim_batch)
    return (timing.forward_s + timing.first_backward_s
            + max(nb - 1, 0) * timing.steady_backward_s + timing.cleanup_s)


def project_storage_bytes(d_model: int = D_MODEL, bytes_per_elem: int = 4,
                          n_checkpoints: int = 1) -> dict:
    """Aggregate peak storage for the d_model x d_model transport: one fp32
    running sum + n_checkpoints + one final lens file."""
    _pos_int(d_model, "d_model")
    _pos_int(bytes_per_elem, "bytes_per_elem")
    if type(n_checkpoints) is not int or n_checkpoints < 0:
        raise Q35QBlock("n_checkpoints must be a non-negative int")
    matrix_bytes = d_model * d_model * bytes_per_elem
    peak = matrix_bytes * (1 + n_checkpoints + 1)  # running sum + ckpts + final
    return {"matrix_bytes": matrix_bytes, "n_checkpoints": n_checkpoints,
            "projected_peak_bytes": peak}


def project_fit(n_prompts: int, timing: Phase1Timing, d_model: int = D_MODEL,
                dim_batch: int = 1, workers: int = 1, uncertainty: float = 0.2,
                ceiling_s: int = WALL_CLOCK_CEILING_S) -> dict:
    """Aggregate-only fit projection with an uncertainty margin and a per-worker
    ceiling check. Wall time divides across identical workers (horizontal
    prompt sharding is an n_prompts-weighted mean over independent prompts)."""
    _pos_int(n_prompts, "n_prompts")
    _pos_int(workers, "workers")
    _nonneg_number(uncertainty, "uncertainty")
    _pos_int(ceiling_s, "ceiling_s")
    per = project_prompt_seconds(timing, d_model, dim_batch)
    total = per * n_prompts / workers
    total_margin = total * (1.0 + uncertainty)
    proj = {
        "d_model": d_model,
        "dim_batch": dim_batch,
        "backward_passes_per_prompt": backward_passes_per_prompt(d_model, dim_batch),
        "projected_prompt_seconds": per,
        "n_prompts": n_prompts,
        "workers": workers,
        "projected_wall_seconds": total,
        "projected_wall_seconds_with_margin": total_margin,
        "ceiling_seconds": ceiling_s,
        "uncertainty": uncertainty,
        "within_ceiling_per_worker": total_margin <= ceiling_s,
        "single_worker": workers == 1,
    }
    scan_aggregate_only(proj)
    return proj


def single_worker_feasible(n_prompts: int, timing: Phase1Timing,
                           d_model: int = D_MODEL, dim_batch: int = 1,
                           uncertainty: float = 0.2,
                           ceiling_s: int = WALL_CLOCK_CEILING_S) -> bool:
    """True iff a single-worker fit is projected (with margin) within the
    24-hour ceiling. False means Phase 3 needs an exact horizontal-shard
    manifest instead of a single-worker fit."""
    proj = project_fit(n_prompts, timing, d_model, dim_batch, workers=1,
                       uncertainty=uncertainty, ceiling_s=ceiling_s)
    return bool(proj["within_ceiling_per_worker"])
