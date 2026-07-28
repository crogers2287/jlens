# STEER ADDENDUM — temporal reinstatement, cache-lineage, and positional-memory gates

Date: 2026-07-28

Parent remote head: `2027176d19bc22ae3e7cc26dbede6722d8b346ff`

Status: binding future-protocol correction; no current execution authorization

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains exact-target-runtime Q35Q provenance and immutable GPTQ loader/runtime admission.
- GitHub currently reports this repository as public. Aggregate-only commit restrictions remain binding.
- No weight staging, model execution, GPU execution, hidden-state capture, attention capture, cache capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized by this document.
- Every privacy, sealed-data, verifier, provenance, derivative, parity, resource, cleanup, comparator, nuisance-control, intervention, production-gating, and stop rule remains binding.

## New primary evidence and narrow interpretation

Pink et al., **Temporal Context Reinstatement Drives Episodic-Like Order Memory in Long-Context Language Models**, arXiv `2607.22575v1`, reports a long-context temporal-order task and a mechanistic analysis of Llama-3.1-8B-Instruct and Llama-3.1-70B-Instruct.

The reported design:

1. places a complete long document in one encoding span;
2. later presents two verbatim 50-word segments and asks which appeared first;
3. randomizes answer-label assignment and evaluates both label orders;
4. fits head-specific temporal directions on a long random-word sequence;
5. tests those directions on held-out natural, shuffled, and transcript corpora;
6. distinguishes temporal structure present in the encoding value cache from temporal structure observed during retrieval;
7. localizes a dominant retrieval head in each primary model;
8. removes or amplifies the fitted temporal component during the retrieval spans.

The authors report:

- distance-dependent temporal-order performance in humans and both Llama models;
- preserved model performance under sentence-block shuffling, reducing reliance on narrative reconstruction as the sole explanation;
- one dominant temporal-reinstatement head in each primary Llama model;
- 64 percent and 39 percent average attention mass from those heads onto the queried encoding spans in the 8B and 70B conditions respectively;
- a 10–15 percentage-point average performance reduction after removing the temporal component;
- up to a 9 percentage-point improvement for Llama-3.1-8B-Instruct after amplifying the selected direction by the reported factor;
- preliminary qualitatively similar heads in Mistral-7B-v0.2 and Qwen2.5-7B.

The paper points to `mathispink/temporal-context-reinstatement` and `mathispink/icmemory-kit`. At inspection time the paper repository is pinned at `6a68ad3a5652d6a7556f9951e6b323bf8815e25d` and contains a release notice rather than the reproduction implementation. ICMemory-Kit is pinned at `83b954dd51473d1ba7608fb58a0ed3a8b31a1ce6`; its README describes an August 2026 code release and a preview API, not an immutable completed implementation.

The binding interpretation is narrow:

- The result supports a causal temporal-order mechanism in the tested long-context tasks and model conditions.
- A temporal code is not a semantic event representation, episodic narrative, truth signal, correctness monitor, semantic workspace, or general memory state by default.
- A head that retrieves relative position for a forced-choice ordering task is not thereby a universal long-horizon memory head.
- Attention concentration is not the causal result; the directional interventions are the stronger evidence and remain scoped to the intervention, task, models, and runtime.
- The published direction was fitted using known sequence position. That supervised alignment does not establish that an unsupervised monitor can discover or use the same coordinate prospectively.
- The primary models are dense grouped-query-attention Llama checkpoints. Nothing establishes transfer to quantized Qwen3.5/Qwen3.6 MoEs, Agents-A1, hybrid attention, sliding-window attention, recurrent memory, tool agents, or production serving.
- Exact independent reproduction remains unavailable until the promised code and data release is present, immutable, and admitted.

## Binding ontology: temporal position is not semantic memory

Future compatible studies must separately identify at least:

