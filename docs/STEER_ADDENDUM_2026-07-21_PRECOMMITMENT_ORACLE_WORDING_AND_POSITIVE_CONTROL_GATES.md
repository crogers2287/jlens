# STEER ADDENDUM — precommitment-oracle wording and positive-control gates

Date: 2026-07-21
Parent remote head: `a6af7ff004a5bbb5234879767dfaeddf915a784a`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, intervention, production-gating, and stop rule. It authorizes no
weight retrieval, model execution, GPU use, hidden-state or router capture,
Jacobian fitting, sealed evaluation, control action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains production-path upstream/runtime
provenance composition. This addendum changes a future scientific claim
boundary and mandatory control set; it does not displace that milestone.

GitHub still reports `crogers2287/jlens` as public. Only aggregate program
control and public-source engineering material may be committed. Prompts,
outputs, token data, per-example labels, hidden states, router traces,
Jacobians, verifier records, model weights, caches, credentials, host paths,
and private environment details remain prohibited.

## Triggering primary evidence

Jo, `Committed Before Reasoning: Behavioral Reproduction and Preliminary
Activation-Level Evidence of Answer Pre-Commitment in an Open-Weight LLM`,
arXiv `2607.16451v1`, submitted 2026-07-17, studies a narrow Qwen3-8B car-wash
prompt on which the model frequently commits to an answer that conflicts with
the task premise.

The public reproduction material inspected for this correction is
`JO-HEEJIN/interview_mate`, branch `docs/car-wash-repro`, path
`car_wash/paper_4`. The inspected README has immutable Git blob identity
`8de02993666ee16a0d63628fcdb254a5a139aee5`.

The source reports:

- 194 walk, 10 drive, and 6 indeterminate outcomes across 210 rollouts;
- wrong-commitment rates of 85--100% across the reported conditions;
- no behavioral repair from a 4,096-token thinking budget in that prompt;
- preliminary activation-oracle readouts before answer emission;
- a large change in positive-control sensitivity when the oracle query changed
  from an open question to a closed forced-choice question, while activations
  and inspected positions were held fixed; and
- small samples, no significant within-rollout positional gradient, one model,
  one core task, and one externally trained oracle.

The source's methodological result is material even if its behavioral and
activation findings fail to generalize:

> A negative or weak target-conditioned activation-oracle result is not
> interpretable when the oracle has not first demonstrated sensitivity under
> the exact query wording, answer vocabulary, template, model, checkpoint,
> layer, position policy, and runtime condition being evaluated.

## Bounded interpretation

The source does not establish:

- objective-correctness prediction;
- causal answer precommitment;
- a universal answer-before-reasoning failure mode;
- reliable temporal localization of commitment onset;
- open-set or target-blind semantic monitoring;
- robustness across tasks, prompt phrasings, checkpoints, quantizations,
  architectures, modalities, languages, or serving runtimes;
- MoE router semantics;
- long-horizon agent-error prediction;
- Agents-A1 transfer; or
- safe intervention.

The activation oracle is a separately trained LoRA-based readout. It is not a
parameter-free property of the unmodified target model. Its query wording,
answer vocabulary, prompt template, checkpoint, compatibility patch, and
inference path are part of the monitor artifact.

The observed precommitment readout also appeared in most of the small number of
rollouts that eventually produced the correct answer. A commitment-associated
signal is therefore not automatically an objective-error signal.

## Binding endpoint separation

Future compatible studies must distinguish:

1. **Candidate activation:** evidence favoring one answer, plan, tool action, or
   semantic candidate over alternatives.
2. **Policy commitment:** evidence that the current candidate will govern the
   next output or action.
3. **Answer emission:** the answer, plan, tool call, or action actually emitted.
4. **Objective outcome:** correctness under an admitted external verifier or
   environment result.
5. **Self-judgement:** the model's later endorsement of its own output.
6. **Recoverability:** whether later reasoning, retrieval, verification, or
   repair can still change the outcome before an irreversible action.

