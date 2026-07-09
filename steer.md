# steer.md — post-M12 larger-run steering

M1 through M12 are complete. Do not redo the earlier harness, review, or verifier-hardening work.

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
- M12 verifier hardening and reviewed escalation calibration

M12 result:

- json_object_check was added and routed for JSON/object tasks.
- Regex remains available for true regex tasks.
- The M11 JSON false-positive was fixed.
- The 7 escalated live rows were reviewed against public benchmark ground truth.
- First auto-vs-human agreement was computed on the comparable row.
- Before/after improved from escalation 7 to 6 and auto_was_wrong 1 to 0.
- Full test suite is green at 36 tests.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M13 larger Agents-A1 live run

M13 should scale from the 25-task live run to a larger bounded live run now that the JSON verifier issue is fixed.

Suggested command:

/jlens-m13-larger-agents-a1-live-run

## M13 objectives

1. Build or select a 100-250 task mixed workload.
2. Include task categories that verifiers can score: math, exact answer, JSON/object, regex, retrieval-needed, and explain/open-ended.
3. Keep the run bounded and resumable.
4. Run against the live agents-a1 endpoint on fred.
5. Record local detailed run files only in the ignored local run directory.
6. Produce a public-safe aggregate report with no task text.
7. Produce an escalation queue for review.
8. Review a representative escalated subset, not necessarily every row if the run is large.
9. Report auto-vs-human agreement where review exists.
10. Report escalation rate, verifier distribution, auto_was_wrong count, retrieval-needed count, checker-needed count, failures, and runtime.
11. Compare M13 results to the M11/M12 25-task baseline.
12. Keep auto_outcome as candidate, not gold.
13. Keep production mode gated.

## M13 deliverables

- data/prompts/agents_a1_m13_batch.jsonl or documented local batch path
- config/agents_a1_m13_run.json or update to existing run config
- reports/outcomes/agents_a1_m13_summary_sample.json
- public-safe reviewed subset summary if review is performed
- docs/M13_LARGER_AGENTS_A1_RUN.md
- tests for batch validation, aggregate report, resume behavior, and comparison report
- updated STATE.md and reports/FINDINGS.md

## M13 stop condition

- larger bounded batch exists
- live or dry-run path works with the new batch
- aggregate summary contains no task text
- escalation queue is generated
- at least a small escalated subset has a review path
- before/after comparison against M11/M12 exists
- public artifacts pass commit-safe checks
- production mode remains gated

## After M13

Choose the next path based on results:

- M14A: calibration from reviewed Agents-A1 records
- M14B: broaden benchmark scale and task diversity
- M14C: add missing-label dataset converters
- M14D: improve verifier coverage for open-ended explain tasks

## Repository hygiene

Do not commit local detailed records, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
