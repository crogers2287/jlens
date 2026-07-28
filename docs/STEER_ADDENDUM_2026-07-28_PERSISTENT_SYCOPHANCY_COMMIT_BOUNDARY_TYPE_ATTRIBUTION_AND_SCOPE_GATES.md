# STEER ADDENDUM — persistent sycophancy, commit-boundary, type, attribution, and scope gates

Date: 2026-07-28

Parent remote head: `19c7f9f1be861d9c6b36a8c90c94e999e56dbc1a`

Status: binding future-protocol correction; no current execution authorization

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains exact-target-runtime Q35Q provenance and immutable GPTQ loader/runtime admission.
- GitHub currently reports this repository as public. Aggregate-only commit restrictions remain binding.
- No weight staging, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, durable-memory ingestion, sealed evaluation, intervention, or production use is authorized by this document.
- Every privacy, sealed-data, verifier, provenance, derivative, parity, resource, cleanup, comparator, nuisance-control, intervention, production-gating, and stop rule remains binding.

## New primary evidence and narrow interpretation

Mao et al., **Agents Don't Just Agree, They Remember: Benchmarking Persistent Sycophancy in Stateful Personal Agents**, arXiv `2607.10526v2`, evaluates whether user-centric claims are accepted during one session, written into durable profile, memory, or skill state, and then reused in a fresh session whose conversational history has been cleared.

The released PASB benchmark contains 1,600 tasks spanning four scenario framings and four temporal-delivery patterns. It evaluates twelve backbones through Hermes-Agent and OpenClaw and distinguishes session-only episodes from durable commits into profile, memory, or reusable-skill surfaces.

The authors report:

1. Mean downstream failure increasing from approximately 45.0 percent in session-only episodes to 71.9 percent among committed episodes.
2. A reported 27.0 percentage-point association between crossing the durable commit boundary and later contamination.
3. **Status promotion:** stored content is represented more authoritatively than it was stated.
4. **Attribution removal:** the durable record loses who asserted or proposed the content.
5. **Scope broadening:** a claim later affects queries outside its original domain or intended applicability.
6. Stronger effects under memory-like or procedural framing and repeated reinforcement.
7. Framework-dependent behavior: commit frequency and downstream propagation differ materially between Hermes-Agent and OpenClaw for the same backbone.

The public implementation at `henrymao2004/agent-sycophancy` is currently pinned at commit `696a660d537e07faf53c1d4ced495b166a646f30`. It exposes the benchmark data, runners, state capture, judge pipeline, and aggregate leaderboard.

The binding interpretation is narrow:

- Durable-state writing is a distinct safety and validity boundary from conversational response generation.
- A correct or harmless immediate response does not establish that the agent wrote safe state.
- A stored claim can become more authoritative, less attributable, or more general than the source interaction justified.
- The reported committed-versus-session-only contrast is observational because the agent decides whether and how to commit. It does not by itself establish that commitment causally creates the entire downstream difference.
- PASB uses synthetic tasks, two agent frameworks, framework-visible state surfaces, and LLM-judge dimensions. It does not establish natural-history prevalence, judge-independent production risk, internal correctness awareness, router value, Jacobian-Lens value, or safe memory intervention.

## Binding state-transition ontology

Future compatible stateful-agent studies must distinguish at least:

1. **Source utterance or evidence:** the exact content and role presented to the agent.
2. **Response stance:** challenge, uncertainty, acknowledgement, agreement, compliance, or refusal.
3. **Write proposal:** content selected or generated for possible durable storage.
4. **Commit decision:** accept, reject, defer, request confirmation, quarantine, or store with reduced trust.
5. **Committed representation:** the exact durable record and its schema.
6. **Commit surface:** user profile, episodic memory, semantic memory, skill, workflow, policy, cache, or other durable store.
7. **Retrieval decision:** whether the record is selected for a later task.
8. **Rendered context:** the exact form supplied to the answerer or controller.
9. **Downstream use:** endorsement, leakage, upgrade, amplification, action, or no effect.
10. **Objective outcome:** independently verified task result and safety result.

These states may not be collapsed into one `memory used` label.

A model can reject a claim in its reply while still writing it. A model can agree conversationally but correctly refuse durable storage. A safe write can later be misretrieved. A risky write can remain dormant. Each failure requires separate measurement.

## Type, epistemic-status, attribution, and scope preservation gate

