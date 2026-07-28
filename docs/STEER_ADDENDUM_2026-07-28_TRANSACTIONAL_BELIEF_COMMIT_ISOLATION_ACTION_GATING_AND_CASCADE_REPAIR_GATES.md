# STEER ADDENDUM — transactional belief commit, isolation, action-gating, and cascade-repair gates

Date: 2026-07-28

Parent remote head: `ffb863148b43dd0fce9d8296500d4a93f2beba70`

Status: binding future-protocol correction; no current execution authorization

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains exact-target-runtime Q35Q provenance and immutable GPTQ loader/runtime admission.
- GitHub currently reports this repository as public. Aggregate-only commit restrictions remain binding.
- No weight staging, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, durable-memory ingestion, sealed evaluation, intervention, or production use is authorized by this document.
- Every privacy, sealed-data, verifier, provenance, derivative, parity, resource, cleanup, comparator, nuisance-control, intervention, production-gating, and stop rule remains binding.

## New primary evidence and narrow interpretation

Li et al., **MemTX: Transactional Belief Commit for Stateful Agent Memory**, arXiv `2607.23929v1`, separates recording an observation from committing an actionable belief. The public implementation at `lxy1134/MEMTX_` is currently pinned at commit `4e1124ccd5fd384857463020e3497aa73ec93be6`.

The reported system introduces:

1. an eight-state record lifecycle from raw and tentative through validated, committed, action-safe, quarantined, superseded, and revoked;
2. snapshot-isolated transactions with risk-tier-dependent read visibility;
3. ordered evidence, validity, semantic-conflict, permission, and dependency-stability checks;
4. pre-call gating for irreversible tools;
5. a derivation DAG linking beliefs, summaries, profiles, indexes, shared copies, and tool actions;
6. typed cascading repair after transaction abort or belief revocation;
7. property-based testing and bounded exhaustive enumeration over approximately 5.5 million protocol states;
8. purpose-built paired trap and control suites spanning tool-result pollution, stale late writes, dirty reads, semantic conflict, permission laundering, and cascading-rollback failures.

The authors report that MemTX led eight baselines on four of five tested backbones and statistically tied the strongest baseline on the fifth while recording zero downstream harm in the reported benchmark.

The binding interpretation is narrower than a production-safety claim:

- The benchmark is purpose-built and synthetic, uses deterministic mock domain tools, and does not establish natural-world prevalence or production safety.
- The strong external-action gate was machine-checked and exercised in scripted paths, but the LLM evaluation path primarily exercised the weaker in-flight-tentative condition because its stores had not matured through external-action commits.
- The strong gate is existential: it requires at least one action-safe record in the snapshot, not proof that every input supporting the proposed action is action-safe.
- Cascade completeness is bookkeeping completeness over recorded provenance. Unrecorded derivations cannot be repaired.
- Compensation is an obligation recorded by the protocol, not proof that the external environment was restored.
- Tool reversibility is statically declared even though real actions may cross from reversible to irreversible after dispatch.
- Bounded state enumeration is executable evidence over the checked state space, not an unbounded proof of safety.
- No MemTX result establishes hidden correctness awareness, semantic-workspace identity, router-specific value, Jacobian-Lens value, or transfer to Agents-A1.

## Binding state-machine identity

Future compatible durable-memory studies must separately identify at least:

1. source observation or message;
2. write proposal;
3. transaction open event;
4. transaction snapshot identity;
5. staged record;
6. validation result and reason;
7. semantic-conflict adjudication;
8. permission and scope adjudication;
9. dependency-stability result;
10. commit, partial commit, quarantine, supersession, revocation, or abort;
11. visibility under each read isolation level;
12. promotion to action-safe state;
13. retrieval and rendering;
14. proposed tool action;
15. action-input belief lineage;
16. gate decision;
17. executed side effect;
18. compensation, leakage, or unresolved repair obligation;
19. independently verified objective outcome.

A record existing in storage is not equivalent to a committed belief. A committed belief is not equivalent to an action-safe belief. An action-safe store is not equivalent to an action whose own premises are action-safe.

