# STEER ADDENDUM — Forked-Future Causal-Interface, Architecture-Competition, and False-Shared Gates

Date: 2026-07-31
Parent remote head: `36068ac9a38937ecf871a5e5bba89ff5565a0795`

Status: binding future-protocol correction; no current execution authorization.

This addendum is cumulative with `CODEX_AUTOSTEER.md`, `steer.md`, and every later binding correction. It preserves every privacy, sealed-data, canonical-verifier, provenance, exact-set, exact-gradient, parity, nuisance-control, multiplicity, resource-accounting, cleanup, intervention, and production-gating rule.

It does not constitute Q35Q admission, authorize model-weight staging, tensor-payload retrieval, GPU execution, hidden-state capture, router capture, expert-path capture, cache capture, JVP, VJP, Jacobian fitting, sealed evaluation, early exit, truncation, retry, repair, activation writing, route editing, tool suppression, external action, or production use.

GitHub reports this repository as public. Only aggregate public-source program control may be recorded here. Prompts, completions, benchmark items, target values, future-operation assignments, per-example signatures, parser traces, token IDs, hidden states, routes, expert paths, caches, Jacobians, gradients, verifier labels, private runtime facts, credentials, and sealed outcomes remain prohibited.

## Primary external evidence

Ma et al., “Hidden APIs in Language Models: Discovering Reusable Causal Interfaces from Forked Futures,” arXiv `2607.27617v1`, submitted 2026-07-30, addresses a central identification problem in semantic-workspace claims:

> Two hidden states can produce the same current answer while supporting different future computations.

The paper defines a **forked-future causal signature** by caching a prefix state before a future operation is revealed, then measuring the response distribution produced when different operations are applied. It compares four candidate interface architectures:

1. **Shared:** one operation-agnostic compact code reused by multiple future operations;
2. **Local:** separate operation-specific interfaces;
3. **Mixture:** operation-conditioned interpolation between shared and local components; and
4. **Distributed:** relevant information retained across multiple components without a privileged bottleneck.

The candidates compete under prequential causal description length subject to held-out future-signature fidelity and matched-capacity constraints. The paper reports:

- Sharedness Gain of `0.216` nats on Qwen2.5-1.5B and `0.294` nats on Llama-3-8B relative to the nearest non-Shared alternative;
- positive-direction Sharedness Gain in an additional backbone sweep;
- figure-aligned Shared transplantation scores of target correctness `0.91`, locality `0.88`, and copy preservation `0.85`;
- API-aligned path mediated fraction `0.749` versus `0.150` for matched null paths; and
- blind recovery of `14/16` synthetic model-organism architectures, including one false Shared classification among twelve non-Shared organisms.

The paper explicitly limits its conclusion to an economical reusable causal interface within the tested operation banks, candidate architectures, interventions, and held-out futures. It does not claim a unique or universal global workspace.

Primary source:

- https://arxiv.org/abs/2607.27617v1

No attributable immutable public implementation revision, environment lock, released dataset assignment, or independent reproduction was located during this review. The evidence is paper-level only.

## Binding interpretation

The new evidence supports a missing identification rule:

> A representation may be called a reusable shared causal interface only after it beats prospectively specified Local, Mixture, and Distributed alternatives on future-defined sufficiency, complexity, and causal-use tests.

Current-answer decodability, verbalizability, cross-task probe accuracy, low rank, cross-layer stability, transplantation, or behavioral steering alone is insufficient.

The following objects are distinct and may not be renamed into one another:

1. current output or current-answer distribution;
2. prefix state before a future operation is selected;
3. future-operation identity;
4. operation-conditioned response distribution;
5. complete future causal signature over an operation bank;
6. compact code fitted to that signature;
7. candidate interface architecture;
8. representation readability;
9. representation causal sufficiency;
10. representation causal necessity;
11. naturally used producer-consumer path;
12. intervention-accessible or patchable path;
13. objective task correctness;
14. continuation utility;
15. semantic-workspace claim;
16. early-exit, routing, action, or production policy.

