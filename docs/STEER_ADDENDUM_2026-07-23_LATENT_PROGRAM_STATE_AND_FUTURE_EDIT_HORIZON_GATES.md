# Steering addendum — latent program state and future-edit horizon gates

Date: 2026-07-23

Status: binding future-protocol correction; no current execution authorization

## Scope and unchanged controls

This addendum applies to every future coding-agent, hidden-state, trajectory,
router-telemetry, semantic-workspace, sparse-feature, transcoder,
directional-JVP, Jacobian-lens, early-abort, escalation, repair, or steering
claim that predicts a current or future software-artifact property.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. It authorizes no weight staging, model
execution, GPU execution, hidden-state capture, route capture, Jacobian fitting,
sealed scientific evaluation, intervention, or production deployment.

Every existing privacy, sealed-data, verifier-independence, provenance,
exact-loading, numerical-parity, derivative-parity, resource, cleanup,
intervention, production-gating, and stop rule remains binding.

GitHub currently reports this repository as public. Only aggregate
public-source program-control information may be committed. Prompts, source
code from evaluated tasks, outputs, token IDs, per-example labels, hidden
states, route traces, Jacobians, caches, credentials, local paths, and private
logs remain prohibited.

## Triggering primary evidence and narrow interpretation

Silva, Tu, and Monperrus, “Latent Programming Horizons in Coding Agents,”
arXiv `2607.05188v1`, submitted 2026-07-06, studies linear residual-stream
probes during real multi-step software-engineering trajectories.

The associated public implementation was inspected at immutable commit
`ASSERT-KTH/program-probes@bee2b060146bd4468a8f7802c11dc03b77a12d15`.
The public trajectory and per-edit-label release is
`ASSERT-KTH/latent-programming-horizons-trajs`; the release does not include the
hidden-state tensors or trained probes.

The reported experiment uses mini-swe-agent v2.2.8 with
`Qwen3.6-35B-A3B` and `Laguna-XS.2` on SWE-Bench Verified and SWE-Bench Pro.
The paper reports 22,714 trajectories, a median trajectory length of 52 agent
steps and roughly 36k tokens, task-identifier-separated train/test splits, and
hidden-state sampling every five tokens. Linear probes decode current program
properties including syntactic well-formedness, full test correctness, partial
improvement, and regression, with reported best-layer AUC up to approximately
0.83–0.84. Separate probes trained for future labels remain above chance at
lookahead horizons extending to roughly 25 steps in the headline result.

The source is directly relevant because one tested model is a large sparse MoE
from the same broad Qwen3.6 family used beneath Agents-A1. The result is still
not an Agents-A1 result and does not establish route-specific or
Jacobian-specific value.

The paper’s own limitations are binding to the interpretation:

- decodability is not causality;
- only two models, one agent scaffold, and two coding benchmarks were tested;
- label imbalance materially affects some endpoints;
- the shuffled-label control tests probe capacity but does not rule out visible
  trajectory, task-difficulty, current-state, progress, or censoring confounds;
- prediction of the future state reached by the realized trajectory is not
  proof that the model explicitly planned that state; and
- no passive-monitor utility, early-abort utility, repair utility, or production
  safety result was established.

## Binding endpoint separation

Future compatible work must keep these objects separate:

1. **Current artifact state:** the exact repository, files, diff, dependencies,
   environment, and test state at the decision boundary.
2. **Current program property:** an externally computed property of the current
   artifact, such as parsing, compilation, test behavior, or regression status.
3. **Future realized artifact property:** the property of the artifact reached
   by one subsequently realized trajectory at a frozen lookahead.
4. **Candidate edit or plan:** what edit, tool action, or repair the model is
   currently disposed to attempt.
5. **Path-specific future prediction:** prediction of which branch will occur
   under the frozen generator, harness, sampling policy, and environment.
6. **Eventual task outcome:** final success under an independent objective
   evaluator.
7. **Causal use:** evidence that the model uses the represented information to
   choose its next edit or action.
8. **Policy utility:** a frozen monitor/controller improves objective outcome and
   cost without violating risk, privacy, or production gates.

Passing an earlier endpoint does not establish a later endpoint. In particular,
a probe that predicts the future state of the realized trajectory may be
encoding current artifact quality, task difficulty, trajectory progress,
scaffold policy, or a broad success basin rather than a specific intended edit.

## Event clock and horizon gate

Every future “horizon” claim must freeze the event clock before data capture.
Report lookahead separately in:

- model tokens;
- assistant turns;
- tool calls;
- artifact-changing edits;
- verifier or test executions;
- elapsed wall time; and
- remaining fraction of the admitted trajectory budget.

A statement such as “25 steps ahead” is incomplete without the step ontology.
Tool reads, shell commands, edits, tests, retries, summaries, and no-op actions
may not be silently treated as interchangeable.

For every horizon `k`, freeze:

