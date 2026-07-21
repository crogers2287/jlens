# STEER ADDENDUM — Representation-conditioned context pruning and hidden-state capture gates

Date: 2026-07-21

Parent remote head: `ea1ebe1380b10940931ece7b00285b549da9dd81`

Status: binding future-protocol correction; no current execution authorization

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- GitHub currently reports this repository as public. Aggregate-only commit restrictions remain binding.
- No weight staging, tensor-payload retrieval, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, context mutation, intervention, or production use is authorized by this document.
- Every privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, cleanup, commit-safety, comparator, nuisance-control, production-gating, and stop rule remains binding.

## New primary evidence and narrow interpretation

Wang et al., **SWE-Pruner Pro: The Coder LLM Already Knows What to Prune**, arXiv `2607.18213v1`, submitted 2026-07-20, reports a learned line-level context-pruning head that consumes the coding agent backbone's own last-layer hidden states.

Primary sources inspected:

- paper: `https://arxiv.org/abs/2607.18213`;
- public implementation: `Ayanami1314/swe-pruner-pro` at immutable revision `6cd7f819ba5740b527ce52855982ce254df45291`;
- source-release commit: `622f24ed6c73b5acb174436382b736ec79a25edd`;
- patched serving target: SGLang `0.5.10.post1`.

The public evidence supports only the following bounded statements:

1. The method reads last-layer hidden states generated while the frozen backbone prefills a new tool response.
2. A learned length-aware feed-forward head assigns per-token keep probabilities and converts them to per-line decisions by majority vote.
3. The training labels were generated from multi-turn coding-agent trajectories by Claude Sonnet 4.6; uncertain lines were retained rather than treated as safe deletions.
4. The reported backbones are two open-weight MoEs: Qwen3-Coder-Next, approximately 80B total and 3B active, and MiMo-V2-Flash, approximately 309B total and 15B active.
5. On the reported read-only multi-turn tasks, the method reduced aggregate token use by as much as 39.4 percent while roughly preserving task quality.
6. On SWE-Bench Verified the result was backbone-dependent: MiMo-V2-Flash gained nineteen resolves out of five hundred but increased input tokens and API calls, while Qwen3-Coder-Next lost six resolves while reducing input tokens and increasing API calls.
7. The method does not prune the tool response before the immediately following generation. The current turn attends to the full raw response; only later turns receive the pruned replacement.
8. The released SGLang path required repairs for mixed hidden-state and non-hidden-state batching, chunked-prefill accumulation, and prefix-cache coverage.
9. After those repairs, the authors report exact shape agreement on forty-eight reference samples and median cosine similarity of 0.997, but not exact numerical equality or full-tail parity.
10. Moving hidden states outside the engine can create very large payloads; the released implementation therefore supports binary downcasting and an in-engine head.

These are external public results. They do not establish correctness awareness, privileged introspection, safe deletion, universal context compression, production hidden-state capture correctness, Agents-A1 transfer, or any Jacobian-Lens result.

## Binding correction: relevance readout, pruning policy, and context mutation are separate objects

Future work must distinguish:

1. **Representation readout:** a frozen head estimates whether a line or span appears relevant from already-produced hidden states.
2. **Pruning policy:** a frozen rule converts scores into keep, summarize, defer, retrieve-on-demand, or delete decisions.
3. **Context mutation:** the harness changes the information available to later model calls.
4. **Outcome monitor:** a signal predicts correctness, failure, requirement loss, or risk.
5. **Controller:** a policy uses any signal to change execution.

A representation may encode line relevance without encoding correctness. A useful pruner may improve task success by reducing context interference without detecting model error. A deletion policy is an intervention even when the backbone weights and current-turn logits are unchanged.

No context-pruning result may be represented as passive monitoring, correctness prediction, early-error detection, semantic-workspace validation, or safe intervention unless the corresponding endpoint is evaluated separately.

## Temporal information boundary

Every context-pruning study must state exactly when the raw observation is visible and when the mutation takes effect.

