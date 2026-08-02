# STEER ADDENDUM — depth-partitioned replay, query conditioning, and MoE resume-parity gates

Date: 2026-08-02
Parent remote head: `1f2c2016a84a40b62b078b76f449c21687693e90`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every later cumulative protocol correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, exact-gradient, numerical-parity, resource, intervention, rollback, action, and production-gating rule. It authorizes no model-weight retrieval, model execution, GPU use, hidden-state capture, Jacobian fitting, sealed evaluation, early exit, truncation, adaptive routing, external action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and public-source engineering material may be committed. Prompts, benchmark items, outputs, token ids, per-example predictions, residual states, caches, routes, expert identities, Jacobians, verifier labels, credentials, host paths, and sealed outcomes remain prohibited.

## Triggering primary evidence

Hanzuo Liu et al., `Understanding Is Done Early: A Depth Division of Labor in Large Language Models and Its Use for Unbounded-Context Memory`, arXiv `2607.28263v1`, submitted 2026-07-30, introduces CoMem. The public implementation inspected for this correction is `liuhanzuo/COMem` at commit `e272745b472787f96457d7712086a6917e9f2b30`.

CoMem processes each stored chunk only through an intermediate depth `j`, caches the resulting per-token residual tensor, retrieves a bounded set of chunks, packs those states with the query under fresh contiguous positions, and re-executes layers `[j:L]`. The paper distinguishes a layer at which semantic content is probe-accessible from a later zero-shot readable boundary and from the query-conditioned computation performed by the upper layers.

The paper reports a Qwen3-8B flagship using a separately trained rank-32 self-distillation LoRA, plus an adapter-free arm. It also reports an adapter-free efficiency control at 128k and sparse-MoE experiments on Qwen3-30B-A3B and Hunyuan Hy3. On Hy3, a contiguous split-and-resume self-test at `j in {0,1,40,80}` produced zero reported logit difference, including a dense-to-MoE boundary, because every downstream router and expert was re-executed. This is useful evidence that exact depth partitioning can be engineered on a large sharded MoE under a particular runtime. It is not evidence that arbitrary cached states, split depths, serving paths, quantized runtimes, or Agents-A1 are equivalent.

The public repository adds two important limitations. Its sharded-MoE implementation does not support the resumed-band KV-cache decode path across devices and instead uses recomputation. It also states an architecture-specific assumption that the tested router is a pure function of token hidden state. That assumption may not be transferred to a router depending on position, recurrent state, capacity state, batch composition, sequence stage, auxiliary features, or distributed dispatch state. The latest inspected commit also corrects evaluation defaults to match the paper's actual sample counts, showing that executable evaluation defaults are part of result identity.

No CoMem result has been independently reproduced in jLens. No CoMem artifact has been admitted for Agents-A1. No paper result establishes correctness awareness, semantic-workspace identity, safe early exit, error causality, or Jacobian-Lens incremental value.

## Binding interpretation

The evidence exposes a distinction not fully bound by the existing cache-transport, recurrent-interface, stage, or early-exit rules:

> Semantic accessibility at depth, direct readout at depth, exact suffix-resume compatibility, query-conditioned utility after suffix recomputation, retrieval quality, final objective correctness, and safe control value are different scientific objects.

The following may not be renamed into one another:

1. information decodable from a residual state;
2. information causally retained by a truncated prefix;
3. information usable by the native suffix under the original execution context;
4. information usable after chunk-local encoding, retrieval, repacking, and position reassignment;
5. zero-shot output readability from a split state;
6. fidelity after adapter or self-distillation training;
7. final task success;
8. correctness or error awareness;
9. completion, stopping, routing, or action readiness; and
10. a natural semantic workspace.

A probe peak does not establish that comprehension is complete. A good suffix-resumed answer does not establish that the cached state is a final semantic representation. A low logit difference on one self-test does not establish runtime equivalence on the deployment population. A trained adapter that makes deeper states usable creates a new checkpoint condition rather than revealing an unchanged native boundary.

## Depth-partition artifact identity

