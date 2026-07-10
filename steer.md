# steer.md — M28 telemetry ablation and calibration

M1 through M27 are complete on the objective error-prediction track. Do not
redo the M26 dataset build or the one-shot M27 frozen holdout evaluation; the
holdout has now been read once and any further fitting against it must be
labeled exploratory.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Current state after M27

- Frozen six-baseline holdout results (n=32, 9 fail/23 pass): majority .719;
  metadata_only band shortcut .969; logits_only .969 (balanced .978, fail
  recall 1.0); router_only .812 (fail recall 1.0, precision .60);
  router_plus_logits .906; full_telemetry 1.000.
- Licensed claim: within one controlled category, telemetry recovers and
  slightly extends the difficulty signal; the increment over the metadata
  shortcut is one task at n=32 and is not statistically established.
- Router-only over-flags within category; logits-window signals carry most of
  the error information.
- All public artifacts aggregate-only; per-task labels/predictions private.
- Full suite green at 123 tests; candidate-only and production gates active.

## M28 — telemetry ablation and calibration (current milestone)

Goal: identify which telemetry signals carry the predictive value observed in
M27, and calibrate the full-telemetry score, all under the M28 protocol frozen
in `data/prompts/m26_error_manifest.json`.

Requirements (predeclared in the M26 manifest):

- Single-feature and leave-one-out ablations over the ten full_telemetry
  features (entropy, selected-token probability, top-k margin, router entropy,
  expert concentration, decode-window shift, decode length, high-entropy and
  low-confidence counts, margin trend), same frozen centroid family,
  train-fit/holdout-eval.
- Calibration score: softmax over negative squared centroid distances as
  pseudo-probability of fail; 4 equal-count holdout reliability bins; ECE.
- False-positive/false-negative analysis aggregated by band only.
- Threshold proposal derived from the train split only and marked
  candidate-only; no production threshold may be set.
- Verifier contradiction stays excluded as a feature: the deterministic
  verifier defines the label, so using it as input would leak labels.
- Report feature importance honestly: n=32 holdout rankings are descriptive,
  not stable importance.

Deliverables:

- `src/m28_ablation_calibration.py` and `tests/test_m28_ablation_calibration.py`
  (already present with the frozen protocol; run against real private data)
- `reports/telemetry/hf_m28_ablation_calibration.json` (ablation table,
  reliability curve, ECE, FP/FN by band, candidate-only threshold)
- `docs/M28_TELEMETRY_ABLATION_CALIBRATION.md`
- Full test suite green

Stop condition: feature importance reported without overstatement; calibration
outputs marked candidate-only; no production threshold; tests green.

## After M28

The three-milestone autoloop limit (M26–M28) is reached at M28 completion.
Stop after committing the M28 steer update. Candidate follow-ups requiring a
new operator instruction:

- Scale the within-category dataset (more tasks per band, finer bands) to
  power the telemetry-vs-metadata increment test that n=32 cannot decide.
- A second task category (e.g. deterministic string transformation) to test
  whether the logits-window error signal transfers across categories.
- Reviewed calibration of the candidate threshold against human-audited
  outcomes before any production discussion.

## Repository hygiene

Do not commit private prompts/outputs, per-task predictions/labels, token
IDs/text, raw tensors, paths, weights, caches, or detailed records. Public
reports remain aggregate. No candidate becomes gold and production remains
gated until explicit audited unlock criteria are defined.
