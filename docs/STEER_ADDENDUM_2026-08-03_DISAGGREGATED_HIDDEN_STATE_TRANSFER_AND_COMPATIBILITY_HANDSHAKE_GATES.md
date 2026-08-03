# STEER ADDENDUM — disaggregated hidden-state transfer, compatibility handshakes, and request-lineage gates

Date: 2026-08-03
Parent remote head: `bec14e6600dc8f700f982fe83d41f68f810db2a8`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every later cumulative protocol correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, exact-gradient, numerical-parity, resource, intervention, rollback, action, and production-gating rule. It authorizes no model-weight retrieval, model execution, GPU use, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, early exit, truncation, adaptive routing, external action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control records and public-source engineering material may be committed. Prompts, benchmark items, outputs, token ids, per-example predictions, hidden states, KV contents, router arrays, expert traces, Jacobians, verifier labels, credentials, host paths, tenant identifiers, and sealed outcomes remain prohibited.

## Triggering primary implementation evidence

The public `vllm-project/vllm` repository changed its NIXL prefill/decode disaggregation handshake in commit:

`952694e3843e478dd99cffd132c756d582fe8a94`

Commit title:

`[Bugfix] Validate NIXL speculative config compatibility (#49230)`

The change increments `NIXL_CONNECTOR_VERSION` from 5 to 6 and adds explicit compatibility factors for EAGLE/MTP-style hidden-state-based speculative configurations. The handshake now binds, where applicable:

- speculative method;
- draft-model identity;
- draft-model revision;
- draft-model code revision;
- parallel-drafting state;
- effective speculative KV-cache dtype; and
- auxiliary hidden-state layer ids.

The implementation intentionally permits `num_speculative_tokens` to differ between prefill and decode instances. It also intentionally excludes the draft attention-backend override from the compatibility hash because the resolved transfer-relevant KV block layout is checked separately at runtime.

This is production engineering evidence that distributed hidden-state or draft-state movement requires a compatibility contract beyond base-model identity. It is not evidence that a successful handshake establishes scientific equivalence, hidden-state equality, correctness-monitor validity, Jacobian validity, privacy safety, or transfer to Agents-A1.

No jLens result has independently reproduced this vLLM path. No disaggregated hidden-state transport artifact is admitted for Q35Q or Agents-A1. The active Q35Q milestone and all existing gates remain unchanged.

## Binding distinction: transport compatibility is not executable equivalence

The following are separate claims and may not be renamed into one another:

1. the producer and consumer can exchange blocks without an immediate protocol error;
2. the transferred regions have compatible byte sizes and layouts;
3. the producer and consumer use compatible speculative configurations;
4. the transferred hidden states correspond to the same request, prefix, token positions, and layer boundaries;
5. the transferred values equal a local non-disaggregated reference;
6. downstream logits, routes, caches, tokens, parser state, verifier outcomes, VJPs, and JVPs match;
7. the extraction path is observation-only;
8. the telemetry adds sealed objective value; and
9. the path is safe for production monitoring or control.

A compatibility hash is a transport admission mechanism. It is not a scientific parity proof.

Hash equality does not establish equality of factors intentionally excluded from the hash. Runtime layout acceptance does not establish numerical equality. A permitted difference in speculative-token count remains a distinct execution condition for latency, scheduling, cache pressure, draft behavior, hidden-state timing, and any derived monitor.

Disabling handshake enforcement is prohibited for any scientific capture, sealed evaluation, or production-monitoring claim.

## Disaggregated capture artifact identity

Every future prefill/decode-disaggregated hidden-state, EAGLE/MTP auxiliary-state, KV-connector, NIXL, remote-cache, or equivalent telemetry experiment must freeze at minimum:

