# STEER ADDENDUM — latent-KV transport integrity, endpoint trust, and fail-closed handoff gates

Date: 2026-07-30
Parent remote head: `b109bfcdff770782482ba44c2b946e581351fcc4`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every later cumulative protocol correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, exact-gradient, numerical-parity, resource, commit-safety, intervention, rollback, and production-gating rule. It authorizes no model-weight retrieval, model execution, GPU use, hidden-state or cache capture, Jacobian fitting, sealed evaluation, latent communication, external action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains exact-target-runtime Q35Q provenance, loader, tensor-consumption, ordering, forward, VJP, JVP, and finite-difference admission. This addendum changes the evidence required for any future transported hidden-state, KV-cache relay, latent-message, semantic-workspace, or multi-agent serving claim. It does not displace the active milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and public-source engineering material may be committed. Prompts, questions, answers, visible commitments, per-example messages, hidden states, embeddings, KV rows, caches, routes, expert identities, Jacobians, verifier labels, task records, credentials, transport keys, host paths, private environment details, and sealed outcomes remain prohibited.

## Triggering primary evidence

Luís Brito and Carlos Baquero, `When Latent Agents Lie: KV-Cache Integrity in Multi-Agent LLM Collaboration`, arXiv `2606.28958v1`, submitted 2026-06-27, studies a planner-specialist-verifier-coordinator system in which specialists emit short visible commitments and transport full KV-cache state to a final coordinator.

The paper separates two threat boundaries that ordinary latent-message evaluation does not identify:

1. **Endpoint or specialist compromise:** the producer itself emits malicious text, malicious KV, or both.
2. **On-path transport tampering:** an honest payload is changed after production and before receiver consumption.

The reported experiments show that plausible visible text does not validate the associated hidden state. Random, scaled, sign-flipped, norm-matched, and white-box manipulations can damage the receiver while leaving the visible commitment unchanged or plausible. Simple magnitude filters detect some naive corruptions but fail against adaptive norm-matched attacks.

The paper implements an HMAC-SHA256 manifest that binds specialist identity, record or session identity, model identity, visible-commitment hash, tensor metadata, and a payload digest. Its recorded replay accepts `774/774` honest payloads and rejects `295/295` recorded tampered payloads. Detected post-handoff substitutions can then be dropped or downgraded before receiver use.

That positive result is bounded. A transport MAC does not establish that a compromised endpoint generated honest semantics, does not defend a stolen or mis-scoped key, does not provide remote attestation, does not prove privacy, does not validate model correctness, and does not establish broad production security. The paper reports that semantic malicious specialists and compromised endpoints remain outside the MAC boundary.

No attributable immutable public implementation revision was admitted during this correction. The result remains primary paper-level evidence, not an independently reproduced jLens artifact.

## Binding interpretation

The evidence exposes a protocol distinction not fully captured by latent-message causal controls, cache-lineage checks, visible verifiers, anomaly filters, or ordinary provenance records alone:

> Message content, producer trust, transport integrity, payload authenticity, freshness, receiver compatibility, receiver acceptance, and objective task value are different scientific and systems objects.

The following identities may not be renamed into one another:

1. sender or specialist identity;
2. sender process, host, runtime, and trust boundary;
3. model, tokenizer, adapter, cache-schema, and checkpoint identity;
4. visible commitment;
5. hidden payload before handoff;
6. canonical manifest bytes;
7. authentication tag;
8. transport channel and intermediaries;
9. hidden payload after transport;
10. receiver process, runtime, and trust boundary;
11. freshness, sequence, and anti-replay state;
12. compatibility decision;
13. integrity or authenticity decision;
14. semantic or policy acceptance decision;
15. receiver-consumed payload;
16. fallback or quarantine action;
17. independently verified task outcome;
18. privacy exposure;
19. availability and denial-of-service cost; and
20. complete systems cost.

A payload can be authentic but malicious because the authenticated endpoint produced it. A payload can be semantically useful but unauthenticated because transport provenance is missing. A valid tag can accompany a stale or replayed payload if freshness is not bound. A byte-identical payload can still be incompatible with the receiver if model, cache, positional, or runtime identities differ. Successful transport verification does not establish objective correctness.

