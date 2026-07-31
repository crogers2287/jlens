# STEER ADDENDUM — Decision-Scope, Evidence-Scope, Candidate-Identity, and Commit-Hierarchy Gates

Date: 2026-07-31
Parent remote head: `d0f53e73d939a983cabbe97a5dcbfa40443796bd`

Status: binding future-protocol correction; no current execution authorization.

This addendum is cumulative with `CODEX_AUTOSTEER.md`, `steer.md`, and every later binding correction. It preserves every privacy, sealed-data, canonical-verifier, provenance, exact-set, exact-gradient, parity, nuisance-control, multiplicity, resource-accounting, cleanup, intervention, and production-gating rule.

It does not constitute Q35Q admission, authorize model-weight staging, tensor-payload retrieval, GPU execution, hidden-state capture, router capture, expert-path capture, cache capture, JVP, VJP, Jacobian fitting, sealed evaluation, early exit, truncation, retry, repair, tool suppression, external action, or production use.

GitHub reports this repository as public. Only aggregate public-source program control may be recorded here. Prompts, completions, benchmark items, target values, per-example candidate spans, parser traces, token IDs, hidden states, routes, expert paths, caches, Jacobians, gradients, verifier labels, private runtime facts, credentials, and sealed outcomes remain prohibited.

## Primary external evidence

Lee et al., “Where and When to Commit: Candidate-Aware Decoding for Diffusion Language Models,” arXiv `2607.28166v1`, submitted 2026-07-30, separates two inference-time control axes that are often pooled:

1. **where to accelerate:** local position or block commitment while decoding continues; and
2. **when to stop:** global sequence termination that freezes every remaining unresolved position.

The paper introduces:

- **Confidence-Verified Commit (CVC):** global termination requires confidence plus sustained argmax stability over a dynamically extracted candidate-answer span;
- **Block-Wise Early Commit (BWEC):** a cheaper confidence rule may accelerate non-final blocks while leaving the final block and global stop under CVC; and
- **LATCH:** the combination of one scope-matched gate per control axis.

The authors report evaluation on 11 zero-shot tasks across LLaDA and Dream, with one frozen hyperparameter setting. The reported results remain within 2.0 percentage points of full-decoding accuracy in 22 model-task settings while obtaining 9.3–17.8x end-to-end throughput speedups on short-answer tasks and 2.0–3.3x on long-reasoning tasks.

The paper’s key diagnostic is narrower and more general than its system result: candidate stabilization is strongly task-dependent, and a fixed-region or position-aggregated confidence statistic can appear stable before the answer candidate itself stops changing. The paper explicitly classifies candidate stability as a convergence diagnostic rather than correctness.

Primary source:

- https://arxiv.org/abs/2607.28166v1

The arXiv record links `https://github.com/ming053l/LATCH-dLLM`, but that repository returned not found during this review. No immutable attributable implementation revision, environment lock, result artifact, or independent reproduction was admitted. The evidence is paper-level only.

## Binding interpretation

The new evidence supports the following bounded correction:

> Evidence may authorize only a decision whose scope is no broader than the scope directly observed and prospectively validated by that evidence.

A local token, position, layer, block, route, expert, candidate, or short-window statistic may support a local scheduling or observation claim. It may not be promoted directly into sequence termination, final-answer commitment, tool suppression, episode termination, irreversible action, or production enforcement.

The following objects are distinct and may not be renamed into one another:

1. position-level confidence or stability;
2. token-level commitment;
3. block- or layer-level advancement;
4. candidate-answer identity;
5. candidate-answer stability;
6. sequence-level completion;
7. objective answer correctness;
8. continuation utility;
9. tool-call or action readiness;
10. episode-level success;
11. safety or policy acceptability;
12. production authorization.

Candidate stability is not correctness. Correctness is not proof that stopping was utility-optimal. Utility-optimal stopping is not safety. Safe termination in a replay benchmark is not authorization for an irreversible external action.

## Commit-hierarchy identity gate

Every future early-exit, truncation, adaptive-depth, speculative, recurrent, route-aware, hidden-state, semantic-workspace, or Jacobian-based controller must bind the exact decision hierarchy.

At minimum, identify separately:

- **micro-commit:** one token, masked position, expert transfer, expert execution, cache entry, or local state update;
- **stage commit:** one decoding block, model layer range, recurrent cycle, reasoning segment, tool-planning stage, or subagent stage;
- **candidate commit:** one parsed answer, action proposal, tool call, or structured output candidate;
- **sequence commit:** final generated response or answer termination;
- **episode commit:** no further retrieval, tool use, memory access, retry, repair, delegation, or environment observation;
- **external-action commit:** an action whose effects leave the replayable model boundary; and
- **production-policy commit:** enforcement, blocking, routing, escalation, or actuation in a live system.

For each level, freeze:

- exact consumer and executed boundary;
- decision time and available information state;
- candidate set and unresolved alternatives;
- reversibility and fallback behavior;
- downstream computation skipped or changed;
- complete compute, latency, memory, transfer, and verifier consequences; and
- independently verified objective and failure event.

A controller evaluated only at one level is admitted only at that level.