A readout may predict one or more endpoints. It may not be described as hidden
error awareness, objective correctness, truth, or safe stopping evidence unless
objective-outcome value is independently established after conditioning on
candidate activation, policy commitment, confidence, answerability,
self-judgement, and cheaper observable signals.

## Oracle-query and positive-control admission

Every target-conditioned activation oracle, concept readout, template lens,
classifier prompt, or forced-choice semantic readout must freeze:

- oracle/model artifact identity and digest;
- training corpus and objective where available;
- target model, checkpoint, processor, precision, and runtime;
- exact oracle query wording;
- answer vocabulary, label mapping, tokenization, and parsing rule;
- chat template, system prompt, demonstrations, and position policy;
- inspected layers, normalization boundary, pooling, and aggregation;
- thresholds, abstention rule, and tie handling;
- compatibility patches and dependency identities; and
- selection, calibration, and certification populations.

Before a negative or null result may support absence-of-signal language, the
oracle must pass a prospectively frozen positive-control gate under the same
configuration. The positive control must establish that the oracle can recover
an explicitly present or independently induced target distinction at the same
layers and positions without using the sealed outcome.

Required positive-control reporting includes:

- per-wording sensitivity and specificity;
- open-question versus forced-choice wording where compatible;
- paraphrase, synonym, answer-order, and label-name permutations;
- tokenizer and multi-token answer variants;
- neutral-context and unrelated-content defaults;
- literal target mention and lexical-inversion controls;
- position-matched and length-matched controls;
- full counts, cluster-aware uncertainty, and abstentions; and
- the exact acceptance criterion frozen before outer validation.

Failure of the positive-control gate means the scientific result is
`oracle_unvalidated_for_condition`, not evidence that the target representation
lacks the concept or commitment.

Passing the positive-control gate establishes only local oracle sensitivity. It
does not establish semantic completeness, target-blind coverage, calibration,
objective-correctness value, or causal validity.

## Wording-robustness and researcher-degrees-of-freedom gate

Oracle wording is a model input and a selection degree of freedom. It may not be
silently optimized after viewing evaluation outcomes.

- Wording families, answer vocabularies, templates, and parsing rules must be
  generated or chosen on training-only data.
- The number of attempted oracle queries and abandoned configurations must be
  recorded in the private audit ledger and summarized in aggregate.
- Outer validation and sealed evaluation must use the frozen query set.
- The best wording may not be selected separately for each test task, model,
  layer, outcome class, or subgroup.
- Prompt paraphrases must be clustered when estimating uncertainty.
- Pooled results may not hide wording conditions with reversed polarity,
  chance-level sensitivity, or deterministic default behavior.
- A result that exists only for one hand-selected query must be classified as
  query-conditioned evidence.

The no-concept-list and target-blind baselines in existing protocol remain
mandatory. Query-conditioned activation oracles cannot replace them.

## Precommitment chronology gate

A pre-emission readout does not by itself establish answer-before-reasoning.
Future chronology claims must freeze and compare explicit boundaries:

1. prompt completion;
2. first hidden reasoning token or latent step;
3. first candidate-specific representation;
4. first statistically detectable commitment-associated readout;
5. first emitted candidate token;
6. first complete answer or action;
7. verifier or tool feedback;
8. correction or repair; and
9. irreversible external action.

Required controls include answer-order reversal, premise-preserving paraphrase,
counterbalanced correct labels, matched easy and hard items, cases where the
initial candidate changes, and cases where early candidate activation does not
predict the final output.

A readout observed before answer text but after candidate-specific internal or
visible reasoning may be described as pre-emission. It may not be described as
pre-reasoning without an admitted earlier boundary and a prospectively frozen
localization test.

## Mandatory comparators

For every compatible precommitment or correctness claim, report matched results
for:

1. prompt and task metadata;
2. final and intermediate logits, margins, entropy, and candidate-token
   likelihoods;
3. answer-order and lexical baselines;
4. explicit self-judgement and confidence;
5. passive linear hidden-state probes;
6. the target-conditioned activation oracle;
7. a no-oracle or target-blind representation baseline;
8. peer-model and embedding representations where admitted;
9. bounded trajectory summaries;
10. router, workspace, sparse-feature, transcoder, directional-JVP, or Jacobian
    features only after their existing admission gates; and
