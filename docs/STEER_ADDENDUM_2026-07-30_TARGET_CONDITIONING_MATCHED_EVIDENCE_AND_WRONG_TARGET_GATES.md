# Steering Addendum — Target Conditioning, Matched-Evidence, and Wrong-Target Gates

Date: 2026-07-30

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `8c316f793cf5d7fd48563883f34461d928bfb173`

## Scope and inherited restrictions

This addendum applies to every future hidden-state outcome monitor, router-telemetry
readout, Jacobian-Lens readout, semantic-workspace claim, correctness or error
probe, early-exit or truncation predictor, retry or repair predictor, tool-action
monitor, branch selector, recurrent-depth policy, and Agents-A1 evaluation.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No model-weight staging, tensor-payload
retrieval, model execution, GPU execution, hidden-state capture, router capture,
cache capture, JVP, VJP, Jacobian fitting, sealed scientific evaluation,
intervention, or production use is authorized by this document.

Every existing privacy, sealed-data, canonical-verifier, provenance, exact-set,
exact-gradient, parity, nuisance-control, multiplicity, resource-accounting,
cleanup, commit-safety, intervention, and production gate remains binding.

GitHub reports this repository as public. Only aggregate public-source program
control is recorded here. Prompts, completions, evidence passages, target
questions, token IDs, per-example scores, verifier labels, hidden states, router
arrays, expert paths, KV caches, Jacobians, gradients, model weights,
credentials, host paths, private runtime facts, and sealed outcomes remain
prohibited from this repository.

## New primary evidence

Kong and Li, “Same Evidence, Different Target: Decoding How Diagnostic Evidence
Bears on Causal Questions from Language-Model States,” arXiv `2607.26929v1`,
submitted 2026-07-29, introduces paired prompts that repeat diagnostic evidence
verbatim while changing the causal target.

The target can differ in population, outcome, estimand, pathway, or identifying
assumptions. Each prompt is labeled `Favors`, `Challenges`, `Unresolved`, or
`Wrong Target` according to how the unchanged evidence bears on the stated
causal question. A pair counts as recovered only when both target-conditioned
prompts are classified correctly.

The paper reports linear readouts from the final-token hidden state of the
penultimate transformer block for Qwen2.5-7B-Instruct, Qwen3-8B, and
Llama-3.1-8B-Instruct. On a primary benchmark of 49 pairs across nine diagnostic
families, reported balanced accuracy ranges from 0.654 to 0.659 and complete-pair
recovery ranges from 18 to 21 pairs. The reported hidden-state readouts exceed a
linear answer-option-logit classifier and text baselines. A family-held-out
analysis reportedly recovers at least one pair in each of the nine families.

Primary source:

- https://arxiv.org/abs/2607.26929v1

No attributable immutable public implementation revision was identified during
this review. The evidence is therefore paper-level only and is not an admitted
reproduction artifact.

A separate recent paper, Rahman et al., “Probing the Origins of Reasoning
Performance: Representational Quality for Mathematical Problem-Solving in RL
vs. SFT Fine-Tuned Models,” arXiv `2607.26119v1`, reports checkpoint-dependent
correctness-probe and layer-ablation differences between RL- and SFT-tuned
models. That result reinforces the existing rule that adaptation creates a new
checkpoint and invalidates untested monitor transfer. It does not require a
separate protocol change beyond the gates already binding here and elsewhere.

## Binding interpretation

The new evidence supports only the following bounded claims:

1. Under the reported models, prompts, layer, token position, labels, splits,
   and linear readout, hidden states contain decodable information about how a
   diagnostic result bears on a stated causal target.
2. Holding evidence text fixed while changing the target is a useful control
   against evidence-only, sentiment, lexical-pattern, and familiar-diagnostic
   shortcuts.
3. Row-level accuracy can conceal target confusion. Complete paired or grouped
   recovery is a stricter measure when one evidence item supports multiple
   target-conditioned labels.
4. A model can represent the evidence and still apply it to the wrong target.
5. The result does not establish a generic correctness variable, objective
   causal reasoning, model-native use, causal necessity, introspective access,
   a semantic workspace, or a writable control direction.
6. The result does not establish transfer to Qwen3.5, Qwen3.6, Agents-A1,
   architectural MoEs, tool-use agents, long-horizon environments, or production
   control.

