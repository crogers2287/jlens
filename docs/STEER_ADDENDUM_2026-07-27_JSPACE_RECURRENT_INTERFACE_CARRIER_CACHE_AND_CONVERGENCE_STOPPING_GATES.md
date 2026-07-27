# STEER ADDENDUM — J-space recurrent-interface, carrier-cache, and convergence-stopping gates

Date: 2026-07-27
Parent remote head: `3c9bc74df2cfaf1dae12c5f517f7afb689cfc077`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every later cumulative protocol correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, derivative, corpus, resource, retry, intervention, and production-gating rule. It does not constitute Q35Q admission, authorize weight staging or GPU use, reopen M38E, permit Agents-A1 capture, or establish an internal jLens scientific result.

## Primary external evidence

The external work-in-progress preprint `J-CoT: Chain-of-Thought in J-Space`, arXiv `2607.21981v1`, was submitted on 2026-07-24.

The reported method converts a fitted Jacobian-lens dictionary from a passive readout instrument into an active recurrent computation interface:

- the main experiment uses a reasoning-adapted `Qwen3-8B-Base` checkpoint;
- eight non-decoded carrier positions are appended after the prompt;
- layer 12 is used for recurrent read-in and layer 28 for recurrent extraction;
- read- and write-layer dictionaries are fit from randomized low-rank averaged-Jacobian estimates on 1,000 pretraining-like sequences of 128 tokens;
- carrier activations are decomposed through a nonnegative elastic-net operator into vocabulary-indexed coefficient matrices called `J-thoughts`;
- the coefficient state is reconstructed through the read-layer dictionary and repeatedly propagated through layers 13–28;
- recurrence terminates when normalized J-thought change is below `0.02` for two consecutive cycles, subject to a maximum-cycle budget;
- after stopping, the final carrier states are propagated through the remaining layers and retained as fixed prefix key/value states during answer generation;
- `J-CoT-Train` optimizes carrier embeddings and a shared read gate while freezing the Transformer and fitted dictionaries;
- `J-CoT-Zero` does not optimize those interface parameters, but still operates on a separately reasoning-adapted checkpoint and changes the execution graph, recurrence, carrier positions, cache state, and answer-conditioning path.

The paper reports three-seed results on eight mathematical, scientific, and coding benchmarks under a shared Qwen3-8B backbone. It reports an unweighted average of `47.9` for J-CoT-Zero, `50.2` for J-CoT-Train, and `47.5` for the strongest listed latent-reasoning baseline. It also reports scaling experiments on dense Qwen2.5 and Llama-3.1 backbones from 7B through 405B with recurrent-cycle budgets of 4, 8, and 16.

These are author-supplied results from a work-in-progress preprint. The arXiv record inspected for this correction does not link an immutable attributable implementation or complete released artifacts sufficient for independent reproduction. The large-model scaling claims, fitted dictionaries, reasoning-adapted checkpoints, carrier states, generations, and complete runtime receipts have not been independently reproduced in jLens.

## Binding interpretation

The new evidence changes a scientific and control boundary not fully captured by passive readout, activation-steering, temporal-state, or early-exit rules alone:

> A Jacobian-lens artifact used to read activations and the same artifact used as an active recurrent state interface are different scientific and production objects. Once fitted coordinates are extracted, reconstructed, repeatedly injected, used to create cache entries, or used to stop computation, the system is an intervention-bearing recurrent architecture, not a passive monitor.

The following objects are distinct and may not be renamed into one another:

1. passive Jacobian readout;
2. fitted J-space dictionary or frame;
3. coefficient extractor;
4. residual reconstruction map;
5. recurrent carrier state;
6. recurrent execution graph;
7. state-change or convergence statistic;
8. adaptive cycle-allocation policy;
9. prefix-KV answer-conditioning mechanism;
10. interface-trained artifact;
11. objective correctness or task outcome;
12. deployment decision policy.

Predictive readout value does not authorize recurrence. Reconstruction fidelity does not establish semantic identity. Recurrent utility does not establish passive correctness monitoring. State convergence does not establish correctness, completion, safety, or irreversibility readiness.

## Recurrent-interface artifact identity

Every future J-space, sparse-coordinate, tuned-lens, SAE, transcoder, hidden-state, router, or other learned-coordinate recurrent interface must freeze at minimum:

- exact backbone repository, immutable revision, model class, tokenizer, processor, chat template, and reasoning mode;
- all pretraining, instruction-tuning, reasoning-adaptation, or domain-adaptation identities used before interface evaluation;
- exact fitted dictionary artifact, fit corpus, fit budget, estimator, source and target layers, stage, position policy, precision, runtime, and digest;
- coefficient-extraction objective, nonnegativity rule, sparsity penalty, quadratic penalty, solver, initialization, convergence tolerance, maximum iterations, active-set behavior, and numerical fallback;
- reconstruction normalization, column scaling, epsilon, clipping, dtype, accumulation precision, and residual insertion boundary;
- carrier count, carrier initialization, token positions, positional encoding, attention permissions, masking, language-model-target exclusion, and inter-carrier connectivity;
- recurrent read layer, write layer, repeated block range, number of cycles, maximum cycles, stopping statistic, threshold, patience, and undefined-state behavior;
- prompt-state caching, carrier-state caching, prefix-KV construction, cache layout, cache dtype, paging, reuse, invalidation, and answer-conditioning path;
- interface parameters, optimizer, training corpus, labels, unroll depth, seeds, checkpoint-selection rule, and artifact digest;
- decoding, verifier, stopping, retry, repair, and final-answer-selection rules;
- complete monitor, recurrence, extraction, reconstruction, cache, generation, and verifier cost.

Any change to these identities defines a separate recurrent artifact or runtime condition unless equivalence is prospectively established.

## `Zero`, `training-free`, and base-model terminology gate

Terms such as `zero`, `training-free`, `parameter-free`, `base-model`, and `no adaptation` must be scoped to the exact component that is not trained.

A method may not be represented as training-free for deployment when it depends on any of the following:

- a reasoning-adapted or instruction-adapted checkpoint;
- a fitted Jacobian, tuned-lens, SAE, transcoder, projection, or dictionary artifact;
- development-set selection of read/write layers, carrier count, thresholds, cycle limits, or stopping patience;
- learned carrier embeddings, gates, adapters, selectors, or final-answer heads;
- task-specific prompt templates, answer processing, or calibration;
- a changed recurrent graph, carrier-token insertion, or cache-conditioning mechanism.

Permitted wording must name the unchanged component, for example `no interface-specific gradient updates on a fixed reasoning-adapted checkpoint`. It may not imply that the deployed system is the untouched pretrained model or ordinary inference path.

## Transport and reconstruction admission gate

A coefficient coordinate retaining the same vocabulary index across layers does not establish that its meaning, causal role, or downstream effect is invariant across those layers.

Before a fitted coordinate system is admitted as a recurrent transport interface, report on held-out populations:

- extraction-reconstruction error at every participating layer;
- direct versus sequential multi-hop transport error;
- coefficient support stability, sign or nonnegativity sensitivity, and active-set churn;
- residual-space and final-logit divergence after transport;
- downstream hidden-state, attention, route, expert-path, cache, and continuation divergence;
- sensitivity to corpus, fit seed, fit budget, sequence length, position, stage, tokenizer, precision, quantization, runtime, and serving state;
- conditioning, dictionary coherence, rank, null-space behavior, and solver non-uniqueness;
- failures where low reconstruction error coexists with materially different continuations or outcomes.

A mathematical bound conditional on small recovery defect is not evidence that the condition holds on the deployment population. Reconstruction and re-extraction agreement is an interface-fidelity result, not semantic equivalence or objective utility.

## Carrier and cache-lineage gate

Carrier positions and their resulting key/value states are active model inputs and cache artifacts. They are not bookkeeping-only telemetry.

Future carrier-based studies must separately report:

- ordinary prompt-only baseline;
- neutral carriers with no recurrent read-in;
- carriers with matched position and compute but random, zero, mean-embedding, and learned initializations;
- carrier count and placement sweeps;
- inter-carrier attention enabled and disabled;
- carriers excluded and included in relevant attention paths;
- answer generation with and without retained carrier prefix-KV;
- exact effects of positional shifts caused by appending carriers;
- cache memory, bandwidth, paging, scheduler, batching, and prefix-reuse costs;
- cache invalidation and replay behavior under retries, tool calls, context extension, and serving migration;
- future-token and route divergence caused by carrier KV state.

A gain from the full system cannot be attributed to J-space transport unless carrier-token compute, extra depth, added prefix memory, position changes, and cache conditioning are held fixed or independently ablated.

Carrier content, fitted coefficients, hidden states, cache entries, prompts, outputs, routes, task records, and per-example predictions remain private or sealed scientific data under all existing rules. Aggregate-only public-repository restrictions remain binding.

