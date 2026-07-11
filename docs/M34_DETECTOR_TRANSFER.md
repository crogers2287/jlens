# M34 — Second-category detector transfer (RESULT: transfer_failed)

M34 asked whether the frozen M30 detector transfers from pure multiplication
to mixed `a*b + c` expressions, and whether telemetry-gated tool routing
remains useful and efficient under that shift. Preregistration: manifest
commit `7300b20` (before any generation or capture); implementation `5220b32`;
steer `7b2e462`. Final milestone of the bounded autoloop.

## Design (frozen before capture)

- 384 fresh `a*b + c` tasks over the six M32/M33 multiplication bands with a
  per-band additive term c in [2, 99]; (a, b) tuples disjoint from everything
  M29-M33 generate (regression-tested); seed `m34-transfer-v1`.
- One GPU phase: greedy 64-token originals. Frozen M30 classifier, threshold
  0.5, no refit/recalibration/tuning on M34 data.
- T1 transfer classification preregistered: maintained (precision >= .80 AND
  recall >= .75), degraded (below either bound but H1 useful), failed
  (otherwise). No reproduction gate — degradation is the measurement.
- H1/H2 routing rules identical to M33.

## Results (`reports/telemetry/hf_m34_transfer_evaluation.json`)

- The category shift collapsed the model: **18 pass / 366 fail (95.3% failure
  rate)** vs ~53-57% on pure multiplication. Even the easiest band (2-digit x
  1-digit + c) failed 57/64.
- Frozen trigger on the shifted set: precision .966 (trivially high at a 95%
  base failure rate), **recall .612** (232 triggers; misses 39% of failures).
  Per-band recall is structureless relative to the multiplication pattern
  (band_1 .49, band_4 .44, band_5 .38, band_6 .81).
- **T1 = transfer_failed**: recall is far below .75, and H1 is not useful.
- H1 not established: telemetry routing .630 vs random routing .617
  (delta +.013, CI [-.060, .083]). At a 95% base failure rate any routing
  strategy hits failures — the detector has no selection advantage. Vs
  no-repair the delta is +.583 (CI [.534, .633]) but the claim rule requires
  beating random too.
- H2 not established: uplift retention .612 (CI [.560, .665]) below .80;
  invocation fraction .604 also above the .60 bound.
- Zero errors introduced in any arm (verifier-first held).
- One float32 artifact surfaced and was fixed during evaluation: `top_k_mass`
  1.0000001 exceeded the frozen schema's maximum of 1; clamped at capture
  write and telemetry read (no-op for all previously validated milestones;
  commits `f747193`, `c84e054`).

## Interpretation

The frozen detector does not transfer to the shifted category — but the
failure mode is informative. The shift did not merely miscalibrate the
detector; it moved the task so far outside the model's competence region
(95% failure) that *selective* routing is pointless there: tool-on-every-task
is the correct policy, and no failure predictor — however good — can add
value when nearly everything fails. Telemetry gating earns its keep only in
the mixed-competence regime (M33: ~56% failure, retention .889); category
shifts require either detector retraining on the new distribution or a
category-level competence prior deciding when to bypass the gate entirely.
This completes the M32P arc: the M30 signal is real but distribution-bound.

## Gating

Aggregate-only public artifacts (check_commit_safe passed); operands/prompts/
outputs/per-task predictions private and gitignored. Candidate-only;
production remains gated; no weight training; no training data from tool
outputs. The bounded autoloop STOPS here per steer.md; any further milestone
requires a fresh operator decision.