## Required target identity

Every compatible monitor or intervention study must bind the target independently
of the evidence and independently of the model output. At minimum, freeze:

1. **Evidence identity:** exact evidence available at the monitoring boundary,
   including source, timestamp, provenance, parser state, and whether it is
   observed, retrieved, generated, inferred, or privileged.
2. **Target population:** the examples, users, environments, repositories,
   trajectories, branches, or deployment regime to which the claim applies.
3. **Target outcome:** the exact event to predict or control.
4. **Target horizon:** the token, action, tool call, branch, episode, or elapsed
   time at which that outcome is evaluated.
5. **Target estimand:** point outcome, counterfactual contrast, marginal utility,
   conditional risk, route utility, intervention effect, or another frozen
   quantity.
6. **Target pathway:** direct model output, tool execution, environment change,
   verifier decision, downstream agent action, or another causal path.
7. **Target assumptions:** parser, verifier, missingness, exchangeability,
   consistency, no-interference, freshness, environment-snapshot, and policy
   assumptions required for the label to be meaningful.
8. **Target availability boundary:** the earliest point at which the label or
   sufficient information for it exists.
9. **Readout target:** the exact class, score, rank, probability, regression
   quantity, or relational decision fitted from the representation.
10. **Objective outcome:** the independently verified result, kept separate from
    the fitted readout and from the model’s own later behavior.

A monitor artifact identity is incomplete without the full target definition.
The same feature extractor paired with a different target is a different monitor.
A change in population, outcome, horizon, estimand, pathway, verifier, parser,
or policy creates a new scientific condition requiring prospective calibration
and sealed evaluation.

## Matched-evidence, different-target gate

Whenever a claimed signal could reflect the evidence text, evidence polarity,
diagnostic family, task family, answer format, or familiar lexical pattern,
construct matched groups in which the evidence is held fixed and the target is
changed.

Compatible studies must include, where definable:

- the same evidence paired with a target it favors;
- the same evidence paired with a target it challenges;
- the same evidence paired with a target it leaves unresolved;
- the same evidence paired with a substantively wrong or non-addressed target;
- paraphrased targets preserving the same estimand;
- targets that alter only population, outcome, horizon, pathway, or assumption;
- answer-option and display-order permutations;
- matched evidence polarity and lexical overlap;
- content-free or evidence-only controls;
- target-only controls;
- full-prompt controls;
- answer-option-logit, next-token, length, entropy, margin, and text baselines.

All members of a matched evidence group must remain in one train, calibration,
validation, or sealed partition. Diagnostic-family selection, target-template
selection, layer selection, feature selection, thresholding, and policy tuning
must occur without sealed group labels.

Report at minimum:

1. row-level class metrics;
2. complete-pair or complete-group recovery;
3. target-confusion matrix;
4. wrong-target false-positive and false-negative rates;
5. performance conditional on identical evidence;
6. performance conditional on held-out target templates;
7. performance conditional on held-out diagnostic or task families;
8. the incremental value over evidence-only, target-only, full-text, option-logit,
   and transparent behavioral baselines;
9. source-group-clustered uncertainty;
10. all inspected target constructions and multiplicity corrections.

A pair is not recovered when only the easier or lexically favored target is
correct. High row accuracy with low complete-group recovery is evidence of target
confusion, not general target-sensitive reasoning.

## Wrong-target and evidence-target leakage gate

The label `Wrong Target` is scientifically distinct from `Unresolved`.

- `Unresolved` means the evidence is relevant to the target but insufficient to
  determine the requested relation under the frozen assumptions.
- `Wrong Target` means the evidence addresses another population, outcome,
  estimand, horizon, pathway, or assumption and therefore does not answer the
  stated target.

Future datasets and verifiers must freeze this distinction before fitting. They
must include adjudication for cases where multiple targets are partially
addressed, where the evidence changes an intermediate variable but not the
specified endpoint, where a proxy is substituted for the outcome, or where a
short-horizon effect is presented as a long-horizon effect.

Required leakage controls include:

- exact and approximate overlap between target words and label words;
- option-token frequency and option-position priors;
- prompt-template and diagnostic-family identity;
- evidence sentiment, polarity, negation, and modality;
- answer-region and future-token exclusion;
- source-document, author, repository, environment, and scenario-group
  disjointness;
