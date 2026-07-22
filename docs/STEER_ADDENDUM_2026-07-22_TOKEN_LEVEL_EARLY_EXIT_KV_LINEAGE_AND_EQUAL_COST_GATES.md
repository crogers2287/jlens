# STEER ADDENDUM — token-level early-exit KV-lineage, cross-request, and equal-cost gates

Date: 2026-07-22

Status: **binding design correction; not launch authorization.**

This addendum strengthens the existing early-exit boundary in
`docs/STEER_ADDENDUM_2026-07-15_M39_METACOGNITION_TEMPORAL_AND_EARLY_EXIT_BOUNDARY.md`.
It does not alter the active Q35Q milestone, establish a scientific result,
authorize model or GPU execution, permit weight staging, weaken any privacy or
sealed-data rule, replace independent verification, or authorize early exit,
truncation, retry, routing intervention, activation steering, or production use.

The active milestone remains **production-path upstream/runtime provenance
composition**. The no-milestone-drift rule remains binding.

## Primary evidence motivating this correction

`River-LLM: Large Language Model Seamless Exit Based on KV Share`
(ACL 2026 long paper; arXiv:2604.18396) supplies a concrete token-level
intermediate-exit design that exposes protocol requirements not stated
explicitly enough in the earlier boundary.

The reported system:

- evaluates dense models no larger than 8B parameters, not Agents-A1 or another
  comparable large MoE;
- copies backbone decoder layers into an exit branch and applies W4A16
  post-training quantization to its attention and feed-forward weights while
  retaining KV state at FP16;
- uses hidden-state transition similarity to estimate cumulative approximation
  error and decide whether to enter or remain in the exit branch;
- performs sequence-level exit during prefill and token-level exit during decode;
- uses a batch aggregate, including a minimum across active batch members, in
  the reported exit rule;
- reports practical speedups with nonzero quality changes rather than exact
  output or state parity;
- reports only moderate correlation between its state-transition statistic and
  exit-versus-backbone value similarity;
- does not establish correctness prediction, safe stopping, MoE route parity,
  long-horizon agent utility, or production admission.

No immutable attributable public implementation was located for this correction.
The paper is therefore an external systems result and engineering lead, not an
admitted executable comparator.

## Binding method classification

A River-style system is not merely a passive readout from an unmodified model.
It contains distinct experimental objects:

1. the admitted full backbone;
2. the copied or transformed exit-layer artifact;
3. the exit-layer precision and kernel path;
4. the KV-sharing or KV-propagation mechanism;
5. the state-transition or other exit score;
6. the threshold and candidate-layer policy;
7. the batch aggregation rule;
8. the fallback and recovery rule;
9. the serving scheduler and cache implementation;
10. the final execution controller.

Terms such as `training-free`, `parameter-free`, or `no auxiliary head` do not
mean artifact-free, calibration-free, intervention-free, or production-safe.
A copied, quantized, reordered, fused, cached, or separately dispatched exit
path is a new execution artifact requiring its own immutable provenance and
admission.

The state-transition statistic in River-LLM is evidence about branch
approximation and cache-lineage risk under the reported system. It is not, by
itself, evidence of:

- objective answer correctness;
- model self-knowledge;
- semantic-workspace validity;
- safe truncation;
- recoverability;
- absence of future-token divergence;
- absence of harmful long-horizon effects.

A score that predicts exit-versus-backbone similarity must be described as an
approximation or execution-state signal unless it separately demonstrates
incremental objective-outcome value under the existing correctness-monitor
protocol.

## KV-lineage admission gate

Token-level early exit changes the computation that generates cache state used
by later tokens. A next-token match, logit similarity, hidden-state cosine, or
single-step KL value is insufficient to establish sequence-level equivalence.

Before any token-level exit result may support an efficiency or preservation
claim, the exact KV lineage must be frozen and verified, including:

- the source layer and destination layer for every K and V tensor;
- token position, sequence identifier, batch identifier, cache index, and
  position-encoding state;
- dtype, quantization, scale, layout, stride, packing, and device placement;
- cache-update order and synchronization boundary;
- prefill, chunked-prefill, decode, speculative, retry, and resume behavior;
- prefix/radix-cache hits, misses, eviction, paging, offload, and restoration;
- candidate entry and exit layers;
- monotonic or non-monotonic movement between full and exit branches;
- attention implementation, kernels, compiler, serving backend, CUDA, driver,
  hardware, topology, and scheduler;
