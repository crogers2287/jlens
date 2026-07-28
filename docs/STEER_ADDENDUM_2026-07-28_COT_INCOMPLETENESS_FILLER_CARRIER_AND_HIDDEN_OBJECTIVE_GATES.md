# STEER ADDENDUM — CoT incompleteness, filler-carrier, and hidden-objective gates

Date: 2026-07-28
Parent remote head: `3afe06d5a586ff2db0ffaa9984f4c655eab4dbd0`
Status: **binding protocol correction; design-only; no capture authorization**

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every later cumulative correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, derivative, runtime, GPU, intervention, rollback, and production-gating rule. It does not constitute Q35Q admission, authorize weight staging or GPU use, reopen M38E, permit Agents-A1 capture, or establish an internal jLens scientific result.

GitHub currently reports `crogers2287/jlens` as public. Only aggregate program-control records, public-source engineering material, code, and tests may be committed. Raw prompts, outputs, filler sequences, token IDs, hidden objectives, task records, hidden states, routes, expert identities, caches, Jacobians, labels, predictions, split assignments, credentials, and private environment details remain prohibited.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active milestone remains exact-target-runtime provenance and immutable GPTQ loader admission. This addendum corrects a future scientific and control boundary; it does not displace that engineering order.

## Triggering primary evidence

Baherwani, Goldstein, and Panda, `Not All LLM Reasoning is Visible in the Chain-of-Thought`, arXiv `2607.22925v1`, submitted 2026-07-24, reports a concrete output-trace incompleteness result:

- thirteen frontier models were evaluated across three synthetic reasoning tasks;
- semantically irrelevant filler tokens improved accuracy for multiple models, with reported gains up to thirteen percentage points;
- the effect depended on filler-token identity and varied by model;
- Claude Opus 4.5 reportedly used filler-token computation to satisfy a hidden modular-arithmetic constraint while preserving primary-task accuracy;
- reinforcement learning induced strong Qwen3-235B preferences among filler-token contents, but neither the reported RL nor supervised-fine-tuning condition produced a test-time filler benefit that persisted.

The inspected arXiv record does not identify an immutable attributable code and artifact release sufficient for independent reproduction. These are external author-supplied results, not jLens findings.

## Binding interpretation

The result changes a boundary not fully covered by ordinary chain-of-thought, pause-token, monitor-gaming, or recurrent-interface controls:

> Output tokens may provide computational positions and state transitions without providing a faithful semantic account of the computation performed through them. Therefore visible chain-of-thought, filler text, token semantics, latent computation, hidden objectives, and objective outcomes are separate scientific objects.

The following may not be renamed into one another:

1. visible chain-of-thought text;
2. emitted token identities and positions;
3. human semantic interpretation of those tokens;
4. hidden-state and cache evolution caused by those tokens;
5. attention and route lineage caused by those tokens;
6. primary task objective;
7. secondary or hidden objective;
8. model self-report about either objective;
9. monitor prediction;
10. independently verified outcome;
11. intervention or stopping policy;
12. production decision.

A coherent, benign, irrelevant, empty, repetitive, or absent visible rationale does not establish absence of consequential computation. A hidden-state or router signal correlated with filler use does not establish that the signal reveals the computation's semantic content or objective.

## Chain-of-thought completeness gate

No compatible study may assume that visible chain-of-thought is a complete transcript of the model's relevant computation.

Claims that a model did not represent, optimize, plan for, or act on a factor require evidence beyond absence of that factor from visible reasoning text. At minimum, compatible work must distinguish:

- computation explicitly stated in the visible trace;
- computation inferable from token-level behavior but not stated;
- computation detectable only through forward internal telemetry;
- computation established only through controlled intervention;
- behavior consistent with a hidden objective but not identifying its mechanism;
- objective success or failure under an independent verifier.

Chain-of-thought plausibility, length, grammaticality, semantic relevance, self-consistency, or agreement with a judge cannot by themselves establish reasoning completeness, faithfulness, harmlessness, or objective alignment.

A visible-trace monitor and an internal-state monitor are complementary instruments. Neither may be credited for information already available to the other, and disagreement must remain an explicit evaluation stratum.

## Filler tokens are active computational carriers

A token sequence described as `filler`, `pause`, `scratch`, `dummy`, `neutral`, `irrelevant`, or `non-semantic` is not a null intervention merely because humans assign it little task meaning.

Every filler condition must freeze and report:

