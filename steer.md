# steer.md — post-M31 decision gate

M1 through M31 are complete. Do not redo the M30 decisive test (increment
ESTABLISHED) or the M31 intervention study. The M27/M29/M30 holdouts and the
M31 task set are spent as decision targets.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Autosteer status

The operator's telemetry autoloop (up to three milestones from M30) completed
two: M30 (decisive increment, ESTABLISHED) and M31 (intervention study, NOT
ESTABLISHED). The natural third milestone changes the intervention design in
a way the operator's Branch-1 plan did not preregister (it assumed a useful
verdict and trace scaling), so this run stops here for an operator decision.

## Current evidence

### M30 — decisive increment (ESTABLISHED)

- Powered n=192 once-read holdout: full_telemetry .917 vs metadata .818;
  paired Δaccuracy +.099 [+.042,+.156], Δbalanced-accuracy [+.050,+.165];
  27 metadata errors corrected vs 8 introduced.
- window_entropy alone insufficient (+.031, CI spans zero); calibration ECE
  .032 at the .50 threshold (candidate-only).

### M31 — intervention study (NOT ESTABLISHED, decomposed)

- 192 fresh tasks; frozen M30 score (refit verified against the published
  confusion matrix); seeded temperature-0.7 single retry; four
  replace-on-retry policies, none consulting labels.
- Success rates: no_retry .469; always_retry .464; random_retry .458;
  telemetry_triggered .474. Primary deltas span zero → not established.
- Decomposition: the trigger replicated (~89% of 99 triggered retries hit
  real failures — 11 false alarms vs random's 43) but the repair operator is
  the bottleneck: a resample rescues only ~4.5% of triggered failures because
  these arithmetic errors are systematic, not stochastic (retry pass rate
  46.4% ≈ greedy 46.9%).
- Telemetry gating was the only non-losing policy (fewest false alarms and
  introduced errors at matched compute). 4 verified recovery traces (private)
  — far too few to scale trace generation as Branch 1 assumed.

Across M26–M31: every protocol preregistered before generation; every
holdout/decision set read once; no private text/labels/predictions/paths/
tensors committed; agents-a1 restored after every GPU window; full suite
green at 143 tests; candidate-only and production gates unchanged.

## Research position

Detection is validated within the controlled category: internal telemetry
identifies model errors with an established increment over difficulty
metadata and ~89% trigger precision across three consecutive fresh task
sets. Intervention is not: naive resampling cannot repair systematic errors,
so the trigger currently has nothing effective to trigger. The next
substantive question is the repair operator, not the detector.

## Required operator decision before M32

Choose exactly one direction:

### A. Stronger repair operator behind the frozen trigger (recommended)

Preregister an M32 that keeps the frozen M30 trigger and replaces the
resample with a stronger repair operator, evaluated under the same four-
policy design on fresh tasks. Candidate operators, in increasing power:
(1) decomposition reprompt (ask the model to compute digit-by-digit /
step-by-step on retry); (2) checker-guided regeneration reusing the M20
grounded-regeneration machinery; (3) deterministic tool computation as an
upper-bound reference arm (establishes the ceiling any model-side repair
must be judged against). A useful verdict would also restart recovery-trace
generation at meaningful volume.

### B. Transfer test of the detector

Second deterministic category (e.g. string transformation or date
arithmetic) with its own preregistered design, testing whether the
established detector increment transfers beyond arithmetic before investing
further in repair.

### C. Reviewed calibration toward practical advisory use

Wire the frozen candidate p(fail) score into the existing shadow/review
workflow (advisory-only, no actions) and re-measure calibration and trigger
precision on real mixed workloads with human-reviewed outcomes.

### D. End telemetry research

Return to practical supervisor quality work with the detector documented as
a candidate-only research result.

Do not begin M32 until the operator selects A–D. Any new real model run must
remain under the existing approval or stop for a new model/hardware/resource
gate.

## Repository hygiene

Do not commit private prompts/outputs, operands, per-task predictions/labels,
token IDs/text, raw tensors, file-system paths, model weights, caches, or
detailed records. Public reports remain aggregate-only. No candidate becomes
gold and production remains gated until explicit audited unlock criteria are
defined.
