# steer.md — post-M16 calibration steering

M1 through M16 are complete. Do not redo the previous harness, review, verifier, larger-run, metadata-cleanup, or read-only action-routing work.

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

M16 result:

- Added metadata validator for numeric-looking exact-answer rows missing numeric metadata.
- Normalized generators so 7 reused exact rows moved exact -> numeric.
- Validator reports zero numeric metadata gaps on the cleaned M15 batch.
- Added action_record_v1 schema.
- Added read-only action_router.
- Current-info rows route to retrieval_needed action records.
- Checker-needed rows route only to approved deterministic checkers, otherwise skipped.
- Escalated rows route to review_needed.
- Clean rows route to no_action.
- Over M15: checker 160 / no_action 70 / review 19 / retrieval 12.
- Full test suite is green at 54 tests.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M17 reviewed calibration pass

M17 should convert the accumulated reviewed records into a real calibration pass. We now have multiple live runs, reviewed escalated subsets, action records, and improved verifiers. Before another bigger run, summarize what reviewed data actually says.

Suggested command:

/jlens-m17-reviewed-calibration-pass

## M17 objectives

1. Gather all public-safe reviewed aggregate summaries from M11 through M16.
2. Keep private reviewed logs local; do not commit raw prompt/output text.
3. Build a reviewed-record index or aggregate table using only safe fields.
4. Compute auto-vs-human agreement across reviewed comparable rows.
5. Report false-low-risk and false-high-risk where the reviewed data supports it.
6. Separate calibration by task/verifier type: exact, numeric, JSON, math, regex, retrieval-needed, explain-rubric, open-ended explain.
7. Include action-routing outcomes as planned-only counts, not executed success.
8. Identify which categories are mature enough for larger live runs.
9. Identify which categories still need human review, better metadata, or better verifiers.
10. Keep auto_outcome as candidate, not gold.
11. Keep production mode gated.

## Recommended calibration outputs

- reviewed_count by category
- comparable_count by category
- auto_vs_human_agreement by category where meaningful
- false-positive verifier findings already fixed
- remaining known gaps
- retrieval_needed action count
- checker_needed action count
- review_needed action count
- calibration_status per category: usable_shadow, needs_more_review, verifier_gap, metadata_gap, not_supported

## M17 deliverables

- src/reviewed_calibration_report.py or equivalent
- reports/outcomes/agents_a1_reviewed_calibration_summary.json
- docs/M17_REVIEWED_CALIBRATION.md
- tests for reviewed aggregate loading, no-text report, category grouping, and agreement calculations
- updated STATE.md and reports/FINDINGS.md

## M17 stop condition

- reviewed calibration summary exists
- summary contains no raw prompt/output text
- category-level reviewed counts are reported
- auto-vs-human agreement is computed only where comparable
- known verifier fixes and remaining gaps are listed
- production mode remains gated
- public artifacts pass commit-safe checks

## After M17

Choose one:

- M18A: larger 500-task live run with action routing enabled
- M18B: retrieval/checker execution for current-info tasks
- M18C: missing-label dataset converters
- M18D: broader model comparison against another local model

## Repository hygiene

Do not commit local detailed records, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
