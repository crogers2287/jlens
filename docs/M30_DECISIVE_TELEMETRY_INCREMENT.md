# M30 decisive telemetry increment test

M30 is the confirmatory milestone the track has been building toward: a
preregistered, adequately powered, one-shot test of whether internal telemetry
adds statistically meaningful predictive value over difficulty-band metadata
for within-category objective error prediction.

**Verdict under the preregistered rule: ESTABLISHED.**

## Preregistered design

`data/prompts/m30_decisive_manifest.json` was committed before any generation
(operator protocol, steer 2a4699e):

- 768 fresh tasks, six boundary-focused bands × 128, sealed per-band split
  64 train / 32 validation / 32 holdout (totals 384/192/192).
- Operand tuples drawn from a fresh seed with deterministic rejection of every
  tuple the committed M29 manifest generates — no M27/M29 task instance can
  recur as confirmatory data.
- Same invariants as M26–M29: one prompt template, constant `checker_needed`
  applicability, deterministic `math_checker` labels, all generated tasks
  retained, no post-hoc selection.
- The exact M29 frozen nearest-centroid family and feature definitions.
- Primary confirmatory comparison: full_telemetry vs metadata_only, paired
  bootstrap over holdout rows, with the classification rule fixed in advance:
  *established* iff the 95% accuracy-difference interval's lower bound
  exceeds zero and all power minimums are met; *negative* iff the upper bound
  is below zero; otherwise *not established*.
- Validation-only threshold/calibration fitting; holdout read exactly once.
- Power minimums: ≥48/48 train, ≥24/24 validation, ≥40/40 holdout per class.

## Real run

- 768/768 captures in one hardware window (~1 s/task; agents-a1 restored and
  verified afterward). Logits and 24×60 router telemetry on every row; all
  768 actions `checker_needed`; 0 undecided; 0 decode-cap hits.
- Labels: train 210 fail / 174 pass; validation 105 / 87; holdout 103 / 89.
  Every power minimum met — the confirmatory test is adequately powered.

## Holdout results (n=192, read once)

| Baseline | Acc. | Bal. acc. | Fail recall / precision | Acc. 95% bootstrap |
|---|---:|---:|---|---|
| majority_class | .536 | .500 | 1.000 / .536 | [.464, .604] |
| metadata_only | .818 | .807 | .951 / .766 | [.760, .870] |
| logits_only | .854 | .856 | .825 / .895 | [.802, .901] |
| router_only | .833 | .824 | .951 / .784 | [.781, .880] |
| window_entropy | .849 | .858 | .728 / .987 | [.797, .896] |
| **full_telemetry** | **.917** | **.916** | .922 / .922 | [.875, .953] |
| metadata_plus_telemetry | .922 | .921 | .932 / .923 | [.880, .958] |

## Primary confirmatory result

Paired bootstrap over the 192 holdout rows, full_telemetry − metadata_only:

- Δ accuracy **+.099**, 95% CI **[+.042, +.156]**
- Δ balanced accuracy 95% CI **[+.050, +.165]**
- Wins/losses against metadata: telemetry corrects **27** of metadata's
  errors while introducing **8** (149 both right, 8 both wrong)

Both intervals exclude zero in the positive direction and every power minimum
is met, so the preregistered classification is **established**.

Secondary comparisons (descriptive):

- metadata_plus_telemetry − metadata_only: +.104 [+.057, +.156] — at this
  sample size the combination now edges out telemetry alone (.922 vs .917),
  unlike M29's n=96 reversal.
- window_entropy − metadata_only: +.031 [−.042, +.104] — the two-feature
  entropy set is NOT sufficient alone; the established increment belongs to
  the full ten-feature set.

## Calibration (candidate-only)

Validation-derived thresholds, holdout reliability (8 equal-count bins):

- full_telemetry: ECE **.032**, threshold .50 p(fail), holdout balanced
  accuracy at threshold .916
- metadata_plus_telemetry: ECE **.043**, threshold .75, holdout balanced
  accuracy at threshold .938

All thresholds remain **candidate-only, not for production**.

## Scope of the claim

Within one controlled task category (single-expression integer arithmetic),
one model (Qwen1.5-MoE-A2.7B-Chat), and one decode protocol (greedy, 64-token
cap), internal telemetry adds a statistically established ~+10-point accuracy
increment over the difficulty-metadata shortcut for predicting deterministic
pass/fail outcomes on a fresh, sealed, once-read holdout. Not claimed:
transfer to other categories or models, causal interpretation, production
readiness, or any general "the model knows when it is wrong" statement.

Per the operator's result-driven branching, the next milestone is the
telemetry-triggered intervention study (Branch 1).

## Privacy

Public artifacts contain aggregate counts, band definitions, metrics,
intervals, and calibration bins only — no task text, operands, outputs,
per-task labels/predictions, paths, tokens, or tensors. Detailed records stay
gitignored. Candidate-only and production gates remain.

Public artifacts:

- `data/prompts/m30_decisive_manifest.json`
- `reports/telemetry/hf_m30_decisive_run_summary.json`
- `reports/telemetry/hf_m30_decisive_increment_evaluation.json`
