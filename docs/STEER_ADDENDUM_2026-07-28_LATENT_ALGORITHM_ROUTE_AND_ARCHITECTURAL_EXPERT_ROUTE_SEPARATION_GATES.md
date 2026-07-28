# STEER ADDENDUM — Latent algorithm route and architectural expert-route separation gates

Date: 2026-07-28

Status: binding protocol addendum. This file does not reopen M38E, advance Q35Q, authorize model or GPU execution, permit hidden-state or router capture, fit a Jacobian Lens, open sealed labels, authorize intervention, or weaken any privacy, provenance, verifier, derivative-parity, resource, production, or stop rule.

## Program state remains unchanged

- M38E remains terminally closed as `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains exact-target-runtime and loader admission for the Qwen3.5-MoE GPTQ derivative fixture.
- GitHub reports this repository as public. Repository commits remain limited to aggregate program-control records and public-source engineering code or tests.
- No prompts, outputs, token IDs, per-example labels, hidden states, route arrays, expert outputs, Jacobians, or intervention traces may be committed.

## Material public evidence

The COLM 2026 paper **Grounding latent algorithm routing in transformer reasoning**, arXiv `2607.24471v1` submitted 2026-07-27, studies controlled in-context regression tasks whose latent regimes favor ridge-like, lasso-like, Huber-like, or kNN-like solver families.

The authors define a behavioral route proxy by assigning each model output to the closest solver-family output. Across dense decoder-only transformers trained from scratch at 44M–612M parameters, the paper reports that a 306M model closes 80.9% of the oracle-routing gap and reaches route F1 84.1. Route probes peak in middle layers before answer probes, and matched activation patches can shift the closest-solver family while largely retaining answer quality.

A Switch-MoE diagnostic reports that explicit expert routing improves task and route-proxy metrics, but expert identity is only partially aligned with the oracle solver family. For the reported 306M-equivalent top-1 condition, expert purity is 76.9 and normalized expert mutual information is 0.49. The top-2 condition activates more computation and is not an exact FLOP or active-parameter match.

The paper explicitly limits its claims to the controlled benchmark. It does not establish a discrete symbolic router, universal latent algorithm selection in pretrained LLMs, natural-language reasoning transfer, or correspondence between activation-level route variables and architectural MoE expert routes.

The linked public repository is pinned at `xiangbo05/RouteBench@c32d4b91954f6596c698244f2016dfb85da3ba11`. It currently contains a release scaffold and states that benchmark code, configurations, probes, patching utilities, MoE diagnostics, and reproduction scripts are forthcoming. No independent reproduction artifact is presently admitted.

Primary sources:

- https://arxiv.org/abs/2607.24471
- https://github.com/xiangbo05/RouteBench/commit/c32d4b91954f6596c698244f2016dfb85da3ba11

## Binding ontology: distinct route objects

Future work must keep the following objects separate:

1. **Latent regime:** the task-generating condition or structure that makes one solver family preferable under a frozen benchmark definition.
2. **Oracle solver-family identity:** the family selected by a frozen external risk or outcome rule.
3. **Behavioral route proxy:** the family whose output is closest to the model's completed output under a frozen distance function.
4. **Hidden-state route prediction:** a probe or readout predicting a route label from an internal state.
5. **Activation-level route direction:** a fitted direction or subspace whose intervention changes route-proxy behavior.
6. **Architectural router state:** router logits, margins, probabilities, top-k selection, shared-expert terms, capacity state, and dispatch metadata.
7. **Executed expert route:** the exact ordered expert set and weights actually used at each routed layer and token.
8. **Expert contribution:** the expert outputs or residual contributions under the admitted execution path.
9. **Objective task outcome:** independently verified correctness, utility, safety, or task completion.
10. **Control policy:** any decision to continue, stop, reroute, patch, suppress, retry, or alter computation.

Evidence about one object does not establish identity with another.

In particular:

- A closest-solver behavioral proxy is not ground truth for a discrete internal route.
- A hidden-state probe predicting that proxy is not evidence that the model executes the named solver.
- A target-selective activation patch is functional evidence for the patched representation under the frozen intervention, not proof of a complete algorithm-selection mechanism.
- Architectural expert selection is not a semantic solver-family label.
- Expert purity or mutual information below one is evidence against one-expert/one-algorithm identity, not noise to be ignored.
- Objective correctness is not implied by solver-family consistency, answer retention, route stability, or expert specialization.

## Completed-output proxy and leakage gate

The behavioral route proxy in RouteBench is computed from the model's completed answer. It is therefore unavailable at earlier prospective monitoring boundaries unless an independently available prefix-compatible label is defined.

Future studies must freeze and report:

- the solver bank and every solver implementation;
- the distance or scoring rule used to assign the behavioral proxy;
- tie handling and route-margin exclusions;
- whether the proxy uses a completed output, intermediate answer, hidden verifier state, or future trajectory;
- whether the oracle family is defined from population risk, per-example loss, a generated target, or a privileged statistic;
- the exact boundary at which each label becomes available;
- all training, calibration, validation, and sealed populations.

A route label derived from the completed output, final verifier, future token, or future trajectory may be used for retrospective analysis or training labels under the sealed-data rules. It may not be presented as an online feature available before that boundary.

## Solver-bank identifiability gate

A closest-member assignment is conditional on the chosen solver bank. Apparent route recovery can change if the bank omits a better family, contains correlated representatives, or discretizes a continuous strategy.

Required controls include, where compatible:

1. Alternative representatives within each claimed family.
2. Continuous mixtures and input-conditioned mixtures.
3. A richer bank containing plausible omitted strategies.
4. Random and permuted family labels.
5. Margin-stratified analyses and explicit ambiguous-route rates.
6. Multiple output-distance functions.
7. Equivalent-answer and multiple-valid-solution handling.
8. Regime changes under fixed serialization.
9. Semantics-preserving format, lexical, support-order, and paraphrase perturbations.
10. Continuous regime transitions rather than only separated endpoints.

A result that survives one fixed finite solver bank establishes bank-relative route-like behavior, not exhaustive algorithm identification.

## Architectural MoE correspondence gate

For Agents-A1 or another MoE, latent algorithm-route claims require direct measurement of both activation-level and architectural routing objects. At minimum, report:

- oracle solver-family identity;
- behavioral route proxy and margin;
- hidden-state route-probe output;
- architectural router logits, margins, entropy, and top-k selection;
- ordered executed experts and weights;
- shared-expert contribution;
- expert purity and mutual information with the frozen route labels;
- within-regime and within-task route variation;
- cross-layer route ancestry and transition surprise;
- objective outcome and verifier state separately.

Required analyses include:

1. Whether architectural routes predict the oracle family beyond task metadata and boundary hidden states.
2. Whether hidden-state route probes add value beyond architectural router telemetry.
3. Whether architectural routes add value beyond the behavioral proxy and deterministic regime statistics.
4. Whether route-proxy changes occur without architectural route changes.
5. Whether architectural route changes occur without route-proxy changes.
6. Whether selected experts remain mixed across solver families.
7. Whether solver-family information resides in dense attention, shared experts, routed experts, residual state, or combinations.
8. Whether route correspondence persists across layers, positions, seeds, prompts, quantization, and runtime changes.

No one-to-one expert semantic label may be assigned from majority purity alone.

## Exact-compute and architecture gate

Terms such as `equivalent`, `matched scale`, or `same backbone` do not establish equal compute.

Every dense-versus-MoE or top-k comparison must freeze and report:

- total parameters;
- active parameters per token;
- routed and shared expert counts;
- top-k cardinality and expert ordering;
- router and dispatch overhead;
- FLOPs at the measured sequence length;
- KV-cache, activation, communication, and memory traffic;
- capacity factors, token dropping, padding, and overflow behavior;
- precision, quantization, kernels, topology, batching, and scheduler;
- latency, throughput, peak memory, and energy where available.

A top-2 condition with greater active computation is a different compute condition. Accuracy, route F1, expert purity, or intervention effects may not be attributed solely to routing architecture without equal-compute controls or explicit qualification.

## Probe and intervention gate

Route-probe layer selection, subspace dimension, regularization, route labels, patch source/target pairs, patch magnitude, and all thresholds are model selection and must be frozen using training or discovery data only.

Required negative and matched controls include:

- label permutation;
- random directions and equal-dimensional random subspaces;
- same-route, wrong-route, and random-source patches;
- norm-matched and covariance-matched perturbations;
- task-, regime-, answer-, and format-matched controls;
- route-proxy-only, answer-only, metadata-only, hidden-state-only, and architectural-router-only predictors;
- non-route middle-layer directions with matched decodability;
- objective right-to-wrong and wrong-to-right transitions;
- full continuation, cache lineage, later-route divergence, and independent outcome verification.

Earlier probe peaks do not alone establish a causal route-before-answer sequence. They can reflect label geometry, layerwise linear separability, optimization, or information inherited from earlier computation.

Answer retention after an intervention is not objective correctness preservation. It must be accompanied by independently verified outcome, calibration, safety, and regression reporting.

## Agents-A1 scaling directive

The technically credible sequence is now:

1. Complete Q35Q exact-target-runtime provenance, strict loading, packed-tensor consumption, expert/fusion ordering, deterministic forward, activation-VJP, activation-JVP, and finite-difference admission.
2. Admit a tractable Agents-A1 checkpoint or bridge model under its exact tokenizer, task harness, runtime, and verifier.
3. Build a controlled mixed-regime task family with a frozen external solver bank, oracle rule, behavioral proxy, nuisance perturbations, and ambiguous-route policy.
4. Establish deterministic metadata, task-statistic, confidence, hidden-state, spectral, trajectory, memory, program-state, and external-verifier baselines.
5. Demonstrate bank-relative latent route prediction and nuisance robustness without using sealed outcomes or future information as features.
6. Separately admit Agents-A1-35B checkpoint, quantization, router, experts, shared experts, topology, cache, kernels, batching, scheduler, and capture path.
7. Measure architectural expert routes and latent algorithm-route objects jointly while preserving their separate identities.
8. Require architectural router telemetry to add sealed objective-outcome value beyond task statistics, hidden states, route proxies, confidence, trajectory, memory, program state, and verifiers.
9. Test whether router telemetry predicts route disagreement, route ambiguity, or objective failure prospectively rather than merely reconstructing the completed output.
10. Add sparse-feature or transcoder comparators when separately admitted.
11. Add Jacobian-Lens features only after exact derivative parity and only if they add sealed value over the complete cheaper latent-route, architectural-route, hidden-state, spectral, trajectory, memory, and verifier stack.
12. Keep activation patching, forced routing, early exit, truncation, retry, repair, steering, and production control under separate intervention and safety gates with full-compute fallback.

This sequence provides a direct test of whether Agents-A1's explicit expert routing corresponds to task-level computational strategy, rather than assuming correspondence from architecture.

## Privacy and sealed-data boundary

Latent route labels, expert routes, hidden-state probes, and task regimes can jointly increase reconstruction risk.

The following remain prohibited from this public repository:

- prompts, outputs, solver targets, and per-example route labels;
- per-token router logits, expert identities, weights, or route paths;
- hidden states, probe scores, patch vectors, expert outputs, or Jacobians;
- per-example objective outcomes, verifier labels, or split assignments;
- reconstruction, membership, attribute-inference, or covert-channel artifacts tied to private tasks.

Only preregistered aggregate records may be committed after all existing privacy, leakage, retention, sealed-data, and commit-safety checks pass.

## Current blocker and execution order

This addendum does not change the active blocker. Required order remains:

1. Execute the composed Transformers provenance adapter in the exact target runtime.
2. Freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` as one immutable tuple.
3. Bind the actual GPTQModel/Defuser loader and complete executable source closure.
4. Run strict synthetic Qwen3.5-MoE loading.
5. Prove one-time packed-tensor consumption and exact expert/fusion ordering.
6. Prove deterministic forward, activation-VJP, activation-JVP, and finite-difference parity.
7. Pass the complete Phase-0 conjunction before weight staging or GPU authorization.

## Established versus unproven

Established only as external public evidence:

- Dense transformers trained on one controlled benchmark can exhibit bank-relative, nuisance-robust route-like behavior.
- Route-proxy information can be linearly decoded in middle-layer residual states in the reported models.
- Matched activation patches can selectively alter bank-relative route-proxy behavior under the reported conditions.
- Explicit Switch-MoE expert identity is only partially aligned with oracle solver-family identity in the reported diagnostic.
- The current public RouteBench repository is a release scaffold, not a complete reproduction artifact.

Unproven for this program:

- Independent reproduction of RouteBench.
- Universal or natural-language latent algorithm routing.
- A discrete symbolic internal router.
- Identity between hidden route directions and architectural MoE routes.
- One-expert/one-algorithm specialization in Qwen3.5, Qwen3.6, or Agents-A1.
- Prospective correctness prediction from latent-route or expert-route telemetry.
- Incremental router or Jacobian-Lens value beyond cheaper comparators.
- Q35Q target-runtime, loader, tensor-consumption, ordering, forward, or derivative admission.
- Safe early exit, truncation, retry, repair, forced routing, activation steering, or production deployment.

The research program remains unfinished.
