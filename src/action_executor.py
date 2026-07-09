#!/usr/bin/env python3
"""M18 safe action executor — explicit opt-in, fixture/read-only paths only.

Consumes action_record_v1 records and produces aggregate-safe
action_result_v1 records. Execution is DISABLED unless ``enabled=True`` or the
CLI receives ``--execute``. Retrieval is limited to the in-memory/file-backed
FixtureRetrievalAdapter; deterministic checking is limited to an explicit
function allowlist. No shell, subprocess, dynamic import, or model-generated
command is ever executed.

Raw task/output/retrieved context may be supplied from gitignored local inputs,
but never enters an action result or public summary. Evidence is hashed. Both
auto_outcome and action_result remain shadow candidates, never gold.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents_a1_run_report as RUN_REPORT  # noqa: E402
import verifiers as VZ  # noqa: E402


APPROVED_CHECKERS = {
    "math_checker": VZ.math_checker,
    "json_object_check": VZ.json_object_check,
    "numeric_tolerant_check": VZ.numeric_tolerant_check,
}
ALLOWED_RETRIEVAL_SOURCE_KINDS = {"fixture", "public_fixture"}


class RetrievalError(Exception):
    """A bounded retrieval adapter refusal with a stable public error code."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class FixtureRetrievalAdapter:
    """Read-only retrieval from trusted fixture rows.

    Each row is keyed by task id and contains ``context`` (kept transient), an
    optional confidence, and ``source_kind`` = fixture/public_fixture. The raw
    context is returned only to the executor long enough to hash it; it is never
    copied into action_result_v1 or a public report.
    """

    name = "fixture_retrieval"

    def __init__(self, rows: dict[str, dict]):
        self.rows = rows

    @classmethod
    def from_json(cls, path):
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        rows = raw.get("records", raw) if isinstance(raw, dict) else raw
        if isinstance(rows, list):
            rows = {r["task_id"]: r for r in rows}
        if not isinstance(rows, dict):
            raise ValueError("retrieval fixture must be an object or record list")
        return cls(rows)

    def retrieve(self, task_id: str) -> dict:
        # A trusted fixture may provide a bounded wildcard payload for execution-
        # path tests spanning many task ids. It is still fixture-only and the
        # task id remains part of the result evidence hash.
        row = self.rows.get(task_id) or self.rows.get("*")
        if not row:
            raise RetrievalError("retrieval_not_found")
        if row.get("source_kind", "fixture") not in ALLOWED_RETRIEVAL_SOURCE_KINDS:
            raise RetrievalError("retrieval_source_not_allowed")
        context = row.get("context")
        if not isinstance(context, str) or not context.strip():
            raise RetrievalError("retrieval_not_found")
        confidence = float(row.get("confidence", 0.8))
        return {"context": context, "confidence": max(0.0, min(1.0, confidence))}


def _base(action, *, status, executor, result_type, confidence=None,
          verdict=None, followup=True, error=None, evidence_parts=()):
    """Build one fixed-shape, no-text action_result_v1 record."""
    return {
        "task_id": action.get("task_id", ""),
        "action_type": action.get("action_type", "no_action"),
        "action_evidence_hash": action.get("evidence_hash"),
        "action_status": status,
        "executor_name": executor,
        "result_type": result_type,
        "result_confidence": confidence,
        "checker_verdict": verdict,
        "evidence_hash": VZ.evidence_hash(
            action.get("task_id", ""), action.get("action_type", ""),
            status, executor, error or "ok", *evidence_parts),
        "followup_needed": bool(followup),
        "error_code": error,
        "candidate_only": True,
    }


def _checker_kwargs(task: dict) -> dict:
    """Fixed metadata projection; no model-provided callable/command fields."""
    return {
        "known_answer": task.get("known_answer"),
        "expression": task.get("expression"),
        "required_keys": task.get("json_required"),
        "expected_type": task.get("json_type", "object"),
        "expected_value": task.get("expected_value"),
        "tolerance": task.get("tolerance"),
        "rel_tolerance": task.get("rel_tolerance"),
        "expected_units": task.get("expected_units"),
        "accepted_values": task.get("accepted_values"),
    }