- exact target-model repository, immutable checkpoint revision, model class, tokenizer, processor, template, reasoning mode, and adapter set;
- exact producer and consumer vLLM source revisions, installed distributions, source closures, build flags, and connector versions;
- exact NIXL library, transport backend, protocol, registration mode, memory type, and device topology;
- producer and consumer roles, process counts, tensor-parallel sizes, pipeline-parallel sizes, expert-parallel configuration, and rank mappings;
- target-model architecture, dtype, number of layers, hidden size, KV-head count, head size, attention types, sliding-window rules, and cache dtype;
- speculative method and whether it is extraction-only, EAGLE, EAGLE3, MTP, or another admitted method;
- draft-model repository, revision, code revision, architecture, dtype, and quantization;
- auxiliary hidden-state layer ids, their ordering, and the exact pre/post sub-block boundary represented by each id;
- parallel-drafting state, producer and consumer speculative-token counts, and every draft-depth difference;
- target and draft attention backends, resolved KV layouts, block sizes, block shapes, and region metadata;
- hidden-state storage dtype, transfer dtype, casts, packing, strides, alignment, and reconstruction rules;
- chunked-prefill, prefix-cache, preemption, recomputation, retry, cancellation, timeout, and eviction behavior;
- scheduler, batching, request-priority, queueing, and load conditions;
- request-id, sequence-id, prefix, token-position, branch, cache, and generation lineage;
- parser, tool, memory, environment, verifier, retry, stopping, and final-selection identities; and
- complete extraction, synchronization, transport, storage, decode, verifier, and tail-latency cost.

Any change to one of these identities is a distinct executable condition unless prospectively proved equivalent.

## Compatibility-handshake admission gate

Before a distributed hidden-state path may be used, the exact production path must fail closed on incompatible configurations.

Required positive tests include:

- identical method, draft identity, revision, code revision, parallel-drafting state, effective KV dtype, and auxiliary-layer ids;
- explicit versus inherited speculative KV dtype resolving to the same effective dtype;
- permitted producer/consumer speculative-token-count differences, recorded as distinct execution conditions;
- supported heterogeneous tensor-parallel and block-size configurations only where the runtime's region checks pass; and
- resolved attention-backend differences only where every transferred region's layout, size, and semantics are admitted.

Required adversarial tests include rejection of:

- missing speculative configuration on one side;
- wrong speculative method;
- wrong draft model, revision, or code revision;
- wrong parallel-drafting state;
- wrong effective KV dtype;
- missing, extra, duplicated, reordered, or wrong auxiliary-layer ids;
- connector-version mismatch;
- target-model architecture, dtype, layer-count, KV-head, head-size, or cache-format mismatch;
- unsupported KV layout, block shape, block size, memory type, or attention-backend combination;
- disabled compatibility enforcement;
- forged or stale handshake metadata;
- metadata accepted from an unadmitted process or connector implementation; and
- a hash computed from caller-supplied identities rather than the actual live runtime objects.

A successful configuration handshake must still be followed by request-lineage and numerical-parity gates.

## Request, prefix, and block-lineage gate

Hidden states are valid only for the exact token prefix and execution boundary that produced them. Every transferred region must be bound to immutable lineage sufficient to prevent stale, swapped, duplicated, or cross-request state.

At minimum bind:

- request and sequence identity;
- branch, beam, retry, and continuation identity;
- exact token-count and prefix digest under the admitted privacy boundary;
- token-position range and chunked-prefill segment;
- auxiliary layer id and precise layer boundary;
- cache block ids, generation numbers, leases, and ownership epochs;
- producer rank, consumer rank, device, and transfer region;
- transfer creation, registration, completion, consumption, and release events;
- preemption, cancellation, retry, recomputation, and eviction lineage; and
- one-time or explicitly versioned consumption semantics.

Raw prefixes, token ids, states, blocks, and tenant identifiers may not be committed to this public repository. Aggregate pass/fail counts and privacy-safe digests may be recorded only under the existing data-boundary rules.

Required adversarial tests include:

- swapped request ids;
- correct request id with wrong prefix or token range;
- stale block reuse after eviction;
- duplicate block consumption;
- partial region transfer;
- missing or extra layer regions;
- out-of-order regions;
- producer retry feeding an earlier consumer attempt;
- cancelled-request blocks becoming visible to another request;
- preemption and resume with stale lineage;
- cross-rank or cross-tenant region substitution;
- delayed completion after ownership transfer; and
- request-id collision or wraparound.

Any ambiguous lineage is a hard failure, not a recoverable scientific sample.

## Observation-only and local-reference parity gate

The vLLM hidden-state extraction path is implemented through speculative-decoding and KV-connector machinery. Enabling that machinery changes runtime configuration even when the intended use is observation only.

