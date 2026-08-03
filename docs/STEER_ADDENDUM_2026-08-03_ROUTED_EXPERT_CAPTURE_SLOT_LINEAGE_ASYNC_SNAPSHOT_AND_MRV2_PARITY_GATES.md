# STEER ADDENDUM — routed-expert capture slot lineage, asynchronous snapshot, and MRV2 parity gates

Date: 2026-08-03
Parent remote head: `80193213cc9cb179ca1c29eba82423029235a102`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every later cumulative protocol correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, exact-gradient, numerical-parity, resource, intervention, rollback, action, and production-gating rule. It authorizes no model-weight retrieval, model execution, GPU use, hidden-state or router capture, Jacobian fitting, sealed evaluation, route intervention, external action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains exact-target-runtime Q35Q provenance, loader, tensor-consumption, ordering, forward, persistent-state, VJP, JVP, and finite-difference admission. This addendum changes the evidence required for any future native routed-expert telemetry claim. It does not displace the active milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and public-source engineering material may be committed. Prompts, questions, answers, token IDs, request IDs, route arrays, slot mappings, cache-block identities, expert identities, router values, hidden states, Jacobians, verifier labels, private paths, credentials, weights, and sealed outcomes remain prohibited.

## Triggering primary evidence

vLLM merged commit `42ab184ea74ee6cf2966529c77bb51fd825a5d0c`, `[MRV2] Enable routed-experts capture (#50721)`, on 2026-08-03. The change enables the existing routed-experts return path under Model Runner V2 and carries captured target-model route IDs through asynchronous output handling.

The implementation establishes several concrete systems boundaries:

- capture is attached to supported target-model `MoERunner` modules;
- modular routing is captured at a supported `BaseRouter` callback;
- monolithic routing requires an explicit routing-replay capture capability and otherwise fails closed;
- the route tensor is paired with the slot mapping from a `FullAttentionSpec` KV-cache group;
- hybrid cache layouts are not treated as interchangeable;
- route and slot tensors are cloned before the next step can overwrite their backing storage;
- unsupported layer indices, unsupported routers, unsupported monolithic kernels, missing full-attention groups, and absence of any supported MoE router raise rather than silently producing nominal telemetry; and
- capture is initialized on every participating worker while target and draft models remain distinct.

The merged pull request reports focused CPU and CUDA tests, H200 validation, Ray-path validation, and a complete 1,319-example GSM8K comparison on `ibm-research/PowerMoE-3b` in FP16, TP1. It reports identical generated token IDs, text, and complete routed-expert arrays across base MRV1, changed MRV1, changed MRV2, and repeated runs in that tested condition.

Those results are useful but bounded. They do not establish compatibility with Agents-A1, AWQ or GPTQ execution, TP2 or expert parallelism, hybrid recurrent state, speculative target/draft execution, continuous production traffic, hidden-state parity, derivative parity, objective correctness, or safe control use. No jLens reproduction has occurred.

## Binding interpretation

The evidence exposes a route-telemetry boundary that cannot be reduced to a tensor of expert IDs:

> Logical request identity, scheduled token row, KV-slot lineage, KV-group identity, router selection, route weight, physical dispatch, expert execution, capture-buffer state, asynchronous snapshot, reconstructed request history, and scientific outcome are different objects.

The following identities may not be renamed into one another:

1. request, sequence, branch, retry, continuation, tenant, and session identity;
2. prompt, prefix, token, absolute position, relative position, and generation-stage identity;
3. scheduler step, batch row, scheduled-token row, and worker-local row;
4. KV-cache group, attention specification, slot mapping, cache block, block generation, and ownership epoch;
5. model, checkpoint, adapter, quantization, runtime, model-runner, kernel, and topology identity;
6. target-model route versus draft, MTP, EAGLE, or other speculative route;
7. router input, router logits, postprocessing, Top-K set, Top-K order, and route weights;
8. logical expert identity versus physical expert placement, replica, rank, or post-EPLB mapping;
9. selected expert versus dispatched expert versus actually executed expert;
10. shared-expert execution versus routed-expert execution;
11. capture callback, capture buffer, immutable snapshot, D2H transfer, host representation, and persisted record;
12. per-step route rows versus reconstructed per-request route history;
13. route agreement, token agreement, hidden-state agreement, persistent-state agreement, derivative agreement, verifier agreement, and objective agreement; and
14. passive observation, scheduling optimization, routing intervention, early exit, truncation, retry, escalation, external action, and production authorization.

A row containing an expert ID is not self-identifying. A route array without its exact slot, request, position, layer, stage, rank, and runtime lineage is not admissible telemetry.

## Route-slot lineage gate