- fail-closed behavior for missing, duplicated, stale, misindexed, partially
  updated, or incompatible KV state.

The admitted implementation must prove, on synthetic adversarial fixtures and
prospectively frozen neutral workloads:

1. exact token-position and cache-index coverage;
2. absence of missing and duplicated KV entries;
3. deterministic replay under the same execution schedule;
4. bounded per-layer K and V error against the admitted full path;
5. bounded downstream hidden-state and logit divergence;
6. generated-token and finish-reason agreement at frozen decision boundaries;
7. future-token divergence curves after each earlier exit decision;
8. correct behavior through cache hits, chunk boundaries, retries, cancellation,
   eviction, paging, and batch reordering;
9. exact fallback to the full path when lineage cannot be certified.

For an MoE, the same gate additionally requires prospective verification of:

- router-input identity at every affected layer;
- selected expert identities and ordering;
- router weights, margins, and occupancy;
- expert input and output parity;
- parent-route and route-history state;
- changes in later routing caused by an earlier token's exit decision;
- expert placement, dispatch, gather, tensor/expert parallelism, and topology.

Average cosine similarity, aggregate next-token agreement, mean KL, average exit
depth, benchmark score, or throughput cannot substitute for these lineage and
tail checks.

## Prefill-versus-decode separation

Sequence-level prefill exit and token-level decode exit are separate systems.
They must have separate:

- provenance and cache-lineage admission;
- thresholds and calibration;
- quality, latency, memory, and tail-risk reporting;
- prompt-length and generated-length strata;
- context-position and cache-pressure controls;
- fallback and failure behavior.

A prefill result cannot authorize decode exit. A decode result cannot authorize
prefill truncation. A system combining both must report the isolated and joint
contributions and interactions.

## Cross-request and batch-coupling gate

Any exit rule that depends on a batch minimum, maximum, mean, percentile,
occupancy statistic, shared cache state, or scheduler state creates a
cross-request coupling channel.

Future compatible studies must test, at minimum:

- single-request execution;
- homogeneous and heterogeneous batches;
- shuffled batch membership and ordering;
- short and long neighboring requests;
- high- and low-confidence neighboring requests;
- high- and low-KV-pressure neighbors;
- different modalities and task families;
- request arrival, departure, cancellation, retry, and preemption;
- shared versus tenant-isolated controllers;
- adversarial co-tenant attempts to alter another request's exit depth.

Reports must quantify how another request changes the target request's exit
layer, cache lineage, output, latency, memory use, and objective outcome. No
request may expose another tenant's prompt, tokens, routes, hidden states,
outputs, verifier results, cache trace, or per-token exit trace.

A batch-dependent policy cannot be described as request-local. If tenant
isolation, calibration stability, or bounded cross-request influence is not
established, the production default is the admitted full-execution path.

## Mandatory equal-cost comparator set

A future early-exit study must compare, where technically compatible and under
matched tasks, decoding, verifier, runtime, hardware, batching, and total
resource limits:

1. the admitted full model at the deployment precision;
2. the complete model at the best feasible equal-memory static quantization;
3. fixed-depth sequence-level exit;
4. fixed-depth token-level exit;
5. learned or thresholded exit without KV sharing;
6. exit with exact recomputation of skipped state where feasible;
7. monotonic-exit and re-entry-capable policies;
8. River-style KV-shared exit;
9. self-speculative or speculative decoding where compatible;
10. no-exit and fail-closed full-path controls;
11. random and prevalence-matched exit controls.

The comparison must report full-population and prespecified hard-stratum results
for:

- objective task outcomes and verifier outcomes;
- malformed, degenerate, unsafe, and truncated outputs;
- exact token and finish-reason agreement;
- time to first token, time per output token, end-to-end latency, throughput,
  p50/p95/p99 tails, and scheduling delay;
- peak and resident memory, KV memory, cache traffic, host/device transfer, and
  page movement;
- accelerator time, energy where measurable, synchronization, and controller
  overhead;
- retries, fallback frequency, recomputation, and abandoned work;
- calibration drift across sequence length, domains, batches, runtimes, and
  precision states.

