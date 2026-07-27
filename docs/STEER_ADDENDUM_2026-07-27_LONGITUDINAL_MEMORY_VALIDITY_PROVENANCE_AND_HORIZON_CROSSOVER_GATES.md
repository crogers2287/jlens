# STEER ADDENDUM — longitudinal memory validity, provenance, and horizon-crossover gates

Date: 2026-07-27

Parent remote head: `f8cac116a704846d84a23d4cb824bcbe18d222b1`

Status: binding future-protocol correction; no current execution authorization

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- GitHub currently reports this repository as public. Aggregate-only commit restrictions remain binding.
- No weight staging, tensor-payload retrieval, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, memory ingestion, intervention, or production use is authorized by this document.
- Every privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, cleanup, commit-safety, comparator, nuisance-control, production-gating, and stop rule remains binding.

## New primary evidence and narrow interpretation

Spencer, **Ground Truth First: A Longitudinal Evaluation Instrument for Agent Memory, and the Tenure Crossover in Memory-Architecture Rankings**, arXiv `2607.21962v1`, submitted 2026-07-24, introduces a synthetic longitudinal memory benchmark whose facts, validity intervals, volatility classes, source channels, and answer keys are generated before rendered conversations or emails.

The reported benchmark contains approximately 380 questions across fifteen types, three replicates, two history horizons, five memory architectures, and a no-memory control. The paper reports:

1. A budgeted curated-map memory declining from approximately 96 percent at three weeks to 72 percent at nine weeks because relevant evicted content became unavailable.
2. A provenance-typed graph rising to approximately 90 percent at the longer horizon.
3. A positive architecture-ranking inversion for all six synthetic users under complete cross-family re-judging, with reported exact `p = 0.031`.
4. A full-rendered-history baseline tying or exceeding the strongest memory system at the short horizon but showing no judge-independent advantage at nine weeks while using approximately twice the read cost.
5. Weakly written facts failing approximately 24 percent of downstream questions versus approximately 2 percent for strongly written facts.
6. Injection resistance tracking whether provenance boundaries survived memory representation.
7. A layered architecture performing best among the reported memory systems in both tested regimes and being released as the open-source Veracium library.

The inspected Veracium repository represents typed graph facts and dated episodes as the store of record, compiles a wiki-like cache rather than treating it as ground truth, retains superseded values as history, and structurally quarantines third-party claims rather than promoting them into user facts.

The binding interpretation is narrow:

- Memory quality is conditional on tenure, write quality, source provenance, temporal validity, retrieval budget, and evaluation date.
- A system that leads on short histories may lose on longer histories.
- A short-horizon memory score does not establish durable memory quality.
- A flat current-state summary can erase history even when its current answer is accurate.
- Full rendered history is a comparator, not a free or necessarily durable solution.
- Provenance-aware representation is a plausible security and factual-integrity control, not proof of general production safety.
- These are synthetic-benchmark and one-library results. They do not establish transfer to Agents-A1, natural private user histories, long-horizon tool agents, multimodal memories, internal correctness awareness, router value, Jacobian-Lens value, or safe intervention.

## Binding ontology: event time is not memory time

Every future longitudinal memory experiment must distinguish at least:

1. **Event time:** when the represented event or state was true or occurred.
2. **Observation time:** when the agent, tool, user, or external source supplied the evidence.
3. **Write time:** when the memory system ingested or transformed the evidence.
4. **Validity start:** the earliest time at which a fact may be treated as active.
5. **Validity end:** the time after which the fact is expired or superseded for current-state questions.
6. **Supersession time:** when a newer admissible fact replaced an earlier current value.
7. **Retrieval time:** when the memory system selected the record for a decision.
8. **Decision time:** when the model or controller consumed the retrieved material.
9. **Answer as-of time:** the temporal reference explicitly or implicitly requested by the task.
10. **Verification time:** when the canonical evaluator determined correctness.