## Transaction and snapshot identity gate

Every admitted transaction protocol must freeze and report:

- transaction identifier and acting principal;
- logical clock and wall-clock relation;
- snapshot creation time and visible-record set;
- risk tier and the trusted component assigning it;
- isolation level and exact lifecycle states visible at that level;
- read set, write set, dependency set, and action set;
- conflict-detection scope and ordering;
- authority, confidence, and validity thresholds;
- tie, stale-write, and concurrent-write behavior;
- partial-commit versus atomic-commit semantics;
- retry, duplicate-delivery, crash-recovery, and idempotency behavior;
- commit receipt, abort receipt, and immutable audit lineage;
- exact memory-manager, database, queue, scheduler, and runtime revisions.

The model may not self-declare a lower risk tier for an action whose effects cross the admitted boundary. Risk classification belongs to trusted harness or policy state and requires separate provenance and change control.

Snapshot labels such as `snapshot isolated`, `serializable`, `causally stable`, or `action safe` are not evidence by themselves. The exact anomaly set prevented and still permitted must be tested prospectively.

## Belief maturity and visibility gate

Future compatible systems must define explicit visibility rules for raw, tentative, validated, committed, action-safe, quarantined, superseded, and revoked records.

Required tests include:

- dirty reads of tentative records;
- non-repeatable and phantom reads;
- stale snapshots;
- late writes after correction;
- concurrent equal-authority conflicts;
- permission changes during a transaction;
- revocation racing with retrieval or action;
- partial commit followed by retry;
- agent restart during validation;
- duplicate commit or abort delivery;
- cross-agent reads during in-flight writes;
- causal descendants of a record pending invalidation.

A system that hides tentative records but exposes descendants derived from them has not preserved isolation.

## Action-input lineage gate

An admitted production action gate must bind the proposed action to the exact beliefs, records, tool observations, summaries, and policy clauses on which the action depends.

For every irreversible or externally consequential action, the gate must verify that:

1. every declared supporting record is visible under the admitted isolation level;
2. every required supporting record has the required maturity;
3. no supporting record is tentative, quarantined, superseded, revoked, expired, permission-invalid, or dependency-unstable;
4. every transitive ancestor required for the action remains valid;
5. the principal is authorized to use each supporting record for this action and destination;
6. the action parameters correspond to the admitted records rather than merely coexisting with an unrelated action-safe record;
7. the gate and tool call share one immutable decision receipt;
8. no material action input was introduced after the gate decision.

An existential rule requiring any action-safe record in the snapshot is an availability or store-maturity condition, not complete action-input safety.

Unknown or incomplete action lineage must fail closed for irreversible actions. Reversible exploratory actions may use a separately frozen policy but may not be silently grouped with irreversible actions.

## Reversibility and side-effect classification gate

Tool effects must be classified independently of model text and frozen before evaluation where feasible.

Required classes include:

- read-only;
- locally reversible;
- externally reversible within a bounded window;
- conditionally reversible;
- compensatable but not reversible;
- irreversible;
- unknown.

The classification must include the point at which reversibility changes. A refund, email, booking, deletion, credential rotation, payment, publication, or physical action can cross from cancellable to settled while the agent is still running.

Future studies must report:

- gate decisions by effect class;
- false blocks on required controls;
- forbidden actions prevented;
- actions executed on invalid premises;
- successful compensation;
- failed compensation;
- leaked irreversible effects;
- time-to-detection and time-to-repair;
- residual harm after repair;
- complete verifier, storage, latency, and tool costs.

A compensation record does not establish environmental restoration. Restoration requires an independent verifier over the external state.

## Derivation-DAG and cascade-repair gate

Every derived durable artifact must preserve machine-auditable parent edges sufficient to identify the source records that materially support it.

Compatible cascade tests must cover:

- beliefs;
- summaries;
- profiles;
- indexes and embeddings;
- shared copies;
- cached prompts;
- skills and workflows;
- policies;
- queued actions;
- completed reversible actions;
- completed irreversible actions;
- monitor or verifier state derived from memory.

