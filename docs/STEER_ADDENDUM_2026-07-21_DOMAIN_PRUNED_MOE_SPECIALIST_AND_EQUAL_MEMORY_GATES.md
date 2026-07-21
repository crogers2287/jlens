# STEER ADDENDUM — Domain-Pruned MoE Specialist and Equal-Memory Gates

Date: 2026-07-21
Status: binding; cumulative with `steer.md` and every more restrictive addendum
Scope: future MoE compression, expert pruning, static specialist checkpoints, monitor portability, and Agents-A1 scaling

## Why this addendum exists

`Half the Experts, All the Code: One-Shot Domain Pruning of Mixture-of-Experts LLMs for Coding` (arXiv:2607.16721v1) studies static expert deletion on Qwen3.6-35B-A3B and Gemma-4-26B-A4B. The associated public implementation was inspected at immutable commit `cd2a7382c24ec501adca785f647838dfe54696f8` in `anik-jha/moep`.

The reported Qwen result is directly relevant to the nearest public base-family bridge for Agents-A1-35B. Under coding-focused calibration, the authors report that retaining half of the experts per layer preserves HumanEval+ within the benchmark confidence interval, while MBPP+ already shows a statistically significant decline at that point. General-domain perplexity degrades sharply. The winning expert-selection criterion also reverses across the two model families.

The paper further reports that:

- functional code execution can disagree materially with perplexity;
- random expert retention collapses despite nominally large remaining capacity;
- pruning is not uniformly superior to quantizing the full model at the same memory budget;
- the pruning advantage appears only where the full model would require sub-3-bit quantization;
- one verifier-backed repair turn can remove much of the apparent penalty of a heavily quantized full model;
- a pruned checkpoint is produced by static checkpoint surgery and is therefore a different model artifact, not a runtime telemetry setting.

This evidence materially changes the minimum resource-scaling comparator set. A domain-pruned static specialist is now a required optional comparator when the intended Agents-A1 workload is narrow enough to define prospectively. It does not authorize pruning, weight retrieval, model execution, GPU use, scientific evaluation, or production deployment before the existing Q35Q gates pass.

## Artifact-class separation

Future work must distinguish at least:

1. **Unmodified full checkpoint** — the admitted base or agent checkpoint with its complete expert pool.
2. **Statically pruned checkpoint** — a new artifact with experts and router rows removed before execution.
3. **Runtime expert masking or substitution** — an intervention that changes the executed route without changing the stored checkpoint.
4. **Expert skipping** — omission of one or more selected experts during execution.
5. **Expert merging or distillation** — a separately trained or transformed artifact.
6. **Quantized full checkpoint** — the complete expert pool represented at reduced precision.
7. **Pruned-and-quantized checkpoint** — a composed compression artifact requiring both pruning and quantization provenance.

Results from one class may not be represented as results from another. Static pruning is not passive monitoring, not router telemetry, and not evidence that deleted experts were universally unimportant. It establishes only that one frozen specialist artifact retained measured utility on the admitted target distribution under the reported evaluation.

## Separate artifact admission

Every pruned specialist is a new model artifact. Before scientific use, freeze and bind:

- base checkpoint revision and immutable tensor identities;
- pruning implementation commit and dependency lock;
- architecture and modeling-source identities;
- exact retained expert indices for every layer;
- shared-expert, dense-path, MTP, vision, attention, and router treatment;
- expert-selection criterion and all formulas;
- calibration corpora, source revisions, packing, templates, token counts, and exclusions;
- keep ratio and per-layer allocation policy;
- surgery implementation, tensor slicing rules, router-row handling, and metadata edits;
- surviving-weight byte-identity receipts;
- zero-prune base-equivalence result;
- pruned-versus-base-masked equivalence result;
- healing, distillation, or fine-tuning artifact when present;
- export, GGUF conversion, imatrix, quantization, tokenizer, processor, runtime, and serving identities;
- artifact schema, size, and immutable digests.

The public repository may contain aggregate digests, counts, criteria, and pass/fail outcomes only. It must not contain weights, calibration samples, private trajectories, per-example routes, hidden states, outputs, verifier labels, or sealed outcomes.

## Selection and leakage gates

Expert selection is model selection. The following must use training-only or calibration-only populations and be frozen before outer validation, certification, or sealed evaluation:

- target domain definition;
- reference domain definition;
- calibration mixture and weighting;
- expert-scoring criterion;
- keep ratio;
- per-layer allocation;
- magnitude, routing, gate, activation, contrastive, or causal features;
- degeneration or guard thresholds;
- healing or distillation policy;
- quantization recipe;
- benchmark, repair, and fallback policy.

Calibration data may not include sealed tasks, private production trajectories, verifier outcomes, canonical patches, test outputs, or benchmark-derived expert labels. Repository-, task-family-, template-, dependency-pattern-, and benchmark-seed-disjoint evaluation remains mandatory where applicable.

A criterion selected because it performs best on the sealed target benchmark is inadmissible. A model-family winner may not be transferred to another family or checkpoint without prospective validation.

## Functional evaluation gate

Perplexity, router mass, activation norm, smoke prompts, and nominal active parameters are not sufficient pruning gates.

Future pruning studies must report functional, executable, and full-population outcomes appropriate to the intended workload. For coding and agentic workloads, the minimum evaluation includes:

- deterministic executable task outcomes where available;
- success, failure, malformed output, empty output, repetition, timeout, refusal, and verifier-unavailable rates;
- single-shot performance;
- verifier-backed retry or repair performance under a frozen policy;
- long-horizon tool-use and repository-level tasks when the deployment claim concerns agents;
- calibration and selective-risk behavior;
- latency, throughput, memory, accelerator-seconds, storage, conversion, profiling, and repair cost;
- confidence intervals and paired task-level comparisons;
- off-domain and safety regressions.

A pruned model that preserves one code benchmark while losing another has not established lossless coding specialization. A model that preserves coding while degrading general-domain behavior must be described as a domain trade, not a universally equivalent model.

## Equal-memory and equal-cost comparator gate

Every specialist-compression claim must compare at matched deployable memory and complete end-to-end cost against:

1. the admitted full checkpoint at the highest feasible static precision;
2. the full checkpoint quantized to the same memory budget;
3. the pruned checkpoint before quantization;
4. the pruned-and-quantized checkpoint;
5. a random-retention control at the same keep ratio;
6. at least one admitted magnitude-aware criterion;
7. at least one admitted routing- or gate-aware criterion;
8. the uncompressed dense sibling when it is a technically relevant same-family comparator;
9. single-shot and frozen verifier-backed repair execution;
10. no-prune and no-repair controls.

Report both marginal serving cost and amortized profiling, surgery, conversion, calibration, distillation, storage, and recertification cost. Pruning is not operationally necessary when a full quantized checkpoint provides equal sealed utility at equal or lower total cost.

The apparent pruning-versus-quantization crossover must be re-established prospectively for every model, task domain, hardware target, context regime, and serving backend. A crossover observed on one unified-memory device and two code benchmarks is not a universal compression law.

## Cross-domain externality gate

A domain specialist deliberately removes capacity. Future evaluations must therefore include prospectively selected non-target domains covering at least:

- general instruction following;
- factual recall;
- mathematical and scientific reasoning;
- multilingual behavior;
- safety and refusal behavior;
- tool selection and tool argument validity;
- long-context requirement retention;
- multimodal behavior when the source model is multimodal;
- recovery after verifier feedback;
- malformed, adversarial, and out-of-distribution requests.

The target-domain gain, memory reduction, and off-domain loss must be reported jointly. Hidden off-domain damage cannot be omitted because the deployment is described as specialized. Any automatic workload router that selects between the specialist and full model becomes a separate resolution policy requiring calibration, fallback, privacy, verifier, and production admission.

## Monitor portability and recalibration

Pruning changes the numerical model, route space, expert identity set, occupancy distribution, residual dynamics, calibration, and Jacobian. No hidden-state, router, sparse-feature, workspace, transcoder, or Jacobian monitor fitted on the full checkpoint may be reused on a pruned specialist without prospective transfer testing.

For each pruned artifact, future work must either:

1. prove frozen monitor invariance across the admitted full and pruned checkpoints; or
2. fit and certify a checkpoint-specific monitor using independent training, calibration, certification, and sealed-test populations.

Required comparisons include:

- full-model monitor on the full checkpoint;
- transferred full-model monitor on the pruned checkpoint without retuning;
- checkpoint-specific monitor on the pruned checkpoint;
- quantized-full monitor at the same memory budget;
- monitor performance conditioned on keep ratio, criterion, expert occupancy, route history, task domain, repair state, and serving topology.

A signal that appears only after pruning cannot be represented as privileged information present in the original checkpoint. A signal that disappears after conditioning on compression state must be classified as compression telemetry rather than model-internal correctness information.

## Numerical and derivative admission

For every pruned artifact considered for Jacobian-Lens or derivative work, require:

1. exact zero-prune forward equivalence to the admitted base path;
2. exact or preregistered-tolerance equivalence between the pruned model and the base model with deleted experts masked under the same routing semantics;
3. surviving-tensor byte identity before any healing or quantization;
4. exact expert ordering and router-row correspondence;
5. forward agreement after export and quantization;
6. activation VJP agreement;
7. activation JVP agreement;
8. finite-difference agreement;
9. deterministic replay;
10. explicit treatment of shared experts, MTP experts, vision paths, hybrid attention, router renormalization, and fused kernels.

A functional benchmark pass does not establish derivative parity. A pruned GGUF serving artifact cannot substitute for an admitted differentiable runtime without an independently verified equivalence bridge.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q production-path provenance, strict loading, tensor-consumption, expert-ordering, forward, VJP, JVP, and finite-difference admission on the full frozen checkpoint.
2. Establish external checks, metadata, confidence, peer-representation, hidden-state, trajectory, and minimal route baselines on the unmodified full model.
3. Establish matched non-route baselines on the separately admitted Agents-A1-4B dense sibling.
4. Define the target deployment domain prospectively and establish full-model functional and agentic utility on that domain and on frozen off-domain controls.
5. Compare the full model against static quantization at deployable memory budgets.
6. Only then evaluate a separately admitted static domain-pruned specialist as a compression comparator.
7. Re-establish artifact, forward, route, calibration, privacy, and derivative admission for the pruned checkpoint.
8. Compare pruned, quantized-full, and pruned-plus-quantized systems at equal total cost under single-shot and frozen repair policies.
9. Evaluate monitor transfer and checkpoint-specific recalibration on full-population and domain-shifted tasks.
10. Add sparse-feature, transcoder, or Jacobian-Lens features only after cheaper signals and compression baselines fail the sealed incremental-value gate.
11. Keep expert deletion, masking, substitution, skipping, repair, routing between specialist and full models, early exit, truncation, retry, escalation, and activation steering under separate intervention and production gates.

The pruned specialist is optional. It may provide a resource bridge for a narrowly defined deployment, but it cannot replace the full checkpoint in the primary scientific claim, cannot establish Agents-A1-wide monitor behavior, and cannot weaken any existing Q35Q gate.

## Active blocker unchanged

This addendum does not advance Q35Q and authorizes no weights, model execution, GPU work, route capture, hidden-state capture, Jacobian fitting, sealed evaluation, pruning, intervention, or production use.

The active blocker remains production-path upstream/runtime provenance composition:

1. bind the live import to its owning installed distribution and `RECORD`;
2. derive complete live source closure for dispatch, converters, nested operations, model/configuration classes, and loader objects;
3. reject shadow packages, editable installs, and monkeypatching in a clean subprocess;
4. invoke and bind the actual GPTQModel/Defuser loader entry point;
5. freeze the complete immutable runtime tuple;
6. pass the full adversarial integration conjunction;
7. emit only the permitted aggregate result.

## Established

- A public pruning pipeline and exact expert-selection artifacts exist at `anik-jha/moep` commit `cd2a7382c24ec501adca785f647838dfe54696f8`.
- The authors report substantial coding-domain redundancy in Qwen3.6-35B-A3B and Gemma-4-26B-A4B under model-specific informed selection.
- Qwen3.6 retains HumanEval+ within uncertainty at 50% expert retention while MBPP+ shows a significant decline, so losslessness is benchmark-dependent.
- General-domain behavior degrades materially in the reported specialist.
- Random retention and the proposed pure domain-contrastive criterion can collapse despite the same nominal keep ratio.
- Criterion rankings do not transfer across the two reported model families.
- Perplexity is not a reliable functional gate for aggressive expert pruning in the reported experiments.
- Pruning competes with, rather than universally dominates, full-model quantization at equal memory.
- Static expert pruning creates a new model artifact and requires fresh artifact, monitor, numerical, derivative, safety, and production admission.
- Domain-pruned-specialist, equal-memory, cross-domain-externality, repair-policy, and monitor-portability gates are now binding.

## Unproven

- Independent reproduction of the paper and public checkpoints.
- Equivalent results on Agents-A1-35B rather than its public Qwen3.6 base-family comparator.
- Preservation of long-horizon coding-agent, tool-use, multimodal, safety, or general-domain performance.
- A portable expert-selection criterion across checkpoints, domains, quantizations, or model families.
- A universal 50% safe keep ratio or universal sub-3-bit pruning crossover.
- Monitor transfer from the full checkpoint to a pruned specialist.
- Forward, VJP, JVP, finite-difference, route, and fused-kernel parity for the published pruned GGUF artifacts.
- Q35Q provenance, strict loading, tensor consumption, expert ordering, or derivative admission.
- Safe expert deletion, runtime masking, substitution, routing, early exit, retry, escalation, activation steering, or production deployment.
