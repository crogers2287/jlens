# Steering addendum — MoE causal-localization and coalition gate

Date: 2026-07-14

Status: **binding program-control addendum; no scientific capture authorized**.

This addendum incorporates `steer.md`, `CODEX_AUTOSTEER.md`, the frozen M38E
protocol, the amended M39 preregistration draft, and every existing sealed-data,
verifier, privacy, provenance, exact-set, cap-escalation, power, multiplicity,
retry, production, repository-hygiene, cross-milestone independence,
artifact-admission, surrogate-gate, and stop rule. Nothing here changes the
active M38E process, row set, task family, band, seed, cap, threshold, verifier,
eligibility rule, comparator gate, or production gate. M39 remains forward-only,
observation-only, design-only, and capture-prohibited until its own launch
amendment passes every existing gate.

## External evidence and bounded interpretation

`Expert-Aware Causal Tracing of Factual Recall in Sparse MoE Language Models`
(arXiv:2606.03780) reports a two-stage intervention protocol on
Qwen3-30B-A3B-Base and Mixtral-8x7B-v0.1:

1. select a candidate MoE layer using clean-versus-corrupted block-output
   restoration on discovery cases;
2. evaluate the fixed layer on held-out cases;
3. estimate routed expert updates by ablation difference under the original
   routing decision;
4. patch clean-minus-corrupted expert updates into the corrupted run; and
5. compare the selected expert with other clean-active experts from the same
   layer and prompt.

The paper finds a held-out singleton-expert localization on Qwen3-30B-A3B-Base,
but not on Mixtral. For Mixtral, routed multi-expert coalition patches recover
the validated layer-level signal. The binding methodological lesson is therefore:

- block-level rescue is not expert-level evidence;
- router selection is not causal evidence;
- singleton-expert localization is not a universal MoE property; and
- coalition recovery must be tested before concluding that a routed behavior is
  localized to one expert.

This evidence concerns filtered single-token factual-recall diagnostics. It does
not establish completed-error prediction, safe stopping, correction, semantic
expert identity, cross-model expert homology, Agents-A1 transfer, or production
utility.

Primary reference inspected:

- `https://arxiv.org/abs/2606.03780`

## Binding placement in the Agents-A1 scaling sequence

This evidence does not alter M38E or M39 and does not authorize intervention on
Agents-A1 35B.

A causal-localization study may be designed only after all of the following are
true:

1. M38E is finalized honestly under its frozen rules;
2. M39 clears every forward-only predictive-increment gate on its independent
   population;
3. the separate open-MoE instrumentation surrogate is immutably selected,
   admitted, and passes its parity, dispatch, contribution, gradient,
   finite-difference, privacy, memory, and runtime gates; and
4. a new intervention-specific preregistration is committed before any
   outcome-bearing causal row exists.

The causal-localization study is a separate mechanistic gate. It cannot satisfy
M39 power, calibration, predictive-increment, replication, or class-balance
requirements. M38E or M39 rows, outcomes, feature rankings, selected layers,
selected experts, or error families may not be reused to choose causal targets.

## Required causal-localization protocol

Any later confirmatory MoE causal-localization study must freeze all of the
following before capture.

### 1. Independent population and contrast

- Use a fresh population disjoint from M38E and M39 by task, source lineage,
  paraphrase lineage, generator lineage, seed, and model-output lineage.
- Freeze the exact clean condition, corruption or intervention condition,
  target contrast, accepted population, exclusion rules, seeds, and expected row
  set.
- Gold-answer, true-versus-foil, verifier, or corruption-derived quantities are
  labels or intervention targets only. They may not leak into observational
  feature selection or M39 predictors.

### 2. Layer-level localization before expert claims

- Run a prospective layer sweep only on the frozen discovery split.
- Select layers using the exact preregistered restoration/rescue statistic.
- Evaluate selected layers as fixed hypotheses on an untouched validation or
  held-out split.
- A validated MoE-block rescue establishes only aggregate routed-block
  involvement. It does not identify a specific expert.

### 3. Fixed-routing expert contribution intervention

