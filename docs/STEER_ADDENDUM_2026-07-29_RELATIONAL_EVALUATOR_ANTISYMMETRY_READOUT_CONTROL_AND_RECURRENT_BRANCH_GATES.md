# Steering Addendum — Relational Evaluator Antisymmetry, Readout–Control, and Recurrent-Branch Gates

Date: 2026-07-29

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `b61ce5385f7bc106f10fbbfd4e984513475212ec`

## Scope and inherited restrictions

This addendum applies to every future pairwise or listwise hidden-state evaluator,
candidate selector, branch-retention score, strict pre-answer outcome probe,
selective-prediction policy, recurrent-depth allocation rule, semantic-workspace
claim, router-telemetry comparator, Jacobian-Lens readout, or Agents-A1 branch or
control experiment.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No model-weight staging, tensor-payload
retrieval, model execution, GPU execution, hidden-state capture, route capture,
cache capture, JVP, VJP, Jacobian fitting, sealed scientific evaluation,
intervention, or production use is authorized by this document.

Every existing privacy, sealed-data, canonical-verifier, provenance,
exact-set, exact-gradient, parity, nuisance-control, multiplicity,
resource-accounting, cleanup, commit-safety, intervention, and production gate
remains binding.

GitHub reports this repository as public. Only aggregate public-source program
control is recorded here. Prompts, continuations, candidate pairs, token IDs,
per-example scores, verifier labels, hidden states, router arrays, expert paths,
KV caches, residual streams, Jacobians, gradients, model weights, credentials,
host paths, private runtime facts, and sealed outcomes remain prohibited from
this repository.

## New primary evidence

Kirin, “Operational Proto-Introspection in Looped Language Models:
Process-Quality Taps, Executable Branching, and the Readout–Control Boundary,”
arXiv `2607.18553v3`, revised 2026-07-28, studies a frozen 2.6B looped
transformer, Ouro-RLTT.

The reported strict pre-answer study excludes the answer region and gold value.
On GSM8K, hidden states combined with length and log-probability shortcuts reach
AUROC 0.797 versus 0.731 for the shortcut-only baseline, an incremental 0.066
with a task-clustered confidence interval. A Horizon Logic extension reports an
incremental result on a task-disjoint population and an independent new cohort.
The paper also reports selective-prediction and terminal-selection gains under
its corrected protocol.

The same paper reports a clear readout–control separation. Directional steering,
a bounded branch screen, exact-compute loop allocation, and minimal LoRA
direction binding do not produce a validated generative capability gain. A
readable process-quality direction is therefore not automatically a writable
control direction.

The paper's executable substrate uses branch-specific lineage over a 192-slot
loop-by-layer recurrent cache. It reports bit-exact branch/carry/prune checks and
a residual-capture suffix splice that recomputes only the affected suffix.

The primary methodological correction is material to jLens. Earlier relational
figures were inflated by two defects:

1. source-item leakage across evaluation partitions; and
2. a canonical presentation-order prior in a pairwise evaluator.

Under corrected source-item-disjoint and antisymmetrized evaluation, the
relational advantage remains positive but is much smaller. The associated
public implementation and paper repository is pinned for this review at
`VykosMolt/Branching-Looped-Transformer@cb174efd8ae9797b2f3f0e25aa0c8a6098b197fc`.
The upstream revision series explicitly corrects selective-prediction wording,
overclaims, loop indexing, and evaluation inconsistencies.

The binding interpretation is narrow:

1. Hidden states can contain prospectively useful outcome information under the
   reported model, task, cut, probe, and evaluation conditions.
2. Relational readouts can add value beyond pointwise readouts, but the reported
   premium is modest after correction.
3. Decision-level conversion through abstention or candidate selection is not
   generative control.
4. Readability does not establish causal use by the model, introspective
   self-access, semantic-workspace status, or a writable success direction.