Every captured routed-expert row must remain bound to the exact live execution that produced it. The admitted private record must include or deterministically resolve, at minimum:

- request, sequence, branch, retry, continuation, tenant, and session identities;
- prefix digest and tokenizer/template identities;
- absolute and relative token positions;
- prefill, chunked-prefill, decode, verification, replay, or speculative stage;
- scheduler step and batch membership;
- scheduled-token count and valid-row count;
- worker-local row and its reconstruction rule;
- KV-cache group ID and exact cache-spec class;
- slot mapping, block size, block or page identity, ownership epoch, and generation counter where present;
- layer ID and the declared architecture-to-runtime layer mapping;
- target, draft, MTP, EAGLE, verifier, or auxiliary-model identity;
- tensor-, pipeline-, data-, context-, and expert-parallel rank identities;
- logical expert IDs, Top-K order, and declared expert-numbering namespace;
- runtime, model-runner, kernel, quantization, batching, scheduler, and topology identities; and
- capture, snapshot, transfer, consumption, eviction, cancellation, and release lifecycle.

Contiguous row order may not be assumed to equal request order after continuous batching, chunked prefill, prefix reuse, preemption, cancellation, retries, speculative verification, pipeline movement, or cache-block recycling. Reconstruction must use the admitted scheduler and slot lineage, then fail closed on ambiguity.

The exact production path must reject or quarantine:

- missing or extra route rows;
- stale rows from a prior step;
- duplicated or reordered rows;
- wrong-request, wrong-branch, wrong-token, wrong-position, or wrong-layer rows;
- cross-tenant or cross-session rows;
- slot mappings from the wrong KV group;
- cache slots whose ownership epoch changed before consumption;
- target routes labeled as draft routes or draft routes labeled as target routes;
- route arrays whose worker, rank, or pipeline identity is absent;
- partial-rank aggregation presented as complete telemetry; and
- reconstructed histories that cannot prove one-to-one coverage of the declared execution.

Positive controls must prove correct reconstruction under normal execution. Negative controls must deliberately exercise preemption, cancellation, retry, batch compaction, prefix caching, chunked prefill, cache-block reuse, and request interleaving.

## KV-group and hybrid-state gate

A full-attention slot mapping is one execution coordinate system, not a universal token identifier. Hybrid models can contain multiple attention, linear-attention, recurrent, state-space, or external-memory groups with different layouts and lifecycles.

For each architecture and runtime, the study must prospectively prove:

- which KV or state group indexes the captured routes;
- why that group yields a complete and unambiguous mapping for every routed token;
- whether prefill and decode use the same mapping semantics;
- how pipeline and context parallelism change the mapping;
- how recurrent or state-space tokens without ordinary KV slots are represented;
- how prefix caching, cache sharing, sliding windows, or eviction affect lineage; and
- how route rows are joined to any hidden-state, cache, parser, tool, or verifier record.

Selecting the first full-attention group is an implementation rule that must be bound to the exact admitted runtime. It is not architectural proof that the group uniquely identifies all relevant persistent state.

## Snapshot, stream, and mutable-buffer gate

Capture storage reused by the next forward pass is mutable runtime state. Every route snapshot used outside the producing step must be immutable before overwrite can occur.

The exact path must prove:

- only valid current-step rows are included;
- every routed layer overwrites every valid row before snapshot;
- unused rows cannot be interpreted as current data;
- route and slot tensors are cloned or otherwise ownership-transferred before reuse;
- CUDA stream and event dependencies prevent torn or premature host reads;
- async D2H retains source lifetimes until completion;
- zero-copy, Ray, IPC, serialization, and deserialization paths preserve shape, dtype, ordering, and ownership;
- cancellation, exception, timeout, preemption, and worker restart release or invalidate snapshots safely;
- retries do not attach an earlier attempt's routes to a later attempt; and
- concurrent requests cannot observe or overwrite one another's telemetry.

Successful tensor allocation or transport is not evidence of a coherent snapshot. The adversarial ladder must include delayed copy streams, immediate next-step overwrite, forced cancellation, cache reuse, worker failure, and reordered completion.

## Capture-path and kernel gate

Modular-router callbacks and monolithic routing-replay capture are different executable paths. Each must be admitted separately.

For every supported path, bind:

- exact vLLM revision and model-runner version;
- exact model class, MoE layer class, router class, quantization method, kernel, and dispatch implementation;
- whether routing is selected in Python, fused code, a monolithic kernel, or replay output;
- the exact callback boundary relative to score production, Top-K selection, renormalization, capacity handling, dispatch, and expert execution;
- whether any expert IDs are remapped, replicated, grouped, sharded, or reordered after capture;
- whether expert-load balancing changes logical-to-physical placement;
- whether dropped, overflowed, rerouted, or fallback tokens remain visible; and
- whether all participating ranks emit the required portion of the record.