## Endpoint-versus-transport threat-model gate

Every future latent-state handoff study must prospectively declare which adversary controls each boundary:

- sender prompt or evidence;
- sender model weights or adapters;
- sender runtime and hooks;
- sender credentials and transport keys;
- serialization and compression code;
- network, IPC, shared memory, storage, and cache transport;
- receiver runtime and hooks;
- receiver keys and anti-replay state;
- verifier, parser, policy, and fallback path; and
- logging, paging, crash, and persistence systems.

At minimum, results must separate:

1. honest sender and honest transport;
2. malicious sender with intact transport;
3. honest sender with on-path tampering;
4. malicious sender plus on-path tampering;
5. compromised authentication key;
6. stale or replayed authentic payload;
7. wrong-session, wrong-example, or wrong-turn authentic payload;
8. wrong-model or wrong-cache-schema authentic payload; and
9. receiver compromise.

A transport-integrity result may only claim protection against the explicitly tested post-production modifications under an uncompromised key and admitted receiver. It may not be described as latent-state safety, semantic validation, Byzantine robustness, secure multi-agent reasoning, or trustworthy workspace communication without separate evidence.

## Canonical manifest and serialization gate

Authentication is meaningful only over one deterministic, unambiguous byte representation. Every compatible implementation must freeze and verify at minimum:

- protocol and manifest version;
- sender, receiver, tenant, session, request, example, turn, and sequence identifiers;
- creation time, expiry or freshness window, and nonce;
- sender and receiver repository revisions and model artifact identities;
- tokenizer, processor, template, adapter, reasoning-mode, and cache-schema identities;
- model class, architecture, layer count, attention type, head counts, head dimension, hidden width, and positional configuration;
- precision, quantization, packing, endianness, layout, contiguity, compression, and decompression identities;
- prefill or decode stage, source layer, destination layer, token or slot coordinates, absolute and relative positions, masks, padding, and sequence lengths;
- visible-commitment digest and the exact binding between that commitment and the hidden payload;
- ordered tensor inventory with exact names, roles, shapes, strides or canonical contiguous layout, dtypes, byte lengths, and per-tensor digests;
- complete payload digest over the exact receiver-consumed bytes; and
- policy, verifier, fallback, and logging revisions that determine acceptance.

Canonicalization must reject ambiguous encodings rather than normalize them silently. The implementation must prospectively define:

- field ordering;
- integer width and signedness;
- text encoding and Unicode normalization;
- floating-point metadata representation;
- treatment of NaNs, infinities, negative zero, and padding bytes;
- path, name, and identifier normalization;
- duplicate fields or duplicate tensor names;
- omitted versus explicit default fields;
- compression framing and dictionary identity;
- tensor concatenation order;
- partial or chunked payloads; and
- manifest extension behavior.

JSON object equivalence, parser output equality, and authenticated byte equality are separate claims. A serializer change creates a new transport artifact unless exact compatibility is prospectively proved.

## Key-management and anti-replay gate

HMAC evidence is conditional on secret-key control. Every future authenticated handoff must freeze and test:

- key generation and entropy source;
- sender and receiver key scope;
- tenant, model, session, and protocol separation;
- storage, retrieval, rotation, expiry, revocation, and deletion;
- process and host access controls;
- key identifiers without publishing key material;
- behavior under missing, stale, revoked, or wrong keys;
- nonce and sequence-number uniqueness;
- replay windows and receiver-side replay state;
- restart, failover, multi-replica, and clock-skew behavior;
- concurrent senders and out-of-order delivery; and
- recovery after suspected compromise.

A single shared key across agents, tenants, models, or environments does not establish endpoint attribution. Key possession proves only possession under the declared scheme; it does not prove that the model, runtime, or evidence source was uncompromised.

Transport keys, derived keys, credentials, or recoverable key material may never be committed to this repository. Aggregate pass/fail counts and public test vectors without private payloads are the maximum public artifact while the repository remains public.