A speedup claim must use actual end-to-end serving measurements. FLOP reduction,
average exit depth, or isolated-layer timing is descriptive only.

## Exit-score and calibration boundary

Future compatible studies must distinguish prediction of:

1. branch approximation error;
2. KV-lineage error;
3. next-token agreement;
4. future-sequence agreement;
5. objective outcome correctness;
6. recoverability before irreversible action;
7. operational utility under the complete controller.

Thresholds, candidate layers, state-transition formulas, pooling, normalization,
sequence exclusions, calibration method, and fallback rules must be selected
using training populations only and frozen before certification and sealed
evaluation.

Required cheap score comparators include, where compatible:

- fixed layers and random exits;
- output-logit margin, entropy, and calibrated confidence;
- adjacent-layer hidden-state and logit convergence;
- state-transition similarity;
- direct full-versus-exit approximation error on training-only fixtures;
- sequence length, token position, task, batch, cache pressure, and serving-state
  nuisance variables.

A signal that loses value after conditioning on cache state, token position,
batch composition, precision, or serving state is execution telemetry, not
privileged correctness information.

When the score is unavailable, uncertified, out of distribution, numerically
unstable, or inconsistent with cache-lineage checks, the default is full
execution. Threshold uncertainty may not be resolved using sealed outcomes.

## Agents-A1 scaling order

This correction does not make early exit the next Agents-A1 milestone. The
binding order remains:

1. complete Q35Q production-path provenance composition;
2. establish strict quantized tensor consumption and expert ordering;
3. establish exact forward, activation-VJP, activation-JVP, and finite-difference
   parity on the admitted static runtime;
4. establish the complete cheaper correctness-monitor comparator stack;
5. admit Agents-A1-4B separately and use it for an observation-only intrinsic
   exit-headroom and KV-lineage feasibility study;
6. require objective-output, future-token, cache-lineage, equal-cost, and tail
   preservation before any 4B control study;
7. admit Agents-A1-35B separately, including hybrid-attention, MoE routing,
   expert-dispatch, multimodal, cache, topology, precision, and serving-state
   behavior;
8. repeat the full KV-lineage and cross-request admission rather than transferring
   thresholds or artifacts from the dense sibling;
9. require router, hidden-state, sparse-feature, transcoder, directional-JVP, or
   Jacobian signals to add sealed value over state-transition, cache-error,
   confidence, and all cheaper comparators;
10. preregister every intervention and production decision on a fresh population.

No public dense-model early-exit result establishes Agents-A1 headroom, route
stability, output preservation, safety, or deployability.

## Privacy, sealed-data, and production boundary

Raw prompts, tasks, answers, token IDs, logits, hidden states, routes, expert
identities, K/V tensors, cache traces, exit scores, per-token exit layers,
precision traces, batch membership, tenant identifiers, predictions, split
labels, verifier labels, and per-example outcomes remain private and
uncommitted.

Only aggregate, privacy-reviewed results may enter the public repository.
Exit-control training, calibration, certification, and sealed evaluation must
use independent populations under the existing leakage and verifier rules.

An admitted monitor does not authorize an exit controller. An admitted exit
controller does not authorize production deployment. Production use requires a
separate prospective gate covering privacy, security, tenant isolation, drift,
rollback, failover, alerting, auditability, tail harm, and full-cost utility.

## Established and unproven boundary

Established from the public River-LLM source is limited to the authors' reported
results on the listed dense models and benchmarks, plus the methodological fact
that a KV-shared token-level exit path creates persistent state consumed by
future tokens and can use batch-coupled thresholding.

Still unproven include:

- independent reproduction and immutable implementation provenance;
- exact full-path equivalence;
- complete future-token and KV-lineage parity;
- safe cross-request and cross-tenant behavior;
- robust calibration under runtime and workload drift;
- extension to hybrid attention, multimodal models, large MoEs, or Agents-A1;
- objective correctness prediction from state-transition similarity;
- incremental router or Jacobian-Lens value after cache and approximation
  controls;
- safe early exit, truncation, retry, route intervention, activation steering,
  or production deployment.

The research program remains incomplete. Q35Q remains
`q35q_artifact_admission_blocked`, and no later scientific or control phase is
authorized by this correction.
