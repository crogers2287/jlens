# steer.md — M30 telemetry-focused decisive increment track

M1 through M29 are complete. Do not reuse the spent M27 or M29 holdouts as decision targets. `CODEX_AUTOSTEER.md` remains the operating contract.

## Operator decision

The operator selects the telemetry research track and authorizes continued work to get the telemetry signal properly characterized and usable.

Start with option A from the post-M29 gate:

**M30 — decisive telemetry-vs-metadata increment test**

This milestone must establish or refute whether telemetry adds statistically meaningful predictive value beyond difficulty metadata in the controlled arithmetic category.

## Current evidence

- M29 used 384 fresh tasks with a sealed 192/96/96 split.
- Holdout: metadata_only .823; logits_only .854; router_only .750; window_entropy .833; full_telemetry .885; metadata_plus_telemetry .865.
- Full telemetry beat metadata by +.063, correcting 12 metadata errors while introducing 6.
- Paired 95% CI was [-.021,+.146], so the increment was not established at n=96.
- Telemetry is the best point-estimate system tested, but the decisive question is still statistical increment over metadata.
- M29 power analysis estimated a holdout near n≈200 at the observed discordance/effect size.
- Full suite was green at 130 tests; candidate-only and production gates remain.

## M30 preregistered design

Before any generation or capture, commit a public-safe manifest that freezes:

1. A fresh 768-task arithmetic dataset using the same controlled single-expression category and constant checker applicability.
2. Six boundary-focused difficulty bands, 128 tasks per band.
3. Per-band split fixed before generation:
   - 64 train
   - 32 validation
   - 32 holdout
4. Total split:
   - 384 train
   - 192 validation
   - 192 sealed holdout
5. Seeded unique operand generation with every generated task retained.
6. Deterministic `math_checker` pass/fail labels from same-run outputs.
7. Zero post-hoc selection or regeneration based on labels.
8. The exact M29 frozen nearest-centroid classifier family and feature definitions for the primary confirmatory test.
9. Primary comparison:
   - metadata_only
   - full_telemetry
10. Secondary descriptive baselines:
   - majority
   - logits_only
   - router_only
   - window_entropy
   - metadata_plus_telemetry
11. Paired-bootstrap 95% CI over holdout prediction differences.
12. Claim rule:
   - telemetry increment is established only if the paired full_telemetry − metadata_only accuracy CI excludes zero in the positive direction and all power/class minimums are met.
13. Validation-only threshold and calibration fitting.
14. The holdout may be read exactly once after protocol, features, classifier, and thresholds are frozen.

## M30 requirements

- Run on fresh tasks; do not reuse M27/M29 rows as confirmatory data.
- Keep prompt family and action applicability constant.
- Capture real logits and router telemetry from the HF/safetensors backend.
- Keep hidden-state capture disabled unless separately preregistered and justified before capture.
- Report class balance, undecided count, decode-cap count, and all power shortfalls honestly.
- Report paired wins/losses and both accuracy and balanced-accuracy deltas.
- Report calibration/ECE, but keep thresholds candidate-only.
- Public reports must remain aggregate-only.
- Restore and verify `agents-a1` after the GPU window.
- Run full repository tests and commit-safety checks.
- No production policy or threshold unlock.

## M30 deliverables

- `data/prompts/m30_decisive_manifest.json`
- deterministic private task generator/output path
- M30 capture/evaluation scripts or extensions
- `reports/telemetry/hf_m30_decisive_run_summary.json`
- `reports/telemetry/hf_m30_decisive_increment_evaluation.json`
- `docs/M30_DECISIVE_TELEMETRY_INCREMENT.md`
- tests covering preregistration, split sealing, one-read holdout behavior, paired increment logic, no-selection invariants, public no-text/no-ID output, and commit safety
- updated `STATE.md` and `reports/FINDINGS.md`

## M30 stop condition

- 768 fresh tasks are captured or any preregistered shortfall is reported without replacement.
- The sealed 192-task holdout is evaluated exactly once.
- The telemetry-vs-metadata increment is classified as established, not established, or negative under the preregistered rule.
- Public artifacts contain no task text, operands, outputs, per-task labels/predictions, paths, token text/IDs, tensors, weights, or caches.
- Full suite and commit-safe checks pass.
- Candidate-only and production gates remain.

## Telemetry-focused continuation after M30

After committing M30, update `steer.md` as a separate commit using the result-driven branch below.

### Branch 1 — increment established

Proceed to **M31 telemetry-triggered intervention study**:

- freeze the M30 score without refitting
- compare no retry, random retry, always retry, and telemetry-triggered retry/checking
- use deterministic correctness labels
- measure verified success improvement, additional compute, false alarms, and errors rescued
- begin creating verifier-grounded recovery traces only from objectively verified outcomes

### Branch 2 — positive point estimate but increment still not established

Proceed to **M31 stronger frozen classifier family** on fresh preregistered data:

- regularized logistic regression and one small nonlinear baseline
- metadata-only, telemetry-only, and metadata+telemetry ablations
- train fit, validation tuning, sealed fresh holdout once
- no architecture search after holdout capture

### Branch 3 — telemetry ties or loses to metadata materially

Proceed to **M31 transfer/falsification study** in a second deterministic category before any runtime-control claim. Do not keep scaling arithmetic indefinitely.

## Autosteer authorization

A telemetry-focused autoloop is authorized for up to three milestones total starting with M30, subject to `CODEX_AUTOSTEER.md` limits.

Stop immediately for:

- test or privacy failure that cannot be safely repaired
- model download, hardware, or resource decision outside the existing approved Qwen/HF plan
- any need to change the preregistered confirmatory protocol after seeing holdout outcomes
- any proposal to promote candidate telemetry scores into production policy

## Repository hygiene

Do not commit private prompts/outputs, operands, per-task predictions/labels, token IDs/text, raw tensors, file-system paths, model weights, caches, or detailed records. Public reports remain aggregate-only. No candidate becomes gold and production remains gated until explicit audited unlock criteria are defined.