- the current decision boundary and label boundary;
- whether the target is the next edit, the artifact after `k` generic steps, the
  artifact after `k` edits, or the final artifact;
- the eligible trajectory population;
- handling of trajectories that terminate before `k`;
- maximum step, token, timeout, retry, and context limits;
- label carry-forward behavior between edits;
- hidden-state sampling stride and pooling;
- all train, tuning, certification, and sealed-test populations.

Report full horizon curves rather than a selected furthest-above-chance point.
Layer, horizon, endpoint, and model selection must be corrected for multiplicity
or confirmed on a prospectively held-out population.

## Censoring, persistence, and survivorship controls

Long-horizon samples are selected by future trajectory length. Successful,
failed, timed-out, truncated, and looping trajectories can therefore enter the
eligible population at different rates.

Required reporting includes:

- counts and label prevalence at every horizon;
- exclusion and censoring counts by objective outcome;
- trajectory-length and remaining-budget distributions;
- results on a fixed common population across horizons;
- results without the common-population length filter where feasible;
- clustered uncertainty at the task and trajectory levels;
- sensitivity to inverse-probability weighting or prospectively frozen length
  strata where censoring is material; and
- performance of a persistence baseline that predicts the future property from
  the current externally measured property.

A horizon result that disappears after current-state, progress, or censoring
controls must be classified as state persistence or trajectory-selection
telemetry, not future-plan evidence.

## Mandatory task and trajectory separation

Multiple trajectories from one issue are not independent task samples.

At minimum:

- no task identifier may appear across train, validation, certification, and
  sealed-test splits;
- uncertainty must cluster all rollouts of the same task;
- repository, project, issue-family, and benchmark leakage must be measured;
- template-disjoint and repository-disjoint transfer must be reported where
  feasible;
- hyperparameter, layer, horizon, and threshold selection must remain inside the
  training/tuning populations; and
- cross-benchmark transfer may not be described as model-family or scaffold
  transfer.

A public trajectory release is an external audit target, not an admissible
source for jLens sealed evaluation tasks.

## Mandatory cheaper comparators

Every compatible future-program probe must compare, at the identical decision
boundary, against:

1. current parser, compiler, test, linter, type-checker, and deterministic
   artifact checks available under the admitted task contract;
2. the current property itself and simple persistence/transition models;
3. task, repository, benchmark, language, issue, and base-commit metadata;
4. step index, remaining budget, response length, context length, retry count,
   edit count, test count, timeout state, and trajectory phase;
5. last tool type, last command class, last test result, failing-test count,
   changed-file count, diff size, and visible error summaries;
6. token-space and bounded trajectory-summary baselines;
7. final and intermediate logits, entropy, margins, and calibrated confidence;
8. explicit self-judgement and predicted next action;
9. passive linear hidden-state probes for current and future properties;
10. peer-model or dense-sibling representations when separately admitted;
11. direct route and expert-path summaries only after MoE telemetry admission;
12. sparse-feature or transcoder streams; and
13. Jacobian-lens features only after exact derivative admission.

An internal feature must add sealed objective-outcome or future-property value
after conditioning on all technically available cheaper comparators. A gain over
shuffled labels alone is insufficient.

## Branch and planning-identifiability gate

Prediction of the artifact reached by one sampled rollout does not establish an
explicit internal plan.

When technically feasible, future planning claims must use frozen same-prefix
branching:

- replay the identical task, artifact, environment, prompt, history, cache, and
  decision boundary;
- generate multiple continuation branches under prospectively frozen seeds or
  sampling policies;
- record branch diversity and future-property prevalence;
- compare prediction of a broad branch-invariant property against prediction of
  the specific realized branch;
- compare the target model with a scaffold-only or task-only predictor;
- include counterfactual branches where the next edit, tool action, or final
  outcome differs; and
- keep future branch labels unavailable to feature construction and route or
  controller selection.

If a state predicts that most plausible branches improve but not which branch
will be taken, the claim is broad task-state or recoverability prediction. It is
not a demonstrated encoded edit plan.

## Label and verifier provenance

Every program-property label must freeze:

- repository and base-commit identity;
- patch-application order;
- dependency and environment identity;
- parser/compiler/test commands;
- test selection, timeout, retry, and flaky-test policy;
- baseline comparison state for improvement and regression labels;
- malformed, unavailable, and indeterminate outcomes;
- label carry-forward and token-to-edit alignment;
- evaluator code and immutable artifact identities; and
- independent audit and sealed-evaluation populations.

A label derived after the decision boundary is permitted as a retrospective
training or evaluation target only. It may not enter the feature, pair-selection,
calibration, threshold, route-selection, or intervention path.

## Hidden-state capture and privacy

All existing hidden-state capture admission remains binding, including exact
layer, normalization, token-position, batching, chunked-prefill, prefix-cache,
KV-cache, quantization, kernel, topology, serialization, and replay controls.

