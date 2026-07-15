# STEER ADDENDUM — M39 metacognition comparators, temporal hidden-state block, and early-exit boundary

Status: **binding design amendment; not launch authorization.**

This addendum amends `docs/M39_FORWARD_ONLY_COMPARATOR_PREREG.md` before any
M39 outcome-bearing capture. It does not authorize scientific capture, alter
M38E, weaken any frozen threshold, permit cross-milestone data reuse, or relax
sealed-data, verifier, provenance, privacy, power, parity, resource,
commit-safety, or production gates.

## Evidence motivating this amendment

The following work is relevant but does not establish any result on Agents-A1:

- `Metacognition in LLMs: Foundations, Progress, and Opportunities`
  (arXiv:2607.11881v1) separates **monitoring** from **control** and catalogs
  confidence-, representation-, interpretability-, and agent-level methods.
  Its GitHub repository is an organized bibliography, not an executable
  Agents-A1 baseline.
- `LLMs Know When They Know, but Do Not Act on It: A Metacognitive Harness for
  Test-time Scaling` (arXiv:2605.14186v1) uses frozen pre-solve and post-solve
  self-assessment signals to control retries and aggregation. It is evidence
  that behavioral self-monitoring is a necessary comparator, not evidence that
  the policy transfers to Agents-A1 or that internal telemetry is causal.
- `Adaptive Tool Use in Large Language Models with Meta-Cognition Trigger`
  (ACL 2025, Anthology 2025.acl-long.655) derives representation-space signals
  for tool invocation. It motivates comparison against low-cost behavioral and
  representation baselines; it does not establish M39's verifier-backed task
  endpoint.
- `Code Correctness Signals in LLM Hidden States: Pre-Generation Probing and
  Repair Geometry` (arXiv:2606.14530v2) reports leakage-controlled hidden-state
  correctness signals on one Qwen3-4B code model and demonstrates the importance
  of train-fold-only nuisance residualization. Its public code/README and paper
  may not always be synchronized; exact paper version and code commit must be
  pinned before borrowing a formula or result.
- `Spatiotemporal Hidden-State Dynamics as a Signature of Internal Reasoning in
  Large Language Models` (arXiv:2605.01853v1) proposes adjacent-token and
  layer-concentration dynamics as a training-free correctness signal. This is a
  candidate aggregate feature family, not an established MoE or Agents-A1
  mechanism.
- `When Are Experts Misrouted? Counterfactual Routing Analysis in
  Mixture-of-Experts Language Models` (arXiv:2605.07260v1) reports that standard
  routes can be least informative on fragile reasoning tokens across several
  MoEs. Counterfactual routing and router updates are interventions and remain
  outside M39's observation-only scope.
- `The Diminishing Returns of Early-Exit Decoding in Modern LLMs`
  (arXiv:2603.23701v1) reports lower intrinsic early-exit potential for MoE and
  state-space models than dense transformers. The public TIDE repository shows
  a useful dense-model engineering lead, but its listed Qwen benchmark is Qwen3
  8B and it does not establish safe early exit on Qwen3.5 MoE or Agents-A1.

These sources justify stronger comparators and confound controls. They do not
justify changing M38E, starting an Agents-A1 intervention, or claiming safe
truncation.

## Binding monitoring-versus-control separation

M39 remains a **monitoring** study. It may measure completed-error prediction
only after the primary answer is sealed and before the verifier verdict is
exposed to any feature pipeline.

No M39 signal may decide, during M39 capture, whether to:

- stop or continue generation;
- retry, revise, aggregate, retrieve, or invoke a tool;
- change token caps, temperature, seeds, routes, experts, or compute allocation;
- steer activations or modify router or expert parameters.

Any later control policy requires a separate fresh-population preregistration
with verifier-backed utility, compute accounting, regret/harm analysis, parity,
privacy, power, and production gates. Monitoring success alone is not control
success.

## Required behavioral metacognition comparator

The M39 launch amendment must include an isolated **behavioral metacognition
block** unless a pre-capture feasibility smoke records it as unsupported.

The block must freeze:

1. one pre-solve self-assessment prompt producing a bounded probability or
   ordinal score of prospective success;
2. one post-solve self-assessment prompt producing a bounded probability or
   ordinal score that the already-sealed answer is correct;
3. exact prompt text, model/runtime identity, context construction, token budget,
   sampling settings, seeds, parsing, invalid-output handling, and missingness;
4. whether scores are raw, calibrated, or both, with calibration fit only inside
   training folds;
5. exact latency, token, and compute accounting for the comparator calls.

The pre-solve and post-solve assessments must run as stateless, isolated calls.
They may not alter the primary answer, generation context, telemetry stream, or
verifier. The post-solve call may read the prompt and sealed answer but never a
verifier result, accepted answer, failure subtype, gold comparison, or any
quantity derived from them.

Behavioral scores and prompts remain private. Only aggregate results may be
committed.

## Incremental comparison hierarchy

The launch amendment must preserve the existing nuisance and router comparisons
and additionally test whether an internal block adds information beyond a model's
own frozen self-assessment.

At minimum, the locked hierarchy must include:

- nuisance baseline;
- nuisance plus behavioral metacognition;
- nuisance plus router;
- nuisance plus behavioral metacognition plus router;
- each candidate internal block added to the strongest applicable preceding
  baseline.