## Receiver compatibility and exact-consumption gate

A valid tag is not permission to consume the payload. Before receiver injection, the admitted path must prove exact compatibility for:

- checkpoint and adapter identities;
- tokenizer and prompt-template identities;
- cache format and schema version;
- attention implementation and positional encoding;
- layer, stream, head, token, slot, and component coordinates;
- precision, quantization, packing, scaling, and decompression;
- prefix and prompt lineage;
- recurrent, hybrid-attention, state-space, and external-memory state;
- batch, sequence, padding, and scheduler placement;
- device, sharding, topology, and communication layout; and
- the exact receiver consumer reached by the handoff.

The receiver must prove one-time consumption of the admitted payload and rejection of missing, extra, duplicated, reordered, truncated, extended, stale, or partially authenticated components. Verification code, hooks, wrappers, and transport middleware must be shown to reach the actual executed consumer rather than a shadow path.

A correctly authenticated payload consumed by the wrong layer, token position, branch, model replica, cache page, expert stream, or session is a failed handoff.

## Visible-commitment binding gate

A visible commitment and hidden payload are separate channels. Future systems that present text for audit while transporting hidden state must bind:

- exact commitment bytes;
- parser and canonicalization revision;
- sender, session, request, example, and turn identity;
- hidden-payload digest;
- production order and timestamp; and
- receiver acceptance decision.

A plausible visible commitment does not validate hidden semantics. A commitment hash proves only that the authenticated payload was associated with those bytes at signing time. It does not prove consistency, entailment, faithfulness, evidence support, or task correctness.

Semantic consistency between visible and hidden channels requires separate, prospectively validated tests and remains subject to all sealed-data and verifier rules.

## Fail-closed acceptance and fallback gate

Integrity failure, compatibility failure, stale-state detection, replay detection, key failure, or uncertain provenance must fail closed before receiver consumption.

Every compatible system must prospectively choose and test one or more explicit responses:

1. reject the entire request;
2. drop only the failed sender payload;
3. use an authenticated visible-text fallback;
4. recompute the sender state locally;
5. execute the admitted no-communication baseline;
6. execute the admitted full-compute single-agent baseline; or
7. enter a separately authorized human-confirmation path.

Silent acceptance, best-effort parsing, partial unverified consumption, stale-cache reuse, or automatic downgrade to an unaudited path is prohibited.

Fallback evaluation must report:

- task outcome after failure;
- false-positive damage to honest payloads;
- latency and throughput effects;
- additional model calls and compute;
- availability loss and denial-of-service amplification;
- privacy and provider exposure;
- retries, queueing, and tail latency;
- whether omitted evidence makes the task unsolvable; and
- whether fallback changes the parser, verifier, policy, or action surface.

A defense that prevents tampered-state consumption but causes unacceptable availability failure is an integrity mechanism with unresolved systems utility, not a production-ready solution.

## Mandatory adversarial test ladder

Before any latent-state transport claim is admitted, the exact production-path verifier and receiver must reject or safely handle, where applicable:

- single-bit and multi-bit payload corruption;
- tensor truncation, extension, duplication, omission, and reordering;
- wrong tensor name, role, shape, dtype, length, stride, packing, scale, or endianness;
- metadata-only tampering;
- payload-only tampering;
- manifest-only tampering;
- tag truncation, substitution, and algorithm confusion;
- duplicate manifest fields and ambiguous canonicalization;
- wrong sender, receiver, tenant, session, request, example, turn, or sequence;
- stale and replayed authentic payloads;
- cross-model, cross-checkpoint, cross-adapter, cross-tokenizer, and cross-runtime swaps;
- cross-layer, cross-position, cross-branch, cross-batch, and cross-cache-page swaps;
- visible-commitment substitution;
- compression and decompression mismatches;
- partial chunk loss, duplication, reordering, and replay;
- concurrent sender races and out-of-order delivery;
- restart and failover with replay-state loss;
- compromised-key simulations;
- malicious authenticated endpoints;
- adaptive norm-matched and gradient-based hidden-state attacks; and
- verifier, hook, wrapper, or middleware bypass.