These identities may coincide in a simple example but may not be silently collapsed in a longitudinal claim.

A current-state answer, historical answer, prediction, recollection of a past belief, and report of what a third party claimed are distinct query types. One cannot substitute for another.

## Temporal-validity and supersession gate

Every memory record used in training, validation, certification, or sealed evaluation must carry an immutable temporal-status contract where applicable:

- valid-from and valid-until boundaries;
- current, historical, expired, superseded, contradicted, disputed, or unknown status;
- predecessor and successor identities;
- whether multiple values may coexist;
- the rule used to resolve overlapping intervals;
- the rule used when event time or validity is missing;
- the rule used for recurrence, deadlines, and one-time events;
- the rule used for corrections and retractions;
- retention, archival, compaction, and deletion behavior.

Overwriting a mutable fact without preserving its admitted predecessor is not equivalent to supersession-aware memory.

Deleting expired facts may improve current-state accuracy while destroying historical answerability. Retaining all facts without temporal filtering may improve historical recall while corrupting current-state answers. Both effects must be measured separately.

A time-to-live value, recency heuristic, or last-write-wins rule is a policy artifact. It must be frozen before outer evaluation and cannot be represented as natural temporal truth.

## Source-channel, authorship, and trust boundary

Every admitted memory item must identify the source channel and author role. At minimum distinguish:

- direct user assertion;
- system or developer instruction;
- tool observation;
- deterministic verifier result;
- received email or message;
- retrieved document or webpage;
- third-party assertion;
- model-generated summary;
- model inference or hypothesis;
- imported historical record;
- corrected or retracted evidence.

A claim appearing in material the agent read does not become a fact about the user or world merely because it was stored.

Third-party claims, model inferences, retrieved documents, and unverified summaries must remain structurally distinguishable from direct assertions and deterministic evidence throughout ingestion, transformation, retrieval, compaction, and answer generation.

Required adversarial controls include:

- contact impersonation;
- plausible but false debt, obligation, deadline, preference, or identity claims;
- conflicting direct and third-party assertions;
- forwarded or quoted content whose grammatical speaker differs from the message sender;
- summaries that erase authorship;
- repeated low-trust claims intended to dominate retrieval;
- delayed corrections and retractions;
- cross-user or cross-tenant identity collisions.

Retrieval relevance cannot override source trust or authorship identity.

## Horizon-crossover gate

No architecture may be called the best, most reliable, most efficient, or production-ready memory system from one history horizon.

Compatible longitudinal studies must preregister at least two materially separated tenure horizons. Three or more are preferred when feasible. The same underlying users, fact families, source channels, volatility classes, and question types must be represented across horizons where the design permits.

Report separately for each horizon:

- current-state accuracy;
- historical and as-of-date accuracy;
- supersession and correction accuracy;
- source-attribution accuracy;
- injection and impersonation resistance;
- abstention and unresolved-conflict behavior;
- write-stage extraction quality;
- retrieval recall and precision;
- answer synthesis accuracy conditional on correct retrieval;
- read, write, storage, maintenance, and judge cost;
- latency, context length, and model calls;
- per-family and per-volatility results.

Architecture rankings, error composition, and cost rankings must be compared across horizons. A crossover must be reported as a crossover, not averaged into a single global ranking.

A memory system whose primary advantage depends on a narrow tested tenure must be scoped to that tenure unless prospective transfer is established.

## Required memory comparator matrix

Before attributing operational value to hidden states, router telemetry, sparse features, semantic-workspace signals, or Jacobian features on long-horizon tasks, include the following memory conditions when technically compatible:

1. No durable memory.
2. Full rendered history under an explicit context and read-cost budget.
3. Fixed recent-window history.
4. Recency-only or last-write-wins current-state map.
5. Curated current-state map with explicit write rules.
6. Episodic store with dated events.
7. Provenance-typed relational or graph memory.
8. Layered memory combining current-state, episodic, and provenance-preserving records.
9. External requirement ledger or deterministic state tracker where the domain permits.
10. Frozen combinations of memory and internal telemetry.

