# STEER ADDENDUM — Jacobian-fit corpus conditionality, seed-null, and atlas-transfer gates

Date: 2026-07-25
Parent remote head: `6f9ca38a8bd5b7921502b451031f2063e29e1b82`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and all later
cumulative protocol corrections. It preserves every privacy, sealed-data,
provenance, verifier, exact-set, derivative, resource, retry, intervention, and
production-gating rule. It does not constitute Q35Q admission, authorize weight
staging or GPU use, reopen M38E, permit Agents-A1 capture, or establish any
scientific result inside this repository.

## Primary external evidence

The public campaign `praxagent/jacobian-lens-research-202607a` froze a
corpus-dependence experiment before fitting at commit
`4b4f7d5d2236f0b4c2a238edcaa9be6d12792870` and reported results at immutable
commit `a13382fa5b3b7a42a014befc06567513a9dadb9a`.

The experiment fit three Jacobian lenses per model under one recipe:

1. WikiText sample A, seed 0;
2. a different WikiText sample B, seed 1, used as a same-corpus finite-sample
   seed null; and
3. CodeParrot, seed 0, used as the cross-corpus arm.

The reported models were GPT-2 small, Gemma-3-270M, and Qwen3.5-0.8B. Fits used
100 prompts per arm, length matched to a 128-token cap, with a shared-vocabulary
probe. The frozen analysis compared fitted boundary movement, whole-map distance
using an off-diagonal-profile CKA construction, and a workspace-band statistic.

The reported same-corpus refits reproduced the same fitted boundary layers in
all three models, with map distances approximately `0.0002` to `0.0005`.
Changing from WikiText to code produced map distances approximately 87 to 292
times that seed null. Fitted boundaries moved by 10 layers on the 17-layer Gemma
model and by 15 layers on the 23-layer Qwen model. GPT-2 retained its fitted
boundaries while its band statistic weakened. Qwen retained nearly the same
band statistic while its fitted boundaries moved substantially.

The source therefore reports two separable forms of corpus dependence:

- boundary or map relocation with little change in one scalar band statistic;
- band-strength change without boundary relocation.

This is external author-supplied evidence. It has not been independently
reproduced in jLens. The result is limited to three sub-1B models, one prose-to-
code contrast, one fitting recipe, 100 prompts per fit, and short sequences. It
does not establish the magnitude or direction of corpus dependence at 4B, 35B,
122B, or 397B scale, on MoE routes, on multimodal or tool trajectories, or under
quantized and production-serving runtimes.

## Binding interpretation

The new evidence changes a scientific claim boundary not fully captured by
merely recording the fit corpus as metadata:

> A fitted Jacobian-lens depth map, boundary, band, direction, rank, or atlas is
> a property of the admitted model and estimator as measured over a specified
> fitting distribution. It is not a model-only property unless cross-corpus
> invariance is prospectively demonstrated against a same-corpus seed null.

Consequently, a reproducible fit at a fixed corpus does not establish corpus
robustness. A stable scalar summary does not establish stable map geometry or
boundary placement. A stable boundary does not establish stable band strength,
readout quality, monitor value, or causal effect.

Absent admitted invariance evidence, use corpus-conditioned language such as:

- `WikiText-fitted boundary`;
- `code-trajectory-fitted map`;
- `tool-trajectory-conditioned lens`;
- `model-by-corpus estimator`.

Do not use unqualified language such as `the model's workspace boundary`, `the
intrinsic phase transition`, `the canonical workspace band`, or `the model's
Jacobian atlas`.

## Fit-population identity gate

Every future Jacobian-lens fit must freeze, hash, and report at least:

- source dataset and immutable revision or exact example manifest;
- inclusion, exclusion, filtering, deduplication, and contamination rules;
- language, modality, task family, domain, and provenance composition;
- prompt, tool, observation, reasoning, and answer-message boundaries;
- prefill versus decode stage and token-position policy;
- sequence-length distribution, truncation, packing, padding, and masking;
- tokenizer and processor revision;
- ordering, sharding, seed, and per-shard example identities;
- model, checkpoint, quantization, runtime, attention, cache, route, topology,
  and serving identities;
