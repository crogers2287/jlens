# STEER ADDENDUM — Adaptive expert cardinality, router-uncertainty, and compute-matching gates

Date: 2026-07-29
Parent remote head: `7bfd8dafc3ffc003a56f28b50eac306980349904`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, cleanup, intervention, production-gating, and stop rule. It
authorizes no model retrieval, model execution, GPU use, telemetry capture,
Jacobian fitting, sealed evaluation, training, adaptive routing, abstention,
early exit, retry, repair, or production action.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains exact-target-runtime Q35Q loader and
derivative admission. This addendum changes future telemetry, comparator,
intervention, and compute-accounting requirements. It does not displace that
milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and
public-source engineering material may be committed. Prompts, outputs, token
identities, per-example routes, router vectors, expert identities, expert
outputs, hidden states, recurrent states, caches, predictions, verifier labels,
sealed outcomes, model weights, credentials, host paths, and private runtime
facts remain prohibited.

## Triggering primary evidence

Saliencro et al., `Spend Experts Where You Are Unsure: Confidence-Adaptive
Routing for Mixture-of-Experts LoRA`, arXiv `2607.26052v1`, submitted
2026-07-28, studies test-time variable-cardinality routing for trained MoE-LoRA
adapters.

The proposed CARE rule:

- computes a softmax router distribution over LoRA experts;
- sorts experts by router weight;
- admits the smallest nucleus whose cumulative mass reaches threshold `tau`;
- computes disagreement among that admitted set;
- may extend the set by up to `gamma` experts when disagreement exceeds `delta`;
- clips the final count to `[k_min, k_max]`; and
- calibrates `tau` on a held-out population so average active expert count meets
  target budget `B`.

The paper reports experiments on MoE-LoRA adaptations of LLaMA-3.1-8B and
Qwen2.5-7B with 16 adapter experts, `k_min=1`, `k_max=8`, and an average budget
matched to fixed `k=4`. It reports improved benchmark accuracy at the same
average active-adapter count, matching fixed `k=4` accuracy with 12% fewer
active experts, and improved shifted-distribution detection from a blended
router-entropy and admitted-expert-disagreement score.

The theoretical confidence result assumes correctness likelihood is monotone in
top-1 router mass. The budget result assumes token utility is non-decreasing and
concave in expert count and that marginal gain is monotone in covered router
mass. The disagreement interpretation treats admitted experts as an ensemble.
Those are substantive assumptions, not established properties of arbitrary
routers, native MoEs, or Agents-A1.

The paper states that code is released, but no attributable immutable public
repository revision was identified during this review. No implementation claim
is admitted by this addendum.

## Bounded interpretation

The evidence supports this narrow correction:

> Router concentration, admitted-expert disagreement, adaptive expert-count
> selection, executed expert cardinality, runtime cost, abstention policy, and
> independently verified correctness are separate scientific and production
> objects.

A peaked router distribution can mean confident expert selection without
implying confidence in the answer. A flat distribution can reflect ambiguity,
load-balancing behavior, weak specialization, distribution shift, temperature,
normalization, or router collapse. Disagreement among an admitted set depends on
which experts were admitted, their scales, their weights, and the cardinality of
the set. It is not a policy-independent epistemic measurement.

Matching mean active expert count does not establish matched wall-clock cost,
peak memory, communication, load balance, latency tail, or energy. A variable-k
policy is a new executable routing condition even when weights and router
parameters are unchanged.

CARE is demonstrated on MoE-LoRA adapters attached to dense backbones. It is not
an admitted method for changing the architectural top-k router of Agents-A1 or
another native large MoE.

## Binding object-identity gate

Every variable-cardinality study must freeze and report these objects separately
where they exist:

1. router input activation boundary;
2. router projection and pre-normalization scores;
3. router temperature, bias, masking, and normalization;
4. normalized router distribution;
5. concentration statistic, entropy, margins, and cumulative-mass curve;
6. deterministic sort, tie, and numerical-precision rule;
7. initial nucleus threshold and initial admitted cardinality;
8. initial admitted expert set and order;
9. initial expert-output boundary used for disagreement;
10. disagreement formula, normalization, epsilon, precision, and reduction;
11. disagreement threshold and extension rule;
12. minimum, maximum, and final expert cardinality;
13. final expert set and order;
14. final mixture-weight source and renormalization;
15. routed expert outputs and combine order;
16. shared-expert, residual, or dense branches;
17. final block contribution and downstream state;
18. passive uncertainty score;
19. compute-allocation, abstention, retry, or other control decision;
20. physical dispatch, capacity, padding, communication, and kernel path;
21. independently verified objective outcome; and
22. full executable runtime identity.

A field called `confidence`, `uncertainty`, `expert_disagreement`, `active_k`, or
`matched_compute` does not satisfy this gate without proving which object and
boundary it represents.

## Passive telemetry versus active policy gate

Router concentration may be evaluated as observation-only telemetry while the
underlying routing policy remains fixed. Replacing fixed top-k with variable-k
routing is an intervention and creates a different executable artifact.

The following must not be conflated:

- prediction of completed error under fixed routing;
- prediction of distribution shift under fixed routing;
- selection of expert cardinality;
- alteration of the model's output by changing cardinality;
- abstention based on the same score;
- early exit, retry, repair, or fallback; and
- production authorization.

M39 remains a forward-only, observation-only completed-error comparator. It may
measure prospectively frozen router concentration, cumulative-mass, margin, and
load summaries under the admitted fixed top-8 Agents-A1 runtime. It may not
change `k`, alter dispatch, abstain, retry, stop, or allocate compute.

Any adaptive-cardinality experiment requires a separate preregistration,
implementation admission, parity suite, outcome population, decision table, and
full-compute fallback. Results collected after adaptive routing changes model
outputs may not be represented as passive-monitor evidence for the fixed-routing
model.

## Cardinality-policy and thermostat gate

A variable-k policy must freeze:

- `k_min`, `k_max`, target mean budget, and any per-layer budgets;
- cumulative-mass threshold and search procedure;
- calibration population, split, digest, size, and sampling weights;
- whether calibration is labeled or unlabeled;
- global versus layer-specific threshold semantics;
- disagreement threshold, extension scale, clipping, and rounding;
- sort, tie, and precision behavior;
- selected-weight renormalization;
- treatment of shared experts and always-on branches;
- treatment of prefill, decode, padding, packed sequences, multimodal tokens,
  tool tokens, and cached prefixes;
- capacity, overflow, dropped-token, and duplicate-dispatch behavior;
- online versus frozen recalibration;
- drift detection, fallback, restart, reshard, and replica semantics; and
- exact deployment distribution on which the budget claim is made.

Threshold selection and thermostat calibration must occur entirely inside the
training or calibration boundary. Sealed or held-out outcomes may not influence
the threshold, budget, cardinality limits, per-layer allocation, disagreement
blend, or fallback rule.

A threshold calibrated on one task mixture, prompt distribution, context-length
distribution, language, runtime, or batch scheduler does not transfer to another
without prospective evidence. If the realized budget drifts, the result is a
different compute condition, not a harmless implementation detail.

## Disagreement identifiability gate

Admitted-expert disagreement is conditional on the admitted set. It is available
only after the relevant expert outputs have been computed. It is therefore not a
pre-expert, policy-independent uncertainty signal.

Required controls include:

1. fixed cardinality with varied router concentration;
2. fixed concentration with varied cardinality;
3. matched cardinality with random admitted experts;
4. matched cardinality with neighboring-ranked experts;
5. matched router weights with permuted expert outputs;
6. matched expert-output norms with altered directions;
7. same initial nucleus with and without the disagreement extension;
8. same final cardinality reached by different initial nuclei;
9. disagreement before and after selected-weight renormalization;
10. shared-versus-routed contribution controls;
11. expert-label permutations preserving load marginals;
12. collapsed, near-uniform, and near-one-hot routers;
13. wrong-but-low-disagreement and correct-but-high-disagreement strata; and
14. independently verified outcome matching.

