# STEER ADDENDUM — Expert-scattering, serving-cost, and router-predictor gates

Date: 2026-07-18

Status: binding protocol addendum. This file does not reopen M38E, advance Q35Q, authorize scientific execution, or weaken any privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, production, or stop rule.

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- No weight staging, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized.
- GitHub currently reports this repository as public. Commits remain restricted to aggregate program-control records and public-source engineering code or tests.

## New public evidence

The July 14, 2026 preprint **Less Experts, Faster Decoding: Cost-Aware Speculative Decoding for Mixture-of-Experts** (`arXiv:2607.12696`) studies the systems cost created by routing during speculative verification.

Its bounded public method and findings include:

1. Verification cost for a sparse MoE depends on the union of experts activated by all draft tokens verified together, not only on token count or nominal active parameters per token.
2. Confidence-first draft selection can produce `expert scattering`: high-probability candidates may activate disjoint expert sets, increasing expert-weight memory traffic and reducing speculative-decoding gains.
3. EcoSpec trains a lightweight predictor of target-model expert activation and uses a dynamic expert buffer to score draft-tree candidates by acceptance likelihood divided by predicted marginal expert cost.
4. The target model retains ordinary lossless speculative verification; the proposal changes candidate selection before verification.
5. The paper reports evaluation on DeepSeek-V3.1 671B, Qwen3-235B-A22B, and GPT-OSS-120B, with reported end-to-end speedups up to `1.62x` and reduced active-expert footprints.

These are external public findings, not admitted results of this repository. No attributable public implementation was located during this review. The paper is an inference-systems study, not a correctness-monitor study. It does not establish error prediction, causal expert localization, safe early exit, or transfer to Agents-A1.

## Binding correction: routing has a systems-cost channel

Router telemetry can affect both prediction and execution cost. Future work must distinguish:

1. Route information used as a correctness feature.
2. Route information used to predict future expert demand.
3. Route information used to schedule, prefetch, cache, or select speculative candidates.
4. Route information produced only after the expensive target-model computation has already occurred.

A route feature that improves latency or expert reuse is not thereby a correctness signal. A route feature that predicts correctness is not thereby a useful scheduling signal.

## Expert-union accounting

Every future MoE efficiency or monitoring comparison must report, where technically available:

- unique experts touched per layer and decision step;
- union of experts touched across a speculative or batched verification group;
- selected versus actually executed expert identities;
- expert-weight bytes transferred or a validated proxy;
- expert-cache residency, hit rate, and eviction policy;
- dispatch, gather, and synchronization cost;
- verifier width, draft-tree width, and accepted-token length;
- monitor or predictor execution cost;
- end-to-end latency, throughput, accelerator-seconds, and memory.

Nominal active-parameter count, generated-token count, or monitor-head latency alone is insufficient.

## Serving-topology confounds

Expert-footprint and latency results are conditional on the serving system. The following must be frozen or explicitly stratified:

- tensor-parallel and expert-parallel topology;
- device count and interconnect;
- expert placement and replication;
- HBM capacity and bandwidth;
- expert offload, prefetch, and cache policy;
- batch size and batch composition;
- speculative method, draft model, and verification budget;
- quantization and kernel backend;
- sequence length and KV-cache state;
- concurrent tenants and scheduler policy.

A route statistic may correlate with latency because of cache state, batch composition, or placement rather than model-internal difficulty. Such a statistic cannot be described as a reasoning-error signal without within-topology correctness controls.

## Router-predictor admission and leakage controls

A lightweight expert predictor is a separate learned model and must receive its own immutable provenance and evaluation record.

The following must be frozen using training data only:

- target checkpoint, tokenizer, processor, quantization, and runtime;
- route-label extraction boundary;
- pre-Top-k versus executed-route target;
- predictor architecture, inputs, context window, and layer coverage;
- loss, sampling, class balancing, threshold, and calibration;
- expert-set approximation and marginal-cost function;
- speculative selection rule and trade-off coefficient.

Predictor training must not use sealed outcomes, verifier labels, future tokens unavailable at the decision boundary, or target routes obtained after the proposed action would have been taken.

Required reporting includes:

1. Per-layer and aggregate route-prediction quality.
2. Expert-set precision, recall, and union-size error.
3. Cost-prediction calibration.
4. Drift across tasks, modalities, checkpoints, runtimes, and quantizations.
5. Performance against frequency, occupancy, parent-route, token, and semantic baselines.
6. The complete cost of collecting route labels and training the predictor.

High route-prediction accuracy does not establish correctness prediction.

## Equal-quality and equal-compute controls

Efficiency comparisons must preserve output semantics or report quality changes separately.

For lossless speculative decoding, the ordinary target verifier remains the correctness authority. For any method that changes executed experts, skips experts, truncates layers, or suppresses candidates, losslessness cannot be assumed and a separate correctness and safety protocol is required.

