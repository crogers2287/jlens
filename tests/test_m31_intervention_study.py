#!/usr/bin/env python3
"""M31 intervention-study tests are CPU-only and no-network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m30_decisive_increment as M30  # noqa: E402
import m31_intervention_study as M31  # noqa: E402
from test_m30_decisive_increment import _synthetic_files  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m31_intervention_manifest.json"
M29_MANIFEST_PATH = ROOT / "data/prompts/m29_power_manifest.json"
M30_MANIFEST_PATH = ROOT / "data/prompts/m30_decisive_manifest.json"


def _rows(*, informative=True, retry_fixes=True):
    rows = []
    for index in range(192):
        original_pass = index % 2 == 0
        retry_pass = (not original_pass and retry_fixes and index % 4 == 1) \
            or (original_pass and index % 8 != 7)
        p_fail = (0.9 if not original_pass else 0.1) if informative else 0.5
        rows.append({"task_id": f"row_{index:03d}", "band": "band_3",
                     "original_pass": original_pass,
                     "retry_pass": retry_pass, "p_fail": p_fail})
    return rows


def test_generation_is_deterministic_and_disjoint_from_m29_and_m30():
    manifest = M31.load_manifest(MANIFEST_PATH)
    tasks = M31.generate_tasks(manifest, M29_MANIFEST_PATH, M30_MANIFEST_PATH)
    assert tasks == M31.generate_tasks(
        manifest, M29_MANIFEST_PATH, M30_MANIFEST_PATH)
    assert len(tasks) == 192
    prior = M31.prior_tuples_by_band(M29_MANIFEST_PATH, M30_MANIFEST_PATH)
    bands = {band["band_id"]: band for band in manifest["bands"]}
    counts = {}
    for task in tasks:
        band = bands[task["m31_band"]]
        a, b = task["expression"].split(band["operator"], 1)
        pair = (int(a), int(b))
        assert pair not in prior[task["m31_band"]]
        assert band["operand_a_range"][0] <= pair[0] <= band["operand_a_range"][1]
        counts[task["m31_band"]] = counts.get(task["m31_band"], 0) + 1
    assert all(counts[band_id] == 32 for band_id in bands)


def test_frozen_score_verification_accepts_match_and_rejects_mismatch(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    del manifest
    split, _ = M30.load_dataset(
        M30.load_manifest(M30_MANIFEST_PATH), labels_path, telemetry_path)
    m30_manifest = M30.load_manifest(M30_MANIFEST_PATH)
    import m27_frozen_error_holdout as M27
    classifier = M27.FrozenDictCentroid.fit(
        [row for _, row in split["train"]],
        [label_row["label"] for label_row, _ in split["train"]],
        m30_manifest["frozen_feature_sets"]["full_telemetry"])
    confusion = {true: {pred: 0 for pred in ("fail", "pass")}
                 for true in ("fail", "pass")}
    for label_row, row in split["holdout"]:
        confusion[label_row["label"]][classifier.predict(row)] += 1
    evaluation_path = tmp_path / "m30_eval.json"
    evaluation_path.write_text(json.dumps(
        {"evaluations": {"full_telemetry": {"confusion_matrix": confusion}}}))
    restored = M31.frozen_m30_classifier(
        M30_MANIFEST_PATH, labels_path, telemetry_path, evaluation_path)
    assert restored.features == classifier.features

    wrong = json.loads(evaluation_path.read_text())
    wrong["evaluations"]["full_telemetry"]["confusion_matrix"]["fail"]["fail"] += 1
    evaluation_path.write_text(json.dumps(wrong))
    try:
        M31.frozen_m30_classifier(
            M30_MANIFEST_PATH, labels_path, telemetry_path, evaluation_path)
    except ValueError as error:
        assert "verification failed" in str(error)
    else:
        raise AssertionError("expected frozen-score verification to fail")


def test_success_delta_bootstrap_zero_for_identical():
    success = [1, 0] * 30
    assert M31._success_delta_bootstrap(success, list(success), "t") == [0.0, 0.0]


def test_policies_share_retry_and_report_costs():
    manifest = M31.load_manifest(MANIFEST_PATH)
    report, triggered = M31.run_policies(manifest, _rows())
    metrics = report["policy_metrics"]
    assert metrics["no_retry"]["retries_used"] == 0
    assert metrics["always_retry"]["retries_used"] == 192
    assert (metrics["random_retry"]["retries_used"]
            == metrics["telemetry_triggered"]["retries_used"]
            == report["trigger_count"] == len(triggered) == 96)
    # A perfect trigger never retries an originally-correct task.
    assert metrics["telemetry_triggered"]["false_alarm_count"] == 0
    assert metrics["telemetry_triggered"]["errors_introduced"] == 0
    assert metrics["telemetry_triggered"]["errors_rescued"] == 48
    assert (metrics["telemetry_triggered"]["verified_success_rate"]
            > metrics["no_retry"]["verified_success_rate"])
    assert report["telemetry_policy_classification"] == "useful"


def test_uninformative_trigger_is_not_classified_useful():
    manifest = M31.load_manifest(MANIFEST_PATH)
    report, _ = M31.run_policies(manifest, _rows(informative=False))
    assert report["telemetry_policy_classification"] in (
        "not_established", "harmful")


def test_harmful_retry_is_classified_harmful():
    manifest = M31.load_manifest(MANIFEST_PATH)
    rows = []
    for index in range(192):
        original_pass = index % 4 != 3
        rows.append({"task_id": f"row_{index:03d}", "band": "band_3",
                     "original_pass": original_pass,
                     "retry_pass": False,
                     "p_fail": 0.9 if original_pass else 0.1})
    report, _ = M31.run_policies(manifest, rows)
    assert report["telemetry_policy_classification"] == "harmful"


def test_policy_report_is_aggregate_only():
    manifest = M31.load_manifest(MANIFEST_PATH)
    report, _ = M31.run_policies(manifest, _rows())
    public = json.dumps(report)
    assert "row_0" not in public and "m31_b" not in public
    assert "task_id" not in public
