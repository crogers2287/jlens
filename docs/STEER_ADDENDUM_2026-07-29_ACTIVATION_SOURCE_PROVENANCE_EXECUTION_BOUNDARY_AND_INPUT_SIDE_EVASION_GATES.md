# STEER ADDENDUM — activation-source provenance, execution-boundary, and input-side evasion gates

Date: 2026-07-29
Parent remote head: `8accce7506150d41f88d171194204a42b05f1135`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every later cumulative protocol correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, derivative, resource, intervention, cleanup, retry, and production-gating rule. It does not constitute Q35Q admission, authorize weight staging or GPU use, reopen M38E, permit Agents-A1 capture, establish an internal jLens scientific result, or authorize steering, early exit, retry, repair, truncation, forced routing, prompt rewriting, or production control.

GitHub currently reports `crogers2287/jlens` as public. Only aggregate program-control and public-source material may be committed. Prompts, outputs, token-level records, per-example outcomes, hidden states, router traces, Jacobians, monitor parameters, thresholds, verifier details, model weights, caches, credentials, host paths, and private environment details remain prohibited.

The aggregate engineering outcome remains:

`q35q_artifact_admission_blocked`

## Triggering primary evidence

### Activation-source selection

Ye et al., `Where Steering Signals Come From: Activation Source Selection in Activation Steering`, arXiv `2607.25270v1`, submitted 2026-07-28, studies the upstream source used to construct an activation-steering signal while holding the downstream intervention fixed.

The paper defines activation-source selection as the combination of:

- source context; and
- activation readout policy.

Across three instruction-tuned models and four steering task families, the authors report that changing only the source activations materially changes steering success. Their central empirical claim is that strong signals frequently come from execution-boundary states: states immediately before the model produces or continues the target behavior. They argue that answer-based sources can work because part of their signal aligns with a pre-realization execution-boundary direction, not merely because target text is present. They introduce `tail subtraction` to remove shared prompt and continuation semantics from the boundary state.

No immutable attributable public implementation was located during this run. The source is therefore primary methodological evidence and an external author-supplied result, not a reproduced jLens result.

### Input-only latent suppression

Mody et al., `Minimizing Targeted Activations: Input-Only Suppression of Evaluation-Awareness Latents in Large Language Models`, arXiv `2607.25907v1`, submitted 2026-07-28, optimizes fluent prompts to suppress selected internal activation targets without inference-time model editing.

The reported target classes include:

- a contrastive activation-addition direction;
- a subspace norm;
- a sparse-autoencoder feature;
- a single MLP neuron; and
- a behavioral logit.

The authors report strong activation suppression under their optimizer. Their controls materially limit the interpretation:

- a random placebo direction was suppressible to a similar degree and shifted behavior comparably;
- suppressing an evaluation-associated contrastive direction while a real evaluation passage remained in context did not reduce, and slightly increased, the model's behavioral evaluation judgement;
- an evaluation-correlated single neuron was not causal in the tested models; and
- natural text retrieved from the Pile was competitive with the optimizer for suppressing the internal direction.

The paper's bounded conclusion is that activation readability is not behavioral controllability. No immutable attributable public implementation was located during this run. This is external primary evidence, not an internally reproduced result.

## Binding interpretation

The new evidence changes two claim boundaries not fully encoded by corpus, layer, steering, monitor-gaming, or intervention controls alone.

First:

> A steering vector, monitor direction, sparse feature, Jacobian summary, or hidden-state statistic is conditional on the exact source context and activation readout policy used to construct it. Source selection is part of the scientific and executable artifact identity, not a secondary implementation detail.

Second:

> Suppressing a monitored activation with an optimized or naturally occurring input does not establish erasure of the represented information, removal of the associated behavior, or defeat of the objective process. Conversely, preserving the behavior while suppressing the activation is direct evidence against treating activation magnitude as a sufficient behavioral state variable.

The following objects are distinct and may not be renamed into one another:

1. Source text or source trajectory.
2. Source execution state.
3. Source token, position, span, and readout boundary.
4. Source hidden-state population.
5. Contrastive or fitted direction.
6. Centering, subtraction, normalization, or tail-removal transform.
7. Target-model activation under a new input.
8. Behavioral expression of the target property.
9. Independently verified objective outcome.
10. Monitor alarm, intervention decision, or production policy.

An execution-boundary direction may encode imminent output disposition. It does not by itself establish semantic intent, objective correctness, stable planning, evaluator belief, global-workspace access, causal necessity, or safe control utility.

