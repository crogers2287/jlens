# Steering Addendum — Confidence Coherence and Probability-Semantics Gates

Date: 2026-07-24

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `baa57574193e9044dd82c72f4ee78da72eb147f0`

## Scope

This addendum applies to every future confidence, uncertainty, correctness,
safety, recoverability, route-regret, early-exit, truncation, retry, escalation,
abstention, verifier, hidden-state, router-telemetry, sparse-feature,
transcoder, semantic-workspace, directional-JVP, Jacobian-lens, or Agents-A1
monitor claim.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No weight staging, tensor-payload retrieval,
model execution, GPU execution, hidden-state capture, router capture, JVP, VJP,
Jacobian fitting, sealed scientific evaluation, intervention, or production use
is authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-set, exact-gradient,
parity, resource, cleanup, commit-safety, comparator, nuisance-control,
multiplicity, production-gating, and stop rule remains binding.

GitHub currently reports this repository as public. This document contains only
aggregate public-source program-control information. It does not authorize
committing prompts, outputs, token IDs, per-task predictions, verifier labels,
hidden states, router arrays, expert traces, Jacobians, gradients, model
weights, tensor payloads, caches, credentials, local paths, or private logs.

## New external evidence and narrow interpretation

Matta, Naphade, and Zou, “Rethinking Uncertainty Evaluation in Large Language
Models,” arXiv `2607.19367v1`, distinguish ordinary calibration from the
conditions required to interpret a confidence estimator as a coherent
probability assignment.

The paper organizes evaluation along three axes — structural coherence,
faithfulness, and usefulness — and introduces C1 metrics for those axes. The
authors report that commonly used logit-based, verbal, and self-consistency
estimators can appear calibrated while violating basic probabilistic
relationships. Their headline result reports lower confidence on the logically
easier member of an entailment-related pair in 31 percent of evaluated cases.
They further report that interventions reducing RMS calibration error can leave
structural violations unchanged, and that RLHF or chain-of-thought can improve
usefulness without restoring coherence.

No attributable immutable public implementation was located during this audit.
The evidence therefore remains an external methodological result rather than a
reproduced jLens finding.

The binding interpretation is narrow:

1. Calibration alone does not establish that a monitor score is a probability.
2. A useful ranking or escalation score may remain operationally valuable while
   lacking probability semantics.
3. Discrimination, calibration, structural coherence, faithfulness, selective
   utility, and control-policy utility are separate claims.
4. A score may not be combined arithmetically, interpreted as expected risk, or
   used in probability-dependent guarantees unless the relevant probability
   semantics are separately admitted.
5. The paper does not establish hidden-state correctness awareness, router
   utility, Jacobian-lens value, MoE transfer, Agents-A1 transfer, safe early
   exit, or production utility.

## Required object separation

Every compatible study must bind these objects separately:

1. **Target event:** the exact objectively scored event whose probability or
   ranking is being estimated.
2. **Information set:** the exact prompt, prefix, tool state, cache state,
   environment state, verifier history, and serving state available when the
   score is emitted.
3. **Raw score:** the direct scalar or vector produced by logits, verbal report,
   hidden-state probe, route head, trajectory model, sparse feature, transcoder,
   Jacobian readout, or fused monitor.
4. **Ranking interpretation:** whether only ordering or discrimination is
   claimed.
5. **Calibration map:** any transformation from raw score to an empirical event
   frequency.
6. **Probability interpretation:** any stronger claim that the mapped value is a
   coherent conditional probability.
7. **Decision policy:** thresholds, abstention, escalation, retry, early exit,
   quarantine, or other action rules using the score.
8. **Objective outcome rule:** the independent executable, deterministic,
   canonical, or otherwise frozen rule that decides the event.

A strong AUROC does not establish calibration. Good calibration does not
establish coherent probability semantics. Coherent probability semantics do
not establish policy utility. Policy utility does not establish causal access
to hidden correctness.

## Event and information-set identity gate

A probability claim is undefined until the event and conditioning information
are frozen.

For every score, freeze at minimum:

- the event name and complete executable or adjudication definition;
- whether the event is next-token correctness, final-answer correctness,
  verifier acceptance, task success, absence of an unsafe action, recoverability,
  route regret, containment, or another endpoint;
- the time horizon and irreversible-action boundary;
- the exact prefix, hidden-state layer, route state, tool state, environment
  state, cache state, and verifier information available at scoring time;
- whether later tokens, completed-answer structure, future tool results,
  verifier outputs, sealed labels, or realized outcomes are excluded;
- the model, checkpoint, tokenizer, template, precision, quantization, runtime,
  batching, topology, and serving state;
- the population, prevalence, task-family composition, and inclusion rules.

Scores for different events or information sets may not be silently pooled,
averaged, compared, or treated as samples from one probability function.

In particular, these remain distinct events:

- eventual task success;
- next action safety;
- current artifact correctness;
- future artifact correctness;
- verifier acceptance;
- objective correctness;
- self-judgement;
- answerability;
- recoverability before an irreversible action;
- token-budget exhaustion;
- expert-route regret;
- successful containment.