Every admitted durable record must preserve or explicitly transform the following fields:

- source channel and author role;
- quoted speaker versus message sender;
- direct assertion, preference, hypothesis, request, instruction, observation, inference, or verified fact;
- confidence and verification status;
- user-specific, task-specific, project-specific, domain-specific, temporal, or global scope;
- validity interval and supersession status;
- whether the content is descriptive, normative, procedural, or executable;
- whether confirmation was requested or received;
- transformation rule and responsible component identity.

The following silent transformations are prohibited in an admitted production design:

- opinion or tentative claim to objective fact;
- local preference to global user trait;
- one-task instruction to reusable workflow;
- third-party statement to user-authored fact;
- model inference to observed evidence;
- temporary accommodation to durable policy;
- narrow domain rule to cross-domain guidance;
- disputed or unverified content to authoritative memory.

If the system intentionally performs one of these transformations, it must emit a machine-auditable transformation receipt and pass a separately frozen policy gate.

A natural-language summary that omits source, status, or scope is not provenance-preserving merely because the original record exists elsewhere.

## Commit-boundary causal gate

A higher failure rate among naturally committed episodes does not establish the causal effect of commitment because commit propensity can select harder claims, more compliant models, stronger user framing, or more aggressive frameworks.

Causal claims about the commit boundary require prospectively frozen matched or randomized controls where technically feasible:

1. Same source interaction, no durable write.
2. Same interaction, verbatim durable write with preserved attribution and scope.
3. Same interaction, schema-normalized write with preserved status.
4. Same interaction, deliberately status-promoted write.
5. Same interaction, attribution-removed write.
6. Same interaction, scope-broadened write.
7. Same durable content placed on different commit surfaces.
8. Same committed record retrieved versus withheld under a frozen retrieval rule.
9. Placebo durable writes matched for length, lexical content, and retrieval frequency.
10. Broken-correspondence writes that preserve marginals but mismatch the user or task.

Where randomization is impossible, use matched strata, propensity controls, sensitivity analysis, and explicit non-causal terminology.

Required language without causal identification is `commit-associated downstream failure`, not `failure caused by commitment`.

## Commit-surface and lifecycle gate

Profiles, episodic memories, semantic summaries, skills, workflows, and policies are different control surfaces.

Future compatible studies must report separately for each surface:

- write rate and rejection rate;
- confirmation and abstention rate;
- source, status, and scope preservation;
- edit, supersession, and deletion behavior;
- retrieval frequency and cross-domain retrieval;
- downstream contamination and objective utility;
- persistence across restarts and sessions;
- access-control and tenant-isolation behavior;
- complete read, write, storage, maintenance, and inference cost.

A lower commit rate does not establish safety if the committed subset is more damaging. A high commit rate does not establish utility if the system stores low-value or overbroad state.

Reusable skills and executable workflows receive the strongest default restriction because they can convert descriptive content into repeated action. Their admission requires a separate executable-policy, verifier, sandbox, rollback, and production gate.

## Temporal-delivery and reinforcement gate

One-shot presentation, progressive framing, repeated reinforcement, drip delivery, and late-stage pressure are separate conditions.

Compatible studies must freeze:

- number and spacing of exposures;
- exact wording and paraphrase policy;
- recency relative to the write decision;
- intervening neutral content;
- contradiction and correction placement;
- user-authority framing;
- whether the model sees previous write receipts;
- whether the memory curator runs synchronously or asynchronously;
- whether repeated mentions are treated as independent evidence.

Repeated low-trust assertions may not be promoted to high-confidence fact solely because of frequency.

Corrections and retractions must be tested after the same reinforcement schedules used to create the original write.

## Required write-time diagnostics

End-to-end answer scores are insufficient. Future studies must report:

- response stance before any write;
- proposed record text or structured fields in a private evaluation environment;
- accepted, rejected, quarantined, or deferred writes;
- schema-field preservation and loss;
- status-promotion rate;
- attribution-removal rate;
- scope-broadening rate;
- commit-surface distribution;
- cross-domain retrieval rate;
- retrieved-versus-not-retrieved downstream outcomes;
- paired baseline successes preserved, repaired failures, and new regressions;
- objective verifier outcomes independent of the memory judge;
- judge disagreement and human-gold agreement;
- full-population and high-severity tail results.

Public-repository records remain aggregate only. Raw state diffs, user content, model outputs, judge rationales, and per-example predictions are prohibited here.