11. random, prevalence-matched, fixed-answer, and never-alarm controls.

All comparisons must use identical populations, boundaries, downstream actions,
selection budgets, calibration data, and full cost accounting.

## Agents-A1 consequence

After all existing artifact and runtime gates pass, the minimum relevant order
for Agents-A1 is:

1. freeze objective outcomes, candidate sets, irreversible-action boundaries,
   and external checks;
2. establish metadata, logits, confidence, self-judgement, and answer-order
   baselines;
3. validate every target-conditioned oracle with per-wording positive controls
   on the separately admitted Agents-A1-4B dense sibling;
4. evaluate passive candidate-activation, commitment, and objective-outcome
   readouts separately;
5. repeat artifact admission and positive-control validation on Agents-A1-35B;
6. capture minimal route telemetry only after the hidden-state and target-blind
   baselines are frozen;
7. test whether route features add objective-outcome value after conditioning on
   commitment and candidate activation;
8. add sparse-feature or transcoder streams; and
9. add Jacobian-Lens streams only after exact derivative parity and sealed
   incremental objective-outcome value over every cheaper comparator.

An Agents-A1 route or Jacobian signal that predicts the model's candidate or
commitment but not objective outcome remains useful process telemetry. It is not
hidden correctness awareness.

## Intervention boundary

This addendum authorizes no intervention. A commitment-associated signal may
not trigger answer replacement, tool suppression, retry, escalation, early
exit, truncation, forced routing, expert intervention, activation steering, or
production enforcement without a separate preregistered policy, fresh-population
utility evaluation, false-positive and false-negative harm budgets, recovery
rules, privacy review, full cost accounting, and production admission.

## Active blocker remains unchanged

The next admissible repository progress remains one CPU-only, clean-subprocess,
fail-closed production adapter that:

1. verifies the frozen upstream Transformers artifact;
2. derives expected source identities from that verified artifact;
3. binds the live import to its owning installed distribution and `RECORD`;
4. derives the complete live source closure;
5. rejects shadow packages, editable installs, monkeypatches, forged identities,
   incomplete closure, wrong ownership, and unadmitted loaders;
6. invokes and binds the actual GPTQModel/Defuser loader entry point;
7. freezes the complete immutable runtime tuple;
8. passes the full adversarial integration conjunction; and
9. emits only the permitted aggregate result.

After that remain strict synthetic loading, exact quantization-tensor
consumption and expert ordering, forward/VJP/JVP/finite-difference parity,
Phase-0 admission, weight staging, and a separately authorized GPU transition.

## Established

- A public preprint and reproduction package report a narrow Qwen3-8B
  answer-precommitment failure and preliminary activation-oracle readouts.
- Under fixed activations and positions, changing the oracle question from open
  to forced-choice materially changed the reported positive-control sensitivity.
- Negative target-conditioned oracle results require condition-matched positive
  controls before absence-of-signal language is admissible.
- Candidate activation, policy commitment, emitted action, self-judgement, and
  objective correctness are distinct endpoints.
- Oracle-query, wording-selection, positive-control, chronology, comparator,
  privacy, and intervention gates are now binding.
- Q35Q remains blocked and no execution or resource gate is weakened.

## Unproven

- Independent reproduction of the reported behavioral or activation findings.
- General answer-before-reasoning behavior beyond the tested prompt and model.
- Reliable commitment-onset localization.
- Objective-error prediction from the reported oracle signal.
- Target-blind or open-set semantic monitoring.
- Nonlinear, multimodal, MoE, coding-agent, tool-use, or long-horizon behavior.
- Transfer to Qwen3.5/Qwen3.6 MoE, Agents-A1-4B, or Agents-A1-35B.
- Incremental route, workspace, sparse-feature, transcoder, hardware-proxy, or
  Jacobian value after commitment, confidence, self-judgement, and cheaper
  comparator controls.
- Complete Q35Q provenance, strict loading, forward parity, or derivative
  admission.
- Safe early exit, abort, retry, escalation, correction, routing intervention,
  activation steering, or production deployment.