The exact hierarchical gate and multiplicity accounting must be frozen before
capture. Failure to support the larger comparison set at the preregistered power
threshold yields `underpowered/inconclusive`; it does not permit deleting the
hardest comparator after outcomes are observed.

A positive internal result may be described as **incremental completed-error
prediction beyond behavioral self-assessment and router telemetry** only if it
clears the corresponding locked comparison. Otherwise the claim must be narrower.

## Train-fold-only nuisance residualization

For every router, routing-load, expert-contribution, hidden-state, temporal, or
future Jacobian-derived feature block, the launch amendment must freeze a
nuisance-control procedure before capture.

The confirmatory internal representation must be residualized or otherwise
conditioned against the frozen nuisance variables inside training folds only.
No regression, normalization, projection, feature selection, layer selection,
or calibration parameter may be fit on validation or held-out rows.

The amendment must specify:

- the exact nuisance matrix and encoding;
- the residualization model and regularization;
- treatment of categorical levels and missing values;
- whether residualization is per feature, jointly multivariate, or implemented
  by an equivalent nested model comparison;
- the train-to-calibration/validation/held-out transform procedure;
- collinearity checks and fail-closed behavior.

Raw-block performance may be reported descriptively, but a raw signal that does
not survive the frozen nuisance-controlled analysis does not establish privileged
internal information.

## Separate temporal hidden-state dynamics block

M39 may include one separately identifiable **temporal hidden-state dynamics
block** if and only if a non-outcome-bearing smoke proves exact capture,
phase attribution, parity, privacy, and resource feasibility.

The block must be defined from preregistered on-device aggregate reductions such
as:

- adjacent-token residual-change norms at a frozen layer set;
- layer concentration or saliency concentration of those changes;
- temporal dispersion, maxima, quantiles, and change-point counts;
- separately reduced prefill and autoregressive-decode summaries.

The exact formulas, normalization, layer set, token exclusions, precision,
missingness, and reduction order must be committed before capture. Full hidden
states, token-level trajectories, layer-by-token matrices, and per-token feature
vectors may not persist.

Do not call the block `StALT` unless the exact published statistic and evaluation
contract are reproduced. A related but modified reduction must use a repository-
specific neutral name and may not borrow the source paper's claims.

If the block cannot be captured without raw-state persistence, output change,
hidden offload, excessive overhead, phase ambiguity, or privacy risk, record
`m39_temporal_block_unsupported` and continue only with already supported frozen
blocks. Do not weaken the gate.

## Counterfactual routing boundary

M39 may observe router logits, selected routes, loads, margins, transitions, and
expert contributions under the frozen executed route. It may not sample
alternative routes, replace selected experts, update a router, or score
counterfactual route utility.

A future counterfactual-routing study must be separately preregistered with:

- equal-compute route alternatives;
- a frozen route-sampling distribution;
- exact next-token or verifier-backed utility;
- route-parity and dispatch-identity tests;
- independent fresh tasks and no M39 held-out reuse;
- harm, compute, multiplicity, and production gates.

## Early-exit and truncation priority

Do not adopt TIDE or another intermediate-layer exit system as the next Agents-A1
milestone. Current evidence does not establish sufficient early-exit headroom or
safety for a large post-trained Qwen3.5 MoE.

The program order remains:

1. establish observation-only completed-error monitoring under M39;
2. establish architecture-matched exact-VJP and lens feasibility under Q35Q;
3. only after a monitoring signal clears its locked held-out gate, preregister a
   separate control study for retry/tool/compute allocation;
4. consider layer-wise early exit only after a model-specific intrinsic-exit
   feasibility study proves meaningful headroom and final-output parity on a
   fresh neutral corpus.

No correctness-preservation claim may be inferred from cosine convergence,
single-prompt stability, token exit rate, or throughput alone.

## Literature and implementation provenance

Any external method adopted into M39 or a successor must pin, before capture:

- exact paper identifier and version;
- exact repository URL and immutable commit;
- exact copied or reimplemented formula;
- deviations from the source method;
- source license and dependency identities;
- synthetic reproduction tests and repository privacy scan.

A paper/code mismatch, mutable branch reference, missing original formula, or
unverifiable implementation identity blocks the borrowed feature until resolved.

## Scoped outcomes

Permitted additional scoped outcomes include:

- `m39_behavioral_metacognition_supported`;
- `m39_behavioral_metacognition_unsupported`;
- `m39_temporal_block_supported`;
- `m39_temporal_block_unsupported`;
- `m39_internal_increment_beyond_self_report_established`;
- `m39_internal_increment_beyond_self_report_not_established`;
- `m39_monitoring_established_control_unproven`.

None authorizes stopping, retry, tool routing, route intervention, activation
steering, or production use.

## Privacy and completion boundary

All raw tasks, prompts, answers, self-assessment text, scores, token IDs,
telemetry, routes, expert identities, hidden summaries, temporal trajectories,
feature vectors, predictions, split labels, verifier labels, and per-example
readouts remain private and uncommitted.

The research program remains incomplete. This addendum strengthens M39's
comparators and confound controls; it does not establish a Jacobian Lens,
Agents-A1 error predictor, metacognitive controller, or safe early exit.