Unsupported kernels or routers must fail closed. A nominal all-zero, truncated, rank-zero-only, or silently omitted route tensor is a hard failure, not missing-at-random data.

Target-model capture must not traverse or combine speculative draft modules unless the protocol explicitly requests a separate draft record. Target and draft route arrays require separate schemas, identities, and calibration.

## Logical selection versus physical execution gate

Top-K expert IDs are not a complete execution trace. Future Agents-A1 studies must distinguish and, where claimed, capture separately:

1. pre-router hidden state;
2. router logits before masking or correction;
3. load-balancing, bias, group, capacity, and renormalization operations;
4. ordered selected logical expert IDs;
5. selected route weights;
6. shared-expert contribution;
7. logical-to-physical expert mapping;
8. dispatched token/expert pairs;
9. dropped, overflowed, rerouted, duplicated, or fallback pairs;
10. expert outputs before combination;
11. reduction and accumulation order; and
12. post-MoE hidden state.

Agreement at one boundary cannot be reported as agreement at another. Route-ID equality does not prove weight equality, physical dispatch equality, expert-output equality, reduction equality, or hidden-state equality.

Elastic expert parallelism, dynamic expert placement, expert replication, and online load balancing create new runtime conditions. A capture implementation that does not bind mapping epochs and physical placement may support logical-route analysis only; it cannot support physical-load, communication, latency, or executed-expert claims.

## Observation-only and parity ladder

Before routed-expert telemetry can be interpreted, capture-enabled execution must be compared with the exact admitted capture-disabled reference.

The prospective ladder must include, where supported:

- MRV1 versus MRV2;
- synchronous versus asynchronous output handling;
- local versus Ray or other distributed execution;
- TP, DP, PP, CP, and EP rank combinations used by the target deployment;
- modular versus monolithic MoE kernels;
- prefill, chunked prefill, decode, and speculative verification;
- prefix caching, preemption, cancellation, retry, and continuous batching;
- hybrid cache/state groups;
- repeated runs under frozen seeds and under declared nondeterministic conditions; and
- capture disabled, IDs only, IDs plus weights, and full admitted telemetry arms.

At minimum, compare separately:

- route-row count and coverage;
- slot mappings and reconstructed request/token/layer histories;
- logical Top-K IDs and order;
- route weights where captured;
- physical dispatch and expert outputs where claimed;
- logits, generated tokens, text, parser state, tool calls, memory operations, verifier outcomes, and objective outcomes;
- persistent KV, recurrent, or hybrid state; and
- activation VJPs, JVPs, and finite differences wherever Jacobian claims are intended.

The PowerMoE MRV1/MRV2 result is a public upstream compatibility result for one FP16 TP1 H200 condition. It is not an Agents-A1 admission artifact and may not set jLens parity tolerances.

If the admitted runtime is nondeterministic, the nondeterminism envelope must be estimated from capture-disabled repeated executions before the capture arm is examined. An envelope cannot be widened after seeing capture-enabled results. Exact dispatch-boundary checks remain required where available.

## Completeness, missingness, and fail-closed analysis gate

Route telemetry is often missing for systematic reasons: unsupported kernels, failed ranks, dropped rows, cache-group mismatches, scheduler races, speculative branches, or overflow behavior. Missingness may therefore correlate with load, difficulty, sequence length, model behavior, or failure.

Every result must report:

- expected and observed rows by request, token, layer, stage, and rank;
- unsupported models, layers, kernels, and execution modes;
- dropped, invalid, duplicated, stale, and quarantined records;
- requests excluded and the exact exclusion reason;
- whether missingness predicts outcome, length, load, route entropy, or verifier failure; and
- sensitivity analyses that treat missing records as failures or worst-case values where appropriate.

Silently dropping incomplete requests or layers is prohibited. A monitor trained only on successfully captured routes is a selected-population monitor until proved otherwise.

## Privacy and public-artifact boundary

Route telemetry can reveal prompt structure, token progression, model internals, tenant activity, load state, cache placement, and potentially memorized or identifying behavior. Slot mappings and cache-block identities can also expose serving topology and cross-request timing.

While the repository remains public:

- raw route IDs, route weights, router logits, slot mappings, cache pages, request IDs, token positions, prompts, outputs, hidden states, and per-example labels remain private;
- public artifacts may contain only aggregate counts, declared schemas, hashes of public code or aggregate artifacts, non-sensitive tolerances, and aggregate pass/fail outcomes;
- no reversible encoding or authenticated/encrypted carrier of private telemetry may be committed;
- worker-local files, crash dumps, traces, logs, and temporary buffers require retention and deletion controls; and
- cross-tenant isolation and access-control tests are mandatory before any production-serving claim.

Privacy admission is separate from scientific utility and runtime parity.

## Binding Agents-A1 scaling sequence

The technically credible route-telemetry path is now:

1. Complete Q35Q provenance, loader, strict tensor-consumption, expert-order, forward, persistent-state, VJP, JVP, and finite-difference admission.
2. Admit Agents-A1-4B under one immutable checkpoint, tokenizer, parser, tool harness, memory system, verifier, sampler, and local runtime.
3. Pin an exact vLLM revision and prove whether the native routed-experts path supports that model, quantization, kernel, and model runner without source modification.
4. Run the complete route-slot lineage and mutable-snapshot adversarial ladder on private synthetic fixtures before any task data.
5. Prove capture-disabled versus capture-enabled observation parity and compare MRV1/MRV2 only within their separately admitted conditions.
6. Reconcile native logical route IDs against dispatch-entry records and, where systems claims are intended, physical expert placement and executed expert outputs.
7. Establish cheap logits, confidence, trajectory, direct hidden-state, parser, tool, memory, and verifier baselines before fitting route or Jacobian monitors.
8. Use route telemetry only as a declared additional channel. Require sealed incremental value beyond cheaper controls for objective correctness, continuation utility, retry, escalation, tool utility, or episode success.
9. Admit Agents-A1-35B independently under its exact quantization, shared and routed experts, hybrid state, expert parallelism, reduction semantics, kernels, topology, scheduler, batching, cache policy, and telemetry path.
10. Freeze the logical-to-physical expert mapping and mapping-epoch schema for every 35B experiment. Recalibrate all route features and thresholds; nothing transfers automatically from 4B.
11. Condition any Jacobian or semantic-workspace analysis on the exact route, slot, runtime, and information state that produced the derivative.
12. Preserve native full-compute execution and independent verification as fallback. Route telemetry alone may not authorize early exit, truncation, expert dropping, route steering, retry, escalation, external action, or production deployment.

## Mandatory adversarial test ladder

Before a routed-expert telemetry artifact is admitted, the exact production path must detect or safely handle, where applicable:

- layer index outside the capture buffer;
- no supported MoE router;
- unsupported router class;
- unsupported monolithic kernel or missing replay support;
- no full-attention KV group;
- wrong KV-group selection;
- wrong slot mapping, block size, cache page, or ownership epoch;
- stale rows from the prior step;
- partial layer overwrite;
- immediate next-step overwrite during delayed D2H;
- missing, duplicated, truncated, padded, or reordered rows;
- request, sequence, branch, retry, token, position, layer, or stage swaps;
- target/draft/MTP route swaps;
- prefill/decode and chunk-boundary swaps;
- preemption, cancellation, timeout, retry, and restart;
- prefix-cache reuse and cache-block recycling;
- TP, DP, PP, CP, and EP rank omission or duplication;
- logical/physical expert remapping and mapping-epoch drift;
- dropped, overflowed, rerouted, or fallback-token behavior;
- zero-copy, Ray, IPC, serialization, and asynchronous-copy corruption;
- cross-request and cross-tenant contamination;
- capture-disabled/capture-enabled parity drift; and
- telemetry consumer bypass, shadow paths, or records that never reach the claimed analysis.

Positive controls must prove honest current-step route acceptance and exact per-request reconstruction. Negative controls must prove that the tests reach the actual capture, snapshot, transfer, reconstruction, and consumer boundaries.

## Current blockers and non-claims

This addendum does not resolve any current blocker. In particular, it does not establish:

- intentional public visibility or a repaired private destination;
- complete Q35Q executable-source closure;
- clean-subprocess monkeypatch and runtime-substitution detection;
- exact GPTQModel/Defuser loader-entry binding;
- one immutable differentiable GPTQ runtime tuple;
- strict Qwen3.5-MoE quantized loading and one-time packed-tensor consumption;
- exact Q35Q expert, fusion, routing, reduction, forward, persistent-state, VJP, JVP, or finite-difference parity;
- native MRV2 route capture on Agents-A1-4B or Agents-A1-35B;
- request-complete route reconstruction under Agents-A1 serving;
- observation-only route capture under Agents-A1 quantization or expert parallelism;
- objective correctness, continuation utility, tool utility, episode success, or safe stopping from route telemetry;
- a natural semantic workspace;
- safe early exit, truncation, adaptive Top-K, expert dropping, route intervention, retry, escalation, external action, or production deployment.

No model-weight staging or GPU execution is authorized before the existing complete admission conjunction passes.