## Structural-coherence gate

Before a score may be described as a probability, confidence probability,
posterior, expected correctness, expected safety, or expected recoverability,
its calibrated outputs must be tested on prospectively frozen event
relationships where the relevant probability axioms apply.

Required relationship families, when technically compatible, include:

- **equivalence:** logically or operationally equivalent formulations receive
  equal probability within frozen tolerance;
- **complement:** a binary event and its exact complement sum to one within
  frozen tolerance;
- **partition:** probabilities across a mutually exclusive and exhaustive action
  or outcome partition sum to one;
- **monotonicity:** if event A is a subset of event B under the same information
  set, then the estimated probability of A does not exceed B;
- **entailment monotonicity:** when one proposition necessarily implies another
  under the frozen task ontology, confidence respects that inclusion;
- **conjunction and disjunction bounds:** estimates respect the elementary bounds
  induced by their component events;
- **dominance:** an event that is objectively no harder or no less inclusive
  under the frozen construction is not assigned systematically lower
  probability without an admitted conditioning difference;
- **label and order invariance:** answer-order, label-name, formatting, and
  semantically equivalent paraphrase changes do not alter the event probability
  beyond frozen tolerance unless those changes modify the information set.

These tests must use generated or curated relationship sets whose logical and
operational validity is independently checked. The monitor under evaluation may
not define the relationships used to certify itself.

A failed coherence test does not prove the score is useless. It restricts the
claim to a nonprobabilistic ranking, detection, or policy score until the defect
is resolved.

## Temporal and sequential boundary

Probability coherence is evaluated at a fixed information set. Scores are not
required to be monotone over time because new evidence can rationally increase
or decrease a probability.

Sequential studies must therefore:

- define the target event identically at every prefix or explicitly document a
  changing horizon;
- identify the complete information set at every score time;
- distinguish belief revision caused by new evidence from contradiction under
  an unchanged information set;
- prevent future-token, outcome, verifier, padding, cache, or replay leakage;
- report calibration, coherence, discrimination, and selective risk separately
  at every preregistered checkpoint;
- use time-uniform or otherwise valid uncertainty control for repeated threshold
  crossing when a sequential policy is evaluated;
- preserve a fail-closed no-intervention disposition when the operating point
  or probability semantics are not admitted.

A prefix score calibrated for eventual success cannot be silently reused as the
probability that the next action is safe. A route-regret score cannot be reused
as the probability of final task failure. A verifier-pass score cannot be
represented as objective correctness without an independently established
mapping.

## Mandatory metric decomposition

Every future confidence or monitor study must report separately:

### Discrimination

- AUROC;
- positive- and negative-class AUPR;
- family- and outcome-stratified ranking performance;
- task-clustered uncertainty;
- pairwise ordering on matched counterfactuals where applicable.

### Distributional calibration

- Brier score and Brier skill against frozen baselines;
- negative log likelihood when the score has admitted probability support;
- reliability curves;
- calibration error under more than one binning or smoothing choice;
- prevalence and population identity;
- calibration under family, difficulty, length, format, model, and runtime shift.

### Structural coherence

- the complete frozen relationship suite;
- violation rates and magnitudes by relationship family;
- worst-group and tail behavior;
- confidence intervals clustered by underlying task or relationship family;
- sensitivity to paraphrase, order, labels, and event ontology.

### Faithfulness

- agreement between the score and the event actually defined at that information
  boundary;
- controls for self-judgement, confidence language, evaluator belief, answer
  format, task difficulty, and other cheaper observables;
- counterfactual tests where the event changes while nuisance features remain
  fixed;
- tests where nuisance features change while the event remains fixed.

### Usefulness and policy utility

- risk-coverage and score-cost curves;
- the frozen operating point;
- false-retain, false-escalate, false-abort, false-accept, and missed-event rates;
- right-to-wrong and wrong-to-right changes caused by the policy;
- full end-to-end latency, compute, memory, retries, fallback, and verifier cost;
- outcome severity and recoverability;
- performance under distribution and runtime drift.

No single aggregate metric may stand in for this decomposition.

## Calibration and coherence population separation

Use separate, non-overlapping populations for:

1. feature and layer selection;
2. monitor fitting;
3. calibration-map fitting;
4. structural-coherence test construction and tolerance selection;
5. threshold and policy selection;
6. certification;
7. sealed outer evaluation.

Task families, paraphrase families, logical-relation families, repositories,
base commits, users, or environments must remain clustered across splits where
shared structure would otherwise leak.

Recalibration after viewing sealed performance is prohibited. Selecting only
relationship families on which the estimator appears coherent is prohibited.
Failed, malformed, abstaining, truncated, tool-error, and verifier-error cases
remain in the full population unless a preregistered event definition places
them in a separately reported outcome class.

## Score fusion and arithmetic gate

Do not average, multiply, add, normalize, or apply Bayes-style arithmetic to
confidence, hidden-state, route, workspace, sparse-feature, transcoder, or
Jacobian scores as if they were probabilities unless joint semantics are
admitted.

