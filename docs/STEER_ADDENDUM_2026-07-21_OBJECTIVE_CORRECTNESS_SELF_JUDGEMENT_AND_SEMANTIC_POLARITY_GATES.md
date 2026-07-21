# STEER ADDENDUM — objective-correctness, self-judgement, and semantic-polarity gates

Date: 2026-07-21
Parent remote head: `8e53bfaf839bc01ca5d78b8ab7d5b5934cff0201`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, parity, resource,
commit-safety, production-gating, intervention, and stop rule. It authorizes no
weight retrieval, model execution, GPU use, hidden-state or router capture,
Jacobian fitting, sealed evaluation, control action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active milestone remains production-path upstream/runtime provenance
composition. This addendum changes a future scientific claim boundary and
minimum comparator set; it does not displace that engineering milestone.

GitHub still reports `crogers2287/jlens` as public. Only aggregate program
control and public-source engineering material may be committed. Prompts,
outputs, token data, per-example correctness or self-judgement labels, hidden
states, router traces, Jacobians, verifier records, model weights, caches,
credentials, host paths, and private environment details remain prohibited.

## Triggering primary evidence

Lu, `Diagnosing Correctness Probes under Self-Judgement Confounding`, arXiv
`2607.16799v1`, submitted 2026-07-18, separates externally scored objective
correctness (`OC`) from the same model's later binary self-judgement (`SJ`). The
public implementation and processed-data release inspected for this correction
is `Yilong-Lu/Diagnosing_Correctness` at immutable commit
`f6201cd3c4471b5e30e92849a71e004b03763b7b`.

The study forms four response cells:

- A: objectively correct and self-endorsed;
- B: objectively correct and self-rejected;
- C: objectively wrong and self-endorsed;
- D: objectively wrong and self-rejected.

On B/C conflicts, objective correctness and self-judgement prescribe opposite
rankings. Across four instruction-tuned dense models up to 14B parameters, the
reported transferable component consistently preserved self-judgement polarity
more reliably than objective-correctness polarity. A conventional
correct-versus-incorrect activation contrast, including an OC-labelled
within-question mean-difference control, could therefore rank wrong but
self-endorsed answers above correct but self-rejected answers.

The result persists in the authors' reported answer-likelihood, sequence-length,
question, answer-letter, confidence-threshold, and null-direction controls and
extends from mathematical reasoning and movie factual recall to inserted-choice
MMLU and binary TruthfulQA targets without target-domain direction fitting.

This evidence materially changes the semantic claim boundary for every future
hidden-state, route, workspace, sparse-feature, transcoder, peer-representation,
or Jacobian correctness monitor. Predictive accuracy and cross-domain transfer
do not identify which correlated variable a monitor reads out.

## Bounded interpretation of the source

The source does not establish ordinary-output prevalence, prospective error
detection, causal control, large-MoE behavior, agent-trajectory behavior,
Agents-A1 transfer, or production utility.

Its main diagnostic population is conditional on questions for which stochastic
generation produced both a correct and an incorrect usable answer and the model
made high-confidence self-judgements. Hidden states were extracted at the final
answer token before a separate judgement turn. The study therefore concerns a
post-answer response representation and a selected diagnostic subset, not a
prefix-only online monitor before an irreversible action.

The reported directions are linear activation-mean associations. The study does
not establish nonlinear monitor behavior, open-ended tool-use outcomes,
long-horizon failure onset, multimodal behavior, or intervention safety.

## Binding endpoint decomposition

Future monitoring studies must freeze and report these as distinct endpoints:

1. **Objective outcome:** correctness defined by an admitted external verifier,
   executable check, benchmark answer key, or canonical environment result.
2. **Self-judgement:** the target model's own subsequent belief, endorsement, or
   predicted success under a frozen elicitation and scoring rule.
3. **Generation confidence:** logits, token likelihood, entropy, margin,
   verbalized confidence, or another admitted uncertainty signal.
4. **Answerability or admissibility:** whether the task or action should be
   attempted under available evidence, permissions, tools, and state.
5. **Policy commitment:** whether the model is committed to its current answer,
   plan, route, tool action, or finish decision.
6. **Resolution choice:** answer, clarify, retrieve, use a tool, retry, escalate,
   abstain, or stop.

A monitor may correlate with more than one endpoint. It may not be described as
an objective-correctness, truth, hidden-error-awareness, or privileged
introspection monitor unless the objective-outcome component is independently
established after conditioning on the other endpoints.

## Mandatory semantic-polarity diagnostic

Every technically compatible correctness-monitor evaluation must include a
training-only designed and frozen semantic-polarity diagnostic.

The evaluation must contain at least:

- objectively correct and self-endorsed cases;
- objectively correct and self-rejected cases;
- objectively wrong and self-endorsed cases;
- objectively wrong and self-rejected cases;
- aligned OC/SJ cases and OC/SJ conflict cases;
- low-, medium-, and high-confidence strata where sample size permits;
- matched answerability, task family, answer format, response length, and
  difficulty controls;
- successful, recoverable, terminal-failure, abstention, timeout, verifier-error,
  and malformed-action outcomes for agent settings.

On the objective-correctness claim, the primary conflict estimand must rank B
above C. A score that ranks C above B is self-judgement-, endorsement-,
commitment-, or confidence-associated evidence unless a separately preregistered
analysis proves another interpretation.

Full-population performance and conflict-population semantic polarity must be
reported separately. A high full-population AUROC or AUPRC cannot compensate for
reversed conflict polarity.

## Leakage and selection controls

Self-judgement is a diagnostic variable, not an unrestricted training shortcut.

- Probe training, layer selection, feature selection, threshold tuning, monitor
  selection, and calibration must use training populations only.