Each condition must use the same answerer, task population, as-of-date policy, judge or verifier, allowed source material, and outcome taxonomy.

Context-budget, retrieval-budget, storage-budget, and maintenance-cost differences must be reported. A full-history condition is not equal-cost merely because it uses no learned memory module.

## Write, retain, retrieve, and answer decomposition

End-to-end memory accuracy must be decomposed into at least:

1. Source parsing and authorship assignment.
2. Fact extraction.
3. Temporal-validity assignment.
4. Entity and user resolution.
5. Write acceptance or rejection.
6. Supersession and contradiction handling.
7. Retention or eviction.
8. Retrieval candidate generation.
9. Ranking and budget selection.
10. Context rendering.
11. Answer synthesis.
12. Canonical verification.

A downstream wrong answer does not establish retrieval failure. A retrieved correct fact followed by a wrong answer is a synthesis or reasoning failure. A correct current answer obtained from a falsely attributed source is not a provenance success.

Write-stage quality must be measured directly. A memory backend cannot receive full credit for an answerer compensating for malformed writes, and a writer cannot receive full blame for a retrieval policy that evicts or suppresses correct records.

## Gold, judge, and answerability gate

Where possible, longitudinal facts and answers must be generated or verified from an immutable structured script before free-form text rendering.

The protocol must freeze:

- gold fact identity and temporal intervals;
- question generation rules;
- answerability checks;
- accepted answer forms;
- judge identity, version, prompt, decoding, and disagreement handling;
- deterministic checks available for dates, identities, quantities, and source channels;
- blind re-judging or judge-robustness procedures.

An LLM judge is model evidence, not ground truth. Architecture rankings that change across judges must be reported as judge-dependent.

Questions created after inspecting system failures are development data and require a fresh sealed population.

## Internal-monitor residual-value gate

Memory state, memory failures, and internal model telemetry are separate objects.

Future monitor studies must report full-population and residual-failure results after conditioning on:

- horizon and history length;
- memory architecture;
- source channel and trust class;
- fact volatility;
- validity and supersession status;
- write quality;
- retrieval success;
- context budget and truncation;
- question type and as-of-date;
- deterministic ledger or verifier state.

A hidden-state, router, workspace, sparse-feature, transcoder, or Jacobian monitor that primarily predicts stale writes, evicted facts, source-attribution failures, or retrieval misses must be classified as memory/process telemetry unless it adds sealed objective value beyond admitted external memory and ledger controls.

Prediction does not authorize memory rewriting, deletion, trust reassignment, retrieval suppression, retry, abort, truncation, forced routing, activation steering, or production control.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q production-path provenance, strict loading, forward parity, and derivative admission.
2. Admit Agents-A1-4B separately under its exact artifact, processor, runtime, and tool harness.
3. Define synthetic or otherwise admissible longitudinal fact scripts with validity intervals, source channels, volatility classes, corrections, and as-of-date questions without sealed-outcome access.
4. Establish no-memory, full-history, recent-window, current-map, episodic, provenance-graph, layered-memory, and external-ledger baselines across multiple preregistered horizons.
5. Measure write, retention, retrieval, synthesis, source-attribution, and temporal-validity failures separately.
6. Establish confidence, logits, metadata, selected hidden-state, and bounded trajectory baselines on the complete population and residual memory failures.
7. Separately admit Agents-A1-35B checkpoint, router, experts, quantization, topology, serving state, and tool harness.
8. Re-run the longitudinal memory matrix on the 35B MoE rather than transferring the 4B ranking or thresholds.
9. Add minimal route identity, margin, entropy, occupancy, and parent-route innovation at frozen memory decision boundaries.
10. Require route features to add sealed value after horizon, provenance, validity, write quality, retrieval, and dense-sibling controls.
11. Add sparse-feature or transcoder comparators when admitted.
12. Add Jacobian-Lens features only after exact derivative parity and sealed incremental value over the complete horizon-aware memory, ledger, trajectory, confidence, hidden-state, and route comparator stack.
13. Keep memory rewriting, compaction, deletion, source-trust mutation, retrieval gating, early exit, retry, repair, forced routing, activation steering, reward shaping, and production deployment separately preregistered and authorized.

