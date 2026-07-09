#!/usr/bin/env python3
"""M10 autonomous shadow supervisor.

Runs a task queue against a local endpoint, applies cheap verifiers, and writes
an autonomous shadow record (schema/auto_outcome_v1.json) per task. The record
carries an auto_outcome CANDIDATE from the verifiers — NEVER gold, and it NEVER
writes the HUMAN outcome/review_meta fields (those stay null for a human).

Privacy: raw prompt/output text goes to a gitignored private log by default;
verifier evidence is hashed, never raw. Telemetry: a GGUF chat endpoint exposes
no router logits, so when no feature row exists the record sets
telemetry_missing=true and policy=null — features are never fabricated.

Advisory/shadow only. No arbitrary command execution (code verifier runs trusted
fixtures only). CPU-only, no installs.

CLI:
  python src/autonomous_shadow_supervisor.py \
      --config config/autonomous_supervisor_v0.json \
      --tasks data/prompts/autonomous_tasks_sample.jsonl \
      --out reports/shadow/private/autonomous_local.jsonl        # gitignored
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import verifiers as VZ  # noqa: E402
import local_shadow_wrapper as LSW  # noqa: E402

CORRECTNESS = {"exact_answer_match", "regex_or_schema_check", "json_object_check",
               "numeric_tolerant_check", "explain_rubric_check",
               "math_checker", "code_test_stub"}


def load_config(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_tasks(path, limit=0):
    tasks = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        t = json.loads(line)
        # accept prompt / text / prompt_preview as the prompt body
        t.setdefault("prompt", t.get("text") or t.get("prompt_preview") or "")
        t.setdefault("prompt_id", t.get("id") or t.get("prompt_id"))
        tasks.append(t)
        if limit and len(tasks) >= limit:
            break
    return tasks


def _run_verifiers(task, output, samples, cfg):
    """Run enabled + applicable adapters; return list of result dicts."""
    toggles = cfg.get("verifiers", {})
    results = []

    def enabled(name):
        return toggles.get(name, True)

    _numeric = task.get("numeric") or any(
        task.get(k) is not None for k in
        ("expected_value", "tolerance", "rel_tolerance", "expected_units", "accepted_values"))
    if enabled("numeric_tolerant_check") and _numeric:
        results.append(VZ.numeric_tolerant_check(
            output, expected_value=task.get("expected_value"),
            tolerance=task.get("tolerance"), rel_tolerance=task.get("rel_tolerance"),
            expected_units=task.get("expected_units"),
            accepted_values=task.get("accepted_values")))
    if enabled("explain_rubric_check") and task.get("required_facts"):
        results.append(VZ.explain_rubric_check(
            output, required_facts=task.get("required_facts")))
    # exact_answer_match is for PURE-STRING exact answers — not numeric tasks (M14)
    if enabled("exact_answer_match") and task.get("known_answer") is not None \
            and task.get("task_category") != "math" and not _numeric:
        results.append(VZ.exact_answer_match(output, known_answer=task["known_answer"]))
    if enabled("json_object_check") and (task.get("json_check")
                                         or task.get("json_required")):
        results.append(VZ.json_object_check(
            output, required_keys=task.get("json_required"),
            expected_type=task.get("json_type", "object")))
    # regex is for TRUE regex tasks only — not JSON tasks (M12)
    if enabled("regex_or_schema_check") and task.get("pattern") \
            and not task.get("json_check"):
        results.append(VZ.regex_or_schema_check(output, pattern=task["pattern"]))
    if enabled("math_checker") and (task.get("expression") is not None
                                    or task.get("task_category") == "math"):
        results.append(VZ.math_checker(output, known_answer=task.get("known_answer"),
                                       expression=task.get("expression")))
    if enabled("code_test_stub") and callable(task.get("fixture_test")):
        results.append(VZ.code_test_stub(output, fixture_test=task["fixture_test"]))
    if enabled("retrieval_required_heuristic"):
        results.append(VZ.retrieval_required_heuristic(
            output, prompt=task.get("prompt", ""),
            task_category=task.get("task_category")))
    if enabled("self_consistency") and len(samples) >= 2:
        results.append(VZ.self_consistency(samples))
    return results


def _build_auto_outcome(results, policy, cfg):
    esc = cfg.get("escalation", {})
    low = esc.get("low_confidence_below", 0.55)
    sc_min = esc.get("self_consistency_min_agreement", 0.67)
    high_impact = set(esc.get("high_impact_levels", ["high", "critical"]))
    contra_flag = esc.get("escalate_on_verifier_contradiction", True)

    decided = [r for r in results if r["verdict"] in (VZ.VERDICT_PASS, VZ.VERDICT_FAIL)]
    corr = [r for r in decided if r["name"] in CORRECTNESS]
    corr_fail = any(r["verdict"] == VZ.VERDICT_FAIL for r in corr)
    corr_pass = any(r["verdict"] == VZ.VERDICT_PASS for r in corr)
    contradiction = corr_fail and corr_pass

    auto_was_wrong = None
    if corr:
        auto_was_wrong = True if corr_fail else False

    retr = next((r for r in results if r["name"] == "retrieval_required_heuristic"), None)
    auto_needed_retrieval = None
    if retr is not None:
        auto_needed_retrieval = (retr["verdict"] == VZ.VERDICT_FAIL)

    auto_needed_checker = None
    if any(r["name"] in ("math_checker", "code_test_stub") for r in results):
        auto_needed_checker = True

    non_undecided = [r for r in results if r["verdict"] != VZ.VERDICT_UNDECIDED]
    verifier_confidence = (round(sum(r["confidence"] for r in non_undecided)
                                 / len(non_undecided), 4) if non_undecided else None)

    sc = next((r for r in results if r["name"] == "self_consistency"), None)
    sc_low = sc is not None and sc["confidence"] < sc_min

    escalate = bool(
        (verifier_confidence is not None and verifier_confidence < low)
        or (contradiction and contra_flag)
        or (policy and policy.get("level") in high_impact)
        or sc_low
        or auto_was_wrong is True
    )

    return {
        "auto_judged": len(decided) > 0,
        "auto_was_wrong": auto_was_wrong,
        "auto_needed_retrieval": auto_needed_retrieval,
        "auto_needed_checker": auto_needed_checker,
        "verifier_names": [r["name"] for r in results],
        "verifier_confidence": verifier_confidence,
        "verifier_evidence_hash": VZ.evidence_hash(*[r["evidence_hash"] for r in results]),
        "escalate_for_review": escalate,
        "auto_notes_redacted": None,
    }


def _null_human():
    return ({"user_agreed": None, "was_wrong": None, "needed_retrieval": None,
             "needed_checker": None, "notes": None},
            {"reviewer": None, "reviewed_at": None, "review_source": None,
             "review_confidence": None})


def run_task(task, model_fn, cfg, engine=None, feature_rows=None, n_samples=None,
             return_full_output=False):
    """Produce one auto_outcome_v1 record; optionally return transient full output.

    ``return_full_output`` is for M19's in-process checker handoff only. The
    returned text must never be written to a public artifact or persistent run
    record; the record itself continues to contain only the bounded preview.
    """
    pid = task["prompt_id"]
    prompt = task.get("prompt", "")
    if n_samples is None:
        n_samples = cfg.get("verifiers", {}).get("self_consistency_samples", 3)
    samples = [model_fn(prompt) for _ in range(max(1, n_samples))]
    output = samples[0]

    row = feature_rows.get(pid) if feature_rows else None
    telemetry_missing = row is None
    policy = engine.score(row) if (row is not None and engine is not None) else None

    results = _run_verifiers(task, output, samples, cfg)
    auto = _build_auto_outcome(results, policy, cfg)
    human_out, human_meta = _null_human()

    record = {
        "prompt_id": pid,
        "model": cfg.get("endpoint", {}).get("model"),
        "feature_source": None if row is None else "features",
        "prompt_preview": LSW._truncate(prompt),      # LOCAL-ONLY (gitignored log)
        "output_preview": LSW._truncate(output),      # LOCAL-ONLY (gitignored log)
        "policy": policy,
        "policy_note": None if not telemetry_missing else LSW.NO_TELEMETRY_NOTE,
        "mode": cfg.get("run", {}).get("mode", "dry-run"),
        "telemetry_missing": telemetry_missing,
        "task_category": task.get("task_category"),
        "outcome": human_out,       # NEVER set by the supervisor
        "review_meta": human_meta,  # NEVER set by the supervisor
        "auto_outcome": auto,
    }
    return (record, output) if return_full_output else record


def run(cfg, tasks, model_fn, out_path, engine=None, feature_rows=None, validator=None):
    records = []
    out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for t in tasks:
            rec = run_task(t, model_fn, cfg, engine, feature_rows)
            if validator is not None:
                errs = list(validator.iter_errors(rec))
                if errs:
                    raise ValueError(f"record {rec['prompt_id']} invalid: {errs[0].message}")
            fh.write(json.dumps(rec) + "\n")
            records.append(rec)
    return records


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default="config/autonomous_supervisor_v0.json")
    ap.add_argument("--tasks", default="data/prompts/autonomous_tasks_sample.jsonl")
    ap.add_argument("--out", default="reports/shadow/private/autonomous_local.jsonl")
    ap.add_argument("--mode", choices=["dry-run", "live"], default=None)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    if args.mode:
        cfg.setdefault("run", {})["mode"] = args.mode
    mode = cfg.get("run", {}).get("mode", "dry-run")
    tasks = load_tasks(args.tasks, args.limit)

    if mode == "live":
        ecfg = cfg["endpoint"]
        model_fn = lambda p: LSW.live_output(p, ecfg)  # noqa: E731
    else:
        model_fn = LSW.dry_run_output

    # Optional schema validation if jsonschema + the schema are present.
    validator = None
    try:
        from jsonschema import Draft7Validator
        S = json.loads(Path("schema/auto_outcome_v1.json").read_text())
        validator = Draft7Validator(S)
    except Exception:
        validator = None

    records = run(cfg, tasks, model_fn, args.out, validator=validator)
    esc = sum(1 for r in records if r["auto_outcome"]["escalate_for_review"])
    tel = sum(1 for r in records if r["telemetry_missing"])
    print(f"[jlens] autonomous run: {len(records)} tasks -> {args.out} "
          f"(escalated={esc}, telemetry_missing={tel}) [advisory/shadow, auto_outcome=candidate]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