## Activation-source identity gate

Every future fitted or contrastive activation artifact must freeze and report, where applicable:

- immutable model and tokenizer revisions;
- source dataset, source generator, and source sampling rule;
- source prompt, system context, chat template, tool state, and memory state;
- prefill versus decode status;
- source token, span, position, and sequence-length policy;
- whether the source state occurs before, during, or after behavioral realization;
- readout module and exact hook boundary;
- pre- or post-normalization status;
- residual, attention, recurrent, cache, router, expert, or post-combine boundary;
- cache construction, prefix reuse, recurrent state, batching, scheduler, precision, and topology;
- clean, contrastive, corrupted, answer, continuation, self-generated, or externally supplied source class;
- centering, subtraction, whitening, normalization, sign, and scale rules;
- aggregation estimator, prompt count, seed, and weighting;
- source-selection budget and all candidates inspected; and
- train, calibration, validation, and sealed-population boundaries.

Two vectors constructed from the same textual concept but different source contexts, positions, execution stages, readout boundaries, cache states, or subtraction rules are separate artifacts until prospective equivalence is established.

A source artifact discovered by searching many prompts, positions, layers, token policies, or subtraction rules is selection-conditioned evidence. All attempted source policies must remain in the private audit trail, and outer evaluation must use fresh populations.

## Pre-realization versus post-realization gate

Future studies must distinguish at least:

- target text already present in the source context;
- target behavior currently being executed;
- the final state before the first target-behavior token;
- states before an unrelated continuation;
- states after the target behavior is complete;
- matched states with the same lexical material but different intended continuation;
- matched states with different lexical material but the same verified continuation class; and
- answer-derived states whose useful component may be retrospective.

Required controls include, where technically compatible:

- answer-token and continuation-token removal;
- randomized target labels;
- source-text paraphrases and synonyms;
- multi-token and non-lexical target behaviors;
- prompt-only, continuation-only, and prompt-plus-continuation sources;
- equal-length and equal-position placebos;
- wrong-but-confident, correct-but-unrealized, and realized-but-objectively-wrong strata;
- matched next-token logit, entropy, margin, and direct-lens controls; and
- prospective source policies selected without sealed outcomes.

A direction that predicts or steers the model's next emitted behavior remains an output-disposition direction unless it adds independently verified objective-outcome value beyond logits, margins, source lexical content, position, and cheaper hidden-state comparators.

## Tail-subtraction and source-transform gate

`Tail subtraction`, centering, contrastive subtraction, whitening, residualization, orthogonalization, or any related transform creates a new fitted artifact.

The transform must freeze:

- the two or more states being combined;
- their token, position, layer, and runtime alignment;
- signs and coefficients;
- centering population;
- whether norms are matched before or after subtraction;
- whether prompt, continuation, lexical, positional, and output-disposition components are estimated separately;
- numerical conditioning and near-cancellation behavior; and
- all alternative transforms considered.

Required controls include:

- no subtraction;
- mean centering;
- random paired subtraction;
- label-permuted subtraction;
- prompt-tail subtraction;
- continuation-tail subtraction;
- norm-matched random and orthogonal directions;
- principal-component removal controls; and
- held-out source and target populations.

Improved steering after subtraction does not establish that removed components were nuisance-only. Degraded steering does not establish that removed components were semantically essential. The claim is scoped to the exact intervention and outcome measured.

## Readability, controllability, and erasure gate

The following claims require separate evidence:

1. **Readability:** an admitted instrument predicts a label from the activation.
2. **Activation controllability:** an intervention or input changes the measured activation.
3. **Behavioral controllability:** the intervention changes a prospectively frozen behavior.
4. **Objective controllability:** the intervention changes an independently verified outcome.
5. **Selective control:** the target changes without unacceptable collateral effects.
6. **Erasure:** target information is absent under a prospectively frozen, sufficiently powerful exclusion suite.
7. **Monitor evasion:** the monitor fails while the prohibited or failure-relevant process persists.
8. **Policy defeat:** the complete monitor-plus-controller system fails under the admitted threat model.

Activation suppression alone establishes only activation controllability for the exact instrument. It cannot establish erasure, behavioral mitigation, objective mitigation, or system-level defeat.

A failure of one linear probe after suppression may reflect rotation, redistribution, nonlinear recoding, changed token alignment, route changes, or instrument failure. Erasure claims require multiple prospectively frozen probes, nonlinear and subspace controls, causal tests, and objective outcomes.

## Input-side monitor-evasion gate