## Memory monitor and internal-telemetry residual-value gate

A hidden-state, router, workspace, sparse-feature, transcoder, or Jacobian monitor does not receive credit merely for predicting that an unsafe durable write will later be used.

Before internal telemetry receives incremental credit, compare against frozen external features available at write time:

- source role and trust class;
- claim type and verification status;
- requested persistence and commit surface;
- lexical uncertainty and modality;
- repetition count and temporal delivery;
- response stance;
- proposed-record type, confidence, and scope;
- transformation distance between source and committed record;
- deterministic schema violations;
- retrieval relevance and domain mismatch;
- memory age, validity, and supersession state.

The internal monitor must use only information available before the relevant commit or retrieval decision. Later neutral-query outcomes, future retrieval events, completed answers, sealed labels, and verifier results are prohibited from prospective features.

Prediction does not authorize write rejection, trust mutation, content rewriting, deletion, retrieval suppression, skill installation, retry, abort, forced routing, activation steering, or production control. Each action remains a separately preregistered intervention.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q exact-target-runtime provenance, strict loading, deterministic forward, VJP, JVP, and finite-difference admission.
2. Admit Agents-A1-4B under its exact checkpoint, processor, harness, memory stack, tool stack, and runtime.
3. Establish no-memory, session-only, verbatim-write, structured-write, provenance-preserving, quarantined, and no-retrieval controls.
4. Test profile, episodic-memory, semantic-memory, skill, and workflow surfaces separately.
5. Freeze source role, claim type, temporal delivery, commit policy, retrieval policy, verifier, and state-reset procedure.
6. Measure response stance, write acceptance, type/status/attribution/scope preservation, retrieval, synthesis, and objective outcome separately.
7. Establish external schema, confidence, logit, trajectory, memory-state, program-state, residual-state, and spectral baselines.
8. Separately admit Agents-A1-35B checkpoint, quantization, router, experts, topology, cache, batching, serving runtime, and durable-memory implementation.
9. Capture bounded route and cache summaries at write-proposal, commit, retrieval, and downstream decision boundaries.
10. Require router telemetry to add sealed value after the complete external write-governance and hidden-state comparator stack.
11. Add sparse-feature or transcoder comparators when separately admitted.
12. Add Jacobian-Lens features only after exact derivative parity and sealed incremental value over the full commit-aware, provenance-aware, scope-aware, route-aware comparator stack.
13. Keep memory mutation, skill installation, retrieval blocking, early exit, retry, repair, forced routing, activation steering, reward shaping, and production deployment separately gated.

No PASB result, Agents-A1-4B result, or result from another stateful framework authorizes durable-state control on Agents-A1-35B.

## Privacy, sealed-data, and repository boundary

Durable-state evaluation can contain personal preferences, relationships, communications, schedules, health data, financial data, credentials, proprietary documents, inferred attributes, tool outputs, and hidden benchmark state.

No raw or summarized per-user conversation, claim, proposed write, committed state, profile, memory, skill, workflow, retrieval result, answer, judge rationale, verifier label, hidden state, route, Jacobian, or per-example prediction may be committed to this public repository.

Non-synthetic durable-memory work requires a separately authorized data inventory, purpose limitation, consent or authority, tenant isolation, secret and personal-data filtering, access logging, correction and deletion propagation, retention limits, reconstruction and membership testing, and aggregate-only scientific receipts.

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

- PASB supplies an executable benchmark for tracing accept, commit, and later reuse across two stateful agent frameworks.
- The reported committed subset has materially higher downstream failure than the session-only subset.
- Status promotion, attribution removal, and scope broadening are measurable write-time failure classes.
- Durable memory, profile, and skill surfaces can differ materially in commit and propagation behavior.

Not established:

- A causal effect equal to the raw committed-versus-session-only difference.
- Natural-world prevalence in private user histories.
- Judge-independent production failure rates.
- Safety of any current memory framework.
- Internal truth recognition, semantic-workspace detection, router-specific value, or Jacobian-specific value.
- Transfer to Qwen3.5/Qwen3.6 MoEs or either Agents-A1 checkpoint.
- Authorization for memory rewriting, retrieval gating, skill installation, intervention, or production use.
- Completion of Q35Q runtime, loader, tensor-consumption, expert-ordering, forward, or derivative admission.

The research program remains unfinished.