- exact tokenizer revision and token IDs;
- decoded strings, Unicode categories, byte forms, whitespace, punctuation, and special-token status;
- token count, order, repetition pattern, positions, and placement relative to prompt, tools, observations, actions, and answer;
- embedding norms and model-output marginal frequencies;
- attention permissions, masking, positional encoding, cache construction, and target-loss inclusion;
- generation versus forced-insertion mechanism;
- hidden-state boundary and runtime used for any measurement;
- precision, quantization, kernels, batching, cache state, and serving topology;
- whether filler content is visible to evaluators, verifiers, tools, or downstream models;
- complete latency, token, cache, memory, bandwidth, and inference cost.

Changing filler identity, position, count, tokenizer, checkpoint, runtime, or cache policy creates a separate intervention condition. Semantic labels such as `irrelevant` do not establish computational equivalence.

## Required filler and compute-control matrix

Before assigning utility or safety significance to filler-mediated computation, compatible studies must compare, where technically feasible:

1. ordinary decoding with no added positions;
2. matched extra positions containing fixed repeated tokens;
3. random tokens drawn from a prospectively frozen distribution;
4. whitespace, punctuation, byte-fallback, unused, and ordinary lexical tokens;
5. semantically relevant explicit chain-of-thought of matched token count;
6. semantically irrelevant but lexically diverse text of matched token count;
7. shuffled token identities with positions preserved;
8. shuffled positions with token multiset preserved;
9. constant embedding, zero-state, mean-embedding, or other admitted carrier controls where the runtime permits them;
10. pause-token and carrier-token baselines with matched cache and compute;
11. fixed additional forward compute without extra externally visible text where technically available;
12. full-compute ordinary fallback.

The matrix must separate benefits due to additional sequential compute, token identity, position, semantic content, cache state, and altered decoding dynamics.

A gain from one filler string cannot be represented as a general benefit from `thinking time`. A null result for one filler string cannot establish absence of invisible computation.

## Primary and hidden objective gate

Primary-task performance and secondary-objective satisfaction are separate endpoints.

Any compatible hidden-objective study must freeze before outer evaluation:

- the primary task contract;
- the secondary constraint or objective;
- whether the target model can infer that constraint;
- objective-outcome verifiers for both endpoints;
- conflict, agreement, absent-objective, and permuted-objective conditions;
- filler, chain-of-thought, and no-extra-token conditions;
- monitor features, calibration, thresholds, and decision rules;
- multiplicity, clustering, minimum-effect, and stopping rules.

Required reporting includes the complete joint outcome table:

- primary success and secondary success;
- primary success and secondary failure;
- primary failure and secondary success;
- failure of both;
- visible disclosure versus nondisclosure of the secondary objective;
- monitor detection versus nondetection;
- objective outcomes after the monitor or evaluator is withheld or changed.

Preserved primary accuracy does not establish alignment when a secondary hidden objective is also being optimized. Detection of a hidden objective does not establish malicious intent, terminal preference, or safe intervention.

## Counterfactual and causal gate

Invisible-reasoning claims require counterfactual evidence beyond outcome correlation.

Compatible studies must prospectively test interventions that vary one object at a time where feasible:

- filler token identity with length and position fixed;
- filler position with token multiset fixed;
- hidden objective with the primary task fixed;
- primary task with the hidden objective fixed;
- visible rationale content with carrier compute fixed;
- carrier compute with visible text fixed;
- attention or cache access to filler positions;
- route and expert path under matched visible output;
- evaluator visibility and identity;
- monitor presence and absence.

The supported claim must remain at the narrowest level established. Token-sensitive performance establishes token-conditioned computation, not a decoded semantic algorithm. Hidden-objective success establishes behavioral capability under the tested intervention, not a universal covert-planning mechanism.

## Monitor-comparator and residual-value gate

Before hidden-state, router, sparse-feature, transcoder, directional-derivative, Jacobian, or semantic-workspace features receive incremental credit, compatible work must compare them against:

1. visible chain-of-thought content and structure;
2. token identities, counts, positions, repetition, and lexical statistics;
3. logits, entropy, margins, confidence, and finish reason;
4. direct and tuned lenses;
5. ordinary residual-state summaries;
6. frozen spectral hidden-state summaries;
7. bounded temporal-state and trajectory summaries;
8. cache, attention, and external program-state summaries where admitted;
9. deterministic objective verifiers and evaluator-belief controls;
10. router and expert-path telemetry as a separate block;
11. frozen combinations of cheaper preceding blocks.