def execute_action(action: dict, *, task=None, runtime=None, enabled=False,
                   retrieval_adapter=None) -> dict:
    """Execute one approved action and return action_result_v1.

    ``task`` contains trusted task metadata. ``runtime`` may contain a private
    full ``output`` or the legacy ``output_preview`` fallback. Neither is
    emitted. This function has no general callable/command execution surface.
    """
    task = task or {}
    runtime = runtime or {}
    action_type = action.get("action_type")

    if not enabled:
        return _base(action, status="skipped", executor="disabled",
                     result_type="no_result",
                     followup=action_type in {"retrieval_needed", "checker_needed",
                                               "review_needed"},
                     error="execution_disabled")
    if action.get("status") != "planned":
        return _base(action, status="skipped", executor="none",
                     result_type="no_result", followup=True,
                     error="action_not_planned")

    if action_type == "retrieval_needed":
        if not isinstance(retrieval_adapter, FixtureRetrievalAdapter):
            return _base(action, status="skipped", executor="none",
                         result_type="no_result", followup=True,
                         error="retrieval_adapter_unavailable")
        try:
            retrieved = retrieval_adapter.retrieve(action.get("task_id", ""))
        except RetrievalError as exc:
            return _base(action, status="failed", executor="fixture_retrieval",
                         result_type="no_result", followup=True, error=exc.code)
        except Exception:
            return _base(action, status="failed", executor="fixture_retrieval",
                         result_type="no_result", followup=True,
                         error="executor_failed")
        # Context stays transient; only its non-reversible evidence hash survives.
        return _base(action, status="completed", executor="fixture_retrieval",
                     result_type="retrieved_context",
                     confidence=round(retrieved["confidence"], 4), followup=True,
                     evidence_parts=(retrieved["context"],))

    if action_type == "checker_needed":
        checker_name = action.get("source_verifier")
        checker = APPROVED_CHECKERS.get(checker_name)
        if checker is None:
            return _base(action, status="skipped", executor="none",
                         result_type="no_result", followup=True,
                         error="checker_not_approved")
        output = runtime.get("output")
        if output is None:
            output = runtime.get("output_preview")
        if not isinstance(output, str) or not output:
            return _base(action, status="failed", executor=checker_name,
                         result_type="no_result", followup=True,
                         error="missing_checker_input")
        try:
            checked = checker(output, **_checker_kwargs(task))
        except Exception:
            return _base(action, status="failed", executor=checker_name,
                         result_type="no_result", followup=True,
                         error="executor_failed")
        verdict = checked["verdict"]
        return _base(action, status="completed", executor=checker_name,
                     result_type="checker_result",
                     confidence=checked["confidence"], verdict=verdict,
                     followup=verdict != VZ.VERDICT_PASS,
                     evidence_parts=(checked["evidence_hash"],))

    # review_needed/no_action are deliberately not automated by M18.
    return _base(action, status="skipped", executor="none",
                 result_type="no_result", followup=action_type == "review_needed",
                 error="action_not_executable")


def execute_all(actions, *, tasks=None, runtimes=None, enabled=False,
                retrieval_adapter=None):
    tasks = tasks or {}
    runtimes = runtimes or {}
    return [execute_action(
        a, task=tasks.get(a.get("task_id"), {}),
        runtime=runtimes.get(a.get("task_id"), {}), enabled=enabled,
        retrieval_adapter=retrieval_adapter) for a in actions]


def _dist(rows, key):
    counts = Counter((r.get(key) if r.get(key) is not None else "none") for r in rows)
    return dict(sorted(counts.items(), key=lambda kv: str(kv[0])))


