# STEER ADDENDUM — KV-eviction identifiability, randomized certificates, and attribution gates

Date: 2026-07-24

Status: **binding design correction; not launch authorization.**

This addendum strengthens the token-level cache-lineage and early-exit rules in
`docs/STEER_ADDENDUM_2026-07-22_TOKEN_LEVEL_EARLY_EXIT_KV_LINEAGE_AND_EQUAL_COST_GATES.md`.
It does not change the active Q35Q milestone, establish a scientific result,
authorize model or GPU execution, permit weight staging, weaken any privacy or
sealed-data rule, replace independent verification, or authorize cache
compression, eviction, recomputation, early exit, retry, routing intervention,
activation steering, or production use.

The active milestone remains **production-path upstream/runtime provenance
composition**. The no-milestone-drift rule remains binding.

## Primary evidence motivating this correction

`Error Certificates for KV-Cache Eviction via Randomized Design`
(arXiv:2607.21475v1, submitted 2026-07-23) supplies a structural result not
stated explicitly enough in the current cache-lineage protocol.

The paper distinguishes permanent deterministic eviction from a known
randomized retention design.

For deterministic value-blind eviction, the reported theorem constructs two
cache worlds with identical retained keys, values, scores, query history, and
all online retained-state statistics, while the true full-cache attention-output
error differs arbitrarily. The paper extends the construction to finite
value-aware summaries through summary-preserving perturbations.

The reported randomized design retains a certainty set and samples the tail by
known Poisson inclusion probabilities. It applies a Hájek correction through a
retained-logit offset and estimates variance from the retained sample. The
reported experiments find:

- 96.9% to 97.7% empirical coverage at the attention-output object on the tested
  replay cells;
- certificate/error Spearman correlations of 0.943 to 0.979 at that object;
- deterministic retained entropy and keep-boundary margin near chance for their
  own eviction-induced failures;
- weak pooled prediction of ordinary task failure on real workloads, with AUC
  0.555 at 6k and 0.572 at 16k;
- output log-probability outperforming the certificate for ordinary failure
  prediction;
- certificate AUC 0.749 and 0.727 for distinguishing eviction-induced from
  inherent failures at the two tested scales;
- post-hoc evidence that certificate-gated full-cache recomputation can beat
  random and confidence gating under the reported streaming-compression setup;
- approximately twofold decode-time overhead in the unoptimized prototype.

The tested models are dense models no larger than 8B, contexts reach 16k, the
agent-memory setting is approximated by compressing history before a later
question, the deployed certificate has measured rather than proved finite-sample
coverage, and the proposed anytime-valid extension remains a proof sketch.

No immutable attributable public implementation was located during this review.
The paper is therefore an external methodological and systems result, not an
admitted executable comparator.

## Binding object separation

Every future cache-compression, cache-monitor, or memory-damage study must keep
at least the following objects distinct:

1. the admitted full-cache model and serving runtime;
2. the cache population available before compression;
3. the retention or eviction design;
4. the importance score or allocation rule;
5. the retained cache and permanently unavailable state;
6. the point estimator used by attention after compression;
7. any variance estimator or error certificate;
8. any ordinary failure predictor;
9. any cache-damage attributor;
10. any escalation, recomputation, retry, or fallback policy;
11. the external verifier and objective task outcome;
12. the production decision policy.

A strong cache-damage attributor is not automatically a strong correctness
predictor. A strong correctness predictor is not automatically a cache-damage
attributor. Neither result authorizes recomputation or deployment.

## Deterministic-eviction identifiability gate

Permanent deterministic eviction destroys information. A monitor computed only
from the retained state cannot be presumed capable of estimating the error
caused by what was deleted.

For a deterministic eviction design, a future study may make a universal or
certified induced-error claim only if it supplies an admitted information path
that closes the missing-data problem, such as:

- retaining sufficient independently verified reference information;
- reversible offload or exact recovery of evicted state;
- exact recomputation from immutable inputs;
- a prospectively frozen randomized design with known inclusion probabilities;
- another formally justified design whose identification assumptions are
  explicitly stated and empirically stress-tested.

Without such a path, retained entropy, attention margin, router state, hidden
state, output confidence, evicted score mass, workspace features, sparse
features, transcoder features, directional-JVP features, and Jacobian features
must be described as **distribution-dependent heuristics** for natural-data
association. They may not be described as certified estimators of the error
introduced by permanent deterministic eviction.

The study must include adversarial indistinguishability fixtures where retained
state and every monitor input remain identical while evicted values, full-cache
attention outputs, later hidden states, later routes, generated continuations,
or objective outcomes change.

Passing natural-distribution prediction does not defeat the structural
non-identifiability result. It establishes only performance on the frozen tested
population.