1. source content identity;
2. source sequence position;
3. encoding token position;
4. encoding hidden state;
5. encoding key and value cache entries;
6. fitted temporal direction and estimator;
7. retrieval query tokens and positions;
8. retrieval attention scores and weights;
9. retrieved value contribution before head concatenation;
10. head output after projection;
11. residual-stream contribution;
12. answer logits and output;
13. independent temporal-order outcome;
14. semantic-content outcome;
15. objective task outcome;
16. intervention and production policy.

A position-correlated coordinate is not automatically a memory of event meaning. A retrieved value contribution is not automatically a recollection. A correct order judgment is not automatically correct state tracking, causal reasoning, source attribution, or current-world knowledge.

Required terminology is scoped unless broader evidence exists:

- `temporal-position direction`;
- `encoding-cache temporal coordinate`;
- `retrieval-phase temporal reinstatement`;
- `task-conditioned temporal-order mechanism`.

Terms such as `episodic memory circuit`, `semantic timeline`, `workspace clock`, `memory truth signal`, or `general temporal reasoning module` require separate prospective evidence beyond the reported ordering task.

## Encoding, retrieval, and inherited-information gate

A retrieval-phase head may appear temporally organized because it:

1. directly retrieves temporally organized values written during encoding;
2. inherits temporal information already written into the residual stream by an earlier component;
3. reflects query position, answer-label structure, segment distance, or prompt format;
4. correlates with content, chapter, topic, lexical drift, or document structure;
5. receives position-dependent behavior from the runtime, cache, mask, or attention implementation.

Future studies must distinguish direct cache retrieval from inherited downstream information.

Minimum evidence for a primary reinstatement claim includes:

- the same frozen direction generalizing to encoding-cache and retrieval representations;
- an explicit sign-orientation rule frozen before held-out evaluation;
- held-out documents and independently generated position structures;
- attention or value-path evidence showing access to the relevant encoding span;
- causal intervention at the identified component and phase;
- matched interventions on inherited residual information and neighboring components;
- proof that the effect is not created by label order, query position, or span resolution.

A temporal direction discovered after inspecting the target task is development evidence. Confirmatory claims require a fresh sealed population.

## Position, distance, content, and tokenizer controls

Compatible temporal-memory studies must prospectively vary or control:

- absolute encoding position;
- relative distance between queried segments;
- segment length;
- query order and answer-label assignment;
- retrieval-prompt position;
- document length and context utilization;
- local and global lexical overlap;
- topic, entity, event, and chapter identity;
- intact, block-shuffled, sentence-shuffled, and content-free sequences;
- repeated-token, random-word, random-token, and natural-text fits;
- tokenizer revision and exact token boundaries;
- whitespace, punctuation, formatting, and special-token placement;
- truncation and padding;
- RoPE or alternative positional encoding configuration;
- attention mask and cache-position semantics;
- prompt template and system-message structure.

Report performance and mechanism strength by distance and position. A pooled average may not hide near-chance short-distance behavior, long-distance degradation, edge effects, or position-specific failure.

A direction fitted on random words, random tokens, or one corpus remains a fit-population-conditioned artifact. Existing corpus-conditionality and fit-budget gates apply in full.

## Cache-lineage and runtime identity gate

Temporal reinstatement claims depend on the exact cache and attention runtime.

The frozen identity must include:

- checkpoint and tokenizer revisions;
- model configuration;
- attention architecture, including MHA, MQA, GQA, sliding-window, hybrid, recurrent, or linear attention;
- query-head to key/value-head mapping;
- pre-concat versus post-concat head boundary;
- key and value projection definitions;
- rotary or other positional transformations;
- cache position identifiers;
- prefix-cache construction and reuse policy;
- chunked-prefill policy;
- offload and reload behavior;
- cache dtype, quantization, compression, eviction, and paging;
- kernel, backend, compiler, precision, batching, topology, and scheduler;
- deterministic and nondeterministic operations;
- extraction and intervention hook locations.

Reusing a prefix cache across many probes creates a distinct executable condition. It must be compared against fresh-prefill execution and proven equivalent for the admitted observable and intervention boundaries.

A query head index is not a complete identity under GQA or MQA. The associated shared key/value head, projection path, expert or dense block lineage, and runtime dispatch must be recorded.

