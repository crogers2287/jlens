# steer.md — post-M11 steering

M1 through M11 are complete.

The first live Agents-A1 run on fred completed successfully. The previous harness work is done and should not be repeated.

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

Live run summary:

- model: agents-a1
- host: fred
- endpoint: llama-swap on port 9069
- run_id: 88e140ea5d129bc3
- tasks: 25
- completed: 25
- failed: 0
- telemetry_missing: 25
- escalated: 7
- escalation_rate: 0.28
- public aggregate: reports/outcomes/agents_a1_run_summary_live.json

The GGUF endpoint did not expose internal telemetry. Keep representing that as telemetry_missing=true and policy=null. Do not invent telemetry.

## Main lesson

The one auto-wrong candidate from the live run appears to be a verifier issue, not a model issue.

The JSON-style task returned a valid object, but the checker was too strict. This is exactly why auto_outcome is only a candidate and why escalated records need review.

## Next milestone: M12 verifier hardening and reviewed escalation calibration

M12 should improve checker quality and review the escalated live-run records before scaling up.

Suggested command:

/jlens-m12-verifier-review-calibration-loop

## M12 objectives

1. Review the 7 escalated records from the M11 live run.
2. Produce a safe aggregate reviewed summary.
3. Compute the first auto-vs-human agreement from reviewed live records.
4. Add a JSON-aware verifier for JSON/object-output tasks.
5. Keep the regex verifier for regex tasks only.
6. Add tests showing valid JSON with harmless trailing whitespace passes.
7. Add tests showing invalid JSON fails or escalates.
8. Re-run the 25-task batch or replay the public fixture after the verifier change.
9. Compare before and after escalation counts.
10. Keep auto_outcome as candidate, not gold.
11. Keep production mode gated.

## Recommended checker behavior

For JSON/object tasks:

- parse with json.loads
- allow harmless whitespace around the JSON
- optionally check expected type or required keys
- pass when parsing and requirements match
- fail or escalate when parsing or requirements fail

For regex tasks:

- use regex only when the task is truly regex-based
- avoid full-output anchors unless that is specifically intended

## M12 deliverables

- updated src/verifiers.py
- reviewed aggregate summary for M11 escalations
- docs/M12_VERIFIER_REVIEW_CALIBRATION.md
- tests for JSON verifier, regex behavior, reviewed aggregate, and before/after comparison
- updated STATE.md and reports/FINDINGS.md

## M12 stop condition

- escalated live rows have a review path
- reviewed aggregate summary exists
- auto-vs-human agreement is computed when reviews exist
- JSON verifier handles the M11 checker issue
- before/after report shows whether checker quality improved
- local detailed records stay local
- public artifacts pass commit-safe checks
- production mode remains gated

## After M12

Choose one:

- M13A larger Agents-A1 live run, 100-250 tasks
- M13B calibration from reviewed Agents-A1 workload records
- M13C add missing-label dataset converters

## Repository hygiene

Do not commit raw captures, local detailed records, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