## Convergence and adaptive-stopping gate

Internal-state stabilization is not objective completion.

Any recurrence, early-exit, truncation, or cycle-allocation policy based on coefficient change, hidden-state change, route stabilization, entropy, confidence, or Jacobian features must freeze and separately evaluate:

- the exact state-distance metric and normalization;
- threshold, patience, minimum cycles, maximum cycles, and tie behavior;
- sensitivity to coefficient scaling, support churn, sparsity, solver tolerance, and numerical precision;
- probability of premature stabilization on incorrect trajectories;
- probability of continued oscillation on correct trajectories;
- correctness conditional on stopping cycle;
- successful-episode survival across the complete stopping cascade;
- calibration and selective risk on the full preregistered population;
- tail failures and irreversible-action cases;
- fallback behavior when the statistic is undefined, unstable, or outside calibration support;
- complete expected and worst-case compute, memory, and latency.

Mandatory equal-system comparators include where technically compatible:

- fixed 1, 2, 4, 8, and maximum-cycle policies;
- random stopping with matched cycle distribution;
- prompt-length, task-family, and difficulty heuristics;
- same-boundary logits, entropy, margin, confidence, and self-judgement;
- raw hidden-state and direct-lens change metrics;
- dense-latent-state recurrence with matched carriers and compute;
- pause or filler tokens with matched positions and compute;
- explicit linguistic CoT with matched sequential compute;
- external verifier-based continuation and stopping;
- no-recurrence ordinary decoding;
- full-compute fallback.

A policy that stops when its internal representation stops changing may be classified as a convergence controller. It may be called an early-exit, completion, correctness, or safety controller only after the corresponding prospective objective and survival gates pass.

## Recurrent-interface comparator gate

A claimed J-space-specific benefit requires incremental value over matched recurrent interfaces, not only over ordinary decoding.

Include where technically feasible:

- direct dense-state recurrence;
- learned low-rank latent recurrence;
- PCA and random orthonormal subspaces of matched rank and energy;
- unembedding, logit-lens, tuned-lens, and raw-residual coordinate systems;
- SAE or transcoder coordinates from multiple admitted families;
- corpus-matched and corpus-shifted fitted dictionaries;
- shuffled vocabulary indexing with preserved dictionary geometry;
- support- and coefficient-scrambled states preserving marginal sparsity and norm;
- learned transport adapters with matched parameter and training budgets;
- carrier-only and prefix-KV-only controls;
- matched fixed-cycle and adaptive-cycle policies.

Vocabulary-indexed labels are not evidence that the transmitted state is linguistically grounded in the operational sense. Required controls include token frequency, model-output marginal, embedding norm, tokenizer structure, Unicode and orthographic artifacts, answer identity, lexical overlap, and generated-output leakage.

## Causal and semantic claim boundary

Improved final accuracy after recurrent extraction and reinjection establishes utility of the complete altered inference system under the tested conditions. It does not by itself establish:

- that the fitted coordinates are the model's natural reasoning medium;
- that vocabulary labels faithfully describe the transmitted computation;
- that the passive J-lens discovered a pre-existing semantic workspace;
- that the recurrent state is a correctness, uncertainty, planning, or error state;
- that the selected read/write layers are intrinsic stages;
- that state stabilization means the answer is complete or correct;
- that the intervention is safe under tool use, long horizons, or irreversible actions;
- that the method transfers across checkpoints, corpora, precisions, runtimes, or architectures.

Removing recurrence, replacing the coordinate system, or changing the cache path is an ablation of the engineered interface, not necessarily an ablation of a naturally occurring model mechanism.

## MoE and Agents-A1 route-lineage gate

Dense-model recurrence results do not transfer to Agents-A1-35B or comparable MoEs.

A future MoE recurrent-interface study must freeze and capture, where admitted:

- router logits, probabilities, top-k identities, ancestry, occupancy, and load balance for every cycle;
- expert-path changes caused by carrier insertion, reconstructed state, cycle count, and cache conditioning;
- nominal and functional route diversity;
- route convergence separately from coefficient convergence;
- expert-output and downstream-state divergence under matched recurrent states;
- per-cycle communication, expert dispatch, all-to-all, memory, and scheduler costs;
- expert-capacity overflow, dropped-token, and load-imbalance behavior;
- dense-sibling or 4B comparators under matched interfaces;
- quantized and serving-specific recurrence effects.

