# STEER ADDENDUM — Speculative expert prefetch, transfer-only routing, and runtime-residency gates

Date: 2026-07-29
Parent remote head: `cfbfb51df6cdfd8591a4d31b9f33c6a20b8385af`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, cleanup, intervention, production-gating, and stop rule. It
authorizes no model retrieval, model execution, GPU use, telemetry capture,
Jacobian fitting, sealed evaluation, training, prefetching, expert offload,
routing modification, early exit, retry, repair, or production action.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains exact-target-runtime Q35Q loader and
derivative admission. This addendum changes future systems-telemetry,
prefetch-comparator, and runtime-accounting requirements. It does not displace
that milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and
public-source engineering material may be committed. Prompts, outputs, token
identities, per-example routes, predicted routes, expert identities, router
vectors, cache traces, transfer traces, hidden states, recurrent states,
verifier labels, sealed outcomes, model weights, credentials, host paths, and
private runtime facts remain prohibited.

## Triggering primary evidence

`SpecPrefetch: Parameter-Efficient Expert Prefetching for Sparse MoE Foundation
Models`, arXiv `2607.24787v1`, studies a lightweight learned predictor that uses
a current-layer representation to predict candidate experts for a later MoE
layer. The predicted candidates are intended to drive asynchronous expert
movement from slower storage into a faster device-resident cache while the
native router remains responsible for the executed expert route.

The paper separates prediction from execution conceptually:

- the predictor proposes likely future experts;
- a scheduler observes cache residency, pending transfers, queue state, and an
  estimated execution window;
- candidates may be prefetched before the target layer executes;
- the native router still selects the experts consumed by the model;
- false positives waste bandwidth or cache capacity; and
- false negatives fall back to ordinary on-demand expert loading.

The paper reports experiments on Qwen3-VL-30B-A3B and DeepSeek-VL2-Tiny,
including up to 20% decoding-throughput improvement on a Snapdragon 8 Elite in
an I/O-constrained condition. It also reports a hot-cache condition where the
prefetch system does not improve throughput. Expert-prediction recall is
therefore a proxy, not a runtime-benefit or correctness metric.

The public implementation is pinned for this correction at:

`wei390/SpecPrefetch@8f90af6eca103dc4b718173b73b72d37024790da`

The repository states that the main forward path keeps native teacher-router
execution and trains a separate future-expert predictor by default while the
backbone, experts, router, output head, and embeddings are frozen. It also
exposes an evaluation `fusion_mode` configuration, warns that checkpoints and
fusion modes must match, silently ignores obsolete second-horizon weights under
`strict=False`, and does not ship its training-data recipe or evaluation
datasets. Those facts prevent treating the released repository as a complete,
immutable transfer-only reproduction without additional admission evidence.

## Bounded interpretation

The evidence supports this narrow correction:

> Future-expert prediction, transfer scheduling, expert residency, executed
> routing, mixture weighting, mathematical model output, runtime speed, and
> independently verified task outcome are separate scientific and executable
> objects.

Predictability of the next layer's expert set does not establish semantic expert
identity, algorithm identity, objective correctness, causal route utility, or a
semantic workspace. A high expert-recall score does not establish that the
expert was resident before execution, that a stall was avoided, or that the
end-to-end system became faster.

A transfer-only prefetcher can in principle leave the model's mathematical
function unchanged. That noninterference is a claim requiring direct proof. A
prefetch implementation may still alter execution order, kernel selection,
precision, synchronization, cache construction, eviction, capacity behavior,
or fallback behavior. If predictor scores are fused into native routing, the
system is no longer transfer-only and becomes a separately admitted model and
control intervention.

The trained predictor, its checkpoint, source boundary, scheduler, cache policy,
storage layout, transfer runtime, and fallback path are executable artifacts.
They are not passive metadata.

## Binding object-identity gate

Every future expert-prefetch study must freeze and report these objects
separately where they exist:

