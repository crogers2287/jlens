# M31 telemetry-triggered intervention study

M31 moves from prediction to intervention: does the frozen M30 telemetry
score, used as a retry trigger, improve verified task success against
no-retry, matched-compute random-retry, and always-retry controls?

**Verdict under the preregistered rule: NOT ESTABLISHED — with a precise
decomposition: the trigger works, the naive resample repair does not.**

## Preregistered design

`data/prompts/m31_intervention_manifest.json` was committed before any
generation or capture:

- 192 fresh tasks (six bands × 32), operand tuples deterministically disjoint
  from both the M29 and M30 manifests. No M31 fitting of any kind.
- Frozen score: the M30 full_telemetry nearest-centroid model, refit
  deterministically from the private M30 train records and verified to
  reproduce the published M30 holdout confusion matrix exactly, with the
  frozen validation threshold p(fail) ≥ .50.
- Original decode: the standard greedy protocol. Retry decode: one seeded
  temperature-0.7 sample per task (deterministic per-task torch generator
  seed), same template and 64-token cap. Sampling was added to the capture
  script as an opt-in flag; the greedy path is unchanged and its tests pass.
- Four replace-on-retry policies on identical tasks and the identical single
  retry capture, none consulting labels: no_retry, always_retry,
  random_retry (fixed-seed subset matched to the trigger count),
  telemetry_triggered (retry iff frozen p(fail) ≥ .50).
- Deterministic `math_checker` labels on original and retry outputs; paired
  bootstrap CIs; classification rule fixed in advance: *useful* iff the
  telemetry policy beats both no_retry and matched-compute random_retry with
  positive CIs excluding zero; *harmful* iff it loses to no_retry with a
  negative CI; otherwise *not established*.

## Real run

- 192 greedy + 192 sampled captures in one hardware window; agents-a1
  restored and verified. All 192 original actions `checker_needed`;
  0 undecided (original or retry); 0 decode-cap hits in either run.
- Original outcomes: 90 pass / 102 fail. Retry outcomes: 89 pass / 103 fail —
  the resampled decode is no more accurate overall than the greedy one.
- Trigger rate .516 (99 of 192).

## Policy results (n=192)

| Policy | Verified success | Retries | False alarms | Rescued | Introduced |
|---|---:|---:|---:|---:|---:|
| no_retry | .469 | 0 | 0 | 0 | 0 |
| always_retry | .464 | 192 | 90 | 6 | 7 |
| random_retry | .458 | 99 | 43 | 3 | 5 |
| telemetry_triggered | .474 | 99 | **11** | 4 | 3 |

Paired success-rate deltas (2000-iteration fixed-seed bootstrap):

| Comparison | Δ success | 95% CI |
|---|---:|---|
| telemetry_triggered − no_retry | +.005 | [−.021, +.031] |
| telemetry_triggered − random_retry | +.016 | [−.010, +.042] |
| always_retry − no_retry | −.005 | [−.042, +.031] |
| random_retry − no_retry | −.010 | [−.042, +.016] |

Neither primary interval excludes zero → **not established**.

## The decomposition that matters

1. **The trigger replicated again.** Of 99 telemetry-triggered retries, only
   11 were false alarms — the frozen score found genuine failures with ~89%
   precision on a third consecutive fresh task set, using a threshold chosen
   on M30 validation data. Random matched-compute retries hit failures only
   ~57% of the time.
2. **The repair operator is the bottleneck.** A single temperature-0.7
   resample rescued only 4 of ~88 correctly-triggered failures (~4.5%). The
   model's multiplication errors are systematic, not stochastic: resampling
   redraws from the same flawed computation and usually fails again
   (retry pass rate 46.4% ≈ greedy 46.9%).
3. **Telemetry gating is still the only non-losing policy.** always_retry and
   random_retry are both net-negative (replacement risk on correct outputs);
   telemetry gating avoided 79 of 90 potential false alarms and introduced
   the fewest new errors (3). Gating helps; the intervention it gates is too
   weak to show through.

Implication for any future intervention milestone: keep the frozen trigger,
replace the repair operator — e.g. checker-guided or decomposition-based
regeneration (the M20 grounded-regeneration machinery is a candidate), or
tool-assisted computation — rather than scaling resample retries.

## Recovery traces

4 verified wrong→right rescues under the telemetry policy were written as
private gitignored trace records (prompt, both outputs, verdicts, trigger
score). Public artifacts carry only this count and the schema field list.
Four traces are far too few for any training use — another reason the
resample operator, not the trigger, is what must change.

## Privacy

Public artifacts contain aggregate policy metrics, deltas, and counts only —
no task text, operands, outputs, per-task labels/predictions/triggers, paths,
tokens, or tensors. Candidate-only and production gates remain; no production
retry policy exists.

Public artifacts:

- `data/prompts/m31_intervention_manifest.json`
- `reports/telemetry/hf_m31_intervention_run_summary.json`
- `reports/telemetry/hf_m31_intervention_evaluation.json`