At minimum distinguish:

- raw tool output before prefill;
- hidden-state capture during prefill;
- the immediately following generation that can still attend to the raw output;
- the next-turn history after pruning or replacement;
- later summaries, retries, branches, resumes, and verifier calls.

A method that prunes only after the next action cannot claim to prevent an error in that action. A future-turn token reduction cannot be represented as current-turn compute reduction. Retrospective line labels cannot establish prospective necessity at an earlier boundary.

## Hidden-state capture is a production-path artifact requiring its own admission

Hidden-state capture is not correct merely because the model returns a tensor with the expected rank.

The admitted capture path must freeze:

- model and checkpoint revision;
- processor and tokenizer;
- requested layer and exact pre-normalization or post-normalization location;
- dtype and any downcast;
- attention implementation;
- serving backend and immutable commit;
- tensor, pipeline, and expert-parallel topology;
- continuous-batching and scheduler policy;
- chunked-prefill policy and chunk size;
- prefix-cache, radix-cache, eviction, and reuse policy;
- request identifiers, token offsets, line mapping, and absolute-position semantics;
- serialization format and in-engine versus off-engine placement;
- capture and pruning-head code, configuration, and digests.

Before scientific use, the capture path must pass a fail-closed adversarial suite covering:

1. all-hidden-state batches;
2. mixed hidden-state and ordinary requests;
3. request reordering inside continuous batches;
4. prompts below, at, and above each chunked-prefill boundary;
5. multiple chunks with exact positional reconstruction;
6. complete and partial prefix-cache hits;
7. identical and overlapping prefixes across requests;
8. cache eviction and re-prefill;
9. cancellation, retry, timeout, and resume;
10. heterogeneous sequence lengths;
11. single-request and concurrent execution;
12. every admitted quantization, attention kernel, and topology.

Validation must report exact tensor shapes, token identities, absolute positions, missing or duplicate positions, maximum and percentile numerical errors, and complete tail behavior. Median cosine similarity is insufficient. A small subset of badly corrupted tokens can control a line-level decision even when median cosine is high.

Passive capture mode must also prove generation-path isolation: unchanged logits, tokens, KV state, router assignments, tool calls, verifier inputs, and scheduler-visible request semantics apart from the measured capture cost.

## Pruning-head artifact and label provenance

A learned pruning head is a separately admitted artifact. Freeze and hash:

- architecture, hidden width, normalization, activation, dropout, and length embedding;
- source layer and token pooling rule;
- tokenizer and token-to-line mapping;
- line aggregation, threshold, gap-filling, minimum-retention, and fallback rules;
- checkpoint bytes and safe serialization schema;
- optimizer, schedule, seed policy, training code, and dependency lock;
- label model, exact label prompt, temperature, schema, and disagreement handling;
- uncertain-line policy;
- training corpus identities, licenses, filters, language mix, output-length limits, and deduplication;
- train, selection, calibration, certification, and sealed-test partitions.

Executable pickle loading is not an admitted production artifact path. Convert weights through an isolated, credential-free lane into a non-executable tensor format with verified schema and digests, or reject the artifact.

## Leakage and partition controls

Line-level labels from the same trajectory, repository, task template, tool command, file, or repeated output are clustered observations.

Future studies must split prospectively by the strongest available unit, including repository, task family, trajectory, environment, template, and source corpus. No trajectory may contribute lines to both training and evaluation.

The following may not enter head training, layer selection, threshold selection, calibration, or certification:

- sealed task outcomes;
- canonical patches or answers;
- future trajectory steps unavailable at the pruning boundary;
- verifier results produced after pruning;
- private production trajectories outside an authorized boundary;
- failure-specific hints created after reviewing sealed errors.

A label generated by another LLM remains model-produced supervision, not ground truth. Its false-delete and false-keep behavior must be validated against human review or executable task outcomes on an independent sample.

## Mandatory comparator stack

Representation-conditioned pruning is a cheaper and more direct comparator than router or Jacobian instrumentation for context-management claims.