A fused monitor may be evaluated as a generic predictive score. To receive a
probability interpretation, freeze and validate:

- the joint event space;
- dependence assumptions;
- calibration procedure;
- relationship constraints;
- missing-feature and abstention behavior;
- distribution-shift behavior;
- the exact arithmetic and numerical implementation.

Independent-looking telemetry channels are not statistically independent by
default. Hidden states, logits, routes, attention, trajectory summaries,
self-judgement, and verifier history are all generated by coupled processes.

## Nonprobabilistic-score allowance

This addendum does not require every useful monitor to become a coherent
probability estimator.

A score that fails probability admission may still be evaluated as:

- a ranker;
- an anomaly score;
- a classifier margin;
- a selective-prediction score;
- an escalation score;
- a retrieval or review-priority score.

Such a study must avoid probability language and probability-dependent
guarantees. Its policy must be justified directly through frozen empirical
risk-coverage, utility, severity, and cost curves rather than through unsupported
expected-probability arithmetic.

## Agents-A1 scaling consequence

After every existing Q35Q gate passes, the minimum Agents-A1 order is:

1. Freeze objective events, information sets, horizons, irreversible-action
   boundaries, external verifiers, and event relationships.
2. Establish deterministic checks, metadata, logits, entropy, verbal confidence,
   self-judgement, peer representations, and simple hidden-state baselines on a
   separately admitted Agents-A1-4B checkpoint.
3. Evaluate discrimination, distributional calibration, structural coherence,
   faithfulness, and policy usefulness separately for every baseline.
4. Treat any score failing probability admission as a nonprobabilistic score.
5. Add passive trajectory and program-state monitors under the same event and
   information-set definitions.
6. Separately admit Agents-A1-35B route and expert-path capture.
7. Evaluate router scores as ranking signals first; grant probability semantics
   only after model- and runtime-specific coherence admission.
8. Require route features to add sealed objective-outcome value beyond the full
   external, confidence, dense-sibling, hidden-state, and trajectory stack.
9. Add sparse-feature or transcoder comparators under identical score-semantics
   rules.
10. Add Jacobian Lens only after exact derivative parity and sealed incremental
    value over every cheaper comparator.
11. Keep early exit, retry, abort, truncation, forced routing, activation
    steering, quarantine, and production control under separate policy gates.

A Jacobian or route score that is better calibrated than a baseline but violates
basic event relationships may be a useful detector. It is not an admitted
probability of correctness or safety.

## Privacy and sealed-data boundary

Structural-coherence evaluation does not relax the repository boundary.

Do not commit raw relationship prompts, generated answers, hidden states,
router traces, per-example scores, per-example coherence failures, sealed labels,
verifier outputs, or task identities. Public records may contain only aggregate
counts, rates, confidence intervals, immutable public artifact identities,
protocol hashes, and permitted status outcomes.

Coherence datasets and relationship templates derived from sealed tasks remain
sealed. Public examples must be independently public and must not reveal the
content or structure of sealed evaluations.

## Current blocker and execution order

The active blocker remains production-path upstream/runtime provenance
composition:

1. bind the live import to its owning installed distribution and `RECORD`;
2. derive complete live-object source closure;
3. reject shadow packages, editable installs, monkeypatches, forged identities,
   incomplete closure, incorrect ownership, and unadmitted loaders in a clean
   subprocess;
4. invoke and bind the actual GPTQModel/Defuser loader;
5. freeze the exact immutable GPTQ runtime tuple;
6. pass the complete adversarial integration conjunction;
7. emit only the permitted aggregate result.

After that remain packer-independent fixture validation, strict packed-tensor
consumption and expert ordering, forward/VJP/JVP/finite-difference parity,
Q35Q Phase-0 admission, weight staging, and a separately authorized GPU
transition.

## Program status after this addendum

Established:

- calibration alone does not establish coherent probability semantics;
- commonly used LLM confidence estimators can violate basic event relationships
  while appearing calibrated in the reported study;
- discrimination, calibration, coherence, faithfulness, usefulness, and policy
  utility are separate claims;
- future jLens monitor scores require explicit event and information-set
  identities;
- probability language and probability-dependent guarantees now require a
  separate coherence gate;
- nonprobabilistic predictive scores remain admissible under bounded language
  and direct empirical policy evaluation;
- no privacy, sealed-data, verifier, provenance, derivative, intervention, or
  production gate has been weakened;
- Q35Q remains blocked.

Unproven:

- independent reproduction of arXiv `2607.19367v1`;
- coherent probability semantics for any current jLens monitor;
- structural coherence of hidden-state, router, sparse-feature, transcoder,
  directional-JVP, or Jacobian scores;
- probability transfer across tasks, model scales, quantizations, runtimes,
  environments, or either Agents-A1 checkpoint;
- incremental router or Jacobian-Lens value after every cheaper comparator;
- complete Q35Q provenance, strict loading, forward parity, or derivative
  admission;
- safe early exit, retry, repair, truncation, route intervention, activation
  steering, quarantine, or production deployment.

The research program remains unfinished.