1. source-layer activation boundary;
2. source token population and prefill-versus-decode condition;
3. source normalization, projection, and predictor input;
4. predictor architecture, rank, parameters, precision, and checkpoint;
5. prediction horizon and target-layer identity;
6. per-token predictor logits and normalization semantics;
7. token aggregation, masking, pooling, and batch reduction;
8. predicted candidate count, set, order, and confidence;
9. native target-layer router input;
10. native router raw, biased, and normalized scores;
11. native selected expert set, order, and consumed mixture weights;
12. shared-expert or always-on branches;
13. expert residency state at prediction time;
14. pending-transfer state and transfer queue;
15. eviction, deduplication, cancellation, and priority policy;
16. source storage tier and destination memory tier;
17. transfer stream, issue time, completion time, and synchronization;
18. on-demand miss path and fallback behavior;
19. physical expert dispatch and kernel path;
20. recurrent state, KV cache, and other model-state lineage;
21. final logits and generated output;
22. independently verified objective outcome; and
23. complete executable runtime identity.

A field called `predicted_experts`, `expert_recall`, `cache_hit`, `ready_recall`,
`prefetch_success`, or `speedup` does not satisfy this gate without proving which
object and boundary it represents.

## Transfer-only noninterference gate

A transfer-only claim requires all of the following:

1. the predictor and scheduler do not modify native router inputs, scores,
   biases, temperature, top-k selection, order, or mixture weights;
2. any fusion path is disabled and pinned, including explicit proof that the
   admitted configuration corresponds to `fusion_mode=none` or an equivalent
   no-fusion condition;
3. predictor outputs are consumed only by the storage-placement and transfer
   subsystem;
4. a prefetched miss cannot substitute a different expert, drop a token, change
   cardinality, reorder experts, alter capacity handling, or change weights;
5. a late transfer takes the same admitted on-demand path as the baseline;
6. a false-positive transfer cannot change mathematical model state;
7. native route indices, order, weights, expert outputs, shared-expert outputs,
   residual states, recurrent states, caches, logits, and verifier outcomes
   match the baseline within prospectively frozen tolerances; and
8. parity holds across cold, warm, and hot cache states, hit, miss, false
   positive, false negative, cancellation, eviction, restart, and concurrent
   transfer conditions.

If any predictor value enters the executed route, expert weighting, hidden-state
update, stopping rule, retry rule, or output policy, the condition is an active
intervention. Evidence from that condition may not be represented as
transfer-only prefetch evidence.

Token-level greedy equality is useful but insufficient by itself. The parity
suite must include exact route and weight identities, logits, intermediate state,
longer decode trajectories, batch and sequence-order variation, and repeated-run
determinism.

## Predictor supervision and artifact-admission gate

Future expert-route labels are retrospective training targets derived from a
teacher execution. They are available for supervised fitting but are not online
features at the earlier prediction boundary.

Every predictor study must freeze:

- teacher checkpoint and exact executable runtime;
- source and target layer identities;
- route-label extraction boundary;
- whether labels represent raw top-k, post-capacity execution, ordered experts,
  mixture weights, or another object;
- token inclusion and exclusion rules;
- prefill and decode populations;
- training, calibration, validation, and sealed partitions;
- loss terms, class weighting, negative sampling, ranking loss, and thresholds;
- candidate count and aggregation rule;
- optimizer, schedule, seed, precision, topology, and stopping rule; and
- predictor checkpoint digest and complete source closure.

No sealed outcome, held-out route, or production trace may influence predictor
training, candidate count, threshold, scheduler priority, eviction policy, or
fallback rule.

An external predictor checkpoint must pass the existing untrusted-artifact,
serialization, schema, dependency, and executable-runtime admission gates. A
repository that omits the training recipe or datasets is not a complete
reproduction package. Silent key dropping under `strict=False` is prohibited in
an admitted path unless every missing and unexpected key is prospectively
enumerated, justified, and fail-closed.

## Runtime-residency and scheduler gate