When technically compatible, future comparisons must include:

1. no pruning;
2. fixed token or line truncation;
3. a recency or sliding-window policy;
4. deterministic structural retention for errors, stack traces, diffs, headings, and requirement identifiers;
5. retrieval or reranking from the full raw output;
6. one-level progressive disclosure or bounded working-set navigation;
7. an external task-conditioned code or text pruner;
8. self-pruning by the same backbone through an explicit prompt;
9. a linear hidden-state relevance probe;
10. the proposed nonlinear hidden-state head;
11. a keep-all fallback at the same invocation boundaries;
12. checklist and requirement-ledger controls where the task has enumerable obligations.

All comparators must receive the same raw observation, task split, decision boundary, harness, verifier, decoding, and retention budget. A hidden-state head is not operationally necessary when a cheaper deterministic, retrieval, progressive-disclosure, or external-pruner policy achieves equal sealed utility.

## Retention-risk and failure accounting

Token savings are not sufficient evidence of safe context mutation.

Required reporting includes:

- essential-line recall and catastrophic false-delete rate;
- false-keep rate and retained-token fraction;
- requirement, permission, credential-boundary, error, traceback, patch, test, and verifier-evidence retention;
- task success and failure by tool-output type;
- recoverable versus irreversible deletion effects;
- whether deleted material can be re-fetched exactly;
- retrieval and recovery latency after a false deletion;
- results under malformed, adversarial, duplicated, reordered, multilingual, and very short outputs;
- full-population results, not only successful or compressible examples.

The frozen safe default for unavailable, malformed, misaligned, out-of-distribution, or uncertified scores is `keep`, not silent deletion. A separately admitted summary or retrieval fallback may be used only when its provenance and failure semantics are frozen.

Pruning may not remove system or developer instructions, immutable requirements, permissions, safety policies, canonical verifier evidence, or sealed-evaluation controls unless a separately preregistered experiment explicitly studies that class and provides a lossless recovery path.

## Full end-to-end cost accounting

Future context-pruning comparisons must include:

- prompt and completion tokens;
- tool calls and API calls;
- hidden-state capture and head latency;
- additional re-forward or re-prefill work;
- KV-cache invalidation, prefix-cache loss, and changed scheduler behavior;
- hidden-state serialization, transfer, storage, and downcasting;
- extra retries, branches, verifier calls, and recovery reads;
- memory, throughput, tail latency, accelerator-seconds, and host overhead;
- training, annotation, feature extraction, and recertification cost;
- task failures and irreversible external actions.

Input-token reduction accompanied by more API calls, more total work, or lower task success must be reported as a tradeoff, not as unqualified efficiency gain.

## Privacy and tenant isolation

Hidden states and line-level relevance scores are input-dependent telemetry and may reveal private code, tool outputs, task intent, or tenant activity.

Raw hidden states, raw prompts, tool outputs, source code, line scores, per-request pruning traces, and private labels remain prohibited from this public repository.

In-engine execution reduces transfer exposure but does not establish privacy. Future admission must test:

- tenant isolation and request-to-score binding;
- stale-buffer and cross-request leakage;
- cache and batch contamination;
- unauthorized debug or telemetry export;
- reconstruction and attribute-inference risk;
- retention, access control, deletion, and audit logging;
- failure behavior when the head or capture path crashes.

Only preregistered aggregate summaries may be committed publicly.

## Drift and portability

A pruning head does not transfer automatically across:

- checkpoints or post-training revisions;
- dense and MoE siblings;
- quantization or dynamic precision states;
- attention backends and serving kernels;
- tokenizer or chat-template revisions;
- context windows, chunk sizes, and cache policies;
- tool schemas, harnesses, repositories, languages, and task families;
- single-turn, multi-turn, multimodal, and long-horizon workloads.

Every material change requires capture-path recertification, recalibration, and fresh sealed evaluation. Reusing a threshold or checkpoint without a prospective transfer test is prohibited.

## Agents-A1 scaling directive

