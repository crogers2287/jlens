# M28 telemetry ablation and calibration

M28 decomposes the M27 result: which of the ten frozen telemetry signals carry
the within-category error prediction, and how calibrated is the full-telemetry
score? Every analysis here follows the M28 protocol predeclared in
`data/prompts/m26_error_manifest.json` (same centroid family, train-fit /
holdout-eval, softmax-distance calibration, train-derived threshold).

Because the holdout was already read once in M27, M28 is a decomposition of a
fixed result, not a fresh predictive test. Rankings below are descriptive at
n=32 and must not be read as stable feature importance.

## Single-feature ablation (train-fit, holdout accuracy / balanced accuracy)

| Feature | Acc. | Bal. acc. | Acc. 95% bootstrap |
|---|---:|---:|---|
| high_entropy_count | 1.000 | 1.000 | [1.0, 1.0] |
| decode_window_entropy | .938 | .923 | [.844, 1.0] |
| expert_concentration | .844 | .891 | [.719, .969] |
| decode_step_count | .844 | .790 | [.719, .969] |
| low_confidence_count | .844 | .790 | [.688, .969] |
| router_entropy | .781 | .848 | [.625, .906] |
| top_k_margin_trend | .688 | .681 | [.531, .844] |
| final_selected_probability | .438 | .609 | [.25, .625] |
| final_top_k_margin | .438 | .609 | [.281, .594] |
| windowed_expert_shift | .312 | .522 | [.156, .469] |

Reading (majority baseline is .719):

- The error signal concentrates in decode-window entropy behavior. The count
  of high-entropy decode steps alone reproduces the full model's perfect
  holdout score, and mean window entropy is close behind.
- Router signals are real but weaker (expert concentration .844, router
  entropy .781), consistent with M27's blunt router-only detector.
- Final-token confidence signals alone (selected probability, top-k margin)
  score below the majority baseline: the last token of a wrong arithmetic
  answer is typically emitted confidently. Error information lives in the
  window during decoding, not in the final token.
- windowed_expert_shift carries essentially nothing here.
- Caveat: high_entropy_count is a count over decode steps, so it partially
  reflects answer length and hence operand size; it does, however, beat the
  pure length feature (decode_step_count .844) by a wide margin, so it is not
  merely length in disguise.

## Leave-one-out ablation

Removing any single feature from the ten-feature set leaves holdout accuracy
at .969–1.000 (maximum drop +.031). The signals are heavily redundant; no
single feature is load-bearing for the full model.

## Calibration (candidate-only)

Pseudo-probability of fail = softmax over negative squared centroid distances
(predeclared). On the holdout, with 4 equal-count bins:

| Bin | n | Mean predicted p(fail) | Observed fail rate |
|---|---:|---:|---:|
| 1 | 8 | .000 | .000 |
| 2 | 8 | .000 | .000 |
| 3 | 8 | .111 | .125 |
| 4 | 8 | 1.000 | 1.000 |

Expected calibration error: **.004**. The scores are strongly saturated near 0
and 1 — a reflection of how separable this dataset is, not a general property
of the score. On a harder or broader task distribution the mid-range bins
would be populated and ECE should be re-measured before any use.

## False-positive / false-negative analysis

Positive class = fail. The full-telemetry model makes zero holdout errors, so
FP = FN = 0 overall and in every band (8/8 correct in each). The informative
FP/FN behavior at feature level is visible in the single-feature table:
router_entropy and expert_concentration alone over-flag passes (M27's .60
fail precision), while final-token features under-flag fails.

## Threshold proposal — candidate-only

Derived from the train split only (balanced-accuracy grid search; the holdout
played no role in selecting it):

- threshold on p(fail): **0.95** — **candidate-only, not for production**
- train balanced accuracy at threshold: .934
- holdout balanced accuracy at threshold (descriptive): .944

This threshold inherits every caveat above (n=32, saturated scores, one task
category, one model). It must not be promoted beyond candidate status without
scaled data, a second category, and human-audited reviewed calibration.
Production remains gated.

## Privacy

The public report contains aggregate ablation metrics, calibration bins, and
band-level counts only — no task text, operands, outputs, per-task labels or
predictions, paths, tokens, or tensors.

Public artifacts:

- `reports/telemetry/hf_m28_ablation_calibration.json`