The systems claim depends on the complete residency and transfer process, not
only predictor recall. Every evaluation must freeze and report:

- expert-cache capacity and allocation unit;
- resident, pending, queued, cancelled, and evicted states;
- eviction and admission policy;
- page cache and host filesystem state;
- storage medium, host memory, interconnect, and device memory;
- measured bandwidth, latency, concurrency, and contention;
- transfer stream, priority, synchronization, and overlap policy;
- prefetch issue horizon and deadline calculation;
- duplicate requests and cross-batch reuse;
- on-demand loading and fallback behavior;
- expert size, packing, quantization, and decompression;
- prefill and decode separately;
- context length, batch size, sequence packing, and scheduler;
- single-user and multi-user workloads;
- p50, p95, p99, and maximum latency;
- throughput, exposed stall time, memory traffic, peak memory, and energy where
  available; and
- initialization, warmup, restart, and cache-reset procedure.

Required metrics remain separate:

1. set recall of predicted future experts;
2. weighted or ordered route recall;
3. expert ready-recall before execution;
4. cache-hit rate;
5. bytes transferred and wasted bytes;
6. evictions and displaced useful experts;
7. exposed transfer stall;
8. end-to-end latency and throughput; and
9. independently verified model outcome.

A simulated LRU reduction does not establish real-device speedup. A speedup under
cold storage does not transfer to a hot-cache workload. A higher prediction
recall can reduce performance if it increases contention, evicts useful experts,
or transfers candidates that miss their deadline.

Required systems controls include no prefetch, oracle future-expert prefetch,
random candidates, frequency-based prefetch, last-route reuse, adjacent-layer
route reuse, LRU-only, matched-byte transfer, matched-cache-pressure, and a
fully resident upper-bound condition where feasible.

## Privacy and public-repository boundary

Per-token predicted experts, native routes, route agreement, expert identities,
cache-residency sequences, transfer timestamps, queue contents, token identities,
hidden states, prompts, outputs, and verifier labels remain prohibited in the
public repository.

Only prospectively defined aggregate summaries may be committed after all
privacy gates pass. Aggregate statistics must not permit reconstruction of a
prompt, token sequence, expert path, user, task, or sealed outcome.

## Derivative and Jacobian consequences

A correctly implemented transfer-only prefetcher should not change the
mathematical function differentiated by Jacobian Lens. That expectation is not a
parity result.

Future derivative work under expert offload or prefetch must prove:

- identical native routes, mixture weights, and model states;
- forward parity under cache hits and misses;
- activation-VJP and activation-JVP parity;
- finite-difference parity;
- repeated-run determinism under asynchronous transfers;
- no derivative path through predictor or scheduler in the transfer-only
  condition; and
- unchanged derivative endpoints and held-fixed context identities.

If predictor scores are fused into routing, if a miss changes the selected
expert set, or if capacity behavior differs, the system is a changed
hybrid-discrete model. It requires separate route-boundary finite differences,
new model identity, new outcome evaluation, and separate intervention and
production authorization.

Predicted future-route telemetry may later be evaluated as a passive comparator,
but it does not become a correctness feature merely because it predicts expert
execution. It must add sealed objective-outcome value beyond current route,
router margins, confidence, token position, task difficulty, hidden-state,
spectral, trajectory, memory, program-state, and verifier controls.

## Agents-A1 scaling consequence

The technically credible sequence is:

1. Complete Q35Q exact-target-runtime provenance, strict loading, packed-tensor
   consumption, expert ordering, deterministic forward, VJP, JVP, and
   finite-difference admission.
2. Admit Agents-A1-4B as the dense bridge under its exact checkpoint, tokenizer,
   hybrid state, cache, harness, verifier, and runtime.
3. Establish deterministic, confidence, trajectory, hidden-state, spectral,
   memory, program-state, and verifier baselines.
