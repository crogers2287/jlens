"""CPU-only tests for M35 track B detector fitting and LOFO discipline."""
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m35_track_b as TB  # noqa: E402


def _row(family, split, fail, f1, f2, task=None):
    return {"task_id": task or f"{family}_{split}_{f1}_{f2}",
            "family": family, "split": split,
            "original_pass": not fail,
            "features": {"f1": f1, "f2": f2}}


def _synthetic_d(seed=7):
    rng = random.Random(seed)
    rows = []
    # mixed family: feature f1 separates pass/fail
    for i in range(40):
        fail = i % 2 == 0
        rows.append(_row("mul_carry", "D", fail,
                         2.0 + rng.random() if fail else -2.0 - rng.random(),
                         rng.random(), task=f"mc_{i}"))
    # near-total-failure family
    for i in range(20):
        fail = i != 0
        rows.append(_row("mul_add", "D", fail, rng.random(), rng.random(),
                         task=f"ma_{i}"))
    # high-competence family
    for i in range(20):
        fail = i == 0
        rows.append(_row("add_carry", "D", fail, rng.random(), rng.random(),
                         task=f"ac_{i}"))
    return rows


def test_hierarchical_uses_prior_gates():
    d_rows = _synthetic_d()
    variants = TB.fit_variants(d_rows)
    high_fail = _row("mul_add", "B_test", True, 0.5, 0.5, task="x1")
    high_pass = _row("add_carry", "B_test", False, 0.5, 0.5, task="x2")
    assert TB.p_fail(variants, "hierarchical", high_fail) == \
        pytest.approx(19 / 20)
    assert TB.p_fail(variants, "hierarchical", high_pass) == \
        pytest.approx(1 / 20)
    mixed = _row("mul_carry", "B_test", True, 3.0, 0.5, task="x3")
    assert TB.p_fail(variants, "hierarchical", mixed) > 0.5


def test_global_variant_separates_mixed_family():
    variants = TB.fit_variants(_synthetic_d())
    fail_like = _row("mul_carry", "B_test", True, 3.0, 0.5, task="y1")
    pass_like = _row("mul_carry", "B_test", False, -3.0, 0.5, task="y2")
    assert TB.p_fail(variants, "global", fail_like) > 0.5
    assert TB.p_fail(variants, "global", pass_like) < 0.5


def test_lofo_maps_withheld_family_to_unknown():
    d_rows = _synthetic_d()
    variants = TB.lofo_variants(d_rows, "mul_carry")
    assert "mul_carry" not in variants["families"]
    assert "mul_carry" not in variants["priors"]
    # global one-hot vector contains no withheld indicator
    assert not any(name == "family_mul_carry"
                   for name in variants["global"].features)
    # scoring a withheld-family row falls back without error
    row = _row("mul_carry", "B_test", True, 3.0, 0.5, task="z1")
    for variant in ("global", "per_family", "hierarchical"):
        assert 0.0 <= TB.p_fail(variants, variant, row) <= 1.0


def test_config_hash_changes_with_fit_data():
    d_rows = _synthetic_d()
    h1 = TB.config_hash(TB.fit_variants(d_rows))
    h2 = TB.config_hash(TB.fit_variants(d_rows[:-1]))
    assert h1 != h2
    assert h1 == TB.config_hash(TB.fit_variants(_synthetic_d()))


def test_detector_metrics_counts():
    d_rows = _synthetic_d()
    variants = TB.fit_variants(d_rows)
    rows = [_row("mul_carry", "B_test", True, 3.0, 0.5, task="m1"),
            _row("mul_carry", "B_test", False, -3.0, 0.5, task="m2")]
    metrics = TB.detector_metrics(variants, "global", rows)
    assert metrics["n_rows"] == 2
    assert metrics["original_fail_count"] == 1
    assert metrics["trigger_count"] == 1
    assert metrics["trigger_precision"] == 1.0
    assert metrics["trigger_recall"] == 1.0


def test_b_test_reread_refused(tmp_path, monkeypatch):
    import json
    rows_path = tmp_path / "rows.jsonl"
    d_rows = _synthetic_d()
    b_row = _row("mul_carry", "B_test", True, 3.0, 0.5, task="b1")
    rows_path.write_text("".join(json.dumps(r) + "\n"
                                 for r in d_rows + [b_row]))
    freeze_path = tmp_path / "freeze.json"
    eval_path = tmp_path / "eval.json"
    TB.main(["--rows", str(rows_path), "--stage", "fit",
             "--freeze-out", str(freeze_path)])
    TB.main(["--rows", str(rows_path), "--stage", "b_test",
             "--freeze-out", str(freeze_path),
             "--evaluation-out", str(eval_path)])
    with pytest.raises(ValueError, match="already been read"):
        TB.main(["--rows", str(rows_path), "--stage", "b_test",
                 "--freeze-out", str(freeze_path),
                 "--evaluation-out", str(eval_path)])