Every future partial-forward, split-depth replay, residual-cache, suffix-resume, HCache-style, CoMem-style, or related Jacobian-acceleration experiment must freeze at minimum:

- exact model repository, immutable checkpoint revision, model class, tokenizer, processor, template, reasoning mode, and adapter set;
- complete runtime tuple, source closure, kernels, compiler, precision, quantization, launch configuration, and distributed topology;
- split boundary `j`, including whether it is before or after normalization, attention, residual addition, routed MoE, shared expert, or other sub-block operation;
- every value crossing the split boundary, not only the principal residual tensor;
- chunking, overlap, sink tokens, padding, masks, ordering, position ids, RoPE construction, absolute offsets, and repacking rules;
- retrieval corpus, index, selector, query representation, top-k, multi-hop logic, tie behavior, deduplication, and document ordering;
- suffix layer range, downstream cache construction, recurrent or state-space state, random state, capacity state, route state, and scheduler state;
- device placement and every inter-device transfer, cast, synchronization, and communication operation;
- generation, parser, verifier, retry, repair, stopping, and final-selection rules; and
- complete write, storage, retrieval, transfer, read, decode, verifier, and tail-latency cost.

Any changed split, position policy, selector, adapter, cache path, route condition, batch composition, topology, or runtime is a distinct executable condition unless prospectively proved equivalent.

## Complete boundary-state gate

Caching only the residual is sufficient only if the admitted suffix is mathematically and operationally determined by that residual plus explicitly reconstructed public inputs. Before a split is admitted, enumerate every live value produced below the boundary and consumed above it, including where applicable:

- residual and normalized residual streams;
- attention masks, position ids, RoPE cosines and sines, and sequence lengths;
- KV, recurrent, state-space, convolutional, hybrid-attention, and external-memory state;
- router inputs, capacity counters, expert-placement metadata, dispatch buffers, and load-balancing state;
- adapter, prefix, prompt, tool, memory, and branch lineage;
- RNG, dropout, stochastic routing, sampler, compiler, and scheduler state; and
- dtype, scale, packing, accumulation, layout, stride, device, and sharding metadata.

Missing auxiliary state may not be silently regenerated from a different context. If the complete suffix input state cannot be enumerated and reconstructed exactly, the split is not an exact replay boundary.

## Exact split-and-resume admission gate

Before split-depth replay is used for scientific measurement or compute acceleration, the exact production path must pass positive and adversarial parity tests on preregistered held-out inputs.

At minimum, test:

- `j=0` against the admitted full forward on the same packed input;
- the proposed operating split;
- adjacent splits on both sides;
- every dense-to-MoE, attention-type, recurrent, state-space, cache, device, and pipeline boundary crossed by the proposal; and
- `j=L` as the no-suffix limit where meaningful.

Compare separately:

1. the boundary state and every auxiliary state crossing it;
2. every downstream layer state;
3. pre-router values, router transforms, top-k identities, weights, capacity decisions, and physical dispatch;
4. shared-expert and routed-expert outputs and reduction order;
5. post-MoE, post-attention, and post-layer states;
6. persistent decode state and cache lineage;
7. logits, token distributions, generated tokens, parser state, and verifier outcome;
8. activation VJPs and JVPs through the admitted suffix; and
9. finite differences at representative boundary-state directions and route-stable regions.

Parity must be tested across repeated execution, batch composition, sequence length, padding, device placement, topology, compilation, cache reuse, retry, and failure paths. Exact token agreement alone is insufficient. Tolerances must be frozen before evaluation and justified against the intended scientific claim.

A split that deliberately repacks chunks under fresh positions is not equivalent to the original full-context forward. It may be compared with a full forward over the same repacked input, but it must be described as a changed context construction rather than exact preservation of the source-document execution.

## Query-conditioning and readout boundary

Every depth claim must separately measure:

- query-blind state content before the query is introduced;
- direct probe or lens readability at the boundary;
- causal utility under the native suffix with the original context construction;
- utility under repacked or retrieved context construction;
- the additional effect of upper-layer query conditioning; and
- independently verified objective outcome.