## Known-design randomized-certificate gate

A randomized certificate is admissible only when the complete sampling design is
known, frozen, recorded, and independently checkable.

The protocol must freeze:

- certainty-set definition;
- tail population definition;
- inclusion probabilities and lower probability floor;
- independent, conditional-Poisson, rejective, reservoir, or other sampling law;
- random seeds and redraw schedule;
- whether one draw is reused across decode steps;
- protected sink and recency positions;
- score computation and allocation rule;
- point-estimator correction, including every logit offset;
- variance estimator and linearization approximation;
- head, layer, token, and step subsampling;
- vector-to-scalar reduction;
- confidence level, range bound, stopping rule, and any e-process construction;
- cache budget, context regime, runtime, batching, topology, precision, kernels,
  and serving scheduler.

Unknown, reconstructed, overwritten, or selectively logged inclusion
probabilities invalidate design-based certification.

A bad importance score may widen a valid design-based certificate, but validity
under a known design does not establish useful task-level prediction. Coverage,
sharpness, ranking quality, task-level attribution, and policy utility must be
reported separately.

## Coverage and target-object boundary

A certificate for a linearized per-head attention-output error is not a bound on:

- downstream residual-stream error;
- later hidden-state or logit divergence;
- future route divergence in an MoE;
- generated-token or finish-reason agreement;
- objective task correctness;
- safety or policy compliance;
- recoverability before an irreversible action;
- production utility.

Each transfer between these objects requires separate empirical admission.

Required reporting includes:

- nominal and empirical coverage;
- undercoverage and overcoverage by layer, head, token, position, length, task,
  cache budget, model, runtime, precision, and serving state;
- certificate width and conservatism;
- point-estimator bias;
- calibration and structural-coherence diagnostics where probability language is
  used;
- full future-token, hidden-state, route, and objective-outcome divergence;
- tail behavior and failed or undefined certificate cases.

A certificate with good average coverage but unusably wide intervals may support
validity without supporting operational value.

## Attribution-versus-prediction gate

Future work must define and evaluate at least three separate events:

1. ordinary task failure;
2. eviction-induced failure, where an admitted full-cache reference succeeds and
   the compressed execution fails;
3. inherent failure, where the admitted full-cache reference also fails.

A signal that predicts ordinary failure may be unable to identify whether cache
compression caused it. A signal that identifies cache damage may be weak at
predicting ordinary failure because inherent task difficulty dominates.

The terms `trust score`, `failure probability`, `cache error`, `damage score`,
`attribution score`, and `recompute priority` may not be used interchangeably.

For prediction, output log-probability, calibrated confidence, entropy,
self-judgement, and external-verifier signals remain mandatory cheap
comparators. For attribution, exact paired full-cache outcomes, evicted score
mass, retained entropy, keep-boundary margin, independent-draw disagreement,
and randomized-design certificates are mandatory where compatible.

## Query-aware versus streaming-memory regimes

Compression performed after the future query is known is a different scientific
object from history compression performed before the later request, tool result,
or user question exists.

Future studies must separately report:

- query-aware prefill compression;
- streaming or multi-turn compression before the future query;
- agent-memory compaction before future tool and environment observations;
- decode-time eviction after generation begins;
- mixed systems combining these regimes.

A near-zero damage rate in query-aware LongBench-style compression cannot
establish safety for persistent agents whose history is compacted before future
requirements are known.

The frozen information set must state exactly what the retention policy knows at
compression time. Future queries, verifier outcomes, later tool results, sealed
labels, and future trajectory information may not leak into retention or
certificate calibration.

## Mandatory comparator and ablation set

Future compatible studies must compare, under matched tasks, budgets, runtime,
hardware, batching, and total cost:

1. full cache with no permanent eviction;
2. deterministic score-based top-k eviction;
3. value-aware deterministic eviction where compatible;
4. uniform random retention;
5. known-probability randomized importance retention with and without point-
   estimator correction;
6. randomized retention with and without the variance/certificate layer;
7. exact recomputation or reversible offload where feasible;
8. two independent randomized draws and disagreement signals;
9. retained entropy, keep-boundary margin, evicted score mass, output
   log-probability, confidence, and self-judgement;
10. random, confidence-gated, certificate-gated, and oracle recomputation;
11. fail-closed full-cache fallback.

The comparison must report objective outcomes, eviction-induced versus inherent
failure, exact token agreement, future-sequence divergence, latency, p50/p95/p99
tails, memory, bandwidth, transfers, energy where measurable, randomization and
certificate overhead, recomputation rate, abandoned work, and end-to-end cost.

Post-hoc recomputation policies must be labeled exploratory and confirmed on a
fresh population before supporting a policy claim.

## MoE route and Jacobian boundary