SWE-Pruner Pro provides public evidence that context-relevance signals can be decoded from last-layer hidden states on two large coding-oriented MoEs. It does not establish an Agents-A1 result.

The technically credible sequence is:

1. Complete Q35Q production-path provenance and exact derivative admission on one frozen static runtime.
2. Establish no-prune, deterministic structural retention, retrieval, progressive disclosure, bounded working-set, and external-pruner baselines.
3. Admit and validate hidden-state capture first on the separately admitted Agents-A1-4B dense sibling.
4. Train a passive line-relevance head only on training data with frozen external labels and no sealed-outcome access.
5. Evaluate that head as a readout without deleting context.
6. If the readout has stable value, preregister a separate context-mutation policy with keep-all fallback, requirement retention, verifier-backed recovery, and full cost accounting.
7. Evaluate the complete policy on Agents-A1-4B before any transfer claim.
8. Admit minimal hidden-state capture on Agents-A1-35B under matched cache, batch, topology, and position tests.
9. Refit or prospectively test transfer; do not assume dense-sibling or public-MoE portability.
10. Compare hidden-state pruning against context-envelope variables, external checklists, peer representations, confidence, and bounded trajectory summaries.
11. Add route telemetry only if it provides sealed residual value beyond the admitted context-management stack.
12. Add sparse-feature, transcoder, or Jacobian-Lens streams only after exact parity and sealed incremental value over every cheaper comparator.
13. Keep deletion, summarization, retrieval substitution, abort, retry, truncation, forced routing, activation steering, and production deployment under separate intervention gates.

A validated context-management baseline may make later Agents-A1 instrumentation cheaper by bounding retained context. It may not be used to alter the sealed evaluation distribution or hide the cost and failures of the pruning policy.

## Current blocker and execution order

This addendum does not change the active blocker.

The next admissible engineering work remains one clean-subprocess, fail-closed production adapter that:

1. verifies the frozen upstream Transformers artifact;
2. binds the live import to its owning installed distribution and `RECORD`;
3. derives complete live source closure for dispatch, converters, nested operations, model/configuration classes, and loader objects;
4. rejects shadow packages, editable installs, monkeypatches, forged identities, incomplete closure, wrong ownership, and unadmitted loaders;
5. invokes and binds the actual GPTQModel/Defuser loader entry point;
6. freezes the complete immutable runtime tuple;
7. passes the full adversarial integration conjunction;
8. emits only the permitted aggregate result.

After that remain strict synthetic loading, exact quantization-tensor consumption and expert-ordering proof, forward/VJP/JVP/finite-difference parity, Phase-0 admission, weight staging, and a separately authorized GPU transition.

## Established versus unproven

Established only as external public evidence:

- A public implementation exists for representation-conditioned line pruning on two large coding-oriented MoEs.
- Last-layer hidden states contain decodable information correlated with externally labelled line relevance in the reported corpus.
- The reported end-to-end quality and efficiency effects are task- and backbone-dependent.
- The released serving path exposed real hidden-state alignment failures under mixed batching, chunked prefill, and prefix caching.
- In-engine heads can reduce hidden-state transfer cost, but context deletion remains a control intervention.
- Representation-conditioned pruning and hidden-state capture correctness are therefore mandatory future comparators and gates for compatible Agents-A1 context-management claims.

Unproven for this program:

- independent reproduction of the paper's benchmark results;
- exact hidden-state numerical parity under the released SGLang patches;
- correctness of hidden-state capture across all production cache, batch, quantization, and topology states;
- human-valid line-necessity labels beyond the reported annotation pipeline;
- safe deletion of requirements, errors, evidence, or future-useful code;
- transfer to Agents-A1-4B or Agents-A1-35B;
- correctness or eventual-failure prediction from the pruning signal;
- incremental router or Jacobian-Lens value after the context-management comparator stack;
- complete Q35Q provenance and derivative admission;
- safe context mutation, early exit, truncation, retry, escalation, expert intervention, activation steering, or production deployment.