Cache equality cannot be inferred from equal generated text. Required parity includes admitted cache tensors or bounded hashes, logits, selected internal summaries, and deterministic replay under the frozen runtime.

## Causal intervention gate

Temporal-direction removal or amplification is an intervention, not a passive readout.

Future compatible intervention studies must freeze:

- target layer, head, tensor boundary, token span, and phase;
- fitted direction and sign convention;
- projection or amplification formula;
- gain values and selection rule;
- whether intervention occurs before or after attention weighting, head concatenation, output projection, residual addition, normalization, quantization, or routing;
- numerical precision and norm preservation;
- random generator and seed policy;
- full compute, memory, latency, and bandwidth cost.

Required controls include:

1. no intervention;
2. matched random directions;
3. orthogonal directions;
4. neighboring principal directions;
5. matched random heads;
6. heads matched on attention mass;
7. heads matched on output norm and layer;
8. removal of the direction outside retrieval spans;
9. removal during encoding only;
10. amplification and attenuation sweeps;
11. query-span and non-query-span placebos;
12. full-head ablation versus directional ablation;
13. residual-stream interventions with matched norm;
14. label-order and prompt-format controls.

Report paired repaired failures, new regressions, unchanged successes, unchanged failures, malformed outputs, calibration changes, and complete cost.

An intervention that improves temporal ordering may damage semantic retrieval, factual accuracy, tool behavior, safety, or other task families. Those outcomes must be measured separately.

## Mechanism transfer and replication gate

No layer, head, direction, gain, threshold, or context-length conclusion may transfer across:

- model family;
- checkpoint revision;
- instruction tuning;
- context architecture;
- tokenizer;
- corpus;
- task format;
- context length;
- precision or quantization;
- runtime or kernel;
- serving topology.

A qualitative outlier head in another model is preliminary transfer evidence, not a common universal circuit.

Independent reproduction requires:

- immutable code and data revisions;
- exact prompts and segment-generation rules;
- exact fitted-direction artifacts or reproducible fitting receipts;
- model and runtime identities;
- full head-search population;
- multiple-comparison policy;
- intervention implementation and audits;
- complete exclusions and failed runs;
- deterministic or bounded-nondeterministic replay;
- aggregate-only public receipts.

Until the announced implementations are released and admitted, the paper is scientific evidence but not executable infrastructure for this program.

## Required long-context comparator matrix

Before semantic-workspace, router, sparse-feature, transcoder, or Jacobian features receive credit on long-context temporal tasks, include when technically compatible:

1. answer logits, margin, entropy, and calibrated confidence;
2. absolute and relative token-position features;
3. segment distance and length;
4. lexical, topic, entity, and document-location features;
5. direct retrieval and deterministic position lookup where available;
6. attention-score and attention-mass summaries;
7. cache key/value norms and bounded low-dimensional summaries;
8. residual-state temporal probes;
9. spectral hidden-state summaries;
10. direct and tuned lenses;
11. temporal-order directions at encoding and retrieval;
12. full-history, recent-window, episodic, provenance, and external-ledger memory baselines;
13. route telemetry as a separate block for MoE systems;
14. frozen combinations of external, cache, hidden-state, route, sparse, and Jacobian features.