Future monitor comparisons must include:

- baseline autoregressive or admitted production decoding;
- the same speculative method without route-cost selection;
- acceptance-only selection;
- occupancy-only and frequency-only expert-cost predictors;
- random cost predictors matched for overhead;
- exact-route oracle selection reported only as an oracle ceiling;
- equal-latency and equal-accelerator-budget comparisons.

A system may not claim monitor savings by omitting the predictor, telemetry, cache-management, replay, or offline route-labeling costs.

## Correctness-monitor confound

Expert scattering may correlate with longer reasoning, semantic diversity, multimodality, tool use, uncertainty, or hard examples. It may therefore appear predictive of failure without carrying incremental correctness information.

Any correctness claim based on expert-union size, cache misses, predicted expert cost, or route dispersion must control for:

- prompt and completion length;
- task family, modality, and language;
- trajectory phase and tool/action state;
- same-boundary logits, confidence, and entropy;
- selected hidden-state summaries;
- route occupancy, parent-route history, and coalition structure;
- serving topology and speculative width.

The primary claim must be sealed incremental correctness value after these controls. Otherwise the signal must be classified as workload or systems telemetry.

## Privacy and retention

Training a route predictor can require large token-by-layer route corpora. Those corpora may encode prompt content, token identity, task family, tool state, and outcome information.

The existing public-repository boundary remains binding. Raw route labels, per-example expert sets, draft trees, prompts, outputs, token IDs, hidden states, Jacobians, verifier labels, cache traces, and reconstruction artifacts must not be committed.

Any future external telemetry store requires a frozen purpose, data minimization, retention limit, access policy, reconstruction threat model, and separate authorization.

## Agents-A1 scaling directive

The technically credible systems-aware sequence is now:

1. Complete Q35Q runtime provenance and derivative admission.
2. Establish metadata, confidence, and selected hidden-state correctness baselines.
3. Capture minimal executed-route identity, weight, margin, and entropy only at frozen decision boundaries.
4. Measure route-capture overhead and active-expert union under the admitted serving topology.
5. Fit occupancy and parent-route baselines before any learned route predictor.
6. Evaluate a training-only lightweight route predictor first as a systems-cost estimator, without correctness claims.
7. Test route innovation, expert-union, and predicted-cost features for sealed incremental correctness value after workload and topology controls.
8. Compare memory-only, hidden-state, router, trajectory, and combined monitors at equal end-to-end cost.
9. Add Jacobian-Lens features only after exact derivative parity and after cheaper signals fail the incremental-value gate.
10. Keep speculative selection, abort, truncation, retry, escalation, expert skipping, forced routing, and activation steering under separate policy and safety gates.

This sequence prevents a large-MoE serving optimization from being misreported as internal error awareness while still exploiting routing locality when it demonstrably reduces total cost.

## Current blocker and execution order

This addendum does not change the active blocker. The required order remains:

1. Production-path upstream/runtime provenance composition.
2. Freeze the complete GPTQModel/Defuser/Optimum/Accelerate/PyTorch/CUDA/backend tuple.
3. Run a strict synthetic Qwen3.5-MoE GPTQ loader fixture.
4. Prove exact tensor consumption, expert ordering, and fusion identity.
5. Prove forward, activation-VJP, activation-JVP, and finite-difference parity.
6. Pass the complete adversarial Phase-0 conjunction.
7. Stage weights only after admission.
8. Obtain a separately authorized GPU-resource transition.
9. Prove full-model derivative parity.
10. Fit Q35Q under the frozen protocol.
11. Run sealed detection-only comparisons with systems-cost, topology, occupancy, dependency, semantic, and incremental-value controls.
12. Begin Agents-A1-native instrumentation only if Q35Q establishes incremental monitor value.

## Established versus unproven

Established only as external public evidence:

- Large-MoE speculative-verification latency can depend strongly on the union of experts touched by selected draft tokens.
- Confidence-first candidate selection can increase expert scattering and expert-weight memory traffic.
- A learned route predictor can be used to estimate marginal expert activation cost before target-model verification.
- Cost-aware selection can preserve standard target verification while reducing the predicted and measured expert footprint in the reported systems.

Unproven for this program:

- Q35Q admission or derivative parity.
- Reproduction of EcoSpec or availability of its implementation.
- Route-predictor accuracy, latency benefit, or cost calibration on Qwen3.5-MoE or Agents-A1.
- Correctness prediction from expert-union size, route dispersion, cache behavior, or predicted expert cost.
- Incremental router or Jacobian-Lens value over metadata, logits, hidden states, trajectory summaries, occupancy, coalition, and systems baselines.
- Safe early exit, abort, retry, escalation, speculative policy changes, expert skipping, forced routing, activation steering, or production utility.
