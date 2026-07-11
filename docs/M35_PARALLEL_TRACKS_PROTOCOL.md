# M35 parallel tracks protocol (A router / B detector / C shadow)

Operator decision (steer commit `c3c67fa`): tracks A, B, C run in parallel.
This protocol incorporates an external design consult (OpenAI Codex,
gpt-5.6-terra, resumed session) and is committed BEFORE any M35 manifest,
task generation, or capture. The M32/M33/M34 decision sets are spent.

## Shared A/B capture campaign — split topology

Four role-disjoint splits, assigned by a stable task key that includes
family, generator/template, operand regime, and seed:

- **D (detector development)** — fit features, normalization, per-category
  calibration, thresholds, and ALL model selection for track B.
- **R (router calibration)** — with B's selected detectors frozen, fit
  category competence priors and the track-A controller here and only here.
- **B-test (sealed detector test)** — evaluate B only; its scores/outcomes
  never tune A.
- **A-test (sealed router test)** — evaluate A only; detector, router, and
  competence priors are frozen before it is opened.

Rules:

- Splits are disjoint at the generator/template and operand-bucket level,
  not merely row-randomized (family indicators and repeated arithmetic
  structure would otherwise leak).
- A's detector components train only on D; A's competence estimates only on
  R; B-test and A-test are separate single-read holdouts.
- Leave-one-family-out (LOFO) analyses for B refit the ENTIRE detector
  pipeline excluding the withheld family — including normalization and
  category encoding; the withheld family's indicator maps to `unknown`.
- Effective sample size is triggered/eligible tasks, not captured tasks.
  Allocation oversamples mixed regimes (where routing is identifiable) and
  spends minimal mass on near-total-failure cells. Cell-level results are
  descriptive; only preregistered aggregate comparisons are confirmatory.

## Task families (regimes are predictions, to be measured not assumed)

1. Multi-digit addition, controlled carry-chain length — predicted high
   success; isolates carry propagation.
2. Multi-digit subtraction with borrowing cascades — predicted mixed;
   state-reversal/borrow structure.
3. Multiplication bands stratified by digit width and carry density —
   mixed; preserves the M33-relevant regime.
4. Exact division constructed as quotient x divisor — predicted mixed/high;
   inverse-operation structure and remainder handling.
5. `a*b+c` with controlled relative magnitudes — near-total failure per
   M34; compositional arithmetic.
6. Modular arithmetic (`a*b mod m`) — speculative mixed/low; algorithmic
   rule tracking rather than place-value computation.

Digit count is a covariate within a family, never a separate "family".

## Track A claim rules (preregistered in the A manifest)

- **A-H1 (fixed budget):** at a predeclared tool-call fraction, the
  hierarchical router beats BOTH count-matched random routing AND a global
  telemetry threshold on verified success; paired bootstrap lower CI bounds
  strictly above zero.
- **A-H2 (fixed success, non-inferiority):** vs tool-on-every-task the
  router is non-inferior in verified success within a predeclared margin
  while using fewer tool calls; paired lower CI for the call reduction
  strictly above zero AND lower CI for the success difference above the
  non-inferiority bound. Tool-on-every-task cannot satisfy A-H2 by
  construction.
- Freeze in the manifest: the budget, the non-inferiority margin, family
  weights, and whether "tool call" counts attempted or completed
  invocations.

## Track B claim rules (preregistered in the B manifest)

- Primary claim is **LOFO**: for each withheld family, the transfer detector
  (trained on the remaining families) is evaluated on the withheld family's
  sealed rows. LOFO establishes robustness across the named withheld
  families under this generator/prompt/model/telemetry/outcome regime — it
  does NOT establish transfer to new operations, new base-rate regimes,
  changed prompting/decoding, or other models, and no such claim is made.
- Pooled held-out performance is secondary and is not transfer evidence.
- Comparators: global detector (M30 recipe refit on D), per-category
  detectors, hierarchical detector. No claim of model-independent telemetry.

## Track C — M33 policy in supervisor shadow mode (advisory-only)

Instrumentation requirements (the three standard failures, inverted):

1. Log the eligible denominator and abstentions, not just recommendations.
2. Version everything: policy, detector, feature schema, calibration, and
   decision-time configuration (config hash in every rollup).
3. Never mix advisory recommendations with downstream supervisor actions or
   tool outcomes — shadow must stay causally interpretable.

Aggregate-only rollup schema, keyed by time window x workload class x
inferred family/regime x policy version x score band:

- eligible originals; excluded/unknown-family originals; recommendations;
  advised tool-call rate;
- original verified outcome where available; recommendation/outcome
  contingency counts (for BOTH recommended and not-recommended cases);
  final supervisor disposition where available;
- actual tool invocations (independent of advice, clearly separated);
- verifier availability/failure counts; latency and tool-cost totals;
- policy/detector/calibration/feature-schema/model versions + config hash.

No production action or threshold unlock without reviewed audit criteria.

## Sequencing

1. This protocol commit.
2. Track C implementation starts immediately (CPU, supervisor code).
3. A/B campaign manifest(s) preregistered next (family generators, split
   assignment rules, allocation counts, claim rules, seeds), then one
   serialized GPU capture campaign, then B fitting on D, router on R, sealed
   reads of B-test and A-test in that order.
4. Privacy/hygiene unchanged: aggregate-only public artifacts;
   check_commit_safe on everything staged under reports/; production gated.