- parser and canonicalization artifacts;
- target labels derivable from metadata or deterministic task structure;
- completed-output, later-action, verifier, or replay information unavailable at
  the prospective boundary.

A model that predicts the diagnostic family, evidence polarity, or familiar
wording without resolving the target has not passed this gate.

## Multiple objective targets in agent systems

For Agents-A1 and comparable agents, the phrase `error prediction` is
inadmissibly broad unless the target is specified. The following are separate
outcomes and require separate labels, baselines, calibration, and sealed results:

1. syntactic or schema validity of the next action;
2. agreement with the model’s later emitted action;
3. policy acceptability of the proposed action;
4. tool-call execution success;
5. correctness and freshness of the returned observation;
6. correctness of the environment-state interpretation;
7. progress toward the current subgoal;
8. final task success;
9. violation of a safety, privacy, permission, or side-effect constraint;
10. recoverability through retry or repair;
11. positive marginal utility from additional reasoning or tool use;
12. safe early termination under a frozen fallback policy.

A signal for one target may be irrelevant or inversely related to another. For
example, predicting the model’s next tool call does not establish that the call
is valid, safe, useful, or task-successful. Predicting a tool execution failure
does not establish final task failure when repair is available. Predicting final
failure does not establish that additional computation has positive marginal
utility.

No aggregate `error awareness`, `process quality`, `metacognition`, or
`workspace` label may collapse these outcomes unless a preregistered composition
rule and target-specific strata are also reported.

## Router-telemetry consequence

Router logits, margins, entropy, selected experts, mixture weights, transition
surprise, expert disagreement, and expert contribution may correlate with task,
evidence, or target identity without predicting the objective relation between
evidence and target.

Future MoE studies must therefore test router features under matched-evidence,
different-target groups and report whether router telemetry adds target-specific
objective value beyond:

- evidence and target text;
- logits, margins, entropy, and self-judgement;
- pointwise and relational hidden-state readouts;
- trajectory, memory, parser, program-state, and verifier features;
- deterministic task, route, and runtime metadata.

A route difference between two target prompts does not establish expert
specialization for causal reasoning. A stable route under changed targets does
not establish target blindness without checking dense residual, attention,
shared-expert, and later-state representations.

## Jacobian-Lens consequence

A Jacobian-Lens readout is target-conditioned through its prompt, source state,
transport map, decoder, vocabulary, and evaluation objective. It may not be
reported as a generic correctness or error lens.

Future work must distinguish:

1. sensitivity to the evidence representation;
2. sensitivity to the target representation;
3. sensitivity to their interaction;
4. output-token or answer-option rank;
5. target-conditioned relation classification;
6. objective verifier outcome;
7. marginal utility of additional computation;
8. intervention effect under a separately admitted write or control policy.

Required controls include matched evidence with changed targets, matched targets
with changed evidence, evidence-only and target-only residualization, lexical
and option-logit comparators, source-position controls, route-preserving and
route-changing strata, and exact forward/VJP/JVP/finite-difference parity.

A transported vector that ranks the model’s later answer token highly does not
establish that the evidence bears correctly on the target. A Jacobian feature
that predicts one target outcome does not transfer to another target without
prospective evidence. A readable target-conditioned direction is not a writable
success direction.

## Early-exit, truncation, retry, and repair consequence

A stopping or repair policy requires a target beyond predicted failure.

For each candidate decision boundary, separately estimate:

- probability of objective success under immediate stop;
- probability of objective success under ordinary continuation;
- probability of objective success under retry or repair;
- incremental verifier-backed utility of each alternative;
- complete compute, latency, memory, tool, and side-effect cost;
- failure severity and fallback availability.

A monitor that predicts final failure but cannot distinguish irrecoverable
failure from repairable failure is not an early-exit policy. A monitor that
predicts low confidence but not counterfactual continuation utility is not a
compute-allocation policy. Target-conditioned prediction remains observation-only
until a separately preregistered intervention study passes.

## Agents-A1 scaling consequence

After all existing Q35Q gates pass, the minimum credible Agents-A1 sequence is:

1. Admit Agents-A1-4B under an immutable checkpoint, tokenizer, prompt and tool
   templates, parser, hybrid-state implementation, cache path, harness, verifier,
   environment snapshot, and runtime.