Calling admitted experts an ensemble does not establish independent posterior
samples, calibrated epistemic uncertainty, semantic diversity, or causal value.
A disagreement score that improves OOD detection does not establish prospective
correctness prediction.

## Compute-matching and systems gate

Mean active expert count is insufficient for a matched-compute claim. Every
fixed-k versus variable-k comparison must report, at minimum:

- complete per-token and per-layer cardinality distribution;
- prefill and decode cardinality distributions separately;
- mean, median, variance, upper quantiles, maximum, and burst behavior;
- routed and shared active parameters;
- adapter and base-model FLOPs;
- sort, cumulative-sum, disagreement, extension, and control overhead;
- kernel launches and graph breaks;
- static padding or masking waste;
- capacity factors, overflow, dropped tokens, and duplicate dispatch;
- expert-load imbalance and hot-expert concentration;
- memory traffic and intermediate allocation;
- tensor-, pipeline-, data-, and expert-parallel communication;
- topology, placement, batching, scheduler, and sequence packing;
- peak device and host memory;
- throughput and p50/p95/p99 latency;
- failure, retry, and fallback rates; and
- total cost accounting for calibration and any retraining.

A one-pass algorithm is not necessarily one-stage physical execution. If
admitted-expert outputs are required before deciding whether to extend the set,
the implementation must prove how the extension is scheduled and whether
additional dispatch, padding, synchronization, or recomputation occurs.

Equivalent average adapter FLOPs do not establish equal end-to-end latency or
throughput. Static-k and dynamic-k kernels are separate runtime conditions until
measured under the admitted topology and workload.

## Counterfactual route-utility gate

Adaptive allocation is justified only if additional experts improve objective
outcome for the tokens receiving them and removing experts preserves objective
outcome for the tokens losing them.

Required comparisons include:

- fixed `k_min`, fixed target-budget k, and fixed `k_max`;
- random variable-k with the same cardinality distribution;
- cardinality permuted across tokens while preserving layer and batch marginals;
- confidence-only allocation;
- disagreement-only allocation;
- matched-budget position, length, task-family, and difficulty allocation;
- oracle allocation reported only as an upper-bound comparator;
- wrong-to-right, right-to-wrong, unchanged-right, and unchanged-wrong outcomes;
- per-family and distribution-shift strata; and
- complete regression accounting.

Improved aggregate accuracy with the same mean k does not prove that router
uncertainty correctly identified the tokens that needed more experts. The
allocation claim requires token- or task-grouped paired counterfactual evidence
under an independent verifier.

## Derivative and Jacobian consequences

Variable cardinality introduces discrete cumulative-mass and disagreement
boundaries. A derivative computed with the admitted set and cardinality held
fixed answers only a conditional local question.

Future Jacobian work involving adaptive routing must report:

- distance to every cumulative-mass threshold crossing;
- distance to disagreement-extension thresholds;
- fixed-cardinality JVP/VJP parity;
- fixed-set and fixed-order parity;
- finite differences that preserve cardinality;
- finite differences that cross cardinality boundaries;
- route-unchanged, route-changed, and cardinality-changed strata;
- pre- and post-renormalization controls;
- shared-versus-routed branch controls; and
- independently verified outcome effects.

A smooth Jacobian cannot by itself represent the discrete effect of admitting or
removing an expert. Boundary-crossing behavior must be analyzed as a hybrid
discrete-continuous intervention.

## Agents-A1 scaling consequence

The technically credible sequence is:

1. Complete Q35Q exact-target-runtime provenance, strict loading, packed-tensor
   consumption, expert ordering, deterministic forward, VJP, JVP, and
   finite-difference admission.