- estimator implementation, source and target layers, target-position policy,
  accumulation precision, merge rule, and artifact schema.

A changed fitting population defines a separate lens artifact even when all
model and estimator code identities are unchanged.

## Same-corpus seed-null gate

Any claim that a boundary, map, band, direction, rank, feature, or layer is
stable must include a prospectively frozen same-corpus refit null where
technically feasible.

The null must vary ordinary finite-sample factors without changing the named
population, including at least independent example sampling and fit seed. It
must report the complete distribution of the same metrics used for the claimed
cross-condition effect.

A cross-corpus difference is interpretable only relative to this null. Comparing
one corpus fit with one different-corpus fit against zero is insufficient.
Identical same-corpus boundaries do not make the null undefined if other frozen
map-distance or statistic metrics retain nonzero resolution. If every frozen
metric has no measurement resolution, report the comparison as
`underresolved`, not `robust`.

## Cross-corpus sensitivity gate

Before assigning model-level meaning to fitted depth boundaries, workspace
bands, layer phases, directions, or atlas geometry, run prospectively frozen
cross-corpus sensitivity tests covering the populations material to the claim.
Compatible future studies must include, where available:

1. a pretraining-like natural-text corpus;
2. code or structured-symbolic text;
3. agent reasoning and visible trajectory text;
4. tool calls, tool observations, and verifier feedback;
5. successful and failed episodes drawn without sealed-label leakage;
6. relevant languages and modalities;
7. prefill and decode populations as separately admitted stages; and
8. deployment-like length and position distributions.

Report separately:

- whole-map distance;
- boundary movement;
- band or block strength;
- direction and subspace similarity;
- rank and conditioning;
- readout or monitor discrimination;
- calibration and structural coherence where probability language is used;
- causal or intervention effects where separately authorized;
- full resource and storage cost.

No single scalar statistic may substitute for map, boundary, and functional
comparisons. A stable band statistic with relocated boundaries is not corpus
robustness. A stable map geometry with degraded objective monitor value is not
operational robustness.

## Population matching and leakage boundary

Fitting-corpus matching must not consume sealed outcomes, future tool results,
post-decision labels, generated answers unavailable at the monitored boundary,
or evaluation examples selected after viewing sealed performance.

The fit population, corpus-mixture weights, layer choices, map metric,
boundary-finding rule, stability threshold, and transfer decision must be chosen
using training and development data only. Outer validation, certification, and
sealed evaluation remain disjoint.

A correctness-balanced fitting corpus is a label-conditioned estimator and must
be reported as such. A correct-only trajectory fit cannot establish natural
population geometry. A fit on completed transcripts cannot establish prefix-only
or pre-action monitoring without a separately fitted and validated prefix
population.

## Atlas and layer-transfer gate

No boundary, phase label, source-layer set, target layer, direction, subspace,
threshold, calibration, or workspace band from a public atlas may be imported
into Q35Q or Agents-A1 as a model-intrinsic constant.

Transfer requires a prospectively frozen experiment that includes:

- exact source and target artifact admission;
- same-corpus refit nulls on both artifacts;
- matched and deliberately shifted corpus conditions;
- layer-alignment rules chosen without sealed outcomes;
- map, boundary, direction, readout, and objective-outcome transfer metrics;
- a no-transfer fallback.

If corpus movement exceeds the admitted same-corpus null for a claimed object,
that object is corpus-specific unless an independently frozen invariant
representation is demonstrated. Post-hoc realignment after sealed evaluation is
prohibited.

## Monitor and intervention claim boundary

Corpus-dependent lens geometry is not by itself evidence of:

- objective correctness or error awareness;
- semantic or global workspace identity;
- planning, intent, evaluator awareness, or deception;
- recoverability, tool safety, or permission compliance;
- safe early exit, retry, repair, truncation, routing, steering, or production
  control.

A corpus-matched lens may improve a monitor because it better represents the
observed domain. That does not establish a universal latent variable or a
model-intrinsic workspace. Passive sealed monitor value, causal effects, and
policy utility remain separate claims with separate admissions.

## Agents-A1 scaling consequence

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q production-path provenance, strict loading, forward parity,
   activation-VJP parity, activation-JVP parity, finite-difference parity, and
   deterministic replay.
2. Separately admit Agents-A1-4B and establish deterministic checks, external
   verifiers, logits, confidence, visible trajectory, memory, program-state, and
   simple hidden-state baselines.
3. Fit Agents-A1-4B Jacobian lenses only after freezing at least one
   pretraining-like corpus, one agent/tool-trajectory corpus, and their
   same-corpus seed nulls.
4. Evaluate corpus movement in map geometry, boundaries, readout value, and
   objective-error prediction separately.
5. Treat layer bands, directions, and thresholds as corpus-specific when their
   movement exceeds the seed null; do not repair transfer after sealed outcomes.
6. Separately admit Agents-A1-35B hidden-state, cache, router, expert-path,
   quantized, topology, and serving capture.
7. Repeat corpus-sensitivity fitting on the 35B checkpoint rather than importing
   4B, Qwen-base, WikiText, code, or public-atlas coordinates.
8. Establish nominal and functional route, occupancy, ancestry, transition,
   token-frequency, trajectory-phase, and route-regret comparators.
9. Require router and Jacobian features to add sealed objective-outcome value
   beyond the complete external, 4B, raw-state, trajectory, corpus-aware, and
   route-aware comparator stack.
10. Keep projection, ablation, activation steering, early exit, retry, repair,
    truncation, forced routing, router adaptation, and production enforcement
    separately gated.

This adds corpus sensitivity to future fit and transfer studies. It does not
change the active Q35Q engineering milestone and authorizes no new execution.

## Current engineering blocker remains unchanged

The active milestone remains complete production-path Q35Q provenance and
runtime admission:

1. verify frozen upstream-wheel and installed-distribution bytes in the same
   controlled subprocess;
2. reject shadow packages, editable installs, pre-imported modules, and in-memory
   monkeypatching;
3. execute the complete adversarial provenance conjunction in the target runtime;
4. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple;
5. bind the actual GPTQModel/Defuser loader and its complete live-object source
   closure;
6. run the strict synthetic Qwen3.5-MoE loading fixture;
7. prove one-time packed-tensor consumption and exact expert/fusion ordering;
8. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity; and
9. complete Phase-0 admission before weight staging or GPU authorization.

## Established by this correction

- Fit corpus is now a binding scientific identity, not merely provenance
  metadata.
- Model-only boundary, phase, band, direction, and atlas claims require
  cross-corpus invariance against a same-corpus seed null.
- Map geometry, boundary placement, scalar band strength, readout value, and
  policy utility must be reported separately.
- Public atlas coordinates cannot transfer to Q35Q or Agents-A1 without a
  prospective corpus-sensitive transfer study.
- No privacy, sealed-data, verifier, provenance, derivative, intervention,
  resource, or production gate is weakened.

## Still unproven

- Independent reproduction of the external corpus-dependence campaign.
- Corpus effects at larger scales or on MoE, multimodal, long-context, and
  production-serving models.
- The corpus mixture that best represents natural Agents-A1 deployment.
- Corpus-invariant Jacobian boundaries, directions, workspace bands, or
  correctness monitors.
- Transfer of any public Jacobian lens to Q35Q, Agents-A1-4B, or Agents-A1-35B.
- Q35Q runtime admission, strict tensor consumption, expert ordering, forward
  parity, or derivative parity.
- Safe early exit, retry, repair, truncation, forced routing, activation
  steering, or production deployment.
