"""CPU-only tests for the M32 per-band descriptive report."""
import pytest

from m32_band_descriptives import band_summary, check_no_text


def _row(band, original_pass, p_fail, resample_pass=False, bundle_pass=False):
    return {
        "band": band, "original_pass": original_pass, "p_fail": p_fail,
        "candidates": {
            "resample_t07": {"pass": resample_pass},
            "checker_guided_repair": {"pass": bundle_pass},
        },
    }


def test_band_summary_counts_and_rates():
    rows = [
        _row("band_1", True, 0.1),
        _row("band_1", False, 0.9, resample_pass=True),
        _row("band_1", False, 0.9, bundle_pass=True),
        _row("band_1", True, 0.9),   # false alarm
        _row("band_2", False, 0.1),  # missed failure
    ]
    out = band_summary(rows)
    b1 = next(b for b in out if b["band"] == "band_1")
    assert b1["n_tasks"] == 4
    assert b1["original_fail_count"] == 2
    assert b1["trigger_count"] == 3
    assert b1["trigger_true_positives"] == 2
    assert b1["trigger_false_alarms"] == 1
    assert b1["trigger_precision"] == pytest.approx(2 / 3)
    assert b1["trigger_recall"] == 1.0
    assert b1["resample_rescues"] == 1
    assert b1["bundle_rescues"] == 1
    b2 = next(b for b in out if b["band"] == "band_2")
    assert b2["trigger_count"] == 0
    assert b2["trigger_precision"] is None
    assert b2["trigger_recall"] == 0.0


def test_no_text_guard_rejects_stray_strings():
    check_no_text(band_summary([_row("band_1", False, 0.9)]))
    with pytest.raises(ValueError):
        check_no_text([{"band": "band_1", "prompt_text": "1 + 1"}])
    with pytest.raises(ValueError):
        check_no_text([{"band": "compute 12 * 34"}])