Before any extracted state is treated as passive telemetry, compare the enabled path against an admitted local non-disaggregated reference under frozen inputs and execution conditions.

Compare separately:

1. input tokenization, positions, masks, and prefix-cache decisions;
2. target hidden states at every captured layer and token position;
3. target logits and selected-token probabilities;
4. router inputs, router scores, selected experts, weights, shared-expert output, dispatch, and reduction where applicable;
5. target KV, recurrent, state-space, convolutional, or hybrid state;
6. generated tokens, parser state, tool calls, memory actions, and verifier outcomes;
7. request scheduling, batching, preemption, and cache residency;
8. target activation VJPs and JVPs through the captured boundary where Jacobian claims are intended; and
9. finite differences at representative route-stable and route-boundary directions.

Parity must be tested across:

- single-request execution;
- homogeneous and heterogeneous batches;
- chunked prefill;
- prefix-cache hit and miss;
- preemption and resume;
- producer/consumer restart;
- cancellation and retry;
- different admitted tensor-parallel and block-size configurations;
- every admitted attention backend and KV layout;
- long-context and high-cache-pressure conditions; and
- repeated execution under the same frozen schedule.

Token agreement alone is insufficient. Hidden-state cosine similarity alone is insufficient. Transport success alone is insufficient.

If exact equality is not technically attainable, tolerances and failure strata must be prospectively frozen and justified against the specific scientific claim. A tolerance admitted for a cheap monitor does not automatically admit derivative or causal claims.

## Producer/consumer asymmetry and excluded-factor gate

Factors intentionally permitted to differ or excluded from a compatibility hash must be treated as explicit nuisance or condition variables.

### Speculative-token count

Different producer and consumer `num_speculative_tokens` values may be transport compatible but can change:

- draft compute;
- scheduler occupancy;
- cache pressure;
- acceptance and rejection patterns;
- synchronization timing;
- block lifetime;
- latency; and
- downstream request interference.

Every distinct pair is a separate serving condition for monitor calibration and performance reporting.

### Draft attention backend

An attention-backend override excluded from the hash is not irrelevant. The resolved backend, layout, block shape, numerical behavior, and runtime region validation must be recorded and independently tested. Runtime layout equality does not imply hidden-state or derivative equality.

### Tensor parallelism and block size

Heterogeneous tensor-parallel size or block size may be transport supported while changing reduction order, synchronization, scheduling, and numerical behavior. Scientific equivalence requires separate parity evidence.

## Privacy, isolation, and retention gate

Hidden-state transfer creates a high-dimensional cross-process data channel. It must be treated as sensitive model and user-derived data, not harmless metadata.

Before any multi-request or multi-tenant use, require:

- request-scoped buffers and region ownership;
- authenticated and authorized producer/consumer identities;
- least-privilege registration and memory access;
- explicit retention and deletion limits;
- zero reuse before verified release and sanitization;
- no raw state in logs, traces, exceptions, metrics, or public artifacts;
- reconstruction, membership-inference, attribute-inference, and covert-channel review;
- cancellation and crash cleanup;
- cross-tenant isolation tests; and
- fail-closed behavior when isolation cannot be established.

A compatibility handshake does not provide privacy isolation.

## Monitor and semantic-workspace interpretation gate

A transported hidden state is not evidence of a natural semantic workspace, correctness awareness, completion, or safe stopping.

Any future monitor must compare extracted-state features against cheaper controls at the identical decision boundary, including:

- logits, entropy, margins, and end-marker probability;
- prompt and response length;
- elapsed steps and tool count;
- parser and verifier state;
- compact local hidden-state probes;
- trajectory and tool-trace features;
- router and expert-path summaries;
- repeated continuation or forked-future controls; and
- independent external verification.

A monitor improvement that disappears after conditioning on transport timing, cache pressure, batch composition, speculative depth, auxiliary-layer identity, backend, or request scheduling must be classified as serving-state telemetry rather than model-internal correctness information.

Layer selection, feature fitting, thresholds, calibration, and stop policies remain development-only. Sealed outcomes may not influence transport configuration or monitor selection.

## Agents-A1 scaling directive

The technically credible sequence is:

1. Complete Q35Q production-path provenance, strict loading, packed-tensor consumption, expert ordering, forward, persistent-state, VJP, JVP, and finite-difference admission.
2. Admit Agents-A1-4B under one immutable local non-disaggregated runtime.
3. Establish request-scoped local hidden-state capture at a small frozen layer set and prove observation-only parity against capture disabled.
4. Establish cheap behavioral, logit, confidence, trajectory, parser, verifier, router, and direct hidden-state baselines.
5. Only then admit a producer/consumer or remote hidden-state transport path under the full compatibility, lineage, privacy, and local-reference parity gates above.
6. Use distributed capture only if it provides a measured end-to-end advantage after synchronization, transfer, storage, and verification cost.
7. Preserve exact local full-forward spot checks and fail closed on any transport or lineage drift.
8. Admit Agents-A1-35B separately under its native quantization, hybrid state, routed and shared experts, expert parallelism, cache, kernels, topology, scheduler, and telemetry.
9. Re-freeze auxiliary layers, transport layouts, request-lineage schema, monitor calibration, and parity tolerances for 35B. Do not transfer 4B identities or thresholds.
10. Keep hidden-state extraction, speculative decoding, depth replay, early exit, adaptive routing, expert dropping, retry, escalation, external action, and production deployment as separate artifacts and decisions.
11. Require sealed incremental objective value beyond all cheaper controls before attributing value to Jacobian or semantic-workspace features.
12. Preserve native full-compute execution and independent verification as fallback.

This creates a credible scale-out path for Agents-A1 instrumentation without treating distributed transport support as scientific admission.

## Current engineering blocker remains unchanged

The active milestone remains complete production-path Q35Q provenance and runtime admission:

1. resolve repository visibility versus destination-policy disagreement;
2. bind installed runtime files to immutable distribution ownership records;
3. derive complete executable-source closure from actual live runtime objects;
4. detect shadow imports, in-memory monkeypatching, runtime substitution, and process-global leakage in clean subprocesses;
5. bind the exact GPTQModel/Defuser loader and conversion entry;
6. freeze one immutable Transformers, GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, backend, launch, checkpoint-format, kernel, topology, and reduction tuple;
7. run strict synthetic Qwen3.5-MoE quantized loading;
8. prove one-time packed-tensor consumption and exact expert/fusion ordering;
9. prove deterministic forward and persistent-state parity; and
10. prove activation-VJP, activation-JVP, and finite-difference parity.

No model-weight staging or GPU execution is authorized before the full conjunction passes.

## Established by this correction

- vLLM's NIXL connector now treats hidden-state-based speculative configuration as part of producer/consumer compatibility.
- Method, draft identity, draft revision, draft code revision, parallel-drafting state, effective speculative KV dtype, and auxiliary hidden-state layers are transport-relevant identities.
- Connector-version identity is part of the transfer protocol.
- Some factors may be transport compatible while remaining scientifically distinct execution conditions.
- Compatibility-hash equality, runtime layout acceptance, request-lineage integrity, numerical parity, observation-only behavior, and monitor validity are separate gates.
- Distributed hidden-state capture can become a technically credible Agents-A1 scaling mechanism only after local runtime admission and exact lineage/parity evidence.
- No privacy, sealed-data, verifier, provenance, derivative, intervention, resource, action, or production gate is weakened.
- Q35Q remains blocked.

## Unproven

- Independent reproduction of vLLM's changed NIXL handshake behavior in jLens.
- Hidden-state extraction support for Agents-A1-4B or Agents-A1-35B under the intended runtime.
- Numerical equality between local and disaggregated capture.
- Request, prefix, block, and tenant isolation under continuous batching, preemption, retries, failures, or restarts.
- Exact router, expert-path, cache, hidden-state, VJP, JVP, and verifier parity across producer/consumer configurations.
- Net latency or memory benefit after transport, storage, synchronization, and verification costs.
- Incremental correctness or continuation-utility value from transported hidden states or Jacobian features.
- A natural semantic workspace at any captured layer.
- Safe early exit, truncation, adaptive routing, expert dropping, retry, escalation, external action, or production deployment.

The research program remains unfinished. Q35Q remains blocked at production-path upstream/runtime provenance composition.
