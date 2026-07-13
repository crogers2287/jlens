"""Steer-dfcade7 conformance tests for the hardened M38E dev sweep.

Synthetic fixtures only; no engine, no model, no official rows.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

import m38e_dev_sweep as M
from m38e_dev_sweep import (CAP_2048, CAP_4096, GATES, SweepBlocked,
                            band_report, material_reduction, pilot_subset,
                            task_identity, task_set_digest, validate_rows)


def make_task(i, family="mod_chain", band="b1"):
    return {"task_id": f"m38e_{family}_{band}_{i:03d}", "family": family,
            "band": band, "task_index": i,
            "generator_seed_id": M.GENERATOR_SEED_ID,
            "prompt": f"synthetic prompt {i}", "known_answer": str(i)}


IDENT_TASKS = [make_task(i) for i in range(24)]
IDENT = {"run_id": "r" * 16, "manifest_digest": "m" * 64,
         "task_set_digest": task_set_digest(IDENT_TASKS),
         "generator_seed_id": M.GENERATOR_SEED_ID,
         "provenance": {"source_commit": "c" * 40},
         "revision_pinned": "3e522d4e46438c782789b73c8ff4503e0edd037c",
         "tasks": IDENT_TASKS}
OVERRIDE = "o" * 16


def make_row(i, kind="official_2048", verdict="pass", truncated=False,
             **over):
    task = IDENT_TASKS[i]
    row = {**task_identity(task), "run_kind": M.RUN_KIND_OFFICIAL,
           "run_id": IDENT["run_id"],
           "manifest_digest": IDENT["manifest_digest"],
           "task_set_digest": IDENT["task_set_digest"],
           "generator_seed_id": M.GENERATOR_SEED_ID,
           "source_commit": "c" * 40,
           "revision_pinned": IDENT["revision_pinned"],
           "override_hash": OVERRIDE, "attempt_kind": kind,
           "output_cap": (CAP_2048 if kind in ("official_2048",
                                               M.ATTEMPT_KIND_SMOKE)
                          else CAP_4096),
           "verdict": verdict, "truncated": truncated}
    row.update(over)
    return row


# -- resume provenance -----------------------------------------------------

def test_validate_rows_accepts_exact_match():
    validate_rows([make_row(0), make_row(1)], IDENT, OVERRIDE)


@pytest.mark.parametrize("field,value", [
    ("run_id", "x" * 16), ("manifest_digest", "y" * 64),
    ("task_set_digest", "z" * 64), ("source_commit", "d" * 40),
    ("revision_pinned", "deadbeef"), ("override_hash", "p" * 16)])
def test_validate_rows_rejects_provenance_mismatch(field, value):
    with pytest.raises(SweepBlocked, match="mismatch"):
        validate_rows([make_row(0, **{field: value})], IDENT, OVERRIDE)


def test_validate_rows_rejects_unknown_duplicate_and_hash_change():
    ghost = make_row(0)
    ghost["task_id"] = "m38e_ghost_b9_000"
    with pytest.raises(SweepBlocked, match="unknown task id"):
        validate_rows([ghost], IDENT, OVERRIDE)
    with pytest.raises(SweepBlocked, match="duplicate attempt"):
        validate_rows([make_row(0), make_row(0)], IDENT, OVERRIDE)
    tampered = make_row(0, prompt_sha256="0" * 64)
    with pytest.raises(SweepBlocked, match="hash changed"):
        validate_rows([tampered], IDENT, OVERRIDE)
    badcap = make_row(0)
    badcap["output_cap"] = 4096
    with pytest.raises(SweepBlocked, match="cap mismatch"):
        validate_rows([badcap], IDENT, OVERRIDE)


def test_smoke_marker_in_official_ledger_is_named_block():
    bad = make_row(0)
    bad["attempt_kind"] = "smoke_2048"
    with pytest.raises(SweepBlocked, match="attempt_kind"):
        validate_rows([bad], IDENT, OVERRIDE)


# -- pilot escalation --------------------------------------------------------

def test_pilot_subset_deterministic_and_bounded():
    ids = [f"m38e_mod_chain_b3_{i:03d}" for i in range(15)]
    a, b = pilot_subset(list(ids)), pilot_subset(list(reversed(ids)))
    assert a == b and len(a) == 8
    short = pilot_subset(ids[:5])
    assert len(short) == 5
    expected = sorted(ids, key=lambda t: hashlib.sha256(
        ("m38e-4096-pilot-v1:" + t).encode()).hexdigest())[:8]
    assert a == expected


def test_material_reduction_rule():
    def rows(resolved, total):
        return ([{"truncated": False}] * resolved
                + [{"truncated": True}] * (total - resolved))
    assert material_reduction(rows(4, 8))        # half and >=2
    assert material_reduction(rows(2, 4))
    assert not material_reduction(rows(3, 8))    # under half
    assert not material_reduction(rows(1, 2))    # >=half but only 1
    assert not material_reduction([])


# -- eligibility arithmetic ----------------------------------------------------

def band_rows(cc, ci, trunc):
    rows = []
    for i in range(cc):
        rows.append({"verdict": "pass", "truncated": False})
    for i in range(ci):
        rows.append({"verdict": "fail", "truncated": False})
    for i in range(trunc):
        rows.append({"verdict": "fail", "truncated": True})
    return rows


def test_raw_pass_rate_gated_on_full_denominator_inclusive():
    # Both rates are reported; the GATE uses the raw (full-denominator)
    # rate. 16cc/6ci/2tr: raw 16/24 = 0.6667 in range -> eligible.
    r = band_report(band_rows(16, 6, 2), CAP_2048, "not_triggered")
    assert r["raw_verified_pass_rate"] == round(16 / 24, 4)
    assert r["completed_pass_rate"] == round(16 / 22, 4)
    assert r["eligible"]
    # Floor: 6/24 = 0.25 in range passes; 4/24 = 0.1667 < 0.20 fails
    # the raw gate (and cc minimum) — never the completed-only rate.
    ok = band_report(band_rows(6, 16, 2), CAP_2048, "not_triggered")
    assert ok["eligible"]
    low = band_report(band_rows(4, 18, 2), CAP_2048, "not_triggered")
    assert not low["eligible"]


def test_high_pass_band_ineligible():
    r = band_report(band_rows(22, 2, 0), CAP_2048, "not_triggered")
    assert not r["eligible"]          # raw pass 22/24 > 0.80 and ci < 6


def test_truncation_and_completion_gates_exact():
    # 3/24 truncated = 0.125 > 0.10 -> ineligible on the final ledger.
    r = band_report(band_rows(10, 11, 3), CAP_2048, "not_triggered")
    assert not r["eligible"]
    # 2/24 ~ 0.0833 <= 0.10 passes (with rates in range).
    ok = band_report(band_rows(10, 12, 2), CAP_2048, "not_triggered")
    assert ok["eligible"]


def test_escalation_failed_band_is_ineligible_even_with_good_rates():
    r = band_report(band_rows(10, 12, 2), CAP_2048, "escalation_failed")
    assert not r["eligible"]


def test_incomplete_band_ineligible():
    r = band_report(band_rows(5, 5, 2), CAP_2048, "not_triggered")
    assert r["n"] == 12 and not r["eligible"]


# -- steer a9b91f7 additions ---------------------------------------------------

def smoke_row(i):
    r = make_row(i, kind=M.ATTEMPT_KIND_SMOKE)
    r["run_kind"] = M.RUN_KIND_SMOKE
    return r


def test_actual_smoke_row_rejected_by_official_validator():
    # A genuine smoke row (matching every hash/commit/cap) inserted into
    # the official ledger must be rejected on the run_kind boundary.
    with pytest.raises(SweepBlocked, match="run_kind"):
        validate_rows([smoke_row(0)], IDENT, OVERRIDE)


def test_missing_or_unknown_run_kind_blocks():
    r = make_row(0)
    del r["run_kind"]
    with pytest.raises(SweepBlocked, match="run_kind"):
        validate_rows([r], IDENT, OVERRIDE)
    r2 = make_row(0)
    r2["run_kind"] = "m38e_something_else"
    with pytest.raises(SweepBlocked, match="run_kind"):
        validate_rows([r2], IDENT, OVERRIDE)


def test_official_row_rejected_by_smoke_validator():
    with pytest.raises(SweepBlocked, match="run_kind"):
        validate_rows([make_row(0)], IDENT, OVERRIDE,
                      run_kind=M.RUN_KIND_SMOKE,
                      allowed_kinds=(M.ATTEMPT_KIND_SMOKE,),
                      allowed_task_ids={IDENT_TASKS[0]["task_id"]})


def test_smoke_ledger_exact_validation():
    ok = smoke_row(0)
    validate_rows([ok], IDENT, OVERRIDE, run_kind=M.RUN_KIND_SMOKE,
                  allowed_kinds=(M.ATTEMPT_KIND_SMOKE,),
                  allowed_task_ids={ok["task_id"]})
    # out-of-subset smoke row blocks
    with pytest.raises(SweepBlocked, match="subset"):
        validate_rows([smoke_row(1)], IDENT, OVERRIDE,
                      run_kind=M.RUN_KIND_SMOKE,
                      allowed_kinds=(M.ATTEMPT_KIND_SMOKE,),
                      allowed_task_ids={IDENT_TASKS[0]["task_id"]})
    # foreign source commit blocks
    stale = smoke_row(0)
    stale["source_commit"] = "e" * 40
    with pytest.raises(SweepBlocked, match="mismatch"):
        validate_rows([stale], IDENT, OVERRIDE,
                      run_kind=M.RUN_KIND_SMOKE,
                      allowed_kinds=(M.ATTEMPT_KIND_SMOKE,),
                      allowed_task_ids={stale["task_id"]})
    # wrong cap blocks
    badcap = smoke_row(0)
    badcap["output_cap"] = CAP_4096
    with pytest.raises(SweepBlocked, match="cap"):
        validate_rows([badcap], IDENT, OVERRIDE,
                      run_kind=M.RUN_KIND_SMOKE,
                      allowed_kinds=(M.ATTEMPT_KIND_SMOKE,),
                      allowed_task_ids={badcap["task_id"]})
    # duplicate blocks
    with pytest.raises(SweepBlocked, match="duplicate"):
        validate_rows([smoke_row(0), smoke_row(0)], IDENT, OVERRIDE,
                      run_kind=M.RUN_KIND_SMOKE,
                      allowed_kinds=(M.ATTEMPT_KIND_SMOKE,),
                      allowed_task_ids={ok["task_id"]})


def test_smoke_then_official_zero_row_reuse():
    # Official validator sees the smoke row set as foreign; and the
    # official existing-keys set derived from an EMPTY official ledger
    # shares nothing with smoke keys (smoke_2048 != official_2048).
    smoke_keys = {(smoke_row(i)["task_id"], smoke_row(i)["attempt_kind"])
                  for i in range(2)}
    official_needed = {(t["task_id"], "official_2048")
                       for t in IDENT_TASKS[:2]}
    assert smoke_keys.isdisjoint(official_needed)


def test_task_index_and_seed_bound_in_digest_and_rows():
    base = task_set_digest(IDENT_TASKS)
    shifted = [dict(t) for t in IDENT_TASKS]
    shifted[0]["task_index"] = 99
    assert task_set_digest(shifted) != base
    reseeded = [dict(t) for t in IDENT_TASKS]
    reseeded[0]["generator_seed_id"] = "m38e-dev-v2"
    assert task_set_digest(reseeded) != base
    # row-level: task_index change blocks resume
    r = make_row(0)
    r["task_index"] = 99
    with pytest.raises(SweepBlocked, match="task_index"):
        validate_rows([r], IDENT, OVERRIDE)
    r2 = make_row(0)
    r2["generator_seed_id"] = "m38e-dev-v2"
    with pytest.raises(SweepBlocked, match="generator_seed_id"):
        validate_rows([r2], IDENT, OVERRIDE)


def test_expected_tasks_carry_explicit_index_and_seed():
    tasks = M.expected_tasks()
    assert len(tasks) == 288
    assert all(isinstance(t["task_index"], int) for t in tasks)
    assert all(t["generator_seed_id"] == M.GENERATOR_SEED_ID
               for t in tasks)
    ident0 = task_identity(tasks[0])
    assert "task_index" in ident0 and "generator_seed_id" in ident0
