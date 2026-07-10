# M29 scaled objective error prediction power test

M29 answers the question M27 could not: does telemetry add statistically
meaningful predictive value over the difficulty-metadata shortcut? The M27
holdout (n=32) was spent and is not reused as a decision target. M29 scales to
384 new tasks concentrated near the pass/fail boundary and predeclares a
paired incremental-value test.

## Preregistered design

`data/prompts/m29_power_manifest.json` was committed before any generation.
It fixes:

- Six multiplication difficulty bands (64 tasks each) spanning the boundary:
  2×1-digit, 2×2, 3×2, 4×2, 3×3, 4×3. Mid bands were chosen to produce mixed
  outcomes where band membership alone cannot decide the label.
- A sealed per-ID split per band: 32 train / 16 validation / 16 holdout.
  Train fits classifiers; validation selects the candidate threshold and
  calibration mapping only; the holdout is read exactly once after everything
  is frozen.
- The same invariants as M26: one prompt template, seeded unique operand
  generation with all tasks retained, deterministic `math_checker` labels,
  constant `checker_needed` applicability, no post-hoc selection.
- Seven baselines: majority, metadata-only (band one-hot), logits-only,
  router-only, window-entropy (the M28-motivated set, tested here on new
  data), full telemetry, metadata+telemetry.
- The incremental-value rule: telemetry adds meaningful value only if the
  paired-bootstrap 95% accuracy-difference interval over holdout rows
  excludes zero and all power minimums are met.
- Power minimums: ≥24/24 train, ≥10/10 validation, ≥20/20 holdout per class.

## Real run

- 384/384 captures in one hardware window (~1 s/task; agents-a1 restored and
  verified afterward); logits and 24×60 router telemetry on every row; all
  384 actions `checker_needed`; 0 undecided; 0 rows hit the decode cap.
- Labels by split: train 106 fail / 86 pass; validation 54 / 42; holdout
  51 / 45. Every power minimum met — the increment test is adequately
  powered at the predeclared thresholds.
- The boundary design worked: band_1 all pass, band_2 ~12% fail, band_3
  ~53% fail, band_5 ~66% fail, band_4/6 ~90%+ fail.

## Holdout results (n=96, read once)

| Baseline | Acc. | Bal. acc. | Fail recall | Fail prec. | Acc. 95% bootstrap |
|---|---:|---:|---:|---:|---|
| majority_class | .531 | .500 | 1.000 | .531 | [.427, .635] |
| metadata_only | .823 | .814 | .961 | .766 | [.740, .896] |
| logits_only | .854 | .859 | .784 | .930 | [.781, .917] |
| router_only | .750 | .740 | .902 | .708 | [.656, .833] |
| window_entropy | .833 | .842 | .706 | .973 | [.760, .906] |
| full_telemetry | .885 | .887 | .863 | .917 | [.823, .948] |
| metadata_plus_telemetry | .865 | .865 | .863 | .880 | [.792, .927] |

## Incremental value over metadata-only (paired bootstrap, predeclared)

| Comparison | Δ accuracy | Δ acc. 95% CI | Δ bal. acc. 95% CI | Wins/losses vs metadata | Established? |
|---|---:|---|---|---|---|
| metadata+telemetry − metadata | +.042 | [−.031, +.115] | [−.020, +.127] | 9 / 5 | **No** |
| full_telemetry − metadata | +.063 | [−.021, +.146] | [−.006, +.153] | 12 / 6 | **No** |
| window_entropy − metadata | +.010 | [−.094, +.115] | [−.063, +.121] | 14 / 13 | **No** |

Under the predeclared claim rule, **telemetry's increment over the difficulty
shortcut is not established**: every paired 95% interval includes zero. The
point estimates are consistently positive (full telemetry corrects twice as
many metadata errors as it introduces, 12 vs 6), and the balanced-accuracy
interval for full telemetry only barely includes zero — but "barely not
established" is not established.

## What M29 did establish

1. **The M28 single-feature story did not replicate at boundary difficulty.**
   high_entropy_count-based window_entropy scored .833 here versus 1.000 on
   the easy/hard M27 holdout — the perfect score was substantially a
   band-separability artifact, which is exactly what this power test was
   designed to expose. Its precision remains excellent (.973) but recall is
   .706: mid-window entropy flags a *kind* of failure, not all failures.
2. **Telemetry and metadata make different errors.** Metadata-only over-flags
   (fail recall .961, precision .766); logits-only under-flags with high
   precision (.930). Full telemetry balances both at the best overall point.
3. **Adding band metadata to telemetry does not help** (.865 vs .885 for
   telemetry alone) within this frozen centroid family — telemetry already
   encodes the difficulty signal.
4. **Calibration degrades off the easy/hard split, as M28 predicted.** With
   mid-range bins now populated: full-telemetry ECE .059 (was .004),
   metadata+telemetry ECE .117. Validation-derived thresholds (.70 / .75
   p(fail)) reach holdout balanced accuracy .859 / .825 — all
   **candidate-only, not for production**.

## Power arithmetic for the next step

At the observed effect (Δ ≈ +.06, 18/96 discordant), the paired CI half-width
is ≈ .085; a decisive test at this effect size needs a holdout of roughly
n ≈ 200 (about 2× the discordant count at the same rate). That is one more
scaling step, not a redesign.

## Privacy

Public artifacts contain aggregate counts, band definitions, metrics,
intervals, and calibration bins only — no task text, operands, outputs,
per-task labels/predictions, paths, tokens, or tensors. All detailed records
stay gitignored. Candidate-only and production gates remain.

Public artifacts:

- `data/prompts/m29_power_manifest.json`
- `reports/telemetry/hf_m29_power_run_summary.json`
- `reports/telemetry/hf_m29_power_evaluation.json`