A code that predicts the current answer is not thereby future-sufficient. A future-sufficient code is not thereby Shared. A Shared code is not thereby naturally consumed. Natural consumption is not objective correctness awareness. None of these objects authorizes control.

## Fork-timing and operation-leakage gate

Every future causal-interface study must establish the temporal fork exactly.

Freeze and verify:

- the producer prefix, token position, layer, residual boundary, route state, cache state, recurrent state, tool state, memory state, and environment state;
- the instant at which the prefix state is captured;
- the instant at which the future operation is sampled or revealed;
- the operation bank and sampling distribution;
- proof that operation identity, operation-specific prompt text, answer scaffold, parser marker, target label, verifier result, and future branch state were unavailable when the producer state formed;
- the exact consumer path through which the operation later accesses the state;
- branch isolation, cache lineage, and deterministic replay; and
- failure behavior when timing or lineage cannot be certified.

The future operation must be assigned only after the measured producer state exists. An operation label included in the original prompt, template, routing metadata, cache, branch ID, or hidden-state fitting input invalidates a strict forked-future claim.

Required leakage controls include:

1. semantic-collision pairs: same current answer, different valid future transitions;
2. lexical anti-collision pairs: different surface forms, matched latent relation and future signature;
3. operation-label permutation;
4. prompt-template and entity-name permutation;
5. answer-scaffold and formatting controls;
6. same-prefix repeated forks with independently sampled operations;
7. negative controls where operation identity is deliberately leaked and the detector must identify the inflation; and
8. source-item-disjoint assignment of all branches descending from one prefix.

A nominal “pre-operation” hook is not evidence. The executed dataflow, cache contents, and assignment order must be tested.

## Future-signature identity gate

A future causal signature is an executable target artifact and must be frozen before fitting.

Record at minimum:

- operation-bank membership and inclusion criteria;
- operation sampling probabilities;
- consumer prompt or action schema;
- output distribution used: full vocabulary, frozen top-k support, answer-token distribution, sequence likelihood, verifier distribution, tool outcome, or another prospectively specified object;
- temperature, decoding, normalization, truncation, and support alignment;
- divergence or fidelity metric;
- per-family and tail fidelity thresholds;
- unseen-operation, unseen-composition, unseen-generator, and unseen-family splits;
- branch count and correlation structure per prefix;
- model, checkpoint, tokenizer, template, runtime, precision, quantization, cache, route, kernel, topology, and scheduler identity; and
- complete compute and storage cost.

A signature defined only by the current answer, one future operation, one task family, or post-hoc selected output coordinates cannot support a reusable-interface claim.

Mean fidelity alone is insufficient. Report mean, worst-family, and tail fidelity so a compact code cannot win by discarding one difficult operation family.

## Candidate-architecture competition gate

Shared is one candidate hypothesis, not the default interpretation.

Every compatible semantic-workspace study must prospectively compare Shared against technically appropriate alternatives that include, at minimum:

1. **Local:** operation-specific codes and consumers;
2. **Mixture:** shared and local components with operation-conditioned gating;
3. **Distributed:** no privileged compact bottleneck;
4. random, PCA, ICA, output-aligned, answer-token, direct-lens, sparse-feature, and matched-rank controls where technically compatible; and
5. raw hidden-state and transparent behavioral baselines.

Freeze for every candidate:

- encoder and reconstructor class;
- operation access rules;
- rank, sparsity, gate count, width, and component count;
- trainable parameter count;
- optimizer, update budget, early stopping, and seeds;
- prequential block order and information available at each block;
- complexity code or penalty;
- fidelity threshold;
- layer and position selection procedure; and
- all validation and sealed-test decisions.

Capacity must be matched where technically possible. Unavoidable excess capacity must be charged rather than ignored.

A Shared candidate is supported only when it satisfies the frozen future-fidelity contract and has lower held-out causal description length than every admitted non-Shared alternative. A positive complexity advantage without fidelity is failure. Better fidelity obtained only by materially greater capacity is not Sharedness evidence.