For an MoE, cache damage can alter later router inputs and selected experts.
Future route or Jacobian studies under cache compression must report:

- full-cache versus compressed router-input divergence;
- selected-expert identities, order, weights, and margins;
- route ancestry and later-route divergence;
- expert-input and expert-output divergence;
- nominal and functional route-diversity changes;
- serving-topology and dispatch effects;
- whether internal telemetry predicts ordinary failure, cache-induced failure,
  or merely cache pressure and sampling variance.

A router, hidden-state, sparse-feature, transcoder, directional-JVP, or Jacobian
signal that adds no value beyond the known cache design, certificate, output
confidence, and external verifier is not privileged correctness awareness.

A signal trained using the paired full-cache result is retrospective unless it is
retrained and evaluated prospectively without access to that future reference.

## Agents-A1 scaling order

This correction does not make cache compression the next Agents-A1 milestone.
The binding order remains:

1. complete Q35Q production-path provenance composition;
2. prove strict quantized-tensor consumption, expert ordering, deterministic
   forward parity, VJP parity, JVP parity, and finite-difference parity;
3. admit Agents-A1-4B separately under a frozen runtime;
4. establish deterministic external checks, confidence, trajectory, program-
   state, memory, compaction, and full-cache baselines;
5. run observation-only query-aware and streaming cache-damage studies on
   Agents-A1-4B, including deterministic indistinguishability fixtures;
6. evaluate known-design randomized certificates only after the full sampling
   and estimator identities are admitted;
7. require prospective attribution, full-cost, tail, and recomputation-policy
   evidence before any cache-control study;
8. separately admit Agents-A1-35B hidden-state, router, expert-path, cache,
   multimodal, quantized, topology, and serving capture;
9. repeat the full identifiability, coverage, route-lineage, and regime analysis
   rather than transferring 4B thresholds, layers, or policies;
10. require route telemetry to add sealed objective-outcome value beyond the full
    cache-design, certificate, confidence, external-verifier, dense-sibling, and
    trajectory stack;
11. add sparse-feature or transcoder comparators;
12. add Jacobian Lens only after exact derivative parity and incremental value
    over every cheaper stage-matched and cache-aware comparator;
13. keep eviction, compression, recomputation, retry, early exit, forced routing,
    activation steering, quarantine, and production use separately gated.

## Privacy, sealed-data, and production boundary

Raw prompts, tasks, outputs, token IDs, logits, hidden states, routes, expert
identities, K/V tensors, cache contents, inclusion indicators, inclusion
probabilities tied to examples, certificate traces, random seeds tied to examples,
per-step errors, predictions, split labels, verifier labels, and per-example
outcomes remain private and uncommitted.

Only aggregate, privacy-reviewed results may enter the public repository.

Design fitting, score fitting, certificate construction, calibration,
certification, recomputation-policy selection, and sealed evaluation must use
independent populations under the existing leakage and verifier rules.

An admitted certificate does not authorize cache compression. Admitted cache
compression does not authorize recomputation control. Admitted recomputation
control does not authorize production deployment.

Production use requires a separate prospective gate covering workload drift,
query-aware versus streaming regime shifts, privacy, tenant isolation,
randomness quality, logging integrity, certificate availability, fallback,
rollback, alerting, auditability, tail harm, and full-cost utility.

## Established and unproven boundary

Established from the public source is limited to the reported theorem under its
stated assumptions and the authors' reported results on the listed dense models,
contexts, tasks, retention designs, and prototype.

The paper supports the methodological distinctions that:

- permanent deterministic eviction can make induced error structurally
  unidentifiable from retained online state;
- known randomized retention can make a compression-channel error estimable at a
  specifically defined attention-level object;
- cache-damage attribution and ordinary failure prediction are different tasks;
- query-aware and streaming-memory compression are materially different regimes;
- a design-based certificate can support recomputation scheduling without being
  the best general correctness predictor.

Still unproven include:

- independent reproduction and immutable implementation provenance;
- finite-sample theorem-level coverage for the deployed scalar certificate;
- validity of the sketched anytime extension;
- transfer beyond the tested dense models, 16k contexts, tasks, and runtime;
- genuine multi-turn agent-memory performance;
- large-MoE and Agents-A1 route-lineage behavior;
- certificate validity after quantization, batching, distributed serving, cache
  paging, reuse, merging, or cross-request sharing;
- prospective objective-error prediction from cache-side signals;
- incremental router or Jacobian-Lens value after cache-aware comparators;
- safe cache eviction, compression, recomputation, retry, early exit, route
  intervention, activation steering, or production deployment.

The research program remains incomplete. Q35Q remains
`q35q_artifact_admission_blocked`, and no later scientific or control phase is
authorized by this correction.