def build_summary(actions, results, *, run_id="m18-safe-action-fixture",
                  checker_input_mode="trusted_fixture_or_full_private_output") -> dict:
    """Aggregate planned-vs-executed comparison with no raw text fields."""
    retrieval = [r for r in results if r.get("action_type") == "retrieval_needed"]
    checkers = [r for r in results if r.get("action_type") == "checker_needed"]
    completed_retrieval = sum(r["action_status"] == "completed" for r in retrieval)
    completed_checkers = sum(r["action_status"] == "completed" for r in checkers)
    summary = {
        "run_id": run_id,
        "n_actions": len(actions),
        "planned_action_type_distribution": _dist(actions, "action_type"),
        "before_status_distribution": _dist(actions, "status"),
        "after_action_status_distribution": _dist(results, "action_status"),
        "executor_distribution": _dist(results, "executor_name"),
        "result_type_distribution": _dist(results, "result_type"),
        "error_code_distribution": _dist(results, "error_code"),
        "current_info_retrieval": {
            "planned": len(retrieval),
            "completed": completed_retrieval,
            "executable_followup_rate": (
                round(completed_retrieval / len(retrieval), 4) if retrieval else None),
            "grounded_regeneration_still_required": sum(
                r["followup_needed"] for r in retrieval),
        },
        "verifier_only_checkers": {
            "planned": len(checkers),
            "completed": completed_checkers,
            "checker_input_mode": checker_input_mode,
            "correctness_interpretation": (
                "not_valid_from_legacy_truncated_previews"
                if checker_input_mode == "legacy_truncated_preview_replay"
                else "fixture_or_full_input_execution_path_only"),
            "execution_rate": (
                round(completed_checkers / len(checkers), 4) if checkers else None),
            "verdict_distribution": _dist(
                [r for r in checkers if r.get("checker_verdict") is not None],
                "checker_verdict"),
        },
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only: no prompt/output/retrieved-context text",
        "note": ("Fixture/read-only action execution only. Retrieval completion proves "
                 "an executable follow-up path, not answer correctness; grounded "
                 "regeneration and human calibration remain required."),
    }
    assert_no_text(summary)
    return summary


def assert_no_text(obj, where="root"):
    """Reject raw task/output/context-bearing fields recursively."""
    forbidden = set(RUN_REPORT.FORBIDDEN_KEYS) | {
        "context", "retrieved_context", "retrieved_text", "model_output"
    }
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in forbidden and isinstance(value, str):
                raise AssertionError(f"forbidden text value at {where}.{key}")
            assert_no_text(value, f"{where}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            assert_no_text(value, f"{where}[{i}]")


def _load_jsonl(path, key):
    if not path:
        return {}
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    return {row[key]: row for row in rows}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--actions", required=True)
    ap.add_argument("--tasks", default=None,
                    help="trusted task metadata JSONL (may remain private)")
    ap.add_argument("--records", default=None,
                    help="private runtime JSONL with output/output_preview")
    ap.add_argument("--retrieval-fixture", default=None,
                    help="trusted fixture JSON; raw context never enters output")
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", default=None)
    ap.add_argument("--execute", action="store_true",
                    help="explicitly enable approved execution (default disabled)")
    args = ap.parse_args(argv)

    actions = [json.loads(line) for line in open(args.actions, encoding="utf-8")
               if line.strip()]
    tasks = _load_jsonl(args.tasks, "prompt_id")
    runtimes = _load_jsonl(args.records, "prompt_id")
    adapter = (FixtureRetrievalAdapter.from_json(args.retrieval_fixture)
               if args.retrieval_fixture else None)
    results = execute_all(actions, tasks=tasks, runtimes=runtimes,
                          enabled=args.execute, retrieval_adapter=adapter)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for result in results:
            fh.write(json.dumps(result) + "\n")
    if args.summary:
        has_full = any(isinstance(r.get("output"), str) for r in runtimes.values())
        has_preview = any(isinstance(r.get("output_preview"), str)
                          for r in runtimes.values())
        input_mode = ("full_private_output" if has_full else
                      "legacy_truncated_preview_replay" if has_preview else
                      "trusted_fixture_or_full_private_output")
        summary = build_summary(actions, results, checker_input_mode=input_mode)
        dest = Path(args.summary); dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(summary, indent=1) + "\n")
    completed = sum(r["action_status"] == "completed" for r in results)
    print(f"[jlens] action executor: enabled={args.execute} actions={len(actions)} "
          f"completed={completed} -> {out} [fixture/read-only, candidate-only]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
