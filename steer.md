# steer.md — post-M23 frozen telemetry holdout

M1 through M23 are complete. Do not redo the practical supervisor track, fixture
telemetry, M22 real probe, or M23 same-run training batch.

`CODEX_AUTOSTEER.md` remains part of the operating contract.

## Autosteer mode

Default mode completes one milestone, commits implementation, updates this file
separately, and stops. Loop mode requires `CODEX_AUTOSTEER_LOOP=true` or explicit
operator instruction.

The current approval covers the existing Qwen MoE checkpoint on Thor, local-only
loading, dual-3090 BF16 use, hidden capture disabled, and temporary llama-swap
unload/restore. Stop for another model/download/license, a changed hardware plan,
new dependency, live retrieval, or materially larger resource footprint.

## Current state

- M1–M20: practical local supervisor track through grounded regeneration
- M21: fixture-first HF/safetensors telemetry backend
- M22: real eight-task HF MoE telemetry validation
- M23: 32-task within-model telemetry/outcome validation

M23 result:

- Predeclared 8 checker / 8 retrieval / 8 review / 8 no-action tasks before run.
- Qwen chat-template output and internal telemetry came from the same decode.
- 32/32 completed; logits and 24-layer × 60-expert router telemetry available.
- Actual routes exactly matched the balanced predeclared groups.
- Deterministic checker: 7 pass / 1 fail; fail/pass effects withheld at n=1/7.
- Nine prose tasks hit 64 tokens; every checker and control reached EOS first.
- Router entropy/concentration showed descriptive group separation, with fixed-
  seed bootstrap intervals excluding zero for checker/retrieval/review contrasts.
- Task category, prompt form, verifier applicability, and output length remain
  confounds. No threshold/policy/predictive claim was made.
- All detailed records/captures remain private; public artifacts are aggregate.
- Full suite green at 95 tests. Production remains gated.
- agents-a1 serving was restored and verified.

## Next milestone: M24 frozen holdout evaluation

M24 tests whether an M23-only telemetry classifier generalizes to unseen task IDs.
The holdout manifest, features, model family, and metrics must be frozen before any
M24 telemetry is inspected. Do not tune on holdout results.

### Frozen holdout selection

Use exactly 40 unseen existing public task IDs, 10 per predeclared class. The
initial 48-ID preregistration referenced unavailable source IDs; this was caught
and corrected before any M24 capture. Model/features/metrics are unchanged:

- checker: `m19_m_008` through `m19_m_017`
- retrieval: `m15_c_008`–`m15_c_009` plus `m19_c_000`–`m19_c_007`
- review: `m15_x_008` through `m15_x_017`
- no-action controls:
  - `m15_e_004` through `m15_e_008`
  - `m15_j_002` through `m15_j_004`
  - `m15_r_002` through `m15_r_003`

No M22/M23 task ID may appear in the holdout.

### Frozen features and classifiers

Use only these M23 aggregate features:

1. decode-window mean entropy
2. final selected-token probability
3. final top-k margin
4. mean router entropy
5. mean expert concentration

Train on the 32 private M23 detailed records and M23 actual action labels only.
Freeze three nearest-centroid classifiers before reading M24 captures:

- full: all five features
- logits-only: features 1–3
- router-only: features 4–5

For each classifier:

- standardize with M23 training mean and sample standard deviation
- use one centroid per actual M23 action class
- predict minimum squared Euclidean distance
- break exact ties lexicographically
- do not tune weights, thresholds, features, or class priors

### Frozen metrics

Report on M24 only:

- accuracy
- balanced accuracy
- macro F1
- aggregate confusion matrix
- per-class precision/recall/F1/support
- fixed-seed 2,000-bootstrap 95% interval for accuracy
- majority-class baseline accuracy (expected 0.25 on the balanced holdout)
- full versus logits-only versus router-only comparison

Do not perform significance tests, threshold fitting, model selection, or retry a
different manifest after seeing results.

### M24 runtime objectives

1. Commit the corrected ID/group-only 40-task manifest before the real run.
2. Use the same approved model/hardware/local-only/chat-template/router-only plan.
3. Capture up to 64 tokens and record cap reach honestly.
4. Derive Qwen-specific verifier/action outcomes from the same private capture.
5. Validate all telemetry/runtime/action/result rows against existing schemas.
6. Apply the frozen M23 classifiers to M24 features without updating centroids.
7. Public artifacts may contain aggregate metrics/confusion only, never per-task
   predictions, IDs, text, paths, raw tensors, or model weights.
8. Restore agents-a1 after the capture window.
9. Keep all labels candidate-only and production gated.

### M24 deliverables

- `data/prompts/m24_holdout_manifest.json` with public IDs/groups only
- frozen classifier/evaluation code with CPU fixture tests
- private 40 raw captures and detailed telemetry/outcome/action/result records
- public aggregate holdout run summary
- public aggregate frozen-evaluation report
- `docs/M24_FROZEN_HOLDOUT_EVALUATION.md`
- updated `STATE.md` and `reports/FINDINGS.md`

### M24 stop condition

- manifest is frozen and disjoint from M22/M23 before the real run
- exactly 40 holdout tasks complete or an honest fixed-manifest blocker is reported
- same-run Qwen telemetry/outcome linkage validates
- classifiers use only M23 training aggregates and remain unchanged after holdout
- all frozen metrics are reported without per-task leakage or tuning
- private rows validate; public artifacts pass privacy/commit-safety checks
- full test suite passes; production remains gated

## After M24

- If the full classifier materially exceeds 0.25 and is stable across classes,
  proceed to M25 confound-controlled paired prompts; do not deploy a policy.
- If only router/logits ablations work, focus M25 on that frozen feature family.
- If performance is near baseline or collapses by class, stop the telemetry-policy
  branch and return to practical verifier/retrieval quality work.
- If same-run or privacy integrity fails, repair it before any further model run.

## Repository hygiene

Do not commit private prompts, outputs, per-task predictions, token IDs/text, raw
tensors, paths, weights, caches, or detailed records. Public reports stay aggregate;
candidate-only and production gates remain until audited unlock criteria exist.
