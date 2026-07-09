# steer.md — post-M17 execution steering

M1 through M17 are complete. Do not redo the previous harness, review, verifier, metadata-cleanup, action-routing, or reviewed-calibration work.

## Current state

Completed milestones:

- M1 RouterGuard feasibility
- M2 DecodeGuard telemetry and feature discovery
- M3 risk-labeling scaffold and training gate
- M4 benchmark-gold ingestion foundation
- M5 end-to-end benchmark telemetry smoke prototype
- M6 PolicyEngine v0 advisory runtime
- M7 local wrapper and runtime records
- M8 review and calibration loop
- M9 local workflow and aggregate reporting
- M10 autonomous supervisor
- M11 first live Agents-A1 run
- M12 JSON verifier hardening and reviewed escalation calibration
- M13 110-task live Agents-A1 run
- M14 numeric-tolerant verifier and explain-rubric coverage
- M15 261-task live Agents-A1 run after verifier fixes
- M16 metadata cleanup and read-only action routing
- M17 reviewed calibration pass

M17 result:

- Consolidated reviewed subsets from M11-M16.
- Scanned 44 reviewed-log records.
- Found 19 human-reviewed records.
- Found only 3 objectively comparable records.
- The comparable disagreements were the already-found verifier false-positives.
- Those false-positives are already fixed: JSON in M12, numeric in M14/M16.
- Category status:
  - usable_shadow: exact, numeric, json, math, regex
  - needs_more_review: explain-rubric
  - verifier_gap: open-ended explain
- Action-routing counts are planned-only: retrieval 12 / checker 160 / review 19 / no_action 70.
- Full test suite is green at 58 tests after the post-completion CLI bugfix.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M18 execute retrieval/checker actions safely

M18 should move from planned action records to controlled execution for safe cases. The biggest near-term value is current-info and checker-needed tasks: the system already knows what should be retrieved or checked, but M16 only planned actions. M18 should execute approved actions in a bounded, auditable way and then re-score the result.

Suggested command:

/jlens-m18-safe-action-execution-loop

## M18 objectives

1. Add an action executor for read-only retrieval_needed actions.
2. Add an action executor for approved deterministic checker_needed actions.
3. Keep execution disabled by default unless an explicit flag/config enables it.
4. Restrict retrieval to safe/public or fixture sources first.
5. Restrict checkers to approved deterministic functions or fixture commands only.
6. Never execute arbitrary shell commands from model output.
7. Produce action_result records linked to action_record_v1.
8. Re-score or summarize tasks after action execution.
9. Compare planned-only vs executed-action outcomes.
10. Report current-info improvement separately from verifier-only categories.
11. Keep private raw task/output content local.
12. Keep auto_outcome and action_result as candidates, not gold.
13. Keep production mode gated.

## Recommended action_result record

Each action result should be aggregate-safe:

- task_id
- action_type
- action_status: completed, skipped, failed
- executor_name
- result_type: retrieved_context, checker_result, no_result
- result_confidence
- evidence_hash only, no raw retrieved text
- followup_needed
- error_code if failed

## M18 deliverables

- schema/action_result_v1.json if useful
- src/action_executor.py or equivalent
- safe retrieval fixture/source adapter
- deterministic checker execution adapter
- reports/outcomes/agents_a1_m18_action_execution_summary.json
- docs/M18_SAFE_ACTION_EXECUTION.md
- tests for disabled-by-default behavior, retrieval execution, checker execution, no arbitrary command execution, aggregate no-text report, and before/after comparison
- updated STATE.md and reports/FINDINGS.md

## M18 stop condition

- retrieval_needed actions can execute in a safe fixture/public mode
- checker_needed actions can execute only through approved deterministic paths
- action_result records validate and contain no raw text
- before/after report shows what changed after action execution
- current-info tasks are no longer merely flagged; they have executable follow-up path
- public artifacts pass commit-safe checks
- production mode remains gated

## After M18

Choose one:

- M19A: larger 500-task live run with safe action execution enabled
- M19B: broader model comparison against another local model
- M19C: missing-label dataset converters
- M19D: improve open-ended explain verifier coverage with rubric/reference strategy

## Repository hygiene

Do not commit local detailed records, retrieved raw text, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