5. Recurrent cache machinery can make branch experiments executable without
   establishing that the branch policy improves objective outcomes.
6. The evidence does not establish transfer to Qwen3.5, Qwen3.6, Agents-A1,
   architectural MoEs, tool-use agents, long-horizon environments, or
   production control.

## Required object separation

Every compatible study must bind these objects separately:

1. **Source item:** the underlying task, prompt, environment, repository,
   question, or paired preference item from which examples are derived.
2. **Candidate identity:** the exact continuation, branch, state lineage, parser
   result, and verifier target represented by each item in a comparison.
3. **Pointwise representation:** the state or feature extracted from one
   candidate without its comparison partner.
4. **Ordered pair representation:** the feature supplied for candidate A before
   candidate B, including subtraction or concatenation order.
5. **Swapped pair representation:** the feature supplied for candidate B before
   candidate A.
6. **Raw ordered score:** the evaluator output for the ordered pair `(A, B)`.
7. **Raw swapped score:** the evaluator output for `(B, A)`.
8. **Antisymmetrized score:** the frozen combination that removes an order-only
   component, ordinarily `(s(A,B) - s(B,A)) / 2` when mathematically compatible.
9. **Pointwise score:** the independently fitted score for one candidate.
10. **Pairwise decision:** the candidate preferred by the admitted relational
    evaluator.
11. **Branch-survival policy:** the rule deciding which candidates remain in a
    pool without committing to one final answer.
12. **Terminal-selection policy:** the rule committing to one candidate.
13. **Selective-prediction policy:** the rule retaining, abstaining, escalating,
    or deferring an entire task.
14. **Generative intervention:** steering, branch injection, recurrent-depth
    allocation, route editing, activation writing, fine-tuning, or another
    operation that changes the produced trajectory.
15. **Objective outcome:** the independent canonical verifier result.
16. **Complete cost:** all candidate generation, representation extraction,
    evaluator, branch, cache, verifier, fallback, and intervention cost.

No one object may be relabeled as another. In particular, branch survival is not
terminal correctness, pairwise preference is not objective correctness,
selective-prediction utility is not generative improvement, and a readable
vector is not a writable control vector.

## Source-item and lineage-disjoint split gate

Row-level random splitting is insufficient whenever multiple rows share an
underlying task, candidate, prompt, source pair, environment, repository,
template, generated sibling, verifier artifact, or recurrent ancestor.

Before fitting or selection, freeze the independent source-item unit and keep
all descendants of that unit in one partition. This includes:

- both orders of a pair;
- all candidates from one task or prompt;
- paraphrases and formatting variants;
- positive and negative siblings;
- retries, branches, and sampled continuations;
- cache-derived or recurrent-depth views of the same trajectory;
- multiple layers, loops, positions, and pooling variants;
- all verifier renderings or parser-normalized copies;
- all examples sharing a repository, base commit, user, environment snapshot,
  or tool state when that shared structure can leak the label.

Feature selection, layer selection, probe fitting, regularization, calibration,
threshold selection, pair construction, and policy selection must occur without
sealed source-item labels. Confidence intervals and hypothesis tests must be
clustered by the true independent source unit.

Any result produced with source-item leakage is invalidated, not merely
qualified. Re-running the metric on a corrected split creates a new result.

## Relational-evaluator antisymmetry and order gate

Every pairwise evaluator must be audited in both presentation orders.
Fixed-order accuracy alone is inadmissible.

For every held-out pair, report at minimum:

- `s(A,B)` and `s(B,A)` in private evaluation artifacts;
- antisymmetry residual `s(A,B) + s(B,A)` when the intended relation is
  antisymmetric;
- the antisymmetrized decision score;
- accuracy in the canonical order;
- accuracy in the swapped order;
- flip consistency under order reversal;
- the fraction of decisions unchanged when only presentation order changes;
- score offset and variance attributable to order;
- pointwise and relational performance under the same source-item split;
- the relational-minus-pointwise premium with source-clustered uncertainty.

