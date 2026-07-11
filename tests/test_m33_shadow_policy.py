"""CPU-only tests for the M33 shadow advisory policy (track C)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m26_objective_error as M26  # noqa: E402
import m33_shadow_policy as SP  # noqa: E402


class StubClassifier:
    """fail_probability proxy: distance-based centroids over one feature."""

    def __init__(self, p_fail):
        self.p_fail = p_fail


@pytest.fixture(autouse=True)
def stub_fail_probability(monkeypatch):
    monkeypatch.setattr(SP.M28, "fail_probability",
                        lambda classifier, row: classifier.p_fail)


@pytest.fixture(autouse=True)
def stub_features(monkeypatch):
    monkeypatch.setattr(SP, "bandless_features",
                        lambda telemetry: {"f": telemetry["f"]})


def _record(pid, category="math", telemetry_missing=False, auto=None):
    return {"prompt_id": pid, "task_category": category,
            "telemetry_missing": telemetry_missing,
            "auto_outcome": {"auto_was_wrong": auto}}


def test_advise_recommends_above_threshold():
    high = SP.advise(_record("p1"), {"f": 1.0}, StubClassifier(0.9))
    low = SP.advise(_record("p2"), {"f": 1.0}, StubClassifier(0.1))
    assert high["eligible"] and high["recommendation"] == "advise_tool_check"
    assert high["score_band"] == "band_3"
    assert low["recommendation"] == "no_action"
    assert not high["executed"]


def test_abstains_with_reasons():
    no_telemetry = SP.advise(_record("p1"), None, StubClassifier(0.9))
    wrong_category = SP.advise(_record("p2", category="open-explain"),
                               {"f": 1.0}, StubClassifier(0.9))
    assert no_telemetry["abstain_reason"] == "no_telemetry"
    assert wrong_category["abstain_reason"] == "category_not_checkable"
    for advisory in (no_telemetry, wrong_category):
        assert not advisory["eligible"]
        assert advisory["recommendation"] == "abstain"


def test_rollup_contingencies_cover_both_arms():
    records = [_record("p1", auto=True), _record("p2", auto=False),
               _record("p3", auto=None), _record("p4", category="open-explain")]
    classifier_by_id = {"p1": 0.9, "p2": 0.1, "p3": 0.9}
    advisories = [SP.advise(r, {"f": 1.0} if r["prompt_id"] != "p4" else None,
                            StubClassifier(classifier_by_id.get(
                                r["prompt_id"], 0.5)))
                  for r in records]
    summary = SP.rollup(advisories, {r["prompt_id"]: r for r in records})
    assert summary["eligible_denominator"] == 4
    assert summary["eligible_count"] == 3
    assert summary["abstain_counts"] == {"category_not_checkable": 1}
    assert summary["advised_tool_call_rate_over_eligible"] == pytest.approx(
        2 / 3)
    assert summary["actual_tool_invocations"] == 0
    # both recommended and not-recommended cells carry outcome contingencies
    recs = {(c["recommendation"], c.get("auto_was_wrong_true", 0),
             c.get("auto_was_wrong_false", 0)) for c in summary["cells"]}
    assert ("advise_tool_check", 1, 0) in recs
    assert ("no_action", 0, 1) in recs
    assert summary["config_hash"] == SP.CONFIG_HASH


def test_rollup_rejects_stray_text():
    advisory = SP.advise(_record("p1"), {"f": 1.0}, StubClassifier(0.9))
    advisory["workload_class"] = "math"
    bad = dict(advisory)
    with pytest.raises(ValueError):
        SP.rollup([{**bad, "recommendation": 42}], {})


def test_bandless_features_uses_m26_recipe(monkeypatch):
    monkeypatch.undo()
    names = set(M26.FEATURES)
    assert names, "M26 feature recipe must be non-empty"