The public program-probes implementation uses chunked KV-cache inference for
long trajectories. Any jLens reproduction must establish capture-position
coverage and numerical agreement across chunk boundaries before scientific use.

Raw task code, prompts, conversations, commands, diffs, test logs, hidden states,
per-step scores, route traces, and future labels remain private and gitignored.
Only prospectively permitted aggregate counts, metrics, uncertainty summaries,
and immutable public-source identities may enter this public repository.

## Agents-A1 scaling consequence

The technically credible sequence is now:

1. Complete Q35Q production-path provenance composition.
2. Prove strict quantized tensor consumption, expert ordering, forward parity,
   activation-VJP parity, activation-JVP parity, and finite-difference parity.
3. Freeze coding-task contracts, artifact states, program-property labels,
   event clocks, external evaluators, and irreversible-action boundaries.
4. Separately admit Agents-A1-4B and establish deterministic artifact checks,
   visible trajectory baselines, current-state persistence, and passive linear
   program-property probes.
5. Evaluate future-property horizons on Agents-A1-4B with task-clustered splits,
   censoring controls, fixed populations, and same-prefix branch tests.
6. Establish confidence, self-judgement, peer-representation, temporal-state,
   requirement-ledger, verifier-history, and bounded trajectory comparators.
7. Separately admit Agents-A1-35B and repeat hidden-state capture, calibration,
   and horizon certification rather than transferring layers or thresholds.
8. Capture only the minimum direct route and expert-path telemetry required under
   fixed topology and serving state.
9. Require route features to add sealed value beyond program-state probes,
   artifact checks, progress controls, visible trajectory features, and the
   separately admitted dense sibling.
10. Add sparse-feature or transcoder comparators.
11. Add Jacobian-Lens only after exact derivative parity and sealed incremental
    value over every cheaper comparator.
12. Keep abort, retry, repair, escalation, truncation, route forcing, activation
    steering, and production enforcement under separate gates.

The Qwen3.6-35B-A3B result is a strong external feasibility precedent for a
passive MoE hidden-state comparator. It does not authorize transfer of probe
weights, layers, horizons, thresholds, effect sizes, task labels, or controller
policies to Agents-A1.

## Intervention boundary

This addendum authorizes no early abort, edit suppression, retry, repair,
escalation, truncation, route intervention, activation steering, or production
action.

Any control study must use fresh populations and separately freeze the action,
threshold, fallback, recovery path, false-positive harm budget, false-negative
harm budget, verifier, full cost, and irreversible-action boundary. Current and
future artifact versions must remain recoverable until an independent
replacement rule passes.

## Current blocker and program status

The active blocker remains production-path upstream/runtime provenance
composition for Q35Q. The next admissible implementation must:

1. bind the live import to its owning installed distribution and `RECORD`;
2. derive complete live-object source closure for dispatch, converters, nested
   operations, model and configuration classes, and loader objects;
3. reject shadow packages, editable installs, monkeypatches, forged identities,
   incomplete closure, incorrect ownership, and unadmitted loaders in a clean
   subprocess;
4. invoke and bind the actual GPTQModel/Defuser loader entry point;
5. freeze the exact immutable GPTQ runtime tuple;
6. pass the complete adversarial integration conjunction; and
7. emit only the permitted aggregate result.

After that remain packer-independent fixture validation, exact quantized-tensor
consumption and expert ordering, forward/VJP/JVP/finite-difference parity,
Q35Q Phase-0 admission, weight staging, and a separately authorized GPU
transition.

Aggregate status remains:

`q35q_artifact_admission_blocked`

## Established

- Hidden states in the reported coding-agent experiments contain linearly
  decodable information about current program properties.
- The reported Qwen3.6-35B-A3B experiment is a direct large-MoE feasibility
  precedent for passive coding-agent state probes.
- Future realized program properties were predictable above chance at nonzero
  lookahead horizons under the reported scaffold and datasets.
- Current program state, future realized state, explicit plan, eventual outcome,
  causal use, and controller utility are distinct endpoints.
- Event-clock, censoring, persistence, task-clustering, branch-identifiability,
  cheaper-comparator, capture, label-provenance, and privacy gates are now
  binding.
- Existing privacy, sealed-data, verifier, provenance, derivative,
  intervention, and production gates remain intact.

## Unproven

- Independent reproduction of arXiv `2607.05188v1` and its full public pipeline.
- Causal use of the decoded program properties by either tested model.
- A specific encoded future edit plan rather than task-state, progress, or
  recoverability information.
- Natural-population policy utility or safe early abort from the reported probes.
- Transfer across agent scaffolds, model families, quantizations, serving
  runtimes, tools, or non-coding domains.
- Transfer to Agents-A1-4B or Agents-A1-35B.
- Incremental route or Jacobian-Lens value after all cheaper program-state and
  trajectory comparators.
- Complete Q35Q strict loading, forward parity, or derivative admission.
- Safe early exit, retry, repair, truncation, route intervention, activation
  steering, or production deployment.