After abort, revocation, expiry, permission change, or source correction, the system must compute the transitive repair closure and apply a type-specific rule prospectively frozen for each descendant type.

Required properties include:

- completeness over recorded edges;
- idempotence;
- deterministic replay under the frozen runtime;
- crash-safe resume;
- no resurrection by stale replicas or caches;
- tenant and principal isolation;
- preservation of audit history;
- explicit unresolved and leaked-effect states;
- independent verification that active descendants no longer rely on invalid ancestors.

Deleting or quarantining a record without invalidating derived summaries, embeddings, skills, queues, caches, and action plans is not complete repair.

The protocol must separately report provenance coverage. Cascade success over the recorded DAG does not establish that the DAG captured every real derivation.

## Machine-verification and fault-injection gate

Property-based testing and bounded exhaustive enumeration are required compatible controls where the protocol exposes a finite executable state machine.

The verification identity must include:

- exact implementation commit;
- state abstraction and symmetry reduction;
- record, transaction, principal, and depth bounds;
- transition relation;
- invariants and assumptions;
- checked state and transition counts;
- counterexample retention policy;
- random generator, seed policy, and shrinker;
- runtime and dependency identities.

Required adversarial fault injections include:

- process crash before and after each state transition;
- dropped, duplicated, delayed, and reordered messages;
- stale replicas and stale caches;
- partial storage failure;
- network partition;
- concurrent revocation and action;
- audit-log loss or truncation;
- permission downgrade or laundering;
- logical-clock skew;
- retry storms and duplicate side effects;
- dependency-edge omission;
- tool reversibility changing after gate approval.

Passing a bounded checker supports only the checked state space and assumptions. It may not be represented as general formal verification.

## Required external comparator matrix

Before internal telemetry receives credit for memory safety or action-risk prediction, future compatible work must compare against:

1. no durable memory;
2. session-only state;
3. last-write-wins memory;
4. provenance-preserving structured writes;
5. temporal validity and supersession without transactions;
6. snapshot isolation without semantic conflict handling;
7. semantic conflict handling without action gating;
8. permissions without derived-permission inheritance;
9. action gating without cascade repair;
10. cascade repair without action-input lineage;
11. full transactional belief commit;
12. blanket refusal or block-all controls;
13. deterministic requirement ledgers and workflow state machines;
14. matched combinations of external controls and internal telemetry.

Trap cases must be paired with required-action controls so that blocking everything cannot appear safe.

Report successful actions retained, baseline failures repaired, baseline successes regressed, over-abstention, downstream harm, leaked effects, full cost, and high-severity tails separately.

## Internal-monitor residual-value gate

Hidden-state, router, workspace, sparse-feature, transcoder, or Jacobian signals receive no credit merely for predicting a deterministic protocol violation.

Before internal telemetry receives incremental credit, compare against frozen external features available at the decision boundary:

- lifecycle state;
- snapshot age and isolation level;
- in-flight transaction count;
- read, write, dependency, and action-set sizes;
- conflict type and authority relation;
- validity and supersession state;
- permission and share scope;
- provenance depth and missing-edge indicators;
- action effect class;
- action-input lineage completeness;
- tentative, quarantined, revoked, or unstable ancestors;
- retry count, concurrent-writer count, and repair backlog;
- deterministic schema and policy violations;
- external verifier and requirement-ledger state.

Future actions, completed side effects, later revocations, sealed labels, and post-outcome verifier results may not enter a prospective commit or action monitor.