4. Separately admit Agents-A1-35B's checkpoint, quantization, native router,
   routed and shared experts, hybrid state, cache, kernels, topology, batching,
   scheduler, and capture path.
5. Measure whether expert weight movement or residency is an actual bottleneck
   under the intended local or rented deployment before training a predictor.
6. If offload is necessary, first benchmark no-prefetch, fully resident where
   feasible, LRU/frequency reuse, adjacent-layer route reuse, random prefetch,
   and oracle prefetch under identical storage and cache conditions.
7. Train any future-expert predictor only on nonsealed training and calibration
   populations, with execution routing held fixed.
8. Prove transfer-only route, weight, output, recurrent-state, cache, verifier,
   VJP, JVP, and finite-difference parity.
9. Evaluate cold, warm, and hot cache states; prefill and decode; long context;
   batch and multi-user contention; tool-use and agent trajectories; and restart
   behavior.
10. Require end-to-end throughput or latency benefit after predictor,
    scheduling, transfer, cache pressure, and fallback overhead. Expert recall
    alone is not a scaling result.
11. Keep predicted route telemetry separate from completed-error monitoring and
    prohibit its use for adaptive routing, early exit, retry, repair, or
    correctness claims without separately preregistered evidence.
12. Add Jacobian features only after exact derivative admission and sealed
    incremental objective value over the complete cheaper comparator stack.
13. Preserve ordinary on-demand loading or the admitted fixed-routing runtime as
    the fail-safe fallback.

SpecPrefetch is a credible systems comparator for memory-constrained MoE
serving. It is not evidence that Agents-A1 expert routes are semantically
interpretable, correctness-aware, or safely controllable. It does not alter the
active Q35Q execution order.

## Established by this correction

- Future-expert prediction, transfer scheduling, residency, executed routing,
  runtime cost, and objective outcome are separate binding identities.
- Prediction recall is not ready-recall, cache-hit rate, stall reduction, or
  throughput.
- Transfer-only prefetch requires explicit noninterference and full parity.
- Fusion of predictor scores into routing creates a new model intervention.
- Predictor checkpoints, schedulers, cache policies, and storage layouts are
  executable artifacts.
- Future-route supervision is retrospective training evidence, not an online
  feature at the earlier boundary.
- Hot-cache and cold-storage results are different runtime conditions.
- Asynchronous placement can affect determinism even when mathematical routing
  is intended to remain unchanged.
- Predicted routes do not establish expert semantics, objective correctness, or
  a semantic workspace.
- Existing privacy, sealed-data, verifier, provenance, derivative, GPU,
  intervention, and production gates remain intact.
- Q35Q remains blocked.

## Not established

- Independent reproduction of SpecPrefetch.
- Complete admission of its omitted data recipe, datasets, predictor checkpoint,
  or dependency closure.
- That the released configuration is transfer-only under every fusion mode.
- Route, output, recurrent-state, cache, or derivative parity under real expert
  prefetch.
- Runtime benefit outside the reported I/O-constrained conditions.
- Benefit under hot caches, larger batches, multi-user serving, long-context
  agents, or distributed expert parallelism.
- Semantic meaning or correctness value of predicted future routes.
- Transfer to Qwen3.5, Qwen3.6, or Agents-A1.
- Incremental completed-error value beyond cheaper comparators.
- Complete Q35Q runtime and derivative admission.
- Safe adaptive routing, early exit, retry, repair, forced routing, activation
  steering, or production deployment.

## Current blocker

The active blocker remains exact-target-runtime Q35Q admission:

1. execute the composed Transformers provenance adapter in the exact target
   runtime;
2. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple;
3. bind the actual GPTQModel/Defuser loader and complete executable source
   closure;
4. run strict synthetic Qwen3.5-MoE loading;
5. prove one-time packed-tensor consumption;
6. prove exact expert and fusion ordering;
7. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity; and
8. pass the complete Phase-0 conjunction before weight staging or GPU
   authorization.

No expert-prefetch work is authorized before those gates or by this addendum.
