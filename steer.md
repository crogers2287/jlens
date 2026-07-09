# steer.md — post-M18 live full-output action-run steering

M1 through M18 are complete. Do not redo the previous harness, review, verifier, metadata-cleanup, action-routing, reviewed-calibration, or safe-action-executor work.

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
- M18 safe action execution

M18 result:

- Added action_result_v1 schema.
- Added explicit opt-in action executor.
- Execution is disabled by default.
- Retrieval is limited to fixture/public-fixture paths.
- Checkers are limited to approved deterministic allowlist: math_checker, json_object_check, numeric_tolerant_check.
- No shell, subprocess, dynamic import, arbitrary callable, or model-command surface was added.
- Replayed the M15/M16 action distribution: 261 planned actions.
- Completed 172 approved actions: 12 retrieval fixture actions and 160 checker actions.
- Skipped 89 intentionally: 19 review-needed and 70 no-action.
- Current-info retrieval executable path reached 12/12, but grounded regeneration is still required.
- Historical checker replay is not a model-quality measurement because M15 only retained truncated output previews.
- Full test suite is green at 64 tests.

Important M18 limitation:

- Checker replay from legacy M15 logs used truncated output_preview values.
- The 70 pass / 90 fail checker split is explicitly invalid for correctness measurement.
- Future live runs must pass full model output transiently into the executor before truncating/private logging.
- Do not relabel preview-replay failures as model failures.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M19 live run with full-output transient action execution

M19 should run a new larger live workload with safe action execution integrated into the live path. The key change from M18 is that checker actions must receive the full model output transiently during the run, before any truncation/redaction. Full output may be used locally for execution, but must not be committed.

Suggested command:

/jlens-m19-live-full-output-action-run

## M19 objectives

1. Build or select a 500-task mixed workload using the cleaned metadata and M18 action execution path.
2. Run against the live agents-a1 endpoint on fred.
3. Pass full model output transiently to approved checkers before truncation.
4. Keep private detailed records local and gitignored.
5. Store only preview/redacted output in persistent logs if needed.
6. Execute safe action paths during the live run with explicit opt-in config.
7. Execute retrieval only through fixture/public-fixture adapters unless a later milestone adds a real public retrieval adapter.
8. Execute checkers only through the existing deterministic allowlist.
9. Produce action_result records for executed/skipped actions.
10. Produce a public-safe aggregate summary with no raw prompt/output/retrieved-context text.
11. Compare M19 to M15 and M18: completion rate, escalation rate, action execution rate, checker verdicts from full-output execution, and retrieval followup counts.
12. Report current-info separately: retrieval completed is not answer correctness; grounded regeneration remains separate unless implemented.
13. Review a representative escalated/action-result subset and update calibration summary if useful.
14. Keep auto_outcome and action_result as candidates, not gold.
15. Keep production mode gated.

## M19 deliverables

- data/prompts/agents_a1_m19_batch.jsonl or documented local batch path
- config/agents_a1_m19_run.json or updated run config
- live runner support for transient full-output checker execution
- reports/outcomes/agents_a1_m19_summary_sample.json
- reports/outcomes/agents_a1_m19_action_execution_summary.json
- reports/outcomes/agents_a1_m19_vs_baseline.json
- docs/M19_LIVE_FULL_OUTPUT_ACTION_RUN.md
- tests for transient full-output checker path, no raw text persistence, safe action execution, aggregate no-text report, resume behavior, and baseline comparison
- updated STATE.md and reports/FINDINGS.md

## M19 stop condition

- 500-task live or dry-run path exists
- full model output reaches approved checkers transiently before truncation
- full output is not committed or stored in public artifacts
- checker verdicts are now valid for full-output action execution, not legacy preview replay
- retrieval actions execute only through allowed fixture/public-fixture paths
- action_result records validate and remain candidate-only
- aggregate reports contain no raw task/output/retrieved-context text
- public artifacts pass commit-safe checks
- production mode remains gated

## After M19

Choose one:

- M20A: grounded regeneration for current-info tasks after retrieval
- M20B: broader model comparison against another local model using the same M19 harness
- M20C: missing-label dataset converters
- M20D: improve open-ended explain verifier coverage with rubric/reference strategy

## Repository hygiene

Do not commit local detailed records, full model outputs, retrieved raw text, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