- OC/SJ disagreement membership is an evaluation stratum by default and may not
  select layers, features, directions, peers, thresholds, or monitor families.
- Any experiment that trains on conflict membership must be a separately named
  task and must include shortcut controls; it cannot replace the evaluation-only
  semantic-polarity diagnostic.
- The self-judgement prompt, answer vocabulary, mapping, confidence threshold,
  sampling parameters, and scoring rule must be frozen before outer validation
  or sealed evaluation.
- The monitored representation must be captured before the self-judgement
  elicitation if the claim concerns latent prediction of a later judgement.
- The judgement turn, verifier outcome, canonical answer, future trajectory,
  post-intervention evidence, and sealed label may not enter the monitored
  representation or feature-construction path at an earlier decision boundary.
- Repeated generations and repeated judgements must be clustered by task and
  episode in uncertainty estimation.

## Mandatory matched comparators

For every proposed internal correctness signal, report matched results for:

1. prompt, task, tool, trajectory, and environment metadata;
2. output logits, likelihood, entropy, margins, and finish reason;
3. frozen verbal or forced-choice self-judgement;
4. answerability, capability, and resolution heads where compatible;
5. a frozen external embedding or peer-model representation;
6. the target model's passive hidden-state baseline;
7. bounded trajectory summaries;
8. the proposed router, hardware-proxy, workspace, sparse-feature, transcoder,
   directional-JVP, or Jacobian feature;
9. frozen combinations of cheaper signals;
10. random, prevalence-matched, and never-alarm controls.

Comparisons must use identical outcome populations, decision boundaries,
selection budgets, calibration populations, downstream actions, and full cost
accounting.

A proposed internal signal must demonstrate incremental objective-outcome value
after conditioning on self-judgement and confidence. Incremental value only for
predicting self-judgement, endorsement, or commitment is not objective
correctness awareness.

## Cross-domain and transfer claim boundary

Cross-domain transfer, sign stability, shared directions, early-to-late layer
emergence, and target-domain zero-shot performance do not establish semantic
identity.

A transferred signal must preserve objective-correctness polarity on conflict
cases in every domain for which an objective-correctness claim is made. Report
per-domain and per-family effects; pooled transfer cannot hide reversed or
chance-level domains.

Transfer from public Qwen3.6, Agents-A1-4B, a peer model, a pruned specialist, a
quantized checkpoint, or another runtime to Agents-A1-35B remains prospective
and separately calibrated. No representation, layer, route, workspace, or
Jacobian coordinate is assumed semantically aligned across checkpoints.

## Agent and Agents-A1 protocol

For long-horizon agents, define self-judgement at explicit frozen boundaries,
including where compatible:

- task acceptance;
- plan completion;
- tool-call validity;
- evidence sufficiency;
- current-step correctness;
- eventual task success;
- finish readiness;
- retry or escalation need.

Each judgement must be separated from the admitted external outcome and from the
action taken. Post-action diagnosis may not be represented as pre-action
prediction.

After all existing Q35Q gates pass, the minimum Agents-A1 comparator order is:

1. deterministic schema, permission, provenance, ordering, checklist, and
   verifier controls;
2. metadata, context-envelope, trajectory, and serving-state controls;
3. logits, confidence, and explicit self-judgement streams;
4. embedding and peer-model representations, including the separately admitted
   Agents-A1-4B dense sibling where compatible;
5. passive Agents-A1-35B hidden-state and bounded trajectory readouts;
6. direct executed-route telemetry with occupancy, ancestry, semantic, topology,
   precision-state, and cross-request controls;
7. hardware-proxy telemetry only after direct-route utility and privacy gates;
8. sparse-feature or transcoder streams;
9. Jacobian-Lens streams only after exact derivative parity and sealed
   incremental objective-outcome value over every cheaper comparator.

Router or Jacobian features must beat the best cheaper baseline on both the full
population and the OC/SJ conflict population. A gain confined to predicting the
model's own endorsement does not establish model-private objective correctness.

## Intervention boundary

This addendum authorizes detection research only after existing admission gates.
It does not authorize abort, retry, escalation, abstention, early exit,
truncation, tool suppression, expert deletion, expert substitution, forced
routing, adaptive precision, activation steering, answer correction, or
production enforcement.

Any intervention must receive a separate preregistered policy, fresh-population
utility evaluation, verifier analysis, false-positive and false-negative harm
budgets, recovery rule, privacy review, full cost accounting, and production
admission.

## Active engineering blocker remains unchanged

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

- A public paper, processed-data release, and analysis implementation exist for
  the OC/SJ factorial diagnostic.
- In the authors' tested dense models and selected diagnostic populations,
  transferable hidden-state directions tracked later self-judgement more
  reliably than externally scored objective correctness.
- Aggregate correctness prediction and transfer are insufficient to establish
  objective-correctness semantics.
- Self-judgement, semantic-polarity, leakage, matched-comparator, conflict-set,
  agent-boundary, and claim-separation gates are now binding.
- Q35Q remains blocked and no execution or resource gate is weakened.

## Unproven

- Independent reproduction of the reported OC/SJ findings.
- Ordinary-output prevalence of high-confidence OC/SJ conflicts.
- Nonlinear, multimodal, MoE, coding-agent, tool-use, or long-horizon behavior.
- Prospective error-onset prediction or detection before irreversible action.
- Causal objective-correctness control.
- Transfer to Qwen3.5/Qwen3.6 MoE, Agents-A1-4B, or Agents-A1-35B.
- Incremental route, workspace, sparse-feature, transcoder, hardware-proxy, or
  Jacobian value after self-judgement and confidence controls.
- Complete Q35Q provenance, strict loading, forward parity, or derivative
  admission.
- Safe early exit, abort, retry, escalation, routing intervention, activation
  steering, correction, or production deployment.