Mandatory controls include:

1. randomized presentation order;
2. complete order reversal;
3. candidate-label and display-label permutations;
4. identical-candidate pairs as a null;
5. random candidate pairing with matched length and format;
6. matched lexical and parser-format controls;
7. a no-bias or explicitly antisymmetric evaluator when technically compatible;
8. an evaluator trained with one order distribution and tested on another;
9. source-item-disjoint evaluation of every pair order;
10. a shortcut-only comparator using length, log-probability, format,
    well-formedness, and other transparent features.

Concatenation-based nonlinear evaluators require special scrutiny because they
can learn position-specific priors. A high fixed-order score that collapses
under swapping or antisymmetrization is an order artifact, not relational
knowledge.

Antisymmetrization can reduce a valid asymmetric task signal when the target
relation is not actually antisymmetric. The target relation must therefore be
frozen first. Do not impose antisymmetry on causal direction, temporal order,
entailment direction, containment, or another genuinely asymmetric relation
without a separate justification.

## Strict pre-answer and pre-action boundary

A strict pre-answer or pre-action monitor must prove that its information set
ends before the target event is realized.

Freeze and verify:

- the exact token, layer, loop, route, and cache cut;
- whether the cut is during prefill or decode;
- the answer-region detector and exclusion rule;
- treatment of delimiters, scratchpad endings, parser markers, and tool-call
  prefixes;
- exclusion of gold values, verifier outputs, future tokens, terminal formatting,
  future cache entries, and replay-derived state;
- the target event and horizon at the cut;
- malformed, empty, truncated, abstaining, and parser-error outcomes;
- all shortcut features available at the same boundary.

Required adversarial controls include answer-value aliases, obfuscated answers,
malformed siblings, equivalent formatting, equal-length candidates, shuffled
scratchpad boundaries, content-free terminal markers, and tasks where a correct
answer is not yet realized despite high confidence.

A code comment or nominal hook name is not evidence that the answer region was
excluded. The executed indexing and data-flow path must be tested.

## Decision-level conversion versus generative control

Evidence for any of the following is decision-level only:

- risk-coverage improvement;
- abstention or escalation;
- candidate ranking;
- branch retention;
- terminal selection;
- malformed-output rejection;
- review prioritization.

It does not authorize or support claims about:

- directional activation steering;
- branch-state injection;
- recurrent-depth allocation;
- early termination of reasoning;
- route or expert editing;
- cache rewriting;
- retry or repair generation;
- fine-tuning or reinforcement learning;
- production control.

Every control method creates a separately admitted executable condition. A
positive passive or decision-level result and a negative generative-control
result must both be recorded. Do not average them into a single “actionability”
claim.

A selector may improve outcomes primarily by detecting malformed or
non-executable candidates. Report all-well-formed and all-parser-valid strata
separately before claiming content-sensitive selection.

## Branch survival, terminal selection, and oracle-presence gate

Branch survival and terminal commitment answer different questions.

A branch-retention study must report:

- oracle-present groups and oracle-absent groups separately;
- oracle retention at every pool size;
- pool purity and survivor count;
- random and transparent-shortcut retention at matched pool size;
- whether the retained oracle is later selected;
- whether the retained candidate is executable and verifier-correct;
- total generation and retention cost.

A terminal-selection study must report:

- candidate-pool construction and generation policy;
- number of well-formed and malformed candidates;
- random matched-pool expectation;
- best-of-N or oracle-selection upper bound where available;
- shortcut-only and pointwise selectors;
- relational selector;
- exact ties and abstentions;
- final objective outcome and regressions.

High oracle retention does not establish successful terminal choice. Successful
terminal choice in pools dominated by malformed alternatives does not establish
substantive correctness discrimination.

## Recurrent-state and cache-lineage identity

For looped, recurrent, hybrid-attention, or cache-manipulating systems, freeze:

- physical layer index;
- recurrent or loop iteration;
- logical depth;
- token position;
- source residual boundary;
- cache slot and tensor schema;
- carried versus recomputed state;
- branch parent and complete ancestry;
- prune and reorder history;
- batching and branch packing;
- precision, kernels, placement, and deterministic settings;
- prefix reuse and suffix-recompute boundary;
- parser, verifier, and environment state attached to the branch.

A state at physical layer `l` on loop `u` is not interchangeable with the same
physical layer on another loop. A branch with copied cache entries is not the
same branch if its residual boundary, recurrent state, route history, or
environment lineage differs.

Before any branch result is scientific evidence, require zero-perturbation
identity and branch isolation across:

1. ordinary reference execution;
2. fork with no perturbation;
3. batched and unbatched execution;
4. prune and reorder;
5. prefix carry;
6. suffix recomputation;
7. cache eviction or reconstruction;
8. restart and resumed execution;
9. concurrent branches;
10. a negative control where required carried state is withheld and divergence
    is detected.

“Bit-exact” must specify the compared tensors, runtime, precision, kernel,
topology, and tolerance. Exactness in one runtime does not transfer to another.

## Recurrent-depth and compute-allocation gate

A recurrent-depth policy changes the executed model and is an intervention.

Compare it against:

- native fixed depth;
- fixed shallower and deeper schedules;
- random allocation with the same per-example depth histogram;
- random allocation with the same total layer passes;
- confidence-only and shortcut-only allocation;
- a matched-compute best-of-N or sampling policy;
- an oracle allocation upper bound when definable;
- full-compute fallback.

Report exact layer passes, recurrent iterations, cache operations, branch count,
memory traffic, kernel launches, latency distribution, throughput, peak memory,
and verifier cost. Mean nominal depth is not compute matching.

A score that predicts outcome does not establish that spending more depth on a
high-risk example improves that example. Allocation requires a counterfactual
marginal-utility study: the same task must be evaluated under prospectively
frozen depth alternatives without using sealed outcomes to choose the policy.

A smooth Jacobian at fixed recurrent depth does not represent the discrete
effect of adding or removing an iteration. Derivative studies must separate
fixed-depth local perturbations from depth-boundary counterfactuals.

## Readout geometry and semantic-workspace restriction

A layer, loop, route, cache slot, or subspace may not be called a semantic hub,
global workspace, metacognitive state, introspective channel, or causal
bottleneck from probe accuracy, early readability, recurrent refinement,
transplant correlation, branch survival, or selector performance alone.

Such claims require separately frozen evidence for:

- model-native use of the representation;
- causal necessity and sufficiency under executed interventions;
- matched nuisance and shortcut controls;
- multiple seeds, domains, checkpoints, and architectures;
- pointwise, peer-model, relational, router, trajectory, and Jacobian comparators;
- independently verified objective effects;
- robustness to source-item, order, parser, and boundary controls.

Coordinate stability across loops is distinct from information readability.
Cross-loop transplant success does not prove semantic identity, and transplant
failure does not prove information absence.

## Jacobian-Lens consequence

Future Jacobian-Lens work must distinguish:

1. pointwise residual-to-output sensitivity;
2. pairwise difference sensitivity;
3. ordered-pair evaluator sensitivity;
4. antisymmetrized relational sensitivity;
5. fixed-route and fixed-depth derivatives;
6. route-, branch-, and depth-boundary counterfactuals;
7. passive prediction;
8. selection-policy utility;
9. written-state intervention effects.

A Jacobian that predicts which of two candidates will be preferred does not
establish which candidate is objectively correct. A direction aligned with an
outcome readout does not establish that writing along the direction improves the
outcome. Any writeback requires independent forward, VJP, JVP, finite-difference,
state-lineage, route, cache, and verifier admission.

## Agents-A1 scaling consequence