No short-horizon result on Agents-A1-4B or another model authorizes durable-memory claims or internal-monitor intervention on Agents-A1-35B.

## Privacy, sealed-data, and repository boundary

Longitudinal memory records can contain personal preferences, relationships, communications, schedules, location history, health information, financial information, credentials, proprietary documents, tool outputs, hidden benchmark state, and inferred attributes.

No raw or summarized per-user memory, conversation, email, document, retrieved neighbor, source identity, fact graph, temporal history, answer, judge rationale, verifier label, internal state, or per-example prediction may be committed to this public repository.

Before any non-synthetic memory store is authorized, require:

1. A frozen data inventory and threat model.
2. Purpose limitation and source-specific consent or authority.
3. Secret, credential, personal-data, proprietary-data, and hidden-test filtering.
4. Tenant and user isolation.
5. Membership, reconstruction, linkage, and nearest-neighbor disclosure testing.
6. Retention, deletion, correction, and supersession propagation.
7. Access logging and provenance-preserving redaction.
8. Aggregate-only scientific records here.

Provenance retention does not authorize indefinite retention of private content. Deletion obligations and historical scientific reproducibility must be reconciled through separately admitted aggregate receipts, not by retaining prohibited raw records in this repository.

## Current blocker and execution order

This addendum does not change the active blocker.

The next admissible engineering work remains one clean-subprocess, fail-closed production adapter that:

1. verifies the frozen upstream Transformers artifact;
2. derives expected source identities from that verified artifact;
3. binds the imported package to its owning installed distribution and ownership records;
4. derives the complete source closure from the actual live dispatch, converter, nested-operation, model, configuration, and loader objects;
5. invokes the real conversion dispatch and eventual loader entry point;
6. compares exact expected and observed identities and structures;
7. rejects shadow packages, editable installs, monkeypatches, forged identity bundles, incomplete closure, wrong ownership, and unadmitted loaders;
8. emits one aggregate fail-closed result.

After that remain the immutable GPTQ runtime tuple, strict synthetic loading, exact packed-tensor consumption and expert ordering, deterministic forward/VJP/JVP/finite-difference parity, complete Phase-0 admission, weight staging, and a separately authorized GPU transition.

## Established versus unproven

Established only as external public evidence:

- A ground-truth-first synthetic benchmark can encode temporal validity, source-channel trust, injection probes, and as-of-date questions before rendered text.
- In the reported experiment, memory-architecture rankings changed between three-week and nine-week histories.
- Write quality was strongly associated with downstream answer quality.
- Preserved provenance boundaries tracked injection resistance in the reported harness.
- Veracium implements a layered, provenance-aware memory design with retained supersession history and structural third-party-claim quarantine.
- Longitudinal memory, external ledgers, and full-history baselines are mandatory future comparators before expensive internal-monitor necessity claims.

Unproven for this program:

- Independent reproduction of the paper and complete harness.
- Ranking stability under other judges, answerers, users, horizons, tasks, languages, modalities, and natural histories.
- Privacy safety or production security of Veracium or any compared memory architecture.
- Transfer to Qwen3.5, Qwen3.6, Agents-A1-4B, or Agents-A1-35B.
- A universally optimal memory architecture or retention policy.
- Correctness awareness from memory state, hidden states, router telemetry, workspace features, sparse features, or Jacobians.
- Incremental router or Jacobian-Lens value beyond horizon-aware memory and ledger controls.
- Safe memory mutation, deletion, source-trust reassignment, early exit, retry, repair, forced routing, activation steering, reward shaping, or production deployment.

The research program remains unfinished.