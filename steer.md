# steer.md — post-M14 larger-run steering

M1 through M14 are complete. Do not redo the earlier harness, review, JSON verifier, numeric verifier, explain-rubric, or M13 larger-run work.

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
- M13 larger Agents-A1 live run
- M14 numeric-tolerant verifier + explain-rubric coverage

M14 result:

- Added numeric_tolerant_check for approximate and unit-converted numeric answers.
- Kept exact_answer_match strict for pure string answers.
- Added explain_rubric_check for public fact-checkable explanation prompts.
- Routed numeric tasks to numeric_tolerant_check.
- Routed explain-rubric tasks to explain_rubric_check.
- Both new verifiers are wired into correctness scoring.
- The M13 speed-of-light false-positive now flips wrong to ok and de-escalates.
- Full test suite is green at 45 tests.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M15 larger Agents-A1 live run after verifier fixes

M15 should scale the live workload now that the two known verifier-strictness false positives are fixed: JSON/object output and approximate numeric answers.

Suggested command:

/jlens-m15-larger-agents-a1-live-run

## M15 objectives

1. Build or select a 250-500 task mixed workload.
2. Include the existing categories: math, exact answer, numeric answer, JSON/object, regex, current-info, and explain/rubric.
3. Add enough numeric and explain-rubric rows to test the new M14 verifier coverage.
4. Keep the run bounded, resumable, and failure-tolerant.
5. Run against the live agents-a1 endpoint on fred.
6. Store detailed records only in ignored local paths.
7. Produce a public-safe aggregate report with no task text.
8. Produce an escalation queue for local review.
9. Review a representative escalated subset and compute auto-vs-human agreement.
10. Compare M15 against M13 and M11/M12 baselines.
11. Report escalation rate, verifier distribution, auto_was_wrong count, retrieval-needed count, checker-needed count, failure count, and runtime.
12. Track whether JSON and numeric false positives stay fixed at scale.
13. Keep auto_outcome as candidate, not gold.
14. Keep production mode gated.

## M15 deliverables

- data/prompts/agents_a1_m15_batch.jsonl or documented local batch path
- config/agents_a1_m15_run.json or updated run config
- reports/outcomes/agents_a1_m15_summary_sample.json
- reports/outcomes/agents_a1_m15_vs_baseline.json
- public-safe reviewed subset summary if review is performed
- docs/M15_LARGER_AGENTS_A1_RUN.md
- tests for batch validation, aggregate report, resume behavior, verifier distribution, and baseline comparison
- updated STATE.md and reports/FINDINGS.md

## M15 stop condition

- 250-500 task batch exists
- live or dry-run path works with the new batch
- aggregate summary contains no task text
- escalation queue is generated
- representative escalated subset has a review path
- comparison against M13 and M11/M12 baselines exists
- JSON false-positive remains fixed
- numeric false-positive remains fixed
- public artifacts pass commit-safe checks
- production mode remains gated

## After M15

Choose the next path based on results:

- M16A: calibration from reviewed Agents-A1 records
- M16B: integrate retrieval/checker actions for current-info tasks
- M16C: add missing-label dataset converters
- M16D: broader model comparison against another local model

## Repository hygiene

Do not commit local detailed records, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
