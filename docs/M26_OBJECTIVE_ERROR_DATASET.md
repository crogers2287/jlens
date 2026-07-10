# M26 objective error prediction dataset

M26 opens the post-M25 research track the operator selected: objective
within-category error prediction. M25 falsified telemetry-only action routing,
so M26 stops asking telemetry about workflow metadata and instead asks whether
internal Qwen telemetry co-varies with the model actually being wrong, inside
one fixed task category where prompt family and action applicability never
change.

## Preregistered design

`data/prompts/m26_error_manifest.json` was committed before any task
generation. It fixes:

- One deterministic task category: single-expression integer arithmetic with
  one shared prompt template for all 96 tasks.
- Four difficulty bands (24 tasks each) chosen ex ante to span the pass/fail
  boundary: two-digit addition, two-digit-by-one-digit multiplication,
  two-digit-by-two-digit multiplication, three-digit-by-three-digit
  multiplication.
- A per-ID train/holdout split (16 train / 8 holdout per band) assigned before
  generation, plus a holdout seal: M26 public artifacts may not report holdout
  verdict counts or holdout telemetry aggregates.
- Deterministic operand generation from a fixed seed with unique tuples per
  band; every generated task is retained. Balance is sought ex ante through
  band difficulty, never through post-hoc failure selection.
- Constant action applicability: every task is `math` with a safe expression,
  so the supervisor must plan `checker_needed` for all 96 tasks; drift is a
  stop condition, not a relabeling opportunity.
- The label rule: the deterministic `math_checker` verdict on the same-run
  captured greedy output. Undecided verdicts are excluded from modeling and
  reported. No human selection anywhere.
- The frozen M27 baseline protocol (six baselines, nearest centroid, bootstrap
  intervals) and the frozen M28 ablation/calibration protocol.

## Real run

- All 96 private prompts were generated deterministically from the manifest
  and captured in one hardware window with the same local Qwen MoE, BF16 on
  two 24 GiB GPUs, chat template, greedy decode, 64-token cap, router-only
  capture. `agents-a1` serving was restored and verified afterward.
- 96/96 captures completed with logits and 24-layer × 60-expert router
  telemetry; hidden states stayed disabled.
- All 96 actual actions were `checker_needed` — action applicability held
  constant exactly as declared.
- No train row hit the decode cap; every train arithmetic answer terminated at
  EOS.

## Train-split outcome (holdout sealed)

| Band | Train pass | Train fail |
|---|---:|---:|
| band_a (2-digit +) | 16 | 0 |
| band_b (2-digit × 1-digit) | 16 | 0 |
| band_c (2-digit × 2-digit) | 13 | 3 |
| band_d (3-digit × 3-digit) | 1 | 15 |

Train totals: 46 pass / 18 fail / 0 undecided. The predeclared modeling
minimum (≥8 per class) is met. The difficulty bands worked as designed: errors
concentrate where multiplication gets hard, without any post-hoc selection.

## Train-split telemetry association (descriptive only)

Comparing train fail versus pass rows, with Hedges g and fixed-seed bootstrap
mean-difference intervals (aggregate only, no classifier or threshold):

- decode window entropy is higher on fails (g ≈ +3.0)
- high-entropy step count is higher on fails (g ≈ +2.4)
- expert concentration is higher on fails (g ≈ +1.9)
- router entropy is lower on fails (g ≈ -1.9)
- low-confidence step count is higher on fails (g ≈ +1.6)
- top-k margin trend is more negative on fails (g ≈ -1.2)

These are within-category associations on the train split only. Difficulty
band remains correlated with the label by design, so none of this is
predictive value: the frozen M27 holdout evaluation with an explicit
metadata-only (band shortcut) baseline is the actual test.

## Privacy

Public artifacts contain aggregate counts, band definitions, and group
statistics only — no task text, operands, outputs, per-task labels,
predictions, hashes of private text, paths, tokens, or tensors. The generated
task set, captures, telemetry/runtime/action/result records, and per-task
labels stay in gitignored private locations. Candidate-only and production
gates remain.

Public artifacts:

- `data/prompts/m26_error_manifest.json`
- `reports/telemetry/hf_m26_error_run_summary.json`
- `reports/telemetry/hf_m26_error_telemetry_summary.json`
