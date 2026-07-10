# steer.md — post-M25 telemetry branch decision gate

M1 through M25 are complete. Do not redo the practical supervisor track, HF
backend, same-run training, frozen holdout, or identical-input falsification.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Autosteer status

The explicit loop completed three milestones in this run:

1. M23 within-model telemetry/outcome validation
2. M24 frozen holdout evaluation
3. M25 identical-input router falsification

The three-milestone loop limit is reached. Stop after committing this steer even
if `CODEX_AUTOSTEER_LOOP=true` remains set. A new operator instruction is required
to choose the next research problem.

## Current evidence

### M23 — same-run association

- 32 balanced Qwen tasks, same decode for telemetry and verifier/action outcome.
- Router entropy/concentration separated checker/retrieval/review groups
  descriptively; task category/template remained an explicit confound.
- One checker fail was insufficient for error-prediction analysis.

### M24 — frozen unseen-ID holdout

- Corrected pre-run to 40 valid, M23-disjoint tasks; correction preserved in git.
- M23-frozen router-only classifier reached .700 accuracy [.550,.850], balanced
  accuracy .693, macro-F1 .700 versus majority .275.
- Full features reached .600; logits-only collapsed to .225.
- Unseen IDs still shared action-specific prompt templates and verifier rules.

### M25 — identical-input falsification

- 16 pairs / 32 tasks; prompts byte-identical within each pair, metadata/action
  labels different.
- Actual actions matched intended balanced classes 32/32.
- Outputs identical 16/16.
- Frozen predictions identical 16/16.
- Router entropy and expert-concentration within-pair mean/max differences: 0.
- Frozen accuracy/balanced accuracy .500, macro-F1 .413; no-action recall 0.
- Conclusion: telemetry alone cannot recover metadata-only action requirements.
  M24's .70 performance was substantially prompt-template/category association.

Across M23–M25:

- no model weights/caches/paths/raw text/tensors were committed
- all detailed records remain ignored/private
- candidate-only labels and production gates remain
- agents-a1 was restored after every GPU window
- full repository suite is green at 105 tests

## Research conclusion

Do not fit or deploy a telemetry-only action-routing policy from this branch.

Router telemetry may still be useful, but the next problem must be stated honestly:

- workflow applicability depends on trusted task metadata that may be absent from
  model inputs, or
- model error prediction requires objective within-category pass/fail outcomes,
  not action labels driven by verifier applicability.

Adding metadata after M25 is not a fix to the telemetry-only classifier; it defines
a different supervised routing system.

## Required operator decision before M26

Choose exactly one direction:

### A. Metadata + telemetry action routing

Build a conventional supervised router that explicitly consumes trusted task
metadata plus telemetry. Evaluate metadata-only, telemetry-only, and combined
frozen ablations on held-out prompt families. This tests incremental telemetry
value, not hidden metadata discovery.

### B. Objective error prediction (recommended research continuation)

Collect balanced pass/fail outcomes within one task category using deterministic
checkers, while holding prompt family/action applicability constant. Test whether
router telemetry predicts Qwen correctness. Predeclare difficulty bands and a
train/holdout split; do not select failures after generation.

### C. End telemetry-policy work

Return to practical quality: improve current-info fixtures/retrieval grounding,
open-explain rubric coverage, reviewed calibration, or broader model comparison.

Do not begin M26 until the operator selects A, B, or C. Any new real model run must
remain under the existing approval or stop for a new model/hardware/resource gate.

## Repository hygiene

Do not commit private prompts/outputs, per-task predictions, token IDs/text, raw
tensors, paths, weights, caches, or detailed records. Public reports remain
aggregate. No candidate becomes gold and production remains gated until explicit
audited unlock criteria are defined.