Required controls include same-depth random and label-shuffled probes, same-state wrong-query and no-query conditions, matched query-only and text-retrieval baselines, native full-context execution where valid, and suffix replacements of matched depth and cost.

The phrase `understanding is complete by layer j` is prohibited unless a prospectively defined, architecture-appropriate causal criterion passes across the claimed population. Permitted conclusions must name the actual result, such as `a held-out probe decodes target information at layer j` or `the admitted suffix recovers the objective under the tested repacking condition`.

## Retrieval-versus-depth-reuse gate

A CoMem-style result combines selection and depth reuse. These effects must be separated.

Required comparators include where technically compatible:

- retrieved text with a full forward;
- `j=0` selective full forward over the identical selected pack;
- the same selected pack at each tested split;
- no retrieval with all cached chunks where feasible;
- oracle, lexical, embedding, random, recency, and frequency-matched selectors;
- fixed selector breadth and matched read length;
- same-cost wider and narrower retrieval;
- selector-only and suffix-only adaptations; and
- full-context and full-compute fallbacks.

Selector logic, task-family routing, confidence thresholds, adaptive hop counts, and early-stop rules are separate controllers. They must be frozen outside sealed evaluation and evaluated against matched static and random policies. A task-specific selector that improves results cannot be attributed to residual-state reuse.

## Adapter and distillation boundary

Self-distillation, LoRA, cache-point training, router tuning, or suffix tuning creates a new executable model condition. Native frozen-checkpoint evidence and adapted-checkpoint evidence must remain separate.

An adapter may improve suffix reconstruction while changing hidden states, routes, expert use, logits, calibration, monitor features, and verifier behavior. Any adapted Agents-A1 candidate must be re-admitted for provenance, forward parity, derivative parity, route lineage, objective evaluation, privacy, and production gating. Split depths, thresholds, dictionaries, probes, and policies may not be transferred from the adapted model to the native model or from 4B to 35B without new evidence.

## Passive-monitor and Jacobian boundary

Depth-partitioned replay can reduce repeated lower-layer computation during experiments, but it is not automatically a passive observation.

Caching a boundary state from one execution and repeatedly applying the exact admitted suffix to that same state may be used as an acceleration only after complete split parity is established. Retrieval, repacking, position reassignment, state editing, adapter use, route forcing, cache substitution, or different queries create intervention-bearing conditions.

For Jacobian work, distinguish:

- the full-model Jacobian from original model input;
- the suffix Jacobian from an admitted boundary state;
- a fixed-route suffix Jacobian;
- a router-inclusive suffix Jacobian;
- a Jacobian under original positions and context;
- a Jacobian under repacked or retrieved context; and
- finite changes that cross retrieval, route, parser, stopping, or cache boundaries.

A suffix Jacobian may amortize lower-layer compute, but it cannot be reported as the full-model Jacobian. Any claimed speedup must include boundary-state generation, storage, transfer, reconstruction, suffix execution, and verification cost.

## MoE route-lineage gate

Large-MoE split replay must re-execute every downstream router and expert unless a separately admitted route/cache reuse mechanism is under test. It must never infer that a router is position-blind, state-free, or batch-independent from another architecture.

For every tested split, bind and report:

- whether the split occurs before or after routing;
- raw router inputs and transformed scores;
- top-k identities, order, weights, capacity, and overflow behavior;
- shared-expert execution;
- physical dispatch, all-to-all, combine, accumulation, and synchronization;
- route and expert-path equality under full versus resumed execution;
- route changes caused by repacking, query introduction, positions, batching, topology, or quantization; and
- downstream objective and verifier effects.

Initial Agents-A1 work should split only at admitted block boundaries. Intra-attention, intra-MoE, post-router, or mid-expert splits require a separate complete-state and exact-consumption admission.

## Agents-A1 scaling consequence

The technically credible sequence is now:

1. Complete Q35Q exact-runtime provenance, strict loading, packed-tensor consumption, expert ordering, forward, VJP, JVP, and finite-difference admission.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, template, parser, hybrid state, cache, tool harness, environment, verifier, and runtime.
3. On an unadapted 4B baseline, test block-boundary split replay against the admitted full forward before using cached states for probes or Jacobians.
4. Identify candidate splits using training and development populations only; freeze the split and all parity tolerances before sealed evaluation.
5. Use exact boundary-state reuse, where admitted, to amortize repeated suffix probes, VJPs, JVPs, finite differences, and monitor comparisons. Preserve full-forward spot checks and fail closed on any drift.
6. Keep original-context replay separate from retrieved or repacked memory experiments.
7. Evaluate semantic accessibility, direct readability, suffix utility, error prediction, continuation utility, and objective correctness as separate targets.
8. Admit Agents-A1-35B separately, including quantization, hybrid state, routed and shared experts, reduction semantics, cache, kernels, topology, scheduler, and route telemetry.
9. Re-run the complete split-parity ladder at every candidate 35B boundary. Do not transfer 4B split depths, probe weights, Jacobian ranks, thresholds, selectors, or route assumptions.
10. Treat LoRA, distillation, cache-point training, and adaptive selectors as separately trained or controlled artifacts.
11. Require hidden-state, route, expert-path, semantic-workspace, and Jacobian signals to add sealed objective value beyond logits, confidence, trajectories, parsers, retrieval scores, repeated sampling, continuation tests, and independent verifiers.
12. Preserve native full-context or full-compute execution and independent verification as fallback.

## Current engineering blocker remains unchanged

The active milestone remains complete production-path Q35Q provenance and runtime admission:

1. resolve repository visibility versus destination-policy disagreement;
2. bind installed runtime files to immutable distribution ownership records;
3. derive complete executable-source closure from actual live runtime objects;
4. detect shadow imports, in-memory monkeypatching, runtime substitution, and process-global leakage in clean subprocesses;
5. bind the exact GPTQModel/Defuser loader and conversion entry;
6. freeze one immutable Transformers, GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, backend, launch, checkpoint-format, kernel, and reduction tuple;
7. run strict synthetic Qwen3.5-MoE quantized loading;
8. prove one-time packed-tensor consumption and exact expert/fusion ordering;
9. prove deterministic forward and persistent-state parity; and
10. prove activation-VJP, activation-JVP, and finite-difference parity.

No model-weight staging or GPU execution is authorized before the full conjunction passes.

## Established by this correction

- Semantic accessibility, direct readability, suffix-resume utility, retrieval quality, and objective correctness are separate claims.
- Query-blind cached states require query-conditioned suffix computation before they can support a query-specific output claim.
- Depth partitioning is exact only when the complete boundary state and executable suffix are reproduced under the admitted context construction.
- A repacked fresh-position read is a changed execution context even when suffix execution is internally exact.
- Sparse-MoE split replay must preserve or explicitly measure complete route and expert lineage.
- Adapter-assisted deeper caching is a new model condition, not proof of the native checkpoint's depth boundary.
- Exact suffix replay may become a useful compute-amortization path for Agents-A1 probes and Jacobians only after full parity admission.
- No privacy, sealed-data, verifier, provenance, derivative, intervention, resource, action, or production gate is weakened.
- Q35Q remains blocked.

## Unproven

- Independent reproduction of CoMem's reported results.
- Exact split-and-resume parity on Q35Q, Agents-A1-4B, or Agents-A1-35B.
- Sufficiency of a residual tensor alone at any Agents-A1 split boundary.
- Stationarity of Agents-A1 routing under repacking, fresh positions, different queries, batching, quantization, or distributed execution.
- A universal semantic-content depth or readable boundary.
- Objective error awareness, continuation utility, safe stopping, or action readiness from intermediate states.
- Incremental Jacobian-Lens value beyond direct hidden-state, retrieval, trajectory, confidence, and verifier controls.
- Safe early exit, truncation, adaptive routing, expert dropping, cache substitution, steering, external action, or production deployment.
