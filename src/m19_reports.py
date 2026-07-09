#!/usr/bin/env python3
"""Build M19 aggregate action and baseline-comparison reports.

Inputs may be private runtime/action-result JSONL. Outputs are fixed-key
aggregate summaries with recursive no-text guards. Full model output is neither
required nor accepted by this reporting layer.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import action_executor as EXEC
import action_router as ROUTER
import agents_a1_run_report as RUN_REPORT


def action_summary(records, results, run_id="m19-live-full-output"):
    actions = [ROUTER.route(r) for r in records]
    summary = EXEC.build_summary(
        actions, results, run_id=run_id,
        checker_input_mode="full_transient_output")
    summary["transient_full_output_persisted"] = False
    summary["checker_verdicts_valid_for_execution_input"] = True
    category = {r["prompt_id"]: r.get("task_category") for r in records}
    retrieval = [r for r in results if r.get("action_type") == "retrieval_needed"]
    current = [r for r in retrieval if category.get(r["task_id"]) == "current_info"]
    other = [r for r in retrieval if category.get(r["task_id"]) != "current_info"]
    current_completed = sum(r["action_status"] == "completed" for r in current)
    summary["current_info_retrieval"] = {
        "planned": len(current), "completed": current_completed,
        "executable_followup_rate": (
            round(current_completed / len(current), 4) if current else None),
        "grounded_regeneration_still_required": sum(
            r["followup_needed"] for r in current),
    }
    summary["retrieval_non_current_info"] = {
        "planned": len(other),
        "completed": sum(r["action_status"] == "completed" for r in other),
        "category_distribution": dict(sorted(Counter(
            category.get(r["task_id"]) or "unknown" for r in other).items())),
        "interpretation": "heuristic_false_positive_routes_need_review",
    }
    EXEC.assert_no_text(summary)
    return summary


def baseline_comparison(m19_run, m19_actions, m15_run, m18_actions):
    def rate(n, d):
        return round(n / d, 4) if d else None

    n19 = m19_run.get("n_completed", 0)
    a19 = m19_actions.get("after_action_status_distribution", {})
    summary = {
        "comparison": "M19 vs M15 live run and M18 legacy-preview action replay",
        "workload_size": {
            "m15": m15_run.get("n_completed", m15_run.get("n_records")),
            "m19": n19,
        },
        "completion_rate": {
            "m19": rate(n19, m19_run.get("n_tasks", n19)),
        },
        "escalation_rate": {
            "m15": m15_run.get("escalation_rate"),
            "m19": m19_run.get("escalation_rate"),
        },
        "action_execution_rate": {
            "m18_legacy_preview_replay": rate(
                m18_actions.get("after_action_status_distribution", {}).get("completed", 0),
                m18_actions.get("n_actions", 0)),
            "m19_full_transient_output": rate(
                a19.get("completed", 0), m19_actions.get("n_actions", 0)),
        },
        "checker_verdicts": {
            "m18": m18_actions.get("verifier_only_checkers", {}).get(
                "verdict_distribution", {}),
            "m18_interpretation": "invalid_from_truncated_previews",
            "m19": m19_actions.get("verifier_only_checkers", {}).get(
                "verdict_distribution", {}),
            "m19_interpretation": "valid_for_full_transient_execution_input",
        },
        "retrieval_followup": {
            "m18": m18_actions.get("current_info_retrieval", {}),
            "m19": m19_actions.get("current_info_retrieval", {}),
            "interpretation": "fixture_completion_is_not_answer_correctness",
        },
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only: no prompt/output/retrieved-context text",
    }
    EXEC.assert_no_text(summary)
    return summary


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_jsonl(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--records", required=True)
    ap.add_argument("--action-results", required=True)
    ap.add_argument("--run-summary", required=True)
    ap.add_argument("--m15-summary", required=True)
    ap.add_argument("--m18-actions", required=True)
    ap.add_argument("--action-summary-out", required=True)
    ap.add_argument("--comparison-out", required=True)
    args = ap.parse_args(argv)

    records, results = _load_jsonl(args.records), _load_jsonl(args.action_results)
    act = action_summary(records, results)
    comp = baseline_comparison(
        _load_json(args.run_summary), act,
        _load_json(args.m15_summary), _load_json(args.m18_actions))
    Path(args.action_summary_out).write_text(json.dumps(act, indent=1) + "\n")
    Path(args.comparison_out).write_text(json.dumps(comp, indent=1) + "\n")
    print(f"[jlens] M19 reports: {len(records)} runtime + {len(results)} action "
          f"records -> aggregate-only outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
