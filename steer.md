# steer.md — post-M29 decision gate

M1 through M29 are complete. Do not redo the M26 dataset, the one-shot M27
holdout, the M28 ablation, or the M29 scaled power test. The M27 and M29
holdouts are both spent as decision targets.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Autosteer status

M29 was executed as a single operator-directed milestone (option A from the
post-M28 gate). Stop after committing this steer. A new operator instruction
is required to choose the next milestone.

## Current evidence

### M29 — scaled power test (n=384, sealed 192/96/96 split)

- Boundary-concentrated bands worked: holdout 51 fail/45 pass; every
  predeclared power minimum met; 0 undecided; 0 capped; 384/384
  checker_needed; no post-hoc selection.
- Once-read holdout: majority .531; metadata_only .823; logits_only .854;
  router_only .750; window_entropy .833; full_telemetry .885 [.823,.948];
  metadata_plus_telemetry .865.
- Predeclared paired increment over metadata: full +.063 [−.021,+.146]
  (12 wins/6 losses), meta+tel +.042 [−.031,+.115], window +.010. All
  intervals include zero → **telemetry-vs-metadata increment NOT
  established**. Balanced-accuracy CI for full telemetry misses narrowly
  ([−.006,+.153]); that is unproven, not "nearly proven".
- M28's perfect single-feature result was a band-separability artifact:
  window_entropy scores .833 at boundary difficulty (recall .706, precision
  .973). Mid-window entropy is a high-precision partial failure flag.
- Band metadata adds nothing once telemetry is present (.865 < .885) in the
  frozen centroid family. Telemetry and metadata err differently (metadata
  over-flags, logits under-flag).
- Calibration off easy/hard splits: ECE .059 (full) / .117 (meta+tel);
  validation-derived thresholds .70/.75 p(fail) stay candidate-only.
- Power arithmetic: at the observed Δ≈+.06 with 18/96 discordant holdout
  predictions, a decisive test needs a holdout near n≈200.

Across M26–M29: no weights/caches/paths/raw text/tensors/per-task labels or
predictions committed; detailed records ignored/private; each holdout read
exactly once; full suite green at 130 tests; candidate-only and production
gates unchanged.

## Research position

Within one controlled category, telemetry consistently outperforms the
difficulty shortcut point-wise across two independent frozen holdouts, and
full telemetry is the best single system tested (.885). What is still not
established is the *statistical* increment over metadata at the sample sizes
run so far — the honest blocker is holdout size, not signal absence. The
frozen nearest-centroid family may also understate telemetry (it cannot use
feature interactions).

## Required operator decision before M30

Choose exactly one direction:

### A. Decisive increment test at n≈200 holdout (recommended)

One more scaling step: predeclare ~640–768 tasks with the same six-band
boundary design (or finer), sealed split with a ~200-task holdout, identical
frozen protocol. This either establishes or refutes the increment at the
observed effect size. Roughly 15–20 minutes of capture at ~1 s/task.

### B. Stronger frozen classifier family first

Predeclare a small model upgrade (e.g. regularized logistic regression on the
same frozen features, fit on train, thresholds on validation) and re-run the
n=96 M29 splits as a *new* frozen protocol on fresh captures. Tests whether
the centroid family is leaving telemetry signal on the table before paying
for more data.

### C. Transfer test (second category)

Second deterministic category with its own predeclared bands/split to test
whether the telemetry error signal transfers beyond arithmetic.

### D. Reviewed calibration toward practical use

Wire the candidate p(fail) score into the shadow/review workflow
(advisory-only) and re-measure calibration on real workloads.

### E. End telemetry research

Return to practical supervisor quality work.

Do not begin M30 until the operator selects A–E. Any new real model run must
remain under the existing approval or stop for a new model/hardware/resource
gate.

## Repository hygiene

Do not commit private prompts/outputs, per-task predictions/labels, token
IDs/text, raw tensors, paths, weights, caches, or detailed records. Public
reports remain aggregate. No candidate becomes gold and production remains
gated until explicit audited unlock criteria are defined.