2. Define strict pre-answer and pre-action boundaries for natural text, code,
   tool use, and long-horizon trajectories.
3. Freeze a target registry separating action validity, action agreement, policy
   acceptability, tool success, observation correctness, subgoal progress, final
   task success, prohibited side effects, repairability, continuation utility,
   and safe stopping.
4. Establish evidence-only, target-only, full-text, logit, confidence, entropy,
   self-judgement, pointwise, relational, trajectory, memory, parser,
   program-state, peer-model, and verifier baselines.
5. Construct source-group-disjoint matched-evidence, different-target suites and
   require complete-group recovery rather than row accuracy alone.
6. Establish passive target-conditioned prediction on Agents-A1-4B before any
   steering, retry, repair, early exit, branch allocation, or adaptation study.
7. Separately admit Agents-A1-35B quantization, router, dispatch, expert order,
   mixture weights, routed and shared experts, hybrid recurrent state, cache,
   kernels, topology, batching, scheduler, capture path, parser, tool harness,
   and verifier.
8. Refit or revalidate every target-conditioned readout under native
   Agents-A1-35B route, state, and long-context conditions.
9. Require router telemetry to add sealed target-specific objective value beyond
   the complete cheaper comparator stack.
10. Add Jacobian features only after exact derivative parity and require sealed
    incremental value for each target separately.
11. Study early exit, retry, repair, adaptive routing, or depth allocation only
    under separate counterfactual-utility protocols with full-compute fallback.
12. Keep external side effects, irreversible actions, production gating, and
    deployment authorization separate from monitor accuracy.

The new causal-target benchmark is a methodological comparator, not a transfer
bridge. Agents-A1 requires native target definitions, native runtime admission,
native trajectories, native verifier semantics, and native sealed evidence.

## Active blocker and execution order

The active blocker remains exact-target-runtime Q35Q admission:

1. execute the composed Transformers provenance adapter in the exact target
   runtime;
2. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple;
3. bind the actual GPTQModel/Defuser loader and complete executable source
   closure;
4. run strict synthetic Qwen3.5-MoE loading;
5. prove one-time packed-tensor consumption;
6. prove exact expert and fusion ordering;
7. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity;
8. pass the complete Phase-0 conjunction before weight staging or any authorized
   GPU transition.

This addendum resolves none of those gates and does not change their priority.

## Established

From the reviewed primary sources and current repository state:

- remote jLens engineering and operational status did not advance before this
  protocol review;
- evidence and target identity are separate scientific objects;
- unchanged evidence can require different labels when population, outcome,
  estimand, pathway, horizon, or assumptions change;
- row accuracy can overstate target-sensitive performance when paired or grouped
  target recovery is low;
- `Wrong Target` and `Unresolved` are distinct outcomes;
- a hidden-state readout can add reported value beyond answer-option logits and
  text baselines under the tested models and benchmark;
- a monitor must be calibrated and evaluated for a specific target rather than
  relabeled as generic error awareness;
- router and Jacobian features require matched-evidence, different-target
  controls and target-specific incremental value;
- prediction, counterfactual utility, intervention, and production control remain
  separate claims;
- no existing privacy, sealed-data, verifier, provenance, derivative, GPU,
  intervention, or production gate is weakened;
- Q35Q remains blocked.

## Unproven

- independent reproduction of arXiv `2607.26929v1`;
- immutable admission of implementation, benchmark data, model revisions, and
  dependency closure;
- robustness across additional seeds, target templates, diagnostic families,
  domains, languages, models, layers, positions, and runtimes;
- causal or model-native use of the decoded target relation;
- a general correctness variable, error-awareness state, semantic workspace,
  metacognitive state, or introspective self-access;
- transfer to Qwen3.5, Qwen3.6, Agents-A1, architectural MoEs, or long-horizon
  tool-use agents;
- target-specific incremental router or Jacobian-Lens value over transparent,
  text, logit, hidden-state, relational, trajectory, and verifier comparators;
- positive counterfactual utility from additional reasoning, retry, repair,
  routing changes, or depth changes;
- complete Q35Q loader, tensor-consumption, ordering, forward, and derivative
  admission;
- safe early exit, truncation, retry, repair, branch control, adaptive or forced
  routing, activation steering, cache rewriting, external action, or production
  deployment.

The research program is not finished.