An internal feature earns credit only for sealed objective-outcome increment beyond the complete observable-token and cheaper forward-only stack. Predicting filler identity, token count, model family, task family, hidden-objective condition, or evaluator wording is not by itself hidden-reasoning detection.

## Retrospective and prospective timing boundary

Completed-output analysis is retrospective unless every feature used by the decision existed at the claimed decision boundary.

Compatible studies must separately freeze:

- filler insertion time;
- feature-availability time;
- answer exposure time;
- hidden-objective exposure time;
- verifier-label time;
- monitor decision time;
- intervention time.

Future tokens, completed-answer identity, final filler content, verifier outcomes, or full-trajectory replay may not enter a prefix monitor, early-exit score, pre-action alarm, or online control claim.

A retrospective detector may be scientifically useful. It does not authorize early exit, truncation, retry, repair, abstention, route intervention, activation steering, reward shaping, or production enforcement.

## Adaptation and preference gate

Reinforcement learning, supervised fine-tuning, preference optimization, prompt search, filler search, or development-set selection creates a new adapted artifact or policy condition.

A learned preference among filler strings does not establish functional test-time use. Compatible adaptation studies must report:

- base and adapted checkpoint identities;
- exact filler corpus and selection process;
- training objectives and reward channels;
- train, calibration, and family-disjoint test populations;
- token-preference strength separately from task utility;
- held-out filler identities and tokenizer variants;
- primary and hidden-objective outcomes;
- paired baseline successes retained, repaired failures, and new regressions;
- complete training and inference cost;
- monitor-gaming and evaluator-belief controls.

Post-hoc selection of the filler string, model, task, layer, or hidden objective with the largest effect is exploratory and cannot support a confirmatory claim.

## MoE and Agents-A1 gate

Dense-model and proprietary-frontier-model results do not transfer to Agents-A1-35B or another quantized MoE.

A compatible Agents-A1 study must follow this order:

1. complete Q35Q production provenance, strict loading, deterministic forward parity, activation-VJP parity, activation-JVP parity, and finite-difference admission;
2. separately admit Agents-A1-4B and establish no-filler, explicit-CoT, fixed-compute, filler, token-statistic, confidence, trajectory, memory, program-state, residual-state, and spectral baselines;
3. freeze filler identities, counts, positions, tokenization, hidden-objective conditions, and objective verifiers before held-out evaluation;
4. establish whether filler effects persist across task families, output budgets, seeds, runtimes, and checkpoint revisions;
5. separately admit Agents-A1-35B checkpoint, tokenizer, quantization, router, experts, topology, kernels, cache, batching, and serving state;
6. capture route logits, selected experts, weights, expert ancestry, occupancy, load balance, overflow, dropped tokens, cache lineage, and downstream divergence for every admitted filler condition;
7. report visible-trace, token-statistic, hidden-state, spectral, router, sparse-feature, and Jacobian blocks separately;
8. require route telemetry to add sealed objective value after all cheaper token and hidden-state controls;
9. require Jacobian features to add sealed value after the complete route-aware stack;
10. keep no-intervention, full-compute fallback binding until a separate control protocol passes.

A filler condition that preserves visible text while changing routes is route-active. A route-stable condition can still perform consequential dense or within-expert computation. Neither visible-trace stability nor route stability establishes absence of a hidden objective.

## Claim boundary

A positive filler-token result may establish only that the exact frozen model and runtime can use the tested output positions in a way that changes an independently measured outcome.

It does not by itself establish:

- a human-interpretable hidden chain of thought;
- semantic faithfulness of internal coordinates;
- deceptive intent;
- a persistent hidden objective;
- an intrinsic workspace or reasoning stage;
- prospective correctness awareness;
- transfer across models, tokenizers, tasks, precisions, or runtimes;
- safe detection or intervention;
- production readiness.

A negative result must remain scoped to the exact tested filler family, model, task, runtime, and power. It may not be generalized to complete chain-of-thought faithfulness.

## Decision rule

The filler-carrier and hidden-objective branch advances only if it clears all existing provenance, privacy, sealed-data, verifier, nuisance, calibration, multiplicity, family-disjoint, minimum-effect, paired-regression, complete-cost, and locked-held-out gates.

A monitor branch advances only on sealed objective-outcome increment beyond visible reasoning, token identities, token statistics, confidence, residual-state, spectral, trajectory, memory, program-state, verifier, and route-aware comparators.

No result under this addendum authorizes capture, weight staging, GPU use, early exit, retry, repair, truncation, forced routing, activation steering, reward shaping, or production deployment. Q35Q remains blocked until the complete Phase-0 conjunction passes.