2. Admit Agents-A1-4B as the dense bridge under its exact checkpoint, tokenizer,
   hybrid state, cache, harness, verifier, and runtime.
3. Establish deterministic, confidence, trajectory, hidden-state, spectral,
   memory, program-state, and verifier baselines.
4. Separately admit Agents-A1-35B's fixed top-8 checkpoint, quantization, router,
   routed and shared experts, hybrid state, cache, kernels, topology, batching,
   scheduler, and capture path.
5. Complete M39 only as fixed-routing, observation-only telemetry. Include
   prospectively frozen concentration, cumulative-mass, margin, load, and
   expert-contribution summaries as separate comparator blocks where capture
   parity and privacy gates pass.
6. Require router telemetry to add sealed completed-error value beyond logits,
   confidence, length, position, task difficulty, hidden-state, spectral,
   trajectory, memory, program-state, and verifier controls.
7. If fixed-routing router uncertainty shows stable incremental value, test
   variable cardinality first on an admitted tractable proxy or bridge model
   under a separate intervention preregistration.
8. Prove native Agents-A1 variable-k tensor semantics, capacity behavior, kernel
   behavior, route parity, state lineage, and objective counterfactual utility
   before any 35B adaptive-routing experiment.
9. Compare fixed top-8 against adaptive policies at full systems cost, not mean
   expert count alone.
10. Add Jacobian features only after exact derivative parity and sealed residual
    value over the complete fixed-routing comparator stack.
11. Preserve fixed top-8/full-compute fallback and separately gate abstention,
    retry, repair, early exit, forced routing, activation steering, and
    production deployment.

CARE is an informative comparator for adaptive adapter routing. It is not a
transfer bridge from MoE-LoRA to Agents-A1's architectural MoE and does not
alter the active Q35Q execution order.

## Established by this correction

- Router concentration, expert disagreement, adaptive cardinality, executed
  route, uncertainty readout, control action, runtime cost, and objective outcome
  are separate binding identities.
- Variable-k routing is a new executable artifact even with unchanged weights.
- Disagreement is admitted-set- and cardinality-dependent.
- Mean active expert count is not sufficient compute matching.
- Thermostat calibration population and threshold are artifact identities.
- Fixed-routing monitor evidence cannot be silently reused as adaptive-policy
  evidence.
- Smooth derivatives do not cover cardinality-boundary crossings.
- MoE-LoRA adaptive-routing results do not transfer to native Agents-A1 routing.
- Existing privacy, sealed-data, verifier, provenance, derivative, GPU,
  intervention, and production gates remain intact.
- Q35Q remains blocked.

## Unproven

- Independent reproduction of arXiv `2607.26052v1`.
- Immutable admission of the claimed released implementation.
- Monotonicity between router concentration and correctness in arbitrary models.
- Concavity of per-token utility in expert cardinality.
- Ensemble or epistemic interpretation of selected expert outputs.
- End-to-end compute equivalence under variable cardinality.
- Robustness across deployment distributions, long contexts, languages,
  generation, tools, or persistent agent state.
- Transfer from MoE-LoRA to Qwen3.5, Qwen3.6, or Agents-A1 native MoEs.
- Prospective completed-error value beyond cheaper comparators.
- Safe adaptive routing, abstention, early exit, retry, repair, forced routing,
  activation steering, or production control.
- Complete Q35Q exact-runtime and derivative admission.

## Active blocker

The active blocker remains exact-target-runtime Q35Q admission:

1. execute the composed Transformers provenance adapter in the exact target
   runtime using aggregate evidence only;
2. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple;
3. bind the actual GPTQModel/Defuser loader and complete executable source
   closure;
4. run strict synthetic Qwen3.5-MoE loading;
5. prove one-time packed-tensor consumption;
6. prove exact expert and fusion ordering;
7. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity; and
8. pass the complete Phase-0 conjunction before weight staging or GPU
   authorization.

No finding in this addendum resolves or weakens that blocker.
