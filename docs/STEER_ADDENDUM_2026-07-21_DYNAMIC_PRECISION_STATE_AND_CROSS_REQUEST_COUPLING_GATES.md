# STEER ADDENDUM — Dynamic precision state and cross-request coupling gates

Date: 2026-07-21

Parent remote head: `6ca7c9b605501bfc7bfbcf5282ec51081ec50539`

Status: binding future-protocol correction; no current execution authorization

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- GitHub currently reports this repository as public. Aggregate-only commit restrictions remain binding.
- No weight staging, tensor-payload retrieval, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized by this document.
- Every privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, cleanup, commit-safety, comparator, nuisance-control, production-gating, and stop rule remains binding.

## New primary evidence and narrow interpretation

Yang et al., **PagedWeight: Efficient MoE LLM Serving with Dynamic Quality-Aware Weight Quantization**, arXiv `2607.16184v1`, submitted 2026-07-17, studies a serving runtime in which MoE expert precision changes while requests are executing.

The public paper reports the following bounded facts:

1. Each routed-expert linear block is represented by Any-Precision bit planes and a page-table record containing a committed bitwidth, a desired bitwidth, supported bitwidths, page residence state, and memory size.
2. A runtime planner lowers or restores expert-block precision in response to KV-cache pressure.
3. The planner combines offline Hessian-weighted sensitivity, online routing mass, and prompt-conditioned residual features.
4. Batched serving merges request-level routing masses, prompt residuals, and confidence signals into a batch-level planning table.
5. Page movement is asynchronous and committed only at runtime-defined safe boundaries; a fused mixed-precision MoE kernel consumes the currently committed precision state.
6. The reported experiments use Qwen1.5-MoE-A2.7B, Mixtral-8x7B-v0.1, and Gemma-4-26B-A4B with vLLM 0.20.1 on RTX 6000 Ada and GH200 systems.
7. The authors report FP16-equivalent aggregate accuracy with up to 72.0% GPU-memory savings and 1.94x throughput improvement in their tested settings.

These are external systems results, not admitted results of this repository. No attributable public implementation was located during this review. The paper does not establish per-request forward parity, activation-derivative parity, correctness monitoring, privacy safety, safe early exit, or transfer to Qwen3.5/Qwen3.6 MoE or Agents-A1.

## Binding correction: execution identity may vary inside a request

A serving system with runtime-adaptive expert precision does not execute one fixed numerical model throughout a request. Its effective function depends on at least:

- the committed bitwidth of every expert linear block;
- pending desired bitwidths and page movements;
- the exact boundary at which a precision transition becomes visible;
- KV-cache pressure and allocator state;
- online routing statistics;
- prompt-conditioned planner features;
- batch composition and request weights;
- expert-page residence and transfer state;
- mixed-precision kernel and backend identity.

A checkpoint SHA plus one nominal quantization label is therefore insufficient provenance for telemetry, derivative, correctness, or production claims under adaptive precision.

The exact executed precision state at the claimed decision boundary is part of model/runtime identity.

## Precision-epoch provenance

Any future adaptive-precision experiment must define a **precision epoch** as a maximal interval during which the committed expert-block bitwidth table and relevant kernel/runtime identities are unchanged.

For each admitted run, freeze and bind:

- base checkpoint, processor, tokenizer, model configuration, and artifact digests;
- Any-Precision representation and LUT schema;
- supported bitwidth set for each linear-block class;
- planner code, immutable revision, calibration artifacts, and hyperparameters;
- offline sensitivity corpus, ordering, exclusions, and digests;
- prompt-residual feature definition and fitted-head digests;
- routing-mass definition, update cadence, and aggregation rule;
- KV-pressure thresholds, byte targets, bitwidth floors, depth caps, and reload policy;
- batch-level merge rule and request weighting;
- committed and desired page-table schema;
- safe transition boundary and atomicity semantics;
- CPU/GPU page-transfer implementation;
- fused kernel, compiler, CUDA, driver, serving backend, and device topology;
- complete transition and failure semantics.

Raw per-request precision tables, routes, prompts, hidden states, outputs, page traces, or tenant identifiers remain prohibited from this public repository. Only preregistered aggregate summaries may be committed.

## Forward and derivative parity gates

Average benchmark quality or FP16-equivalent aggregate accuracy cannot establish numerical parity for monitoring or Jacobian work.

Before adaptive precision may be used in a scientific capture path, the admitted policy must establish, for every allowed precision state or a prospectively frozen representative state set:

1. exact or tolerance-preregistered forward agreement against the stated reference;
2. activation VJP agreement;
3. activation JVP agreement;
4. finite-difference agreement;
5. deterministic replay under the same precision-epoch schedule;
6. correct expert ordering, tensor consumption, and mixed-precision kernel identity;
7. transition-boundary behavior before, during, and after page changes;
8. fail-closed behavior for incomplete, delayed, or inconsistent page states.

If the adaptive state space is too large to admit prospectively, the scientific path must use a smaller frozen set of static precision configurations. Unadmitted dynamic states default to no scientific claim and no intervention.

A Jacobian, hidden-state probe, router monitor, sparse feature, or calibration object fitted across mixed precision epochs may not be treated as if it came from one stationary model unless invariance is prospectively established.

## Monitor calibration and nuisance controls

Every future correctness or failure monitor must either:

- prove invariance to the admitted precision state and transition schedule; or
- condition and calibrate explicitly on a frozen precision-state representation.

