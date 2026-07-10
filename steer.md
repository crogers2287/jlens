# steer.md — M27 frozen error-prediction holdout

M1 through M26 are complete. The operator selected the objective
error-prediction track (post-M25 option B). Do not redo the practical
supervisor track, HF backend, action-routing holdouts, the M25 identical-input
falsification, or the M26 dataset build.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Current state after M26

- `data/prompts/m26_error_manifest.json` was committed before generation and
  froze: the arithmetic category/template, four difficulty bands, per-ID 16/8
  train/holdout split, seeded generation with no post-hoc selection, the
  deterministic `math_checker` label rule, constant checker applicability, a
  holdout seal, and the M27/M28 protocols.
- 96/96 same-run Qwen captures with logits + 24×60 router telemetry exist in
  private ignored locations along with per-task labels.
- Train labels: 46 pass / 18 fail / 0 undecided (band_a 16/0, band_b 16/0,
  band_c 13/3, band_d 1/15). The ≥8/≥8 modeling minimum is met.
- Holdout verdicts and holdout telemetry aggregates remain sealed: no public
  artifact reports them and no model has touched them.
- Train fail-vs-pass separation is descriptive only (decode entropy g≈+3.0,
  expert concentration g≈+1.9, router entropy g≈-1.9); difficulty band remains
  an explicit confound to be priced by the metadata-only baseline.
- Full suite green at 123 tests; production gated; candidate-only everywhere.

## M27 — frozen holdout error prediction (current milestone)

Goal: test whether M26 telemetry predicts pass/fail on the sealed 32-task
holdout under the protocol frozen in the M26 manifest.

Requirements (all already predeclared in `m26_error_manifest.json`):

- No refit, feature change, threshold tuning, or task change after reading
  holdout rows; the holdout is evaluated exactly once.
- All six baselines: majority_class, metadata_only (band one-hot),
  logits_only, router_only, router_plus_logits, full_telemetry.
- Train-standardized nearest centroid, squared Euclidean, lexicographic tie
  break, 2000-iteration fixed-seed bootstrap accuracy intervals.
- Undecided rows excluded from modeling and reported.
- Template-leakage framing: train and holdout share the one declared template
  by design; the metadata-only baseline prices the difficulty-band shortcut.
  Telemetry claims value only where it beats that baseline.

Deliverables:

- `src/m27_frozen_error_holdout.py` and `tests/test_m27_frozen_error_holdout.py`
  (already present with the frozen protocol; run against real private data)
- `data/prompts/m27_holdout_manifest.json` (aggregate metadata only)
- `reports/telemetry/hf_m27_frozen_error_evaluation.json` (all six baselines
  with confidence intervals; aggregate-only)
- `docs/M27_FROZEN_ERROR_HOLDOUT.md`
- Full test suite green

Stop condition: frozen evaluation complete with no post-capture tuning; all
six baselines and intervals public and aggregate-only; tests green; production
gated.

## After M27

M28 telemetry ablation and calibration under the manifest-frozen protocol:
single-feature and leave-one-out ablations over the ten full_telemetry
features, softmax-distance calibration with reliability bins and ECE,
false-positive/false-negative analysis by band, and a train-derived threshold
proposal that stays candidate-only. Verifier contradiction stays excluded as a
feature because the verifier defines the label.

## Repository hygiene

Do not commit private prompts/outputs, per-task predictions/labels, token
IDs/text, raw tensors, paths, weights, caches, or detailed records. Public
reports remain aggregate. No candidate becomes gold and production remains
gated until explicit audited unlock criteria are defined.
