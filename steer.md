# steer.md — post-M13 verifier-coverage steering

M1 through M13 are complete. Do not redo the earlier harness, review, verifier-hardening, or larger-run work.

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
- M13 larger Agents-A1 live run

M13 result:

- Built deterministic 110-task mixed batch across 6 categories.
- Ran live against agents-a1 on fred.
- Completed 110/110 with 0 failures.
- Escalation rate improved from 0.28 in M11 to 0.164 in M13.
- JSON verifier fix held at scale with 0 JSON escalations.
- Public aggregate, reviewed-subset, and baseline comparison were committed.
- Private detailed records stayed local.
- Full test suite is green at 40 tests.

New M13 finding:

- The one auto-wrong in the reviewed subset was another verifier-strictness issue.
- exact_answer_match rejected an approximate or unit-converted numeric answer.
- The model was right about the speed of light, but the verifier was too literal.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M14 numeric-tolerant verifier + explain coverage

M14 should improve verifier coverage before running larger batches again. The priority is to fix the exact-answer numeric strictness found in M13 and add better handling for open-ended explain tasks.

Suggested command:

/jlens-m14-verifier-coverage-loop

## M14 objectives

1. Add a numeric-tolerant answer verifier for approximate and unit-converted numeric answers.
2. Keep strict exact-answer matching available for pure string answers.
3. Route numeric exact-answer tasks to the numeric verifier when metadata indicates numeric/units.
4. Add task metadata for numeric tolerance, expected units, aliases, or acceptable ranges.
5. Add tests for speed-of-light style answers, unit conversions, approximate values, and wrong numeric values.
6. Add an explain-task verifier strategy that can score public closed-ground-truth explanation prompts without pretending open-ended subjective answers are gold.
7. For explain tasks, prefer rubric/keyword/fact checklist verifiers with explicit uncertainty and escalation when coverage is weak.
8. Re-score or replay the M13 representative finding and show the numeric verifier flips the false-positive to ok.
9. Produce a before/after aggregate showing change in auto_was_wrong and escalation counts.
10. Keep auto_outcome as candidate, not gold.
11. Keep production mode gated.

## Recommended verifier behavior

Numeric verifier:

- extract one or more numeric values from model output
- normalize simple units where metadata provides expected units
- compare against expected value using absolute or relative tolerance
- support accepted aliases when the answer is numeric plus unit text
- pass when value is within tolerance
- fail when value is clearly outside tolerance
- escalate when no reliable numeric value can be extracted

Explain verifier:

- use only public prompts with objective fact checklists
- count required facts present or absent
- never claim subjective explain answers are gold without a rubric
- escalate when the rubric is incomplete or confidence is low

## M14 deliverables

- updated src/verifiers.py
- updated verifier routing for numeric tasks
- optional schema or metadata docs for numeric tolerance fields
- updated or new public batch rows that exercise numeric tolerance
- reports/outcomes/agents_a1_numeric_beforeafter_sample.json
- docs/M14_VERIFIER_COVERAGE.md
- tests for numeric verifier, routing, explain rubric behavior, before/after comparison, and aggregate no-text reports
- updated STATE.md and reports/FINDINGS.md

## M14 stop condition

- numeric verifier handles the M13 speed-of-light false-positive pattern
- strict exact matching still works for pure string answers
- numeric routing is tested
- explain verifier strategy exists without overclaiming
- before/after report shows whether verifier quality improved
- public artifacts contain no task text where prohibited
- private detailed records stay local
- production mode remains gated

## After M14

Choose one:

- M15A: larger Agents-A1 live run, 250-500 tasks
- M15B: calibration from reviewed Agents-A1 records
- M15C: add missing-label dataset converters
- M15D: integrate retrieval/checker actions for current-info tasks

## Repository hygiene

Do not commit local detailed records, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