A coefficient-convergence stop that materially changes routes on the next cycle is not route-converged. A route-stable state that remains objectively wrong is not correctness-converged.

## Agents-A1 scaling consequence

The technically credible sequence is now:

1. Complete Q35Q production-path provenance, strict loading, deterministic forward parity, activation-VJP parity, activation-JVP parity, and finite-difference parity.
2. Separately admit Agents-A1-4B and establish deterministic checks, external verifiers, logits, confidence, visible trajectory, memory, program-state, simple hidden-state, fixed-compute, and ordinary CoT baselines.
3. Fit any J-space artifact with frozen corpus, fit budget, stage, position, estimator, runtime, precision, and same-corpus refit nulls.
4. Validate extraction, reconstruction, direct and multi-hop transport, support stability, and continuation divergence before recurrent use.
5. Evaluate carriers, repeated blocks, prefix-KV conditioning, and fixed-cycle recurrence as separate components.
6. Compare J-space recurrence against dense-state, learned-latent, PCA, random-subspace, direct-lens, tuned-lens, pause-token, filler-token, explicit-CoT, and verifier-based alternatives at equal complete cost.
7. Evaluate coefficient convergence only as a candidate cycle-allocation signal until prospective objective correctness, survival, tail-risk, and fallback gates pass.
8. Keep all fitting, thresholding, and policy selection outside sealed final evaluation; preserve a no-intervention full-compute fallback.
9. Separately admit Agents-A1-35B hidden-state, cache, router, expert-path, quantized, topology, and serving telemetry.
10. Repeat transport, carrier, cache, route-lineage, convergence, and cost studies on the 35B artifact rather than transferring 4B layers, coordinates, supports, thresholds, or cycle policies.
11. Require J-space, router, sparse-feature, or Jacobian signals to add sealed objective-outcome and policy value beyond the complete cheaper comparator stack.
12. Keep recurrence, early exit, retry, repair, truncation, forced routing, activation steering, reward shaping, and production enforcement separately gated.

## Current engineering blocker remains unchanged

The active milestone remains complete production-path Q35Q provenance and runtime admission:

1. verify frozen upstream-wheel and installed-distribution bytes in the same controlled subprocess;
2. reject shadow packages, editable installs, pre-imported modules, and in-memory monkeypatching;
3. execute the complete adversarial provenance conjunction in the target runtime;
4. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` as one immutable tuple;
5. bind the actual GPTQModel/Defuser loader and its complete live-object source closure;
6. run the strict synthetic Qwen3.5-MoE loading fixture;
7. prove one-time packed-tensor consumption and exact expert/fusion ordering;
8. prove deterministic forward, activation-VJP, activation-JVP, and finite-difference parity; and
9. complete Phase-0 admission before weight staging or GPU authorization.

## Established by this correction

- Passive Jacobian readout and active Jacobian-coordinate recurrence are separate objects.
- Carrier insertion, repeated block execution, coefficient extraction and reconstruction, prefix-KV conditioning, and adaptive stopping define an altered inference architecture.
- `Zero` and `training-free` terminology must be scoped to the exact untrained component.
- Cross-layer coefficient recovery is not semantic, causal, continuation, or objective equivalence.
- State convergence is not correctness or completion.
- Carrier and prefix-KV effects require separate lineage, cost, and ablation controls.
- J-space-specific recurrent utility requires matched non-J recurrent-interface comparators.
- MoE route lineage must be measured across recurrent cycles before Agents-A1 claims.
- No privacy, sealed-data, verifier, provenance, derivative, intervention, resource, or production gate is weakened.
- Q35Q remains blocked.

## Unproven

- Independent reproduction of arXiv `2607.21981v1`.
- Immutable implementation and artifact provenance for the reported J-CoT system.
- Accuracy of the reported 7B-to-405B scaling results.
- Semantic faithfulness of J-thought vocabulary coordinates.
- Cross-corpus, cross-checkpoint, cross-runtime, or cross-precision transport stability.
- Objective correctness, safety, planning, uncertainty, or recoverability prediction from J-thought states.
- Safe adaptive stopping from coefficient convergence.
- Transfer to Qwen3.5/Qwen3.6 MoEs or either Agents-A1 checkpoint.
- Incremental J-space, router, sparse-feature, or Jacobian value beyond every cheaper comparator.
- Complete Q35Q runtime admission, strict tensor consumption, expert ordering, forward parity, or derivative parity.
- Safe recurrence, early exit, retry, repair, truncation, forced routing, activation steering, reward shaping, or production deployment.