After all existing Q35Q gates pass, the minimum credible Agents-A1 sequence is:

1. Admit Agents-A1-4B under an immutable checkpoint, tokenizer, template,
   parser, hybrid-state implementation, cache path, harness, verifier, and
   runtime.
2. Define strict pre-answer and pre-action cuts for natural text, code, tool use,
   and agent trajectories.
3. Establish transparent metadata, length, format, logits, confidence, entropy,
   self-judgement, pointwise hidden-state, peer-model, trajectory, memory,
   program-state, and verifier baselines.
4. Build source-item-disjoint candidate groups while keeping all siblings,
   branches, layers, recurrent views, and pair orders in one split.
5. Evaluate relational readouts only with complete order reversal,
   antisymmetrization, identical-pair nulls, shortcut controls, and
   task-clustered uncertainty.
6. Evaluate passive outcome prediction, selective prediction, branch survival,
   and terminal selection as separate claims.
7. Require all-well-formed and parser-valid candidate-pool controls.
8. Keep steering, branch injection, recurrent-depth allocation, retry, repair,
   early exit, and cache rewriting prohibited during observation-only work.
9. Separately admit Agents-A1-35B quantization, router, dispatch, expert order,
   mixture weights, routed and shared experts, hybrid recurrent state, cache,
   kernels, topology, batching, scheduler, and capture path.
10. Refit or revalidate all pointwise and relational readouts under native
    Agents-A1-35B route and state conditions.
11. Require router telemetry to add sealed completed-error value beyond the
    complete transparent, peer, pointwise, relational, and trajectory stack.
12. Add Jacobian features only after exact derivative parity and require sealed
    incremental value over every cheaper comparator.
13. Study recurrent-depth or branch allocation only under a separate
    intervention preregistration with exact compute matching and full-compute
    fallback.
14. Keep production action, early exit, routing changes, external side effects,
    and irreversible decisions separately gated.

The looped-transformer paper is a methodological comparator, not a transfer
bridge. Agents-A1's architecture, training, routes, state lineage, tool harness,
and outcome distribution require native admission and native evidence.

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

From the reviewed primary source and immutable upstream revision:

- a strict pre-answer hidden-state score can add reported outcome-prediction
  value beyond length and log-probability shortcuts in the tested model and
  domains;
- source-item leakage can materially inflate evaluator results;
- fixed presentation order can materially inflate pairwise nonlinear results;
- antisymmetrized, source-item-disjoint evaluation is required for relational
  claims;
- corrected relational value can remain positive while being far smaller than
  the uncorrected estimate;
- decision-level selective prediction or selection can succeed without a
  validated generative-control gain;
- readable outcome directions are not thereby writable success directions;
- branch/carry/prune and suffix-recompute machinery require explicit state and
  cache lineage plus identity checks;
- recurrent-depth allocation must be exact-compute matched;
- no existing privacy, sealed-data, verifier, provenance, derivative, GPU,
  intervention, or production gate is weakened;
- Q35Q remains blocked.

## Unproven

- independent reproduction of arXiv `2607.18553v3`;
- robustness across additional seeds, domains, models, model sizes, and runtime
  implementations;
- general strict pre-answer correctness awareness;
- causal or model-native use of the readable signal;
- a semantic workspace, metacognitive state, or introspective self-access;
- a general substantive terminal-selection gain;
- generative benefit from steering, branch injection, recurrent-depth
  allocation, route editing, or light adaptation;
- transfer to Qwen3.5, Qwen3.6, Agents-A1, architectural MoEs, or long-horizon
  tool-use agents;
- incremental router or Jacobian-Lens value over transparent, peer,
  pointwise, relational, and trajectory comparators;
- complete Q35Q loader, tensor-consumption, ordering, forward, and derivative
  admission;
- safe early exit, truncation, retry, repair, branch control, forced routing,
  activation steering, cache rewriting, or production deployment.

The research program is not finished.
