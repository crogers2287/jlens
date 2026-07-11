# M32 — Structured repair operators (RESULT: model-side repair falsified on the proxy)

M32 asked whether structured prompting operators (independent deliberate
re-solve, checker-guided repair, two-stage diagnose-then-repair) rescue more
telemetry-triggered failures than plain temperature-0.7 resampling, and whether
a telemetry-gated repair policy beats no-repair and a count-matched random
trigger. Preregistration: `data/prompts/m32_repair_manifest.json` and
`docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`; reactivation commit `1d0f548`.

## Design (frozen before capture)

- 384 predeclared integer-arithmetic tasks, six bands x 64, operands disjoint
  from M29/M30/M31; no post-hoc selection.
- Frozen M30 full-telemetry trigger at threshold 0.5; verifier-first structured
  bundle (a passing original is never replaced — assertion enforced in code).
- Six policies: no_repair, always_structured_bundle,
  random_trigger_structured_bundle, telemetry_trigger_structured_bundle,
  telemetry_trigger_resample_only, telemetry_trigger_tool_upper_bound
  (deterministic ceiling, excluded from H1/H2 by rule).
- H1: bundle rescue > resample rescue on triggered original failures (paired
  bootstrap 95% CI strictly > 0). H2: telemetry-gated bundle beats BOTH
  no_repair AND random trigger (both CIs strictly > 0).
- Single interrupted-and-resumed capture (power outage mid `diagnose_stage_b`);
  the idempotent capture driver validated and skipped existing captures, so all
  phases come from identical frozen prompts and settings.

## Results (`reports/telemetry/hf_m32_repair_evaluation.json`)

- Originals: 181 pass / 203 fail. Frozen trigger reproduced in-band:
  precision .900, recall .887, 200 triggers, 20 false alarms.
- **H1 = repair_not_established** (and directionally reversed): on the 180
  correctly-triggered failures, bundle rescue .0056 vs resample .0333,
  delta -.0278, 95% CI [-.0556, 0].
- **H2 = not_established**: telemetry-gated bundle vs no_repair +.0026,
  CI [0, .0078]; identical vs random trigger. Not strictly positive.
- Operator candidate pass rates on failing originals: independent_deliberate
  .000, checker_guided_repair .000, diagnose_then_repair .0049 (1 unique
  rescue), resample_t07 .0394 (8 unique rescues). The structured operators are
  weaker than resampling at ~7x the decode tokens (~126-128 vs ~18 per
  candidate).
- Verifier-first arms introduced zero errors (stop condition held).
  telemetry_trigger_resample_only rescued 6 but introduced 7 (net negative
  without a verifier gate).
- **Deterministic tool ceiling is large**: .940 verified success vs .471
  no_repair (180/200 triggered tasks rescued at zero decode tokens).
- Exploratory candidate reranking by telemetry: picks a passing candidate 0% of
  the time given one exists (distribution-shift caveat recorded in artifact).

## Secondary band descriptives (`reports/telemetry/hf_m32_band_descriptives.json`)

Required descriptively by the post-M32P steer; non-confirmatory. Produced by
`src/m32_band_descriptives.py` (aggregate-only, no-text guard, tests in
`tests/test_m32_band_descriptives.py`). Trigger precision/recall by band:
band_2 .83/.63, band_3 .64/.77, band_4 1.0/.89, band_5 .86/.95, band_6
1.0/.95 (band_1 had 1 failure, 0 triggers). Consistent with the M32P frontier
finding: the detector is weakest mid-frontier, strongest where failure is
near-certain.

## Interpretation

Structured prompting does not repair this model's arithmetic failures; it is
strictly worse than resampling on the triggered-failure population while
costing ~7x the tokens. Combined with M31 (resample rescue ~4.5%) and M32P
(expert rerouting at random-perturbation rates), model-side self-correction on
the proxy is now falsified across three independent operator families. The
value of the telemetry trigger is routing to *deterministic tools*: precision
.90 gating of a .94-ceiling tool arm.

An external consult (OpenAI Codex, gpt-5.6-terra) reviewed the design before
evaluation; its main concerns (error-vs-repairability estimand gap,
score-stratified analysis) are answered descriptively by the band artifact and
are moot for uplift analysis here because the structured operators pass at ~0%.

## Branch decision (per `docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`)

"Model-side repair not improved but the deterministic-tool ceiling is large" →
**M33 = telemetry-gated tool routing**, with the remaining milestone reserved
for detector transfer/robustness. No claim of model self-correction is made.

## Gating

Aggregate-only public artifacts (`check_commit_safe` passed); 9 private
recovery traces retained locally and intentionally not committed; per-task
labels/predictions/text never public. Candidate-only; production remains
gated; no weight training authorized.