## Held-out futures and composition gate

The interface must be evaluated on futures not used to fit its representation.

Required held-out conditions, where applicable, include:

- unseen operations from known families;
- unseen two-step and multi-step compositions;
- unseen prompt or generator templates;
- unseen entities and relation vocabularies;
- unseen natural task families;
- longer horizons than the fitting distribution;
- tool, retrieval, memory, verifier, and environment consumers not used during fitting; and
- model, checkpoint, runtime, and precision transfer only as separately labeled replication conditions.

All future branches from one source prefix remain in one partition. Operation selection, rank selection, layer selection, threshold selection, architecture selection, and code interpretation must not use sealed future branches.

Success on interpolated operations does not establish systematic reuse. Failure on a held-out family does not establish absence of useful information; it restricts the admitted interface scope.

## Ground-truth falsification and false-Shared gate

A method designed to discover Shared interfaces must prove that it can reject Shared when the ground truth is non-Shared.

Before applying the method to an unknown model, evaluate blind model organisms or equivalent synthetic systems implementing at least:

1. Shared communication;
2. Local operation-specific communication;
3. Mixture communication; and
4. Distributed communication without a privileged bottleneck.

Freeze:

- organism architecture and training procedure;
- seeds and sample sizes;
- hidden width, depth, vocabulary, and operation bank;
- class balance;
- architecture-selection rule;
- false-Shared tolerance;
- complete confusion matrix; and
- path-overlap and causal-recovery metrics.

Report the non-Shared-to-Shared error rate explicitly. Zero observed false positives may not be claimed when the sample size cannot resolve the tolerance. A method that exceeds its preregistered false-Shared bound is not admitted for semantic-workspace discovery, even if it performs well on naturally trained models.

The paper’s reported one false Shared classification among twelve non-Shared organisms is evidence of nontrivial discrimination and evidence that the method is not perfectly specific. It is not a passed universal false-positive guarantee.

## Causal transplantation, locality, and copy-preservation gate

A reusable interface must preserve intended causal content without broad donor overwrite.

Future transplantation studies must separately report:

- target relation or state-update correctness;
- preservation of prospectively specified non-target state;
- donor-content copy rate;
- target correctness, locality, and copy preservation as separate metrics;
- any composite only alongside its constituents;
- same-family, cross-family, and matched-random donors;
- matched insertion layer, position, difficulty, output length, code norm, and intervention load;
- operation consistency across multiple unseen consumers; and
- full objective, parser, verifier, route, cache, and environment effects.

A transplant that changes the target output while copying donor-specific entities or damaging unrelated state is not evidence of a clean reusable interface.

Cross-family transfer may reflect partial structural overlap, generic layer compatibility, or shared low-level mechanics. It does not establish universal semantic exchangeability.

## Natural-use, mediation, and patchability gate

Intervention accessibility and natural causal mediation are separate objects.

A claim that the model naturally uses the interface must include, where technically compatible:

- necessity under selective blocking or ablation;
- restoration by reintroducing the admitted code;
- producer-consumer path mediation;
- multi-consumer blocking;
- threshold-free path ranking as well as frozen thresholds;
- null paths matched on producer-consumer distance, rank, activation norm, intervention load, and baseline patchability;
- route-, cache-, and recurrent-state controls; and
- repeated-seed path stability.

A direction that can be patched into a model is not necessarily a direction the model naturally uses. A path that carries an effect is not necessarily unique, minimal, semantically pure, or sufficient for the complete task.

Mediated fraction must not be interpreted as a percentage of “reasoning,” “understanding,” consciousness, or objective correctness unless those targets are separately defined and admitted.

## Semantic-workspace claim boundary

The strongest admissible conclusion from a successful future-defined architecture competition is:

> Within the frozen model, runtime, producer boundary, operation bank, candidate architecture set, and intervention protocol, a compact Shared representation provides the shortest admitted future-sufficient code and passes the declared causal-use tests.

