# steer.md — post-M15 action-routing steering

M1 through M15 are complete. Do not redo the previous harness, review, verifier, or larger-run work.

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

M15 result:

- Built a deterministic 261-task batch across 8 category types.
- Ran live against agents-a1 on fred.
- Completed 261/261 with 0 failures.
- Escalation rate improved across live runs: 0.28 -> 0.164 -> 0.073.
- JSON false-positive stayed fixed at scale.
- Numeric-tagged false-positive stayed fixed at scale.
- Full test suite is green at 49 tests.

M15 findings:

- The remaining auto-wrong is a task-metadata gap, not a verifier regression.
- A reused speed-of-light exact-answer row lacked numeric metadata and routed to strict exact matching.
- Rubric synonym handling is still basic; synonym mismatch should escalate, not mark wrong.
- Current-info tasks are flagged as retrieval-needed, but the system does not yet run a retrieval/check action.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M16 action routing + metadata cleanup

M16 should turn the current verifier signals into safe next actions. The system already knows when a task needs retrieval or checking; now it needs a controlled action layer that can run approved retrieval/checker steps and re-score the result. Also clean up task metadata so numeric rows route correctly.

Suggested command:

/jlens-m16-action-routing-and-metadata-loop

## M16 objectives

1. Fix public task metadata so numeric exact-answer rows carry numeric metadata.
2. Add validation that detects numeric-looking exact-answer rows missing numeric metadata.
3. Add an action-routing layer for auto_needed_retrieval and auto_needed_checker.
4. Keep actions read-only and fixture-safe by default.
5. For current-info tasks, create a retrieval-needed action record rather than pretending the base model answer is enough.
6. For checker-needed tasks, route to approved deterministic checkers only.
7. Re-run or replay the M15 batch after metadata cleanup and report before/after.
8. Report how many tasks moved from strict exact-answer to numeric_tolerant_check.
9. Report how many current-info tasks were routed to retrieval action records.
10. Keep auto_outcome as candidate, not gold.
11. Keep production mode gated.

## Recommended action record

Each action record should be aggregate-safe and local-safe:

- task_id
- action_type: retrieval_needed, checker_needed, no_action, review_needed
- reason_code
- source_verifier
- confidence
- status: planned, skipped, completed, failed
- evidence_hash only, no raw task text

## M16 deliverables

- metadata validator for task rows
- action routing module or extension to the supervisor
- action record schema if useful
- updated public batch rows or generator metadata fixes
- public-safe before/after report for M15 metadata cleanup
- public-safe action-routing summary
- docs/M16_ACTION_ROUTING.md
- tests for metadata validation, action routing, aggregate no-text reports, and replay/before-after comparison
- updated STATE.md and reports/FINDINGS.md

## M16 stop condition

- numeric metadata gap is detected and fixed in public batch generation
- current-info tasks produce retrieval-needed action records
- checker-needed tasks route only to approved deterministic checkers
- before/after report shows metadata cleanup impact
- action summaries contain no task text
- public artifacts pass commit-safe checks
- production mode remains gated

## After M16

Choose one:

- M17A: calibration from reviewed Agents-A1 records
- M17B: larger 500-task live run with action routing enabled
- M17C: missing-label dataset converters
- M17D: broader model comparison against another local model

## Repository hygiene

Do not commit local detailed records, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
