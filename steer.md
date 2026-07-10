# steer.md — post-M28 decision gate

M1 through M28 are complete. Do not redo the M26 dataset build, the one-shot
M27 frozen holdout evaluation, or the M28 ablation/calibration pass.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Autosteer status

The explicit loop completed three milestones in this run:

1. M26 objective error-prediction dataset (predeclared bands/split/protocols)
2. M27 frozen six-baseline holdout evaluation
3. M28 telemetry ablation and candidate-only calibration

The three-milestone loop limit is reached. Stop after committing this steer
even if a loop flag remains set. A new operator instruction is required to
choose the next milestone.

## Current evidence

### M26 — dataset

- 96 arithmetic tasks, one template, four predeclared difficulty bands,
  per-ID 16/8 train/holdout split committed before generation; deterministic
  math_checker labels from the same-run capture; all tasks retained.
- Constant action applicability held exactly (96/96 checker_needed), excluding
  the M25 metadata-observability failure mode by construction.
- Train: 46 pass / 18 fail / 0 undecided; holdout stayed sealed through M26.

### M27 — frozen holdout

- n=32 (9 fail/23 pass), evaluated once, no post-capture tuning.
- majority .719; metadata_only band shortcut .969; logits_only .969 (balanced
  .978, fail recall 1.0); router_only .812 (fail precision .60);
  router_plus_logits .906; full_telemetry 1.000.
- Licensed claim: within-category telemetry recovers and slightly extends the
  difficulty signal on a frozen holdout. The increment over the metadata
  shortcut is one task at n=32 — not statistically established.

### M28 — ablation and calibration

- high_entropy_count alone reproduces the full model (1.000);
  decode_window_entropy .938; router features .78–.84; final-token confidence
  below majority (.438); windowed_expert_shift .312. Leave-one-out max drop
  .031 (heavy redundancy).
- The error signal lives in decode-window entropy behavior, not final-token
  confidence — wrong arithmetic answers end confidently.
- Calibration ECE .004 but saturated scores; threshold p(fail) ≥ 0.95 derived
  from train only and marked candidate-only/not-for-production everywhere.

Across M26–M28: no weights/caches/paths/raw text/tensors/per-task labels or
predictions were committed; detailed records remain ignored/private; the
holdout was read exactly once for prediction; full suite green at 123 tests;
candidate-only and production gates unchanged.

## Research conclusion so far

Within one controlled task category, internal telemetry — dominated by
decode-window entropy signals — predicts objective model errors on a frozen
holdout. This is the association M23–M25 could not claim. What remains
unproven: a statistically meaningful increment over the difficulty-metadata
shortcut, transfer beyond arithmetic, transfer across models, and calibration
on harder distributions.

## Required operator decision before M29

Choose exactly one direction:

### A. Scale the within-category increment test (recommended)

Grow the dataset (more tasks per band, finer bands near the pass/fail
boundary, e.g. 2-digit×2-digit through 4-digit×3-digit) to power the
telemetry-versus-metadata comparison that n=32 cannot decide. Predeclare a new
holdout; the M27 holdout is spent for confirmatory use.

### B. Second task category (transfer test)

Add a second deterministic category (e.g. exact string transformation or date
arithmetic) with its own predeclared bands/split, and test whether the frozen
window-entropy signal transfers without refitting.

### C. Reviewed calibration toward practical use

Wire the candidate p(fail) score into the existing shadow/review workflow
(advisory-only), accumulate human-reviewed outcomes, and re-measure
calibration on real workloads. No production unlock without audited criteria.

### D. End telemetry research

Return to practical supervisor quality work.

Do not begin M29 until the operator selects A, B, C, or D. Any new real model
run must remain under the existing approval or stop for a new
model/hardware/resource gate.

## Repository hygiene

Do not commit private prompts/outputs, per-task predictions/labels, token
IDs/text, raw tensors, paths, weights, caches, or detailed records. Public
reports remain aggregate. No candidate becomes gold and production remains
gated until explicit audited unlock criteria are defined.
