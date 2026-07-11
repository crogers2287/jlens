#!/usr/bin/env python3
"""M33 routing policy in supervisor SHADOW mode — advisory-only (track C).

Annotates supervisor shadow records with the frozen M33 tool-routing
recommendation and produces an aggregate-only audit rollup. It never blocks,
executes, or performs any action; recommendations live in their own stream,
separate from supervisor actions, so the shadow stays causally interpretable.

Real-workload records have no band metadata, so the frozen M30 classifier is
scored with an explicit `band: unknown` (all band one-hots zero). That basis
is recorded per record and per rollup; per the M35 protocol it is advisory
product telemetry, never a research claim. Records without a telemetry
feature source abstain and are counted in the eligible denominator logging.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import m26_objective_error as M26  # noqa: E402
import m28_ablation_calibration as M28  # noqa: E402

POLICY_VERSION = "m33-shadow-v1"
CHECKABLE_CATEGORIES = ("math", "numeric", "json", "exact")
THRESHOLD = 0.5
SCORE_BANDS = ((0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.01))

CONFIG = {
    "policy_version": POLICY_VERSION,
    "detector": "frozen M30 full_telemetry centroid",
    "threshold_fail_probability": THRESHOLD,
    "score_basis": "bandless_unknown",
    "feature_schema": "m26 FEATURES v1",
    "checkable_categories": list(CHECKABLE_CATEGORIES),
    "tool_call_unit": "advised only; never executed",
}
CONFIG_HASH = hashlib.sha256(
    json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()[:16]


def _score_band(p_fail):
    for index, (low, high) in enumerate(SCORE_BANDS):
        if low <= p_fail < high:
            return f"band_{index}"
    return "band_out_of_range"


def bandless_features(telemetry):
    """M26 feature vector with no band one-hots (band unknown)."""
    row = {}
    for name, getter in M26.FEATURES.items():
        value = getter(telemetry)
        if value is None:
            raise ValueError(f"missing feature {name}")
        row[name] = float(value)
    return row


def advise(record, telemetry, classifier):
    """Advisory-only recommendation for one supervisor shadow record."""
    base = {
        "prompt_id": record.get("prompt_id"),
        "workload_class": record.get("task_category") or "unknown",
        "policy_version": POLICY_VERSION,
        "config_hash": CONFIG_HASH,
        "regime_band": "unknown",
        "mode": "shadow_advisory_only",
        "executed": False,
    }
    if record.get("task_category") not in CHECKABLE_CATEGORIES:
        return {**base, "eligible": False,
                "abstain_reason": "category_not_checkable",
                "recommendation": "abstain", "p_fail": None,
                "score_band": None}
    if telemetry is None or record.get("telemetry_missing"):
        return {**base, "eligible": False,
                "abstain_reason": "no_telemetry",
                "recommendation": "abstain", "p_fail": None,
                "score_band": None}
    try:
        features = bandless_features(telemetry)
    except ValueError:
        return {**base, "eligible": False,
                "abstain_reason": "incomplete_features",
                "recommendation": "abstain", "p_fail": None,
                "score_band": None}
    p_fail = M28.fail_probability(classifier, features)
    return {**base, "eligible": True, "abstain_reason": None,
            "recommendation": ("advise_tool_check" if p_fail >= THRESHOLD
                               else "no_action"),
            "p_fail": p_fail, "score_band": _score_band(p_fail)}


ROLLUP_ALLOWED_KEYS = {
    "workload_class", "score_band", "recommendation", "count",
    "auto_was_wrong_true", "auto_was_wrong_false", "auto_was_wrong_unset",
}


def rollup(advisories, records_by_id):
    """Aggregate-only audit rollup with full contingency counts."""
    cells = {}
    abstain_reasons = Counter()
    for advisory in advisories:
        if not advisory["eligible"]:
            abstain_reasons[advisory["abstain_reason"]] += 1
        key = (advisory["workload_class"], advisory["score_band"],
               advisory["recommendation"])
        cell = cells.setdefault(key, Counter())
        cell["count"] += 1
        record = records_by_id.get(advisory["prompt_id"]) or {}
        auto = (record.get("auto_outcome") or {}).get("auto_was_wrong")
        if auto is True:
            cell["auto_was_wrong_true"] += 1
        elif auto is False:
            cell["auto_was_wrong_false"] += 1
        else:
            cell["auto_was_wrong_unset"] += 1
    rows = [{"workload_class": wc, "score_band": sb, "recommendation": rec,
             **counts}
            for (wc, sb, rec), counts in sorted(
                cells.items(), key=lambda item: str(item[0]))]
    label_keys = ("workload_class", "score_band", "recommendation")
    for row in rows:
        for key, value in row.items():
            if key not in ROLLUP_ALLOWED_KEYS:
                raise ValueError(f"unexpected rollup key: {key}")
            if key in label_keys:
                if not (value is None or isinstance(value, str)):
                    raise ValueError(f"non-label value in rollup: {key}")
            elif not isinstance(value, int):
                raise ValueError(f"non-count value in rollup: {key}")
    total = len(advisories)
    eligible = sum(1 for a in advisories if a["eligible"])
    advised = sum(1 for a in advisories
                  if a["recommendation"] == "advise_tool_check")
    return {
        "schema_version": 1,
        "run_kind": "m33_shadow_policy_rollup",
        "policy_version": POLICY_VERSION,
        "config": CONFIG,
        "config_hash": CONFIG_HASH,
        "eligible_denominator": total,
        "eligible_count": eligible,
        "abstain_counts": dict(abstain_reasons),
        "advised_tool_call_rate_over_eligible": (advised / eligible)
        if eligible else None,
        "actual_tool_invocations": 0,
        "cells": rows,
        "advisory_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate counts only; no ids/text/paths",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--shadow-log", required=True,
                    help="supervisor auto_outcome jsonl (private, read local)")
    ap.add_argument("--telemetry",
                    help="hf telemetry records jsonl keyed by task_id/prompt_id")
    ap.add_argument("--m30-manifest",
                    default="data/prompts/m30_decisive_manifest.json")
    ap.add_argument("--m30-labels",
                    default="reports/shadow/private/m30_error_labels_local.jsonl")
    ap.add_argument("--m30-telemetry",
                    default="reports/shadow/private/"
                            "m30_hf_telemetry_records_local.jsonl")
    ap.add_argument("--m30-evaluation",
                    default="reports/telemetry/"
                            "hf_m30_decisive_increment_evaluation.json")
    ap.add_argument("--advisories-out",
                    default="reports/shadow/private/"
                            "m33_shadow_advisories_local.jsonl")
    ap.add_argument("--rollup-out",
                    default="reports/telemetry/m33_shadow_policy_rollup.json")
    args = ap.parse_args(argv)

    import m31_intervention_study as M31
    classifier = M31.frozen_m30_classifier(
        args.m30_manifest, args.m30_labels, args.m30_telemetry,
        args.m30_evaluation)

    records = [json.loads(line) for line in
               Path(args.shadow_log).read_text().splitlines() if line]
    telemetry_by_id = {}
    if args.telemetry:
        for line in Path(args.telemetry).read_text().splitlines():
            if line:
                row = json.loads(line)
                telemetry_by_id[row.get("task_id")
                                or row.get("prompt_id")] = row

    advisories = [advise(record,
                         telemetry_by_id.get(record.get("prompt_id")),
                         classifier)
                  for record in records]
    out = Path(args.advisories_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(a) + "\n" for a in advisories))
    records_by_id = {r.get("prompt_id"): r for r in records}
    summary = rollup(advisories, records_by_id)
    Path(args.rollup_out).write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[jlens] m33 shadow policy: {summary['eligible_denominator']} "
          f"records, {summary['eligible_count']} eligible, "
          f"abstain={summary['abstain_counts']}, "
          f"advise_rate={summary['advised_tool_call_rate_over_eligible']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