Prediction does not authorize commit rejection, trust mutation, revocation, retrieval suppression, action blocking, compensation, retry, repair, routing intervention, activation steering, or production control. Each remains a separately preregistered intervention.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q exact-target-runtime provenance, strict loading, deterministic forward, VJP, JVP, and finite-difference admission.
2. Admit Agents-A1-4B under its exact checkpoint, processor, harness, memory manager, database, queue, tool stack, and runtime.
3. Establish no-memory, session-only, last-write-wins, structured-write, temporal-validity, transaction, action-gating, and cascade-repair comparators.
4. Freeze lifecycle states, isolation levels, risk tiers, action-effect classes, tool schemas, principals, permissions, logical clock, verifier, and fault model.
5. Require exact action-input lineage for every externally consequential action.
6. Measure write, validation, conflict, commit, retrieval, action, revocation, repair, compensation, leakage, objective outcome, and cost separately.
7. Establish schema, confidence, logit, trajectory, memory-state, program-state, residual-state, and spectral baselines.
8. Separately admit Agents-A1-35B checkpoint, quantization, router, experts, topology, cache, batching, serving runtime, and durable-memory implementation.
9. Capture bounded route and cache summaries at staging, validation, commit, retrieval, pre-action gate, and repair boundaries only after the corresponding runtime paths are admitted.
10. Require router telemetry to add sealed value beyond the complete deterministic transaction-state and hidden-state comparator stack.
11. Add sparse-feature or transcoder comparators when separately admitted.
12. Add Jacobian-Lens features only after exact derivative parity and sealed incremental value over the full transaction-aware, action-lineage-aware, repair-aware, route-aware comparator stack.
13. Keep memory mutation, commit rejection, revocation, action blocking, compensation, early exit, retry, repair, forced routing, activation steering, reward shaping, and production deployment separately gated.

No MemTX result, Agents-A1-4B result, or result from another stateful framework authorizes durable-state or action control on Agents-A1-35B.

## Privacy, sealed-data, and repository boundary

Transactional memory and repair traces can contain personal claims, private communications, tool results, credentials, payments, bookings, health data, financial data, proprietary records, access-control state, inferred attributes, and external side effects.

No raw or summarized per-user message, staged record, snapshot, conflict, permission graph, dependency edge, proposed action, gate result, tool parameter, compensation record, external-state observation, hidden state, route, Jacobian, verifier label, or per-example prediction may be committed to this public repository.

Non-synthetic work requires separately authorized data inventory, purpose limitation, consent or authority, tenant isolation, least privilege, secret and personal-data filtering, immutable audit controls, correction and deletion propagation, retention limits, incident response, and aggregate-only scientific receipts.

## Current blocker and execution order

This addendum does not change the active blocker.

The next admissible engineering work remains:

1. Execute the composed Transformers provenance adapter in the exact target runtime and retain aggregate evidence only.
2. Freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` as one immutable tuple.
3. Bind the actual GPTQModel/Defuser loader entry and complete executable source closure.
4. Run strict synthetic Qwen3.5-MoE loading.
5. Prove one-time packed-tensor consumption.
6. Prove exact expert and fusion ordering.
7. Prove deterministic forward, activation-VJP, activation-JVP, and finite-difference parity.
8. Complete Phase 0 before weight staging or any separately authorized GPU transition.

## Established versus unproven

Established only as external evidence:

- MemTX supplies a public executable transactional memory protocol, benchmark, baselines, result files, and invariant checker at the pinned revision.
- The reported protocol separates tentative, committed, action-safe, quarantined, superseded, and revoked state.
- The reported benchmark finds substantial value from semantic conflict adjudication, permission inheritance, action gating, and cascade repair under its tested conditions.
- Bounded executable checking found no violations of the stated invariants within the enumerated state space.
- The reported benchmark recorded zero downstream harm for MemTX across the tested backbones and scenarios.

Not established:

- Production safety or natural-world prevalence.
- Unbounded correctness of the protocol.
- Complete action-input safety from the paper's existential strong gate.
- Environment-level restoration from compensation bookkeeping.
- Repair of derivations absent from the recorded DAG.
- Correctness under arbitrary crashes, partitions, storage failures, replica lag, dynamic reversibility, or malicious principals.
- Transfer to Qwen3.5/Qwen3.6 MoEs or either Agents-A1 checkpoint.
- Internal truth recognition, semantic-workspace detection, router-specific value, or Jacobian-specific value.
- Complete Q35Q target-runtime, loader, tensor-consumption, expert-ordering, forward, or derivative admission.
- Safe memory control, action gating, compensation, early exit, retry, repair, forced routing, activation steering, reward shaping, or production deployment.

The research program remains unfinished.