Required comparisons include:

- one fixed admitted high-precision model;
- one fixed admitted low-precision model;
- each admitted static mixed-precision configuration;
- the adaptive policy with precision-state features hidden from the monitor;
- the adaptive policy with only aggregate precision-state features available;
- a workload- and KV-pressure-matched control;
- a random precision schedule matched for memory and transition count, where safe;
- a no-transition control.

A monitor improvement that disappears after conditioning on precision state, KV pressure, batch composition, or transition phase must be classified as serving-state telemetry rather than model-internal correctness information.

## Cross-request and cross-tenant coupling

Because PagedWeight merges request-level route and prompt signals into a batch-level planner state, one request can influence the precision used for another request.

Future adaptive-precision evaluation must separately test:

- single-request execution;
- fixed homogeneous batches;
- fixed heterogeneous batches;
- shuffled batch membership;
- adversarial high-KV-pressure neighbors;
- high-routing-mass and low-routing-mass neighbor requests;
- tenant-isolated planners and page tables;
- shared planners with tenant-blind aggregate statistics;
- batch arrival, departure, cancellation, and retry transitions.

Required outcomes include target-request logits, tokens, correctness, calibration, route paths, hidden-state and Jacobian agreement where admitted, latency, memory, and precision schedule.

No monitor or planner feature may expose another tenant's raw prompt, token, route, hidden state, output, verifier result, or precision trace. Aggregate features require a reconstruction, membership-inference, attribute-inference, covert-channel, minimization, retention, and access-control review.

A serving optimization that permits cross-request quality influence without bounded and audited behavior is not admissible for sealed evaluation or production monitoring.

## Planner leakage and label boundary

The adaptive precision planner is a separate learned or calibrated control system.

Its offline sensitivity data, prompt-residual targets, route observations, quality-damage labels, bucket definitions, confidence scores, thresholds, and policy search must use training/calibration populations only.

The planner may not receive:

- sealed correctness outcomes;
- verifier labels unavailable at the transition boundary;
- future tokens or future routes;
- post-intervention evidence;
- private production telemetry outside an independently authorized data boundary.

Prompt-conditioned quality-damage prediction is not correctness prediction. Protecting frequently routed experts is not evidence that those experts contain privileged reasoning state.

## Equal-cost and equal-quality reporting

Adaptive-precision reports must include:

- planner and feature-extraction cost;
- calibration and sensitivity-analysis cost;
- page-table and metadata memory;
- CPU-resident weight pages;
- PCIe or interconnect traffic;
- page-transfer overlap and exposed stalls;
- kernel and dequantization overhead;
- KV-cache capacity gained;
- batch and scheduler effects;
- p50, p95, and p99 latency;
- throughput and accelerator-seconds;
- full-population quality, calibration, and failure taxonomy;
- transition failures, planner unavailability, and recovery behavior.

A memory saving is not a correctness result. An aggregate quality match does not establish per-request or tail-risk parity. A serving improvement cannot be credited to a monitor unless monitor and planner costs are included.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q production-path provenance and exact derivative admission on one frozen static runtime.
2. Establish external-check, metadata, confidence, peer-representation, hidden-state, trajectory, and router baselines under fixed admitted precision.
3. Evaluate static precision sensitivity before any runtime-adaptive precision policy.
4. If adaptive precision is decision-relevant, admit the planner, calibration artifacts, page representation, transition semantics, fused kernel, and precision-epoch schema as a separate serving-system artifact.
5. Establish forward and derivative parity for the prospectively allowed precision states and transitions.
6. Measure monitor calibration and feature stability within and across precision epochs.
7. Test cross-request and cross-tenant coupling under fixed and adversarial batch conditions.
8. Compare fixed-precision and adaptive-precision systems at equal end-to-end cost and full-population quality.
9. Add Jacobian-Lens features only after exact parity and sealed incremental value over every cheaper admitted baseline.
10. Keep precision adaptation, expert skipping, abort, truncation, retry, escalation, forced routing, activation steering, and production deployment under separate intervention and safety gates.

Dynamic precision is an optional serving optimization, not a prerequisite for Agents-A1 monitoring. If it compromises stationarity, provenance, privacy, or derivative admission, use a frozen static precision path for scientific work.

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

- Runtime MoE serving can vary per-expert linear-block precision while a request is executing.
- The reported planner uses KV pressure, online routing mass, and prompt-conditioned residual features.
- The reported batched planner combines request-level signals, creating a real cross-request coupling channel.
- Adaptive expert precision can improve the reported quality-memory-throughput tradeoff on three tested MoE models.
- Precision state and transition timing are therefore necessary provenance and nuisance variables for future adaptive-precision monitor studies.

Unproven for this program:

- independent reproduction of PagedWeight or availability of its implementation;
- per-request output parity or tail-risk parity across precision transitions;
- activation VJP, JVP, or finite-difference parity under adaptive expert precision;
- privacy safety and bounded cross-request quality influence;
- stable correctness-monitor calibration across precision epochs;
- transfer to Qwen3.5/Qwen3.6 MoE or Agents-A1;
- incremental router or Jacobian-Lens value under adaptive precision;
- safe dynamic precision adaptation, early exit, truncation, retry, escalation, expert intervention, activation steering, or production deployment.

The research program remains unfinished. Q35Q remains blocked at production-path upstream/runtime provenance composition.