## Evidence-scope sufficiency gate

A decision may proceed only when the evidence scope covers every object materially frozen by that decision.

Future compatible studies must report:

1. the spatial scope observed: token, span, block, layer, route, expert path, full sequence, full trajectory, or environment;
2. the temporal scope observed: instantaneous, fixed window, recurrent history, complete episode, or cross-episode state;
3. the semantic scope observed: raw state, parsed candidate, action candidate, objective target, verifier event, or policy event;
4. the state omitted from the monitor but affected by the decision;
5. whether omitted state can still change the candidate, route, answer, tool decision, verifier outcome, or environment result; and
6. a prospectively validated aggregation rule when local evidence is combined into a broader decision.

The following promotions are prohibited without separate prospective validation:

- position confidence to sequence termination;
- layer convergence to answer completion;
- route stability to reasoning completion;
- expert-path repetition to correctness;
- hidden-state similarity to safe stopping;
- candidate-answer stability to objective correctness;
- objective correctness on the current artifact to no further tool or environment utility;
- parser-valid output to action validity;
- action validity to safety; and
- replay safety to production authorization.

When evidence does not cover the full decision scope, the system must continue through the admitted full-compute or independently verified path.

## Candidate-identity and parser gate

Any controller claiming candidate-aware stopping must bind candidate identity as an executable artifact.

Freeze at minimum:

- deterministic parser revision and digest;
- task-format assumptions and search region;
- candidate normalization and equivalence rules;
- token-span localization and relocation behavior;
- handling of multiple candidates;
- handling of missing, malformed, ambiguous, or contradictory candidates;
- confidence aggregation over multi-token candidates;
- stability counter, flip counter, patience, threshold, minimum observations, and tie behavior;
- treatment of formatting-only changes;
- verifier and accepted-answer multiplicity; and
- failure behavior outside parser support.

Required controls include:

- raw-token identity versus normalized-candidate identity;
- fixed-region monitoring versus dynamic candidate relocation;
- parser-free global statistics;
- wrong-region and decoy-candidate controls;
- candidate extraction failures counted as failures or prospectively frozen outcomes;
- answer-format and presentation-order perturbations;
- candidate stability on wrong trajectories;
- candidate instability on correct trajectories; and
- external-verifier comparison where available.

A parser may make a controller format-aware. It does not make the controller task-understanding, correctness-aware, model-native, or semantically complete.

## Where-versus-when gate

Local acceleration and global termination must be evaluated as separate interventions.

For every compatible controller, report independently:

- local commitments made while computation continues;
- stages skipped because local evidence declared them complete;
- global stops that terminate all remaining computation;
- downstream candidate changes that would have occurred without the stop;
- objective outcome changes attributable to local acceleration;
- objective outcome changes attributable to global termination;
- interaction between the two interventions; and
- complete cost and quality of each component alone and together.

A safe local commitment does not validate global stopping. A safe global stopping rule does not validate every local scheduling optimization. Gains from the combined system may not be attributed to either component without component ablation.

## Mandatory comparators and outcomes

Where technically compatible, future studies must include:

- no-intervention full-compute execution;
- fixed-budget policies at multiple depths, cycles, blocks, or token budgets;
- random stopping matched to the learned controller’s stop distribution;
- prompt length, task family, elapsed progress, and difficulty heuristics;
- same-boundary logits, entropy, margin, confidence, and self-verdict;
- candidate-identity persistence and candidate-confidence baselines;
- raw hidden-state, direct-lens, route, expert-path, and state-change baselines;
- external-verifier continuation or stopping;
- repeated sampling or self-consistency at equal complete cost;
- retry and repair policies at equal complete cost; and
- native full-compute fallback.

Report separately:

1. parser validity;
2. candidate stability;
3. agreement with the full-compute candidate;
4. objective correctness;
5. continuation utility;
6. tool and environment success;
7. premature-stop rate;
8. unnecessary-continuation rate;
9. false-alarm and missed-event rates;
10. tail failures and irreversible-action cases;
11. expected and worst-case compute, latency, memory, and transfers; and
12. fallback frequency and fallback success.

Average accuracy within a tolerance is insufficient by itself. Averages may hide task-family, horizon, parser, rare-event, or irreversible-action failures.

## Autoregressive and agent boundary

The paper evaluates diffusion-language-model denoising. Its reported speedups and thresholds do not transfer to autoregressive Agents-A1, Qwen3.5, Qwen3.6, or comparable MoEs.

For autoregressive reasoning and agents, the candidate and unresolved state may include:

- unfinished reasoning tokens;
- latent or recurrent state;
- unobserved tool results;
- pending environment changes;
- memory and retrieval opportunities;
- alternative action plans;
- subagent responses;
- parser-incomplete structured output;
- future verifier evidence; and
- safety or permission checks.

A stable visible answer may coexist with unresolved tool, memory, environment, policy, or action state. Future agent studies must therefore distinguish answer-candidate termination from episode termination and external-action authorization.

## MoE, router, and Jacobian boundary

For Agents-A1-35B or comparable MoEs, local router or expert evidence may not be promoted into a broader stopping decision without scope-matched validation.

Future compatible studies must separate:

- per-token router logits and top-k identities;
- layer-local route stability;
- cross-layer expert-path stability;
- recurrent or cross-turn route stability;
- candidate-answer stability;
- full trajectory and environment state;
- objective correctness and continuation utility; and
- action or episode termination.

A router signal that predicts local expert reuse may be useful for prefetch or scheduling while being useless for correctness or stopping. A Jacobian feature with large local sensitivity may identify where a representation can change while providing no evidence that the current candidate is complete, correct, safe, or ready for action.

Router, hidden-state, semantic-workspace, and Jacobian features must show sealed incremental value beyond candidate-aware, parser, trajectory, self-verdict, confidence, external-verifier, and equal-cost sampling controls for the exact decision level claimed.

## Agents-A1 scaling consequence

The technically credible sequence is now:

1. Complete Q35Q production-runtime provenance, exact loader admission, strict synthetic loading, one-time packed-tensor consumption, expert/fusion ordering, deterministic forward parity, activation-VJP parity, activation-JVP parity, and finite-difference parity.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, templates, parser, cache and recurrent state, tool harness, memory policy, environment, verifier, and runtime.
3. Define separate micro-, stage-, candidate-, sequence-, episode-, external-action-, and production-policy decisions.
4. Establish transparent parser, candidate-stability, confidence, self-verdict, trajectory, verifier, repeated-sampling, retry, and full-compute baselines.
5. Evaluate passive monitors only at the decision level their evidence directly covers.
6. Require prospectively validated aggregation before promoting token-, layer-, route-, or candidate-local evidence into sequence or episode stopping.
7. Keep initial work replayable, observation-only, production-disconnected, and free of irreversible external actions.
8. Separately admit Agents-A1-35B quantization, router transformations, shared and routed experts, expert reduction semantics, hybrid state, cache, kernels, topology, scheduler, telemetry, tools, memory, subagents, environment, and verifier.
9. Repeat the complete decision-scope audit under native 35B execution.
10. Require router and expert telemetry to add sealed objective value beyond the complete transparent candidate and trajectory comparator stack.
11. Add Jacobian features only after exact derivative parity and require separate incremental value for candidate stability, objective correctness, continuation utility, episode termination, and action readiness.
12. Preserve native full-compute execution and independently verified action checks as fallback.

## Intervention and production boundary

This addendum authorizes no controller intervention.

No early exit, truncation, block skipping, route editing, expert dropping, retry, repair, retrieval suppression, tool suppression, memory editing, cache rewriting, answer commitment, episode termination, external action, or production enforcement may be enabled from this evidence alone.

Intervention requires a separate preregistered artifact, exact runtime identity, sealed objective evaluation, tail-risk analysis, independent verifier, safe fallback, rollback, auditability, and explicit production authorization.

## Current engineering blocker remains unchanged

The active milestone remains complete production-path Q35Q provenance and runtime admission:

1. bind imported files to immutable distribution-ownership records;
2. derive complete executable-source closure from actual live runtime objects;
3. detect monkeypatching, shadow imports, and runtime substitution in a clean subprocess;
4. bind the exact GPTQModel/Defuser loader and conversion entry;
5. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` as one immutable tuple;
6. run strict synthetic Qwen3.5-MoE quantized loading;
7. prove one-time packed-tensor consumption;
8. prove exact expert and fusion ordering;
9. prove deterministic forward parity; and
10. prove activation-VJP, activation-JVP, and finite-difference parity.

No model-weight staging or GPU execution is authorized before the complete Phase-0 conjunction passes.

## Established by this correction

- Local acceleration and global termination are separate control axes.
- Evidence may authorize only decisions within its prospectively validated scope.
- Candidate identity and candidate stability require an exact parser and temporal policy.
- Candidate stability is not objective correctness, continuation utility, safety, or production readiness.
- Token-, layer-, route-, expert-, and candidate-local evidence cannot directly authorize episode termination or external action.
- Combined acceleration systems require component-level ablation and complete cost accounting.
- Diffusion-model results do not transfer automatically to autoregressive Agents-A1 or architectural MoEs.
- Existing privacy, sealed-data, verifier, provenance, derivative, intervention, and production gates remain intact.
- Q35Q remains blocked.

## Unproven

- Independent reproduction of arXiv `2607.28166v1`.
- Admission of its implementation, models, tasks, parser, hyperparameters, runtime, and result artifacts.
- Robustness under family-disjoint evaluation, parser shift, distribution shift, adversarial formats, long horizons, tool use, memory, subagents, or irreversible actions.
- Transfer from diffusion-language-model denoising to autoregressive decoding.
- Transfer to Qwen3.5, Qwen3.6, Agents-A1-4B, Agents-A1-35B, or comparable MoEs.
- Objective correctness, continuation-utility, or action-readiness value from candidate stability, router telemetry, hidden states, semantic-workspace features, or Jacobian features.
- Complete Q35Q runtime and derivative admission.
- Safe early exit, truncation, retry, repair, adaptive routing, expert dropping, cache rewriting, steering, external action, or production deployment.