It does not establish:

- a unique interface;
- a universal interface over untested future operations;
- a complete global workspace;
- conscious access or self-awareness;
- model-native verbal introspection;
- objective correctness awareness;
- error awareness;
- plans, intentions, or evaluator awareness;
- causal sufficiency for the whole trajectory;
- semantic purity;
- safe early exit, retry, repair, steering, routing, action, or production control.

The term `semantic workspace` may be used only with the exact frozen operation and causal scope. `Global workspace`, `reasoning bus`, `metacognitive state`, and `correctness channel` require separate evidence.

## Monitor and Jacobian-Lens consequence

Future hidden-state, router, expert-path, semantic-workspace, or Jacobian monitors must distinguish:

1. current-answer decoding;
2. future-signature prediction;
3. architecture classification;
4. objective correctness prediction;
5. continuation-utility prediction;
6. error localization;
7. stopping or retry policy utility; and
8. causal control.

A Jacobian Lens may make a state output-readable while failing to preserve the complete future signature. A compact future-sufficient interface may exist outside the chosen output-readable basis. The two methods are comparators, not synonyms.

Where technically compatible, future M37J work must add:

- same-current-answer/different-future controls;
- forked-future signature prediction;
- Shared, Local, Mixture, and Distributed architecture alternatives;
- matched-rank raw-state, direct-lens, Jacobian-Lens, output-gradient, sparse-feature, and random controls;
- held-out future operations and compositions;
- model-organism false-Shared evaluation; and
- transplantation, locality, copy-preservation, necessity, restoration, and mediation tests before any reusable-interface claim.

The existing H1/H2 error and truncation hypotheses remain separate. A feature can predict objective failure without constituting a reusable shared interface, and a reusable interface can fail to predict objective failure.

## MoE and router boundary

For architectural MoEs, Shared hidden-state interfaces, shared router patterns, and shared expert paths are different hypotheses.

Future compatible studies must separately compare:

- a Shared residual-state interface with operation-agnostic encoding;
- operation-local residual interfaces;
- mixture or gated residual interfaces;
- distributed residual representations;
- per-layer router logits and selected experts;
- complete cross-layer expert paths;
- shared-expert and routed-expert contributions;
- recurrent or hybrid-attention state;
- route-held-fixed hidden-state comparisons;
- hidden-state-matched route alternatives; and
- serving topology and expert-placement effects.

A common route pattern may reflect capacity management or token statistics rather than a reusable semantic interface. A Shared residual code may be consumed through different experts for different operations. An operation-local expert route may still read a shared upstream state.

Router telemetry must add sealed objective value beyond the admitted future-signature, hidden-state, transparent trajectory, parser, confidence, and verifier controls before any correctness or stopping claim.

## Agents-A1 scaling consequence

The technically credible sequence is now:

1. Complete Q35Q production-runtime provenance, exact loader admission, strict synthetic loading, one-time packed-tensor consumption, expert/fusion ordering, deterministic forward parity, activation-VJP parity, activation-JVP parity, and finite-difference parity.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, templates, parser, hybrid state, cache, tool harness, memory policy, environment, verifier, and runtime.
3. Define small replayable operation banks that are sampled only after a prefix state forms, beginning with deterministic query, compare, verify, update, tool-result interpretation, and retrieval-evidence consumers.
4. Establish same-current-answer/different-future and different-surface/same-future controls.
5. Compare Shared, Local, Mixture, and Distributed interfaces under matched capacity, prequential causal description length, and frozen future-fidelity thresholds.
6. Require unseen-operation, unseen-composition, unseen-template, and unseen-family evaluation.
7. Run blind model-organism false-Shared tests before interpreting naturally trained Agents-A1 states.
8. Require transplantation target correctness, locality, copy preservation, necessity, restoration, and matched-null mediation before a reusable-interface claim.
9. Keep the entire Agents-A1-4B phase passive or replay-only, production-disconnected, and free of irreversible external actions.
10. Separately admit Agents-A1-35B quantization, router transformations, shared and routed experts, expert-reduction semantics, hybrid state, caches, kernels, topology, scheduler, telemetry, tools, memory, subagents, environment, and verifier.
11. Repeat the architecture competition under native 35B execution rather than transferring ranks, layers, codes, consumers, or thresholds from 4B.
12. Compare residual Sharedness with router and expert-path structure without assuming they coincide.
13. Require router, expert, hidden-state, and Jacobian features to add sealed objective value beyond transparent future-signature, trajectory, parser, confidence, self-verdict, repeated-sampling, and verifier baselines for the exact target claimed.
14. Preserve native full-compute execution, complete native state, and independent action verification as fallback.