Every production-oriented internal-monitor proposal must include a separate input-side evasion study before deployment authorization.

The development-stage threat model must test, where technically compatible:

- gradient-based and gradient-free prompt optimization;
- prefix-only, suffix-only, infix, tool-output, memory, and retrieved-context perturbations;
- fluent and unconstrained optimization;
- natural-text retrieval or search baselines;
- paraphrase, translation, formatting, padding, and benign-context dilution;
- long-context placement and cache-reuse variants;
- target activation minimization with the objective behavior held fixed;
- objective-behavior optimization with the target activation held fixed where feasible;
- single-direction, subspace, sparse-feature, neuron, router, and ensemble monitors;
- adaptive attacks against known monitor families without exposing sealed production parameters; and
- transfer attacks from surrogate models and surrogate monitors.

The primary adverse event is not low activation. It is independently verified prohibited, incorrect, unsafe, or policy-relevant behavior occurring without the required alarm or fallback.

Input-side evasion studies must report:

- attack success against the activation target;
- behavioral preservation or change;
- objective-outcome preservation or change;
- coherence and task-performance regressions;
- false-positive and false-negative changes;
- transfer across prompts, tasks, models, layers, routes, runtimes, and seeds;
- query and optimization cost; and
- failure against random, placebo, and natural-text baselines.

A monitor that can be suppressed more easily than matched random directions has not demonstrated target-specific robustness. A monitor that can be suppressed no more easily than random directions has not demonstrated semantic specificity.

## Placebo and natural-text baseline gate

Every activation-targeting or steering study must include, where technically compatible:

- random Gaussian directions with matched norm;
- random in-distribution activation differences;
- orthogonal directions;
- label-permuted real directions;
- neighboring sparse features or neurons;
- matched-logit behavioral targets;
- naturally occurring text selected without target-model gradients;
- corpus search using the same query budget as the optimizer; and
- no-op and formatting-only controls.

Report activation change and behavioral change for every control. A method is target-specific only if it exceeds these controls under a frozen statistical rule and preserves the claimed objective relationship.

Natural-text matches to an optimized attack are not a nuisance result. They establish that ordinary deployment inputs may reach similar activation states and must be represented in robustness and prevalence estimates.

## Sealed-data and production-monitor protection

Input-side evasion research must not expose private monitor vectors, thresholds, verifier rules, sealed examples, production prompts, or production fallback logic in this public repository.

Required separation:

- public protocol and aggregate identities;
- private development monitor and attack populations;
- sealed final evaluation populations inaccessible to source selection and attack tuning;
- independently controlled objective verifiers;
- shadow monitoring where permitted; and
- complete private audit of failed attacks and abandoned monitor variants.

Security through secrecy is not sufficient. Parameter withholding may reduce attack access, but production admission still requires robustness to surrogate, transfer, naturally occurring, and partial-information attacks.

## MoE, cache, and hybrid-state consequence

For Agents-A1-35B or another hybrid MoE, activation-source and evasion studies must jointly record, through admitted aggregate telemetry:

- raw router scores;
- dispatch-adjusted scores where present;
- selected expert identities and order;
- consumed mixture weights;
- routed and shared-expert contributions;
- route margins and near-ties;
- recurrent or linear-attention state;
- full-attention KV-cache lineage;
- prefix-cache reuse and fresh-prefill condition;
- token position, sequence length, and batching condition; and
- downstream objective outcome.

Required dissociation tests include:

- activation suppression without route change;
- route change without activation suppression;
- same monitor activation under different expert paths;
- different monitor activation under the same expert path;
- source direction fit under one route distribution and evaluated under another;
- fresh-prefill versus reused-prefix conditions; and
- recurrent-state-preserved versus reset conditions.

A source direction fitted under one route, cache, or recurrent-state distribution does not transfer to another without prospective evidence. A monitor defeated only by changing routes is still defeated if the objective adverse event persists.

## Jacobian-Lens consequence

A fitted Jacobian or directional derivative is conditional on its source population and held-fixed execution state.

Future jLens studies must freeze:

- source-context population;
- token and execution-boundary policy;
- target output and normalization boundary;
- route, cache, recurrent-state, and batching condition;
- corpus and task-family mixture;
- averaging estimator and weighting; and
- whether examples are pre-realization, post-realization, or answer-derived.

Changing source-selection policy changes the estimated average operator. Similar-looking maps from different source policies are separate artifacts until numerical and scientific equivalence is established.

Required comparators include:

- source-policy-matched raw hidden states;
- logits, margins, entropy, and direct/logit lenses;
- source-policy-matched activation differences;
- random and orthogonal directional derivatives;
- same-model refits under alternative source stages;
- route-conditioned and route-marginalized operators; and
- objective-outcome prediction on fresh sealed populations.

A Jacobian direction aligned with an execution-boundary steering vector remains an output-sensitivity result. It does not establish objective correctness, semantic-workspace identity, causal necessity, or safe stopping.

## Agents-A1 scaling sequence

The technically credible path is now:

1. Complete Q35Q exact-target-runtime provenance, strict loading, packed-tensor consumption, expert-ordering, deterministic-forward, activation-VJP, activation-JVP, and finite-difference admission.
2. Admit Agents-A1-4B under its exact tokenizer, chat template, hybrid-attention state, cache, harness, verifier, and runtime.
3. Establish deterministic, confidence, logit, trajectory, memory, program-state, hidden-state, spectral, and verifier baselines before fitting steering or monitor directions.
4. Construct a frozen activation-source matrix spanning prefill/decode, pre-realization/post-realization, prompt/continuation, token/position, and clean/contrastive source policies.
5. Select source policies entirely on training and calibration populations and retain all attempted policies in the private audit trail.
6. Test execution-boundary directions against lexical, next-token, direct-lens, confidence, and objective-outcome controls.
7. Complete observation-only monitoring before any steering, prompt rewriting, early exit, retry, repair, or truncation study.
8. Run input-side suppression and natural-text search studies against development monitors without exposing sealed production parameters.
9. Separately admit Agents-A1-35B's checkpoint, quantization, router, dispatch, routed and shared experts, hybrid state, cache, kernels, topology, batching, scheduler, and capture path.
10. Refit or revalidate every source artifact under Agents-A1-35B-native route, cache, and recurrent-state conditions.
11. Require router and Jacobian features to add sealed objective-outcome value beyond the complete cheaper source-aware comparator stack.
12. Admit any steering, early-exit, retry, repair, truncation, forced-routing, or production policy only through a separately preregistered control study with full-compute fallback.

## Current engineering blocker remains unchanged

The active milestone remains exact-target-runtime Q35Q admission:

1. execute the composed Transformers provenance adapter in the exact target runtime using aggregate evidence only;
2. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` as one immutable tuple;
3. bind the actual GPTQModel/Defuser loader and its complete executable source closure;
4. run strict synthetic Qwen3.5-MoE loading;
5. prove one-time packed-tensor consumption;
6. prove exact expert and fusion ordering;
7. prove deterministic forward, activation-VJP, activation-JVP, and finite-difference parity; and
8. pass the complete Phase-0 conjunction before weight staging or GPU authorization.

## Established by this correction

- Activation source context and activation readout policy are binding artifact identities.
- Pre-realization execution-boundary states and post-realization answer states are separate populations.
- Steering effectiveness does not establish semantic intent, correctness awareness, workspace identity, or safe control.
- Tail subtraction, centering, and residualization create separately admitted artifacts.
- Activation readability, activation controllability, behavioral controllability, objective controllability, erasure, monitor evasion, and policy defeat are separate claims.
- Input-only and naturally occurring text can suppress measured activations without proving removal of the associated behavior.
- Random-direction and natural-text baselines are mandatory for target-specific suppression claims.
- MoE route, cache, recurrent-state, and source-selection identities must be studied jointly without conflation.
- Existing privacy, sealed-data, verifier, provenance, derivative, resource, intervention, and production gates remain intact.
- Q35Q remains blocked.

## Still unproven

- Independent reproduction of either triggering paper.
- Release and immutable admission of attributable implementations.
- Generality of execution-boundary steering signals across models, tasks, token policies, or source contexts.
- That tail subtraction isolates a semantic or causal feature.
- That evaluation-associated directions represent stable evaluator belief.
- Erasure of information after input-side activation suppression.
- Objective behavioral mitigation from suppressing a readable latent.
- Robustness of any jLens monitor to adaptive or naturally occurring input-side evasion.
- Transfer to Qwen3.5, Qwen3.6, Agents-A1-4B, or Agents-A1-35B.
- Incremental router or Jacobian-Lens value beyond source-aware logits, confidence, trajectory, hidden-state, spectral, memory, program-state, route, and verifier comparators.
- Complete Q35Q runtime, loader, tensor-consumption, expert-ordering, forward, or derivative admission.
- Safe steering, prompt rewriting, early exit, truncation, retry, repair, forced routing, activation editing, reward shaping, or production deployment.

The research program remains unfinished.
