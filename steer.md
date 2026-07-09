# steer.md — post-M19 grounded regeneration steering

M1 through M19 are complete. Do not redo the previous harness, review, verifier, metadata-cleanup, action-routing, reviewed-calibration, safe-action-executor, or full-output action-run work.

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
- M19 500-task live run with transient full-output action execution

M19 result:

- Built deterministic metadata-clean 500-task batch.
- Ran live against agents-a1 on fred.
- Completed 500/500 with 0 failures.
- Escalation rate improved again: M11/M12 0.28 -> M13 0.164 -> M15 0.0728 -> M19 0.054.
- Full model output reached approved checkers transiently before truncation.
- Full output was not persisted in public artifacts.
- 383/500 actions completed through approved paths.
- Checker actions completed: 360 full-output math checks.
- Retrieval actions completed: 23 fixture retrievals.
- 117 actions were intentionally skipped: review-needed or no-action.
- Checker results are now valid for execution input: 356 pass / 4 fail.
- The 4 fail results are real arithmetic miss candidates requiring review.
- Current-info fixture retrieval reached 20/20.
- 3 retrieval-needed rows were non-current heuristic false positives: 2 explain weather rows and 1 numeric sale-price row.
- All current-info retrieval completions still require grounded regeneration.
- Production remains gated.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M20 grounded regeneration after retrieval

M20 should close the loop on current-info tasks. M19 proved retrieval actions can execute safely, but retrieval completion is not answer correctness. The next step is to use retrieved fixture/public-fixture context to regenerate or revise answers in a controlled way, then verify or review those grounded outputs.

Suggested command:

/jlens-m20-grounded-regeneration-loop

## M20 objectives

1. Add a grounded regeneration path for retrieval_needed tasks after retrieval completes.
2. Keep regeneration disabled by default unless an explicit config or flag enables it.
3. Restrict retrieved context to fixture/public-fixture sources unless a later milestone adds a real retrieval adapter.
4. Pass retrieved context to the model only in the local live path.
5. Do not commit raw retrieved context, raw prompts, or full regenerated outputs.
6. Produce grounded_result records or equivalent aggregate-safe records.
7. Track original answer vs grounded regenerated answer as candidate-only data.
8. Run the current-info subset from M19 through grounded regeneration.
9. Report how many current-info tasks produce a grounded answer.
10. Report how many grounded answers can be checked deterministically, if any.
11. Separate retrieval heuristic false positives from true current-info rows.
12. Review the 4 M19 arithmetic miss candidates and the 3 retrieval heuristic false positives.
13. Update the public calibration summary with reviewed results if useful.
14. Keep auto_outcome, action_result, and grounded_result as candidates, not gold.
15. Keep production mode gated.

## Recommended grounded_result record

Each grounded result should be aggregate-safe:

- task_id
- source_action_id or action_evidence_hash
- grounded_status: completed, skipped, failed
- context_source_kind: fixture, public_fixture, none
- regeneration_model
- result_confidence
- verifier_names
- verifier_verdicts
- evidence_hash only, no raw context or output
- followup_needed
- candidate_only: true

## M20 deliverables

- schema/grounded_result_v1.json if useful
- src/grounded_regenerator.py or extension to the live runner
- public-safe current-info grounded regeneration summary
- public-safe review summary for 4 arithmetic miss candidates and 3 retrieval heuristic false positives
- reports/outcomes/agents_a1_m20_grounded_summary.json
- docs/M20_GROUNDED_REGENERATION.md
- tests for default-off behavior, fixture context use, no raw text persistence, verifier/review routing, aggregate no-text report, and before/after comparison
- updated STATE.md and reports/FINDINGS.md

## M20 stop condition

- retrieval-completed current-info tasks can enter a safe grounded regeneration path
- grounded_result records validate and contain no raw context/output text
- public aggregate distinguishes retrieval completion from grounded answer quality
- 4 arithmetic miss candidates have a review path or reviewed summary
- 3 retrieval heuristic false positives have a review path or heuristic refinement note
- public artifacts pass commit-safe checks
- production mode remains gated

## After M20

Choose one:

- M21A: larger live run with grounded regeneration enabled
- M21B: HF/safetensors telemetry backend for internal logits/router-style research
- M21C: broader model comparison against another local model using the M19/M20 harness
- M21D: improve open-ended explain verifier coverage with rubric/reference strategy
- M21E: missing-label dataset converters

## Repository hygiene

Do not commit local detailed records, full model outputs, retrieved raw text, grounded raw outputs, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
