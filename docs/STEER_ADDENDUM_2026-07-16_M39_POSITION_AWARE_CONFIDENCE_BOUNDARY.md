# STEER ADDENDUM — M39 position-aware confidence comparator and control boundary

Status: **binding design amendment; not launch authorization.**

This addendum amends `docs/M39_FORWARD_ONLY_COMPARATOR_PREREG.md` and the
binding metacognition amendment before any M39 outcome-bearing capture. It does
not authorize scientific capture, alter M38E or Q35Q, weaken any frozen
threshold, permit held-out or sealed-data reuse, or relax verifier, provenance,
privacy, parity, power, resource, commit-safety, or production gates.

## Evidence and scope

`Post-Training Shifts Confidence: A Three-Stage Analysis of How SFT, RL, and
OPD Shape Pre-, Intra-, and Post-CoT Calibration` (arXiv:2607.13753v1) reports
that confidence reliability can differ before reasoning, across relative
positions within a reasoning trace, and after completion, and that the useful
region can depend on the post-training method. This is relevant evidence that a
single whole-trace confidence summary may be an incomplete nuisance comparator.
It does not establish the result on Agents-A1, completed-error prediction, safe
stopping, or production control.

The public repository linked from the paper was a one-commit README placeholder
at audit time (`EIT-NLP/Post-Training-Calibration`, commit
`55d08b6d8aa93dd0e640ae4f7ee5af3b369c4656`). Therefore M39 may not claim to
reproduce `PosConf`, borrow an unverified implementation, or use the paper's
reported gains as an Agents-A1 power prior. The requirement below is a
repository-specific conservative comparator hardening, not adoption of the
external method.

## Binding three-stage comparator structure

The M39 launch amendment must preserve three separately identified stages:

1. the already-required isolated pre-solve behavioral self-assessment;
2. a position-aware autoregressive confidence block reduced from the frozen
   primary generation after it completes;
3. the already-required isolated post-solve behavioral self-assessment over the
   sealed answer.

These stages may not be pooled into one score. The launch amendment must freeze
all formulas, model/runtime identities, context construction, token budgets,
sampling settings, parsing, missingness, calibration, and compute accounting
before capture.

## Position-aware autoregressive confidence block

The nuisance baseline must include a minimal position-aware confidence block
unless a pre-capture parity/resource smoke records
`m39_position_confidence_unsupported`.

The launch amendment must freeze:

- the exact confidence primitive available on the realized generated-token path,
  such as sampled-token log probability, predictive entropy, or a logit margin;
- the exact tensor location, precision, normalization, and relationship to the
  token actually emitted;
- exactly four equal-count relative decode-position bins, ordered from earliest
  to latest, with deterministic handling when the completion has fewer than four
  eligible tokens;
- a minimal fixed reduction set per bin and for the full trace, including exact
  count and finite-value checks; no post-outcome feature expansion is allowed;
- whether a single preregistered trend statistic is included and its exact
  formula;
- exclusions for special, tool, padding, control, or non-generated tokens;
- invalid-output and missing-confidence behavior;
- on-device or in-process reduction proving that raw token-level confidence
  trajectories do not persist.

Relative bins are defined only over eligible autoregressive decode tokens from
the frozen primary answer. They may not use verifier outcomes, accepted answers,
failure types, hidden states, routes, future tokens unavailable at the measured
position, or any output-versus-gold quantity.

The block is measured after the answer is complete and before the verifier
verdict is exposed. It is an observational task-level feature block. It may not
change generation, stop early, retry, select a tool, alter a route, or allocate
compute during M39.

## Required nested comparison

The locked M39 comparison hierarchy must distinguish:

- nuisance without position-aware confidence;
- nuisance with the frozen position-aware confidence block;
- nuisance plus behavioral metacognition;
- nuisance plus behavioral metacognition plus router telemetry;
- each internal block added to the strongest applicable preceding baseline.

A claimed internal increment must survive the strongest preregistered baseline
that includes supported position-aware confidence. If the enlarged comparison
set cannot meet the prospective power and class-balance rules, the outcome is
`underpowered/inconclusive`; the comparator may not be deleted after outcomes
are observed.

All calibration, normalization, residualization, feature selection, and trend
fitting occur inside training folds only. Source-lineage grouping and every
existing leakage control remain binding.

## Model and post-training specificity

Confidence reliability must be treated as checkpoint- and runtime-specific.
M39 may not pool or transfer calibration parameters, relative-position effects,
thresholds, or missingness rules across base, SFT, RL, distilled, quantized, or
serving variants. Agents-A1 must be evaluated under its exact admitted checkpoint
and runtime identity.

A result from the position-aware block may establish only an observational
confidence comparator for that exact M39 population. It does not establish a
safe early-exit rule, truncation rule, aggregation policy, retry policy, or tool
router.

## Scoped outcomes

Permitted additional scoped outcomes are:

- `m39_position_confidence_supported`;
- `m39_position_confidence_unsupported`;
- `m39_internal_increment_beyond_position_confidence_established`;
- `m39_internal_increment_beyond_position_confidence_not_established`.

None authorizes control or production use.

## Privacy and completion boundary

Raw tasks, prompts, answers, self-assessment text, token IDs, token-level
logits, log probabilities, entropies, margins, confidence trajectories, routes,
hidden states, feature vectors, split labels, predictions, verifier labels, and
per-example readouts remain private and uncommitted. Only aggregate protocol,
parity, resource, privacy, and final statistical summaries may be committed.

The research program remains incomplete. This amendment strengthens the M39
nuisance and behavioral comparator boundary; it does not establish a Jacobian
Lens, an Agents-A1 error predictor, a metacognitive controller, safe early exit,
or production utility.