- Define the exact routed expert update tensor, hook point, residual-combination
  convention, shared-expert treatment, dtype, accumulation precision, and token
  position before capture.
- Estimate expert contribution by an explicit ablation or equivalent
  intervention under the original routing decision.
- Do not silently reroute to a replacement expert, renormalize remaining router
  weights, change top-k, alter dispatch, or combine shared-expert terms unless the
  preregistration defines that separate intervention.
- Enabled-path and disabled-path parity, dispatch identity, finite-value,
  determinism, cleanup, and privacy checks remain mandatory.

### 4. Singleton specificity controls

A singleton-expert claim requires all of the following:

- prospective recurrence or support requirements that prevent selection from one
  or two favorable cases;
- discovery-only expert selection;
- held-out comparison against other clean-active experts from the same prompt and
  layer;
- matched routing-weight, matched contribution-norm, and equal-norm controls where
  technically feasible;
- multiplicity correction across searched layers, experts, positions, contrasts,
  and endpoints; and
- a prespecified nontrivial minimum effect, not merely a point estimate above
  zero.

Failure of specificity means the singleton claim fails even if the aggregate
MoE-block patch rescues the target.

### 5. Mandatory coalition analysis

Every confirmatory study must preregister coalition checks rather than treating
them as optional post-hoc repairs. At minimum, define and test:

- the clean-routed top-k coalition;
- the corrupted/noised-routed top-k coalition;
- the union of clean and corrupted/noised routed experts; and
- a matched-size active-expert control coalition.

Coalition membership, weight treatment, duplicate handling, shared-expert
handling, normalization, and patch composition must be frozen. If a coalition
recovers a layer-level effect while no singleton clears specificity, the result
is `coalition-localized / singleton-not-established`, not a single-expert result.

### 6. Model-specific claim boundary

- Expert numbers, layers, routes, or coalitions are model- and revision-specific.
- No cross-model expert identity, semantic homology, or architecture-level rule
  may be inferred from one checkpoint.
- A positive open-MoE surrogate result does not establish Agents-A1 35B transfer.
- A later Agents-A1 35B intervention requires its own immutable runtime,
  high-memory technical feasibility, independent preregistration, rollback plan,
  and safety approval.

### 7. Privacy and repository boundary

Raw prompts, clean/corrupted outputs, gold contrasts, token identities, hidden
states, expert outputs, patch vectors, route identities, per-example rescue
scores, split assignments, and intervention traces remain private and
uncommitted. Public reporting is aggregate-only and must pass the existing
leakage, inversion, provenance, cleanup, and commit-safety audits.

## Required outcomes

The causal gate must use explicit fail-closed outcomes:

- `causal-localization-blocked` when parity, hooks, provenance, privacy, resource,
  dispatch, or intervention identity cannot be verified;
- `block-rescue-not-established` when the held-out MoE-block effect fails;
- `singleton-not-established` when a selected expert fails held-out specificity;
- `coalition-localized / singleton-not-established` when only a routed coalition
  recovers the validated block effect;
- `model-specific-causal-localization-established` only when the exact frozen
  held-out intervention and specificity decision table passes; and
- `exploratory-only` for any analysis selected or revised after outcomes are
  observed.

None of these outcomes establishes completed-error prediction, safe truncation,
early exit, causal correction, routing intervention utility, activation steering,
or production value. Those require separate predictive, causal, safety, utility,
privacy, rollback, and locked-held-out gates.

## Current claim boundary

- M38E remains incomplete and has no finalized scientific result.
- M39 remains design-only, forward-only, and capture-prohibited.
- No observational router, load, contribution, hidden-state, geometry, path,
  semantic-workspace, or Jacobian feature has demonstrated incremental
  completed-error prediction on Agents-A1.
- No MoE block, singleton expert, or expert coalition has been causally localized
  for an Agents-A1 behavior.
- No Jacobian Lens has been fitted or validated on Agents-A1.
- Full Agents-A1 35B backward feasibility remains unproven.
- No safe truncation, early exit, correction, intervention, steering, or
  production utility is established.
- The research program is not complete.