A monitor that predicts errors using only distance, position, truncation, cache eviction, or retrieval failure must be classified as position, runtime, or memory-process telemetry unless it adds sealed objective value beyond those controls.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q exact-target-runtime provenance, strict loading, deterministic forward, VJP, JVP, and finite-difference admission.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, processor, context architecture, cache implementation, harness, and runtime.
3. Build admissible long-context tasks with independently generated temporal ground truth, randomized labels, content-shuffled controls, and multiple context lengths.
4. Establish position, distance, logit, confidence, direct-retrieval, attention, cache-summary, residual-state, spectral, trajectory, memory, and external-ledger baselines.
5. Fit temporal directions under frozen corpus, budget, position, span, estimator, and sign identities with same-population refit nulls.
6. Separate encoding-cache temporal information, retrieval-phase reinstatement, inherited residual information, and objective outcome.
7. Run observation-only studies before any ablation or amplification.
8. Separately admit Agents-A1-35B checkpoint, tokenizer, quantization, router, experts, attention architecture, cache, kernels, topology, batching, and serving runtime.
9. Capture route and cache lineage at encoding and retrieval boundaries only after those paths are admitted.
10. Determine whether temporal retrieval occurs through attention, router-selected experts, shared experts, dense blocks, or combinations rather than importing dense-Llama head coordinates.
11. Require router telemetry to add sealed value after complete positional, cache, attention, residual-state, spectral, memory, and verifier controls.
12. Add sparse-feature or transcoder comparators when separately admitted.
13. Add Jacobian-Lens features only after exact derivative parity and sealed incremental value over the complete temporal-reinstatement-aware and route-aware comparator stack.
14. Keep head ablation, direction removal, amplification, cache rewriting, early exit, retry, repair, forced routing, activation steering, reward shaping, and production deployment separately gated.

No result from Llama-3.1, Mistral, Qwen2.5, Agents-A1-4B, or an unquantized reference runtime authorizes mechanism transfer or intervention on Agents-A1-35B.

## Privacy, sealed-data, and repository boundary

Long-context memory experiments may contain private documents, communications, event histories, source identities, timestamps, user behavior, proprietary text, tool records, and latent personal attributes.

No raw or summarized private document, prompt, queried span, cache tensor, attention map, hidden state, fitted direction, route, Jacobian, answer, verifier label, intervention result, or per-example prediction may be committed to this public repository.

Non-synthetic work requires separately authorized data inventory, purpose limitation, consent or authority, source-specific retention and deletion rules, secret and personal-data filtering, tenant isolation, access control, cache cleanup, reconstruction and membership testing, and aggregate-only scientific receipts.

Prefix-cache reuse must not extend the retention or access lifetime of source material beyond the admitted purpose. Cache eviction and deletion must be independently verified.

## Current blocker and execution order

This addendum does not change the active blocker.

The next admissible engineering work remains:

1. Execute the composed Transformers provenance adapter in the exact target runtime and retain aggregate evidence only.
2. Freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` as one immutable tuple.
3. Bind the actual GPTQModel/Defuser loader and complete executable source closure.
4. Run strict synthetic Qwen3.5-MoE loading.
5. Prove one-time packed-tensor consumption.
6. Prove exact expert and fusion ordering.
7. Prove deterministic forward, activation-VJP, activation-JVP, and finite-difference parity.
8. Complete Phase 0 before weight staging or GPU authorization.

## Established by this addendum

- Temporal position, semantic memory, correctness, workspace state, and objective outcome are separate identities.
- Direct cache retrieval, inherited residual information, and position or prompt confounds must be separated.
- Cache, attention, GQA/MQA mapping, context, fit population, and runtime are binding mechanism identities.
- Temporal-direction interventions require matched component, direction, span, phase, and cost controls.
- Long-context positional and cache comparators are mandatory before router or Jacobian-specific value.
- Dense-model temporal-head findings do not transfer to Agents-A1-35B.
- Existing privacy, sealed-data, verifier, provenance, derivative, GPU, intervention, and production gates remain intact.

## Still unproven

- Independent reproduction of the reported temporal-reinstatement mechanism.
- The announced implementation and data release.
- Generality beyond the tested temporal-order tasks and model conditions.
- A semantic episodic-memory representation rather than a temporal-position mechanism.
- Prospective objective-error, safety, recoverability, or workspace prediction.
- Transfer to Qwen3.5/Qwen3.6 MoEs or either Agents-A1 checkpoint.
- Incremental router or Jacobian-Lens value beyond temporal, cache, attention, hidden-state, memory, and verifier comparators.
- Complete Q35Q target-runtime, loader, tensor-consumption, expert-ordering, forward, or derivative admission.
- Safe cache intervention, head ablation, direction amplification, early exit, retry, repair, forced routing, activation steering, reward shaping, or production deployment.