The ladder must include positive controls showing honest current-session payload acceptance and negative controls proving that the test harness actually reaches the receiver boundary.

Detection rate, honest false-positive rate, semantic task outcome, fallback outcome, privacy exposure, bandwidth, memory, latency, throughput, and tail risk must be reported separately.

## Privacy and confidentiality boundary

Integrity and confidentiality are independent. An HMAC does not hide prompts, evidence, hidden states, credentials, tool results, user identity, or memorized data. Encryption does not establish semantic correctness or endpoint trust.

Future transport studies must separately account for:

- data readable by the sender;
- data present in the hidden payload;
- data exposed to transport intermediaries, storage, logs, crash artifacts, and observability systems;
- data reconstructable by the receiver or auxiliary probes;
- cross-tenant and cross-example reuse;
- retention, deletion, revocation, and cache invalidation;
- encryption identities and key boundaries where used; and
- privacy loss introduced by integrity diagnostics, replay artifacts, or attack generation.

No authenticated or encrypted carrier derived from private or sealed tasks may be committed merely because its plaintext is not directly visible.

## MoE, router, and runtime boundary

For an MoE receiver, authenticated cache transport and model execution remain different objects. A transported state may change router logits, expert identities, mixture weights, capacity behavior, communication, cache residency, recurrent state, and later predictions.

Future MoE handoffs must bind and report separately:

1. transported carrier and exact receiver boundary;
2. pre-router receiver state;
3. raw router values and routing transforms;
4. selected shared and routed experts, ordering, and weights;
5. physical expert execution and communication;
6. expert outputs and residual combination;
7. recurrent, state-space, hybrid-attention, and cache lineage;
8. prediction-distribution effect;
9. independently verified objective outcome; and
10. transport, verification, fallback, and complete systems cost.

Authentication does not make expert routes semantic labels. Route changes do not prove useful communication. Route parity does not prove cache compatibility. Transport checks must be included in the exact runtime identity and parity evidence for any claimed fixed-route or router-inclusive Jacobian.

## Jacobian boundary

The following derivatives remain different maps:

- receiver-state Jacobian with respect to the pre-authentication payload;
- receiver-state Jacobian with respect to the accepted canonical payload;
- receiver-output Jacobian with fixed acceptance and fixed route;
- receiver-output Jacobian including differentiable preprocessing;
- sender-to-message-construction Jacobian;
- end-to-end sender-input to receiver-output Jacobian; and
- finite changes crossing authentication, compatibility, replay, routing, parser, stopping, or fallback boundaries.

Authentication and compatibility decisions are discrete gates. A local derivative inside the accepted branch does not characterize behavior at rejection, replay, downgrade, route-change, or fallback boundaries.

Any Jacobian-based transported-state study must first pass exact forward, VJP, JVP, and finite-difference parity for the admitted sender, serialization, transport, verification, cache, injection, receiver, and route conditions. It must then demonstrate sealed incremental objective value beyond payload norms, metadata, integrity status, transparent cache diagnostics, ordinary hidden-state probes, receiver-state features, route telemetry, and external verifiers.

## Agents-A1 scaling consequence

The technically credible sequence is now:

1. Complete Q35Q exact-target-runtime provenance, loader, packed-tensor consumption, ordering, deterministic forward, activation-VJP, activation-JVP, and finite-difference admission.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, templates, parser, reasoning mode, hybrid state, cache, harness, verifier, environment, and runtime.
3. Establish transparent text, logit, confidence, hidden-state, spectral, trajectory, memory, program-state, parser, peer-model, and verifier baselines.
4. Keep initial semantic-workspace and latent-message work in one process or replay harness where transport can be eliminated as a confound.
5. If state is serialized, paged, stored, or moved between components, freeze the complete manifest, serializer, key, freshness, compatibility, and receiver-consumption identities before scientific interpretation.
6. Evaluate honest, stale, replayed, swapped, corrupted, malicious-endpoint, and compromised-key conditions separately.
7. Preserve the admitted no-communication or ordinary full-compute path as fail-closed fallback.
8. Treat transport integrity, semantic sender trust, message usefulness, objective correctness, and privacy as separate targets.
9. Separately admit Agents-A1-35B quantization, router, shared and routed experts, hybrid attention, recurrent or state-space state, cache schema, kernels, topology, sharding, scheduler, capture path, tool harness, and verifier.
10. Bind every transported state to exact layer, stream, route regime, expert topology, positional lineage, cache page, shard, replica, and request identity.
11. Require router and expert telemetry to add sealed target-specific value beyond integrity status, compatibility diagnostics, ordinary hidden-state features, transparent communication controls, and external verifiers.
12. Add Jacobian features only after exact derivative parity and require separate incremental value for message use, objective content value, endpoint trust, and receiver outcome.
13. Keep message editing, cache rewriting, route editing, early exit, retry, repair, adaptive depth, external actions, and production control separately preregistered and gated.

The initial Agents-A1 path should avoid distributed latent-state handoff until a simpler observation-only single-runtime benchmark has established scientific value. Transport complexity is not evidence of a semantic workspace and should not be introduced before it is necessary.

## Current blocker and execution order

The current blocker is unchanged:

1. execute the composed Transformers provenance adapter in the exact target runtime using aggregate evidence only;
2. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` as one immutable tuple;
3. bind the actual GPTQModel/Defuser loader and complete executable source closure;
4. run strict synthetic Qwen3.5-MoE loading;
5. prove one-time packed-tensor consumption;
6. prove exact expert and fusion ordering;
7. prove deterministic forward, activation-VJP, activation-JVP, and finite-difference parity; and
8. pass the complete Phase-0 conjunction before weight staging or GPU authorization.

No latent-message experiment, cache relay, distributed agent execution, router capture, hidden-state capture, Jacobian fit, communication intervention, or Agents-A1 scaling run is authorized before the applicable artifact, privacy, verifier, derivative, resource, and sealed-data gates pass.

## Established by this correction

- Producer trust and transport integrity are separate claims.
- Visible text does not validate an associated hidden-state payload.
- Authenticity, integrity, freshness, compatibility, acceptance, semantic usefulness, and objective correctness are separate objects.
- Simple magnitude or anomaly filters do not establish protection against adaptive hidden-state attacks.
- HMAC replay evidence establishes a bounded post-handoff substitution check under an uncompromised key, not endpoint honesty or semantic safety.
- Canonical serialization, complete manifest identity, key management, anti-replay state, and exact receiver consumption are part of the executable transport artifact.
- Integrity failure must occur before receiver consumption and must use an admitted fail-closed path.
- Integrity and confidentiality are independent.
- MoE route or expert changes downstream of an authenticated payload are not semantic labels.
- Local Jacobian sensitivity inside the accepted branch does not characterize discrete verification or fallback boundaries.
- Existing privacy, sealed-data, verifier, provenance, derivative, intervention, and production gates remain intact.
- Q35Q remains blocked.

## Not established

- Independent reproduction of arXiv `2606.28958v1`.
- Admission of its implementation, datasets, transformed records, payload artifacts, attack code, keys, models, dependencies, or runtime closure.
- Security against malicious authenticated endpoints, stolen keys, compromised receivers, colluding majorities, remote-attestation failure, or semantic false evidence.
- Privacy or confidentiality of transported KV state.
- General robustness across models, tasks, carrier families, serving systems, key-management systems, and distributed topologies.
- Safe latent-state transport for Agents-A1, Qwen3.5, Qwen3.6, or architectural MoEs.
- Objective correctness prediction from integrity status, payload diagnostics, route changes, hidden states, or Jacobian features.
- Incremental router, expert, hidden-state, semantic-workspace, or Jacobian-Lens value beyond transparent controls and cheaper baselines.
- Complete Q35Q runtime and derivative admission.
- Safe production latent communication, cache reuse, external action, early exit, retry, repair, routing intervention, steering, or deployment.