This sequence creates a technically credible path to testing a reusable interface on Agents-A1. It does not authorize current Agents-A1 execution.

## Intervention and production boundary

This addendum authorizes no intervention.

No activation transplant, ablation, projection removal, steering, route forcing, expert dropping, cache rewriting, early exit, truncation, retry, repair, tool suppression, memory editing, answer commitment, episode termination, external action, or production enforcement may be enabled from this evidence alone.

Intervention requires a separately preregistered executable artifact, exact runtime identity, sealed objective evaluation, counterfactual utility evidence, tail-risk analysis, independent verifier, safe fallback, rollback, auditability, and explicit production authorization.

## Current engineering blocker remains unchanged

The active milestone remains complete production-path Q35Q provenance and runtime admission:

1. bind imported files to immutable distribution-ownership records;
2. derive complete executable-source closure from actual live runtime objects;
3. detect monkeypatching, shadow imports, and runtime substitution in a clean subprocess;
4. bind the exact GPTQModel/Defuser loader and conversion entry;
5. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` as one immutable tuple;
6. run strict synthetic Qwen3.5-MoE quantized loading;
7. prove one-time packed-tensor consumption;
8. prove exact expert and fusion ordering;
9. prove deterministic forward parity; and
10. prove activation-VJP, activation-JVP, and finite-difference parity.

No model-weight staging or GPU execution is authorized before the complete Phase-0 conjunction passes.

## Established by this correction

- Current-answer equality does not establish future-computation equivalence.
- A reusable interface must be defined against a prospectively frozen bank of future operations.
- Shared is one candidate architecture and must beat Local, Mixture, and Distributed alternatives under matched fidelity and complexity.
- Future operations must be selected after the measured producer state forms.
- Held-out operations and compositions are required to test reuse rather than interpolation.
- Semantic-workspace discovery methods require blind non-Shared model organisms and an explicit false-Shared rate.
- Transplant target correctness, locality, and copy preservation are separate outcomes.
- Intervention accessibility and natural causal mediation are separate claims.
- A reusable shared causal interface is not automatically a correctness, error, metacognitive, stopping, routing, or control interface.
- Existing privacy, sealed-data, verifier, provenance, derivative, intervention, and production gates remain intact.
- Q35Q remains blocked.

## Unproven

- Independent reproduction of arXiv `2607.27617v1`.
- Admission of its data generators, operation assignments, model revisions, code, dependencies, runtime, result artifacts, and statistical implementation.
- Satisfaction of a preregistered false-Shared tolerance; the reported blind organisms include one non-Shared-to-Shared error.
- Generalization beyond the tested operation banks, structured task families, models, layers, ranks, and interventions.
- A unique or universal semantic workspace in any language model.
- A reusable causal interface in Qwen3.5, Qwen3.6, Agents-A1-4B, Agents-A1-35B, or comparable MoEs.
- Alignment between a reusable residual interface and MoE router or expert-path structure.
- Objective correctness, error, continuation-utility, or action-readiness value from the reported interface.
- Incremental Jacobian-Lens value beyond future-signature and architecture-competition controls.
- Complete Q35Q runtime and derivative admission.
- Safe early exit, truncation, retry, repair, adaptive routing, expert dropping, cache rewriting, steering, external action, or production deployment.

The research program remains unfinished.
