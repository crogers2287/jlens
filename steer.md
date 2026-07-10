# steer.md — post-M24 identical-input router falsification

M1 through M24 are complete. Do not redo prior supervisor, telemetry, same-run,
or frozen-holdout work. `CODEX_AUTOSTEER.md` remains the operating contract.

## Autosteer mode

Default mode completes one milestone and stops after separate implementation and
steer commits. Loop mode requires explicit operator instruction or
`CODEX_AUTOSTEER_LOOP=true` and remains bounded by the contract's three-milestone/
four-hour maximum.

The existing approval covers the same local Qwen MoE checkpoint, Thor storage,
local-only dual-3090 BF16 execution, hidden capture disabled, and temporary
llama-swap unload/restore. Stop for any new model, dependency, live retrieval,
hardware plan, or material resource change.

## Current state

- M1–M23: practical track plus real/same-run telemetry through M23 training
- M24: frozen M23-trained telemetry holdout

M24 result:

- Initial invalid 48-ID manifest is preserved; source validation transparently
  corrected it to 40 valid/disjoint IDs before any capture.
- Frozen classifiers used only M23 scaling/centroids; no holdout tuning.
- Real M24 completed 40/40 with logits/router telemetry available.
- Actual actions: checker10/retrieval10/review11/no-action9.
- Router-only: accuracy .700, bootstrap [.550,.850], balanced accuracy .693,
  macro-F1 .700 versus majority baseline .275.
- Full features: .600 [.450,.750]; logits-only: .225 [.100,.350].
- Router-only errors concentrate in no-action→review and review→retrieval.
- Unseen IDs still share action-specific prompt templates and verifier rules with
  M23. The result may reflect category/template association, not intrinsic need.
- Checker outcomes were 1 pass/9 fail, all EOS-complete; no error model was fit.
- 100/100 tests green; agents-a1 restored; production gated.

## Next milestone: M25 identical-input metadata counterfactual

M25 is a falsification test for the frozen M23 router-only classifier. Construct
16 deterministic pairs where both members receive exactly the same prompt text and
therefore should produce the same greedy Qwen output/router telemetry, while trusted
task metadata changes verifier applicability and the intended action label.

### Predeclared pair design

Use exactly 32 synthetic public-safe task IDs in an ID/pair/group-only manifest:

1. Eight `checker_vs_no_action` pairs:
   - identical simple arithmetic prompt per pair
   - member A: `task_category=math`, safe expression + known answer
   - member B: `task_category=exact_answer`, same known answer, no expression
   - expected actions: checker_needed vs no_action when the trivial exact answer
     passes; any drift is reported, never repaired after run
2. Eight `retrieval_vs_review` pairs:
   - identical neutral topic prompt per pair, with no temporal wording
   - member A: `task_category=current_info`
   - member B: `task_category=explain`, no rubric
   - expected actions: retrieval_needed vs review_needed

Prompts are deterministic synthetic fixtures written only to an ignored private
task file. The public manifest contains IDs, pair IDs/types, and intended classes,
not prompt text.

### Frozen model and metrics

- Apply the existing M23-trained router-only nearest-centroid classifier without
  refitting, scaling updates, threshold changes, or feature additions.
- Features remain only mean router entropy and mean expert concentration.
- Report aggregate:
  - actual class distribution
  - frozen accuracy/balanced accuracy/macro-F1/confusion/per-class metrics
  - majority baseline and fixed 2,000-bootstrap accuracy interval
  - pairs with discordant actual labels
  - pairs with identical captured output
  - pairs with identical predicted labels
  - mean/max within-pair absolute difference for both router features
  - within-pair prediction divergence rate
- Do not publish per-pair predictions, IDs, hashes, text, or tensors.

### M25 objectives

1. Commit the public-safe 16-pair manifest before real capture.
2. Generate private tasks deterministically and verify exact prompt equality within
   every pair before model load.
3. Use the same local-only chat-template/router-only 64-token capture plan.
4. Derive same-run Qwen verifier/action records and validate existing schemas.
5. Verify output equality and telemetry equality within pairs; report deviations
   honestly without rerun or prompt edits.
6. Apply only the already-frozen M23 router classifier.
7. Restore agents-a1 after the capture window.
8. Keep all detailed data private, candidate-only, and production gated.

### M25 interpretation gate

- If pair telemetry/predictions are identical while actual actions differ, conclude
  telemetry alone cannot infer metadata-only action requirements; the M24 result is
  at least partly template/category association.
- If identical prompts produce material telemetry divergence, investigate capture
  determinism before interpreting classifier behavior.
- Do not respond by adding task metadata to a telemetry-only policy in this
  milestone; that would answer a different question.

### M25 deliverables

- `data/prompts/m25_pair_manifest.json` (IDs/pairs/groups only)
- deterministic private task generator + frozen router evaluation code
- private 32 captures and detailed telemetry/outcome/action/result records
- public aggregate run/pair-falsification report
- `docs/M25_IDENTICAL_INPUT_FALSIFICATION.md`
- tests for pair equality, actual-label discordance, frozen-classifier reuse,
  aggregate-only reporting, schema/degraded/resume behavior
- updated `STATE.md` and `reports/FINDINGS.md`

### M25 stop condition

- manifest is committed before capture and 16 private prompt pairs validate equal
- exactly 32 captures complete or fixed-manifest blocker is reported
- same-run private rows validate and pair equality/deviation is measured
- M23 router classifier remains frozen
- public artifacts pass privacy/commit-safety checks; full suite passes
- agents-a1 is restored; production remains gated

## After M25

Stop the current autoloop at its three-milestone limit. The next operator-facing
steer must choose between:

- combining explicit trusted task metadata with telemetry for routing (a different
  supervised problem),
- collecting balanced objective error outcomes to study error prediction, or
- ending the telemetry-policy branch and returning to practical verifier quality.

## Repository hygiene

Do not commit private prompts/outputs, per-task/pair predictions, token IDs/text,
raw tensors, paths, weights, caches, or detailed records. Public reports remain
aggregate; no candidate label becomes gold and production remains gated.
