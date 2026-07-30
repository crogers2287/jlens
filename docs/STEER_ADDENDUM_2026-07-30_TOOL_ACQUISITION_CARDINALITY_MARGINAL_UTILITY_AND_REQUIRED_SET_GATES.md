# STEER ADDENDUM — Tool-acquisition cardinality, marginal utility, and required-set gates

Date: 2026-07-30
Parent remote head: `29f997f2277cf6e71ba67881cae0d226304688eb`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, cleanup, intervention, production-gating, and stop rule. It
authorizes no model retrieval, model execution, GPU use, telemetry capture,
Jacobian fitting, sealed evaluation, tool execution, external-state mutation,
early exit, retry, repair, adaptive routing, or production action.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains exact-target-runtime Q35Q loader and
derivative admission. This addendum changes future tool-catalog acquisition,
tool-selection, marginal-utility, privacy-cost, and Agents-A1 control studies.
It does not displace or advance the active milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and
public-source engineering material may be committed. Prompts, tool catalogs
from private deployments, tool descriptions, schemas, credentials, permissions,
arguments, results, outputs, user or tenant identifiers, per-example acquisition
sets, hidden states, routes, caches, Jacobians, sealed outcomes, host paths, and
private runtime facts remain prohibited.

## Triggering primary evidence

`Scores Are Not Decisions: Cost-Aware Stopping for Tool Acquisition in LLM
Agents`, arXiv `2607.27083v1`, studies tool acquisition as two distinct
problems:

1. rank candidate tools by estimated relevance; and
2. decide how many ranked tools to acquire under heterogeneous costs.

Its CAM-DF controller trains on an offline stop-versus-best-continuation payoff
gap, then deploys a stopping rule using features available at the current
acquisition prefix. The paper reports evaluation over 1,343 tasks from five
domains and, in its live retail condition, approximately 37 percent fewer tools
exposed while retaining similar reported task success.

The paper also makes the central limitation explicit: the training target uses
retrospective knowledge of the required-tool set and the best continuation,
whereas the deployed controller does not possess that information online.
Prospective application therefore depends on how required-tool labels are
constructed, whether multiple acceptable tool sets exist, and whether mined
trajectory tool sets are valid proxies for necessity.

No attributable immutable public implementation revision was admitted for this
correction. The described reproduction artifact is anonymized, and live reruns
require external benchmark setup and credentials.

## Bounded interpretation

The evidence supports this narrow correction:

> A tool ranker and a tool-acquisition stopping policy are separate executable
> objects. Relevance score, current-set sufficiency, marginal value of one more
> tool, required-tool membership, objective task success, privacy exposure, and
> production authorization must not be collapsed into one quantity.

The reported result does not establish:

- that the ranked prefix is the optimal subset under heterogeneous costs;
- that a tool used in a successful trajectory was necessary;
- that a labelled required set is unique or complete;
- that fewer acquired tools produce a proportional privacy-risk reduction;
- that read-tool restriction controls write or action tools still available to
  the agent;
- that the policy is robust to required-set label noise, policy drift, catalog
  drift, schema drift, or distribution shift;
- that internal hidden-state, router, expert, or Jacobian telemetry predicts
  tool utility;
- that a stopping score represents correctness, intent, planning, or a semantic
  workspace; or
- that the policy safely controls real external actions.

## Binding object-identity gate

Every future tool-acquisition study must freeze and report separately, where
they exist:

1. base model checkpoint and executable runtime;
2. tokenizer, chat template, reasoning parser, and tool-call parser;
3. full candidate tool catalog before ranking;
4. exact tool names, descriptions, schemas, revisions, and namespace rules;
5. permission, credential, tenant, and environment scope associated with each
   tool;
6. read-only, metered-read, reversible-write, confirmed-write, irreversible, or
   unknown side-effect classification;
7. tool ranker, scorer, prompt, checkpoint, and runtime;
8. raw tool scores and calibrated score semantics;
9. ranking order, tie handling, truncation, and deterministic ordering rules;
10. acquisition controller and its features at each decision boundary;
11. acquired prefix or subset at each step;
12. acquisition depth and stop decision;
13. per-tool cost vector and every scalarization weight;
14. required-tool or acceptable-set label source and revision;
15. offline oracle target, if used;
16. online deployed decision statistic;
17. committed tool registry made available to the agent;
18. tools actually invoked and their execution results;
19. final task output and independently verified outcome;
20. privacy, security, latency, token, monetary, memory, and provider-side cost;
   and
21. fallback policy and complete production-control identity.

A field named `relevance`, `utility`, `sufficiency`, `required`, `stop`,
`tools_exposed`, `privacy_saved`, or `task_success` does not satisfy this gate
without proving which object and boundary it represents.

## Required-set and retrospective-label gate

The required-tool set is ordinarily unavailable at the online acquisition
boundary. It may be used as a nonsealed training or evaluation label only when
its construction and limitations are explicit.

A tool appearing in a successful trajectory is not automatically:

- necessary;
- sufficient;
- minimally sufficient;
- part of every acceptable solution;
- the best tool under another cost vector; or
- evidence that an unused tool had zero marginal value.

Future studies must freeze:

- whether labels describe one minimal set, all acceptable sets, a union, an
  intersection, or a policy-generated trace;
- who or what produced the labels;
- adjudication and disagreement procedures;
- treatment of redundant, substitutable, complementary, and mutually exclusive
  tools;
- handling of tasks solvable with no tool;
- handling of multiple valid plans and tool orders;
- policy revision used to mine trajectory labels;
- train, calibration, validation, and sealed source-group partitions; and
- label regeneration after catalog, policy, schema, or environment changes.

Required controls include:

- exact human- or environment-verified acceptable sets where feasible;
- multiple acceptable-set evaluation;
- successful trajectories containing redundant tools;
- failed trajectories containing all nominally required tools;
- omitted-but-substitutable tools;
- wrong-tool but lucky-success cases;
- policy-mined versus independently adjudicated labels;
- random membership corruption and structured omission/addition noise; and
- sensitivity to label-source revision.

An offline best-continuation target is clairvoyant supervision. It is not an
online signal and may not enter deployed features at the earlier decision
boundary.

## Ranking versus acquisition-policy gate

A ranked list does not determine the optimal acquisition depth. A stopping
policy does not prove that the ranking is correct. A good ranking can support a
bad stopping policy, and a stopping policy can compensate for a weak ranking on
one workload without generalizing.

Future evaluations must compare, at minimum:

1. full catalog;
2. fixed top-k rules over a prospectively frozen grid;
3. fixed score threshold;
4. calibrated score threshold;
5. score-per-cost and other transparent cost-aware rules;
6. matched-cardinality random prefixes;
7. matched-cost random prefixes;
8. frequency, recency, domain, and policy-prior baselines;
9. ranker-only and controller-only ablations;
10. jointly trained ranker and controller;
11. an oracle over ranked prefixes;
12. an unconstrained subset oracle where computationally feasible; and
13. a no-tool condition.

All methods must use the same catalog, schema, permissions, model, parser,
verifier, workload, and cost accounting.

## Prefix restriction and subset-interaction gate

A policy that may only choose a prefix of one ranked list solves a restricted
problem. It does not establish optimal subset acquisition.

Tool utility can be:

- redundant;
- complementary;
- order-dependent;
- conditional on observations from another tool;
- non-monotone because an added tool can increase confusion or attack surface;
- affected by context-window competition; or
- altered by permissions and environment state.

Future claims must distinguish:

- best ranked prefix;
- best subset at the same cardinality;
- best subset at the same scalar cost;
- adaptive acquisition after observations;
- one-shot catalog restriction; and
- complete end-to-end agent policy.

When full subset search is infeasible, the restriction must remain visible.
Prefix-optimal may not be relabelled globally optimal.

## Cost-semantics and scalarization gate

Tool cost is multidimensional. At minimum, report separately:

- tool-description and schema tokens added to context;
- model prefill and decode cost;
- ranker and controller cost;
- latency and tail latency;
- monetary provider charges;
- API rate-limit and quota consumption;
- credential and permission exposure;
- private-data scope reachable through the tool;
- provider logging and audit exposure;
- prompt-injection and malicious-tool attack surface;
- parsing and validation burden;
- memory, cache, and network cost;
- downstream retries, repair, and failure cost; and
- external side effects from actual execution.

A scalar payoff is admissible only after every conversion weight, normalization,
and clipping rule is prospectively frozen. Results must also be reported in the
unaggregated dimensions.

Mean tool count is insufficient. Report the complete acquisition-depth and cost
distributions, tail cases, domain strata, task-success strata, and safety or
privacy regressions.

## Privacy-exposure gate

These are separate exposure events:

1. a tool description or schema is presented to the model;
2. a tool is registered as callable;
3. credentials or permission scope are attached;
4. a provider receives a request;
5. private input is transmitted;
6. a result is returned;
7. the model receives the result;
8. an external audit, billing, rate-limit, or abuse record is created; and
9. state is mutated.

A reduction in acquired catalog size does not establish an equal reduction in
privacy risk. Privacy claims require a frozen threat model and direct accounting
of which data, capabilities, credentials, providers, and side effects were
removed.

Aggregate counts may be committed publicly. Private catalog contents,
permissions, credentials, task-level exposure sets, and per-example privacy
outcomes may not be committed.

## Acquisition versus execution and side-effect gate

Tool acquisition, tool registration, tool invocation, result consumption, and
external-state mutation are separate actions.

A study that restricts only read tools while leaving write or action tools
available has not restricted the complete actionable tool surface. Every result
must report the registry available to the agent after acquisition and all tools
that remain callable outside the ranked or restricted set.

The existing self-speculating-tool-call side-effect gate remains binding.
Irreversible actions remain prohibited. Initial acquisition-policy experiments
must use replay, deterministic local tools, or explicitly allowlisted read-only
interfaces unless a separate transaction, rollback, confirmation, privacy, and
production protocol is admitted.

## Temporal and causal-availability gate

At each acquisition decision, every feature must be available without future
agent tokens, future tool observations, eventual tool usage, final verifier
outcome, or retrospective required-set knowledge.

Feature time, acquisition-decision time, tool-registration time, invocation
time, result-availability time, verifier time, and intervention time must remain
separate.

A second-pass or replay-based score may be studied as retrospective evidence but
may not be described as an online controller without an executable one-pass
path and matched end-to-end cost.

## Observation-only monitor boundary

CAM-DF-style acquisition control is a transparent policy comparator, not a
correctness monitor and not evidence of a semantic workspace.

Any hidden-state, router, expert, Jacobian, or workspace claim must demonstrate
sealed target-specific incremental objective value beyond:

- rank score and calibrated relevance;
- rank margin and rank entropy;
- acquisition depth and cumulative score mass;
- explicit per-tool costs;
- score-per-cost summaries;
- task, domain, catalog, and tool-frequency priors;
- prompt and trajectory length;
- parser and schema validity;
- previous tool actions and observations;
- current progress and finish metadata;
- direct model estimates of tool need;
- ordinary hidden-state and trajectory probes; and
- independent verifier features.

M39 and all current monitoring milestones remain observation-only. They may not
change the acquired catalog, register or remove tools, alter permissions, invoke
tools, stop reasoning, retry, repair, or mutate external state.

## Intervention and production gate

Using an acquisition controller to change the catalog available to an agent is
an intervention and creates a new executable policy condition.

Before any production claim, require:

- prospective source-group-disjoint calibration;
- sealed objective task and safety evaluation;
- explicit no-tool, missing-tool, wrong-tool, and malicious-tool cases;
- distribution-shift and catalog-drift evaluation;
- schema and permission drift evaluation;
- policy-update and model-update recalibration;
- tail-risk and irreversible-action analysis;
- fallback to the admitted full catalog or a prospectively safe minimal catalog;
- fail-closed behavior when labels, costs, permissions, or schemas are unknown;
- complete end-to-end cost accounting; and
- independent authorization under the production-control protocol.

Average reward or average tool-count reduction cannot authorize production when
material task, safety, privacy, or permission regressions remain.

## Agents-A1 scaling priority

The technically credible sequence is:

1. complete exact-target-runtime Q35Q loader and derivative admission;
2. admit Agents-A1-4B under its exact checkpoint, tokenizer, template, parser,
   cache, hybrid state, tool harness, verifier, environment, and runtime;
3. construct a nonsealed, source-group-disjoint tool-acquisition benchmark with
   explicit acceptable-set and no-tool labels;
4. establish full-catalog, fixed-k, threshold, score-per-cost, random,
   frequency, trajectory, and CAM-DF-style transparent baselines;
5. begin with replayable or side-effect-free read-only tools;
6. separate relevance, required-set membership, marginal utility, action
   correctness, task success, privacy exposure, and safe stopping targets;
7. prove passive target prediction before any catalog-changing intervention;
8. evaluate label noise, multiple acceptable sets, catalog drift, schema drift,
   permission drift, and policy drift;
9. separately admit any trained acquisition controller as an immutable artifact;
10. separately admit Agents-A1-35B quantization, router, experts, hybrid state,
    cache, kernels, topology, scheduler, telemetry, tool harness, and verifier;
11. refit and recalibrate under the native 35B route and state conditions;
12. require router telemetry to add sealed target-specific objective value beyond
    the complete transparent acquisition-policy stack;
13. add Jacobian features only after exact derivative parity and require sealed
    incremental value separately for relevance, marginal utility, task outcome,
    and safety targets;
14. evaluate catalog-changing control under a separate intervention protocol;
    and
15. preserve the admitted full-catalog or prospectively safe catalog as fallback.

The triggering paper is a policy and systems comparator. It is not a transfer
bridge to Agents-A1 and does not establish that Agents-A1 expert routes encode
tool need, intent, correctness, or marginal utility.

## Current blocker

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
   finite-difference parity; and
8. pass the complete Phase-0 conjunction before weight staging or GPU
   authorization.

The new evidence resolves none of these gates.

## Established after this addendum

- tool ranking and acquisition stopping are separate executable objects;
- relevance, current sufficiency, marginal continuation value, and objective
  outcome are separate targets;
- offline best-continuation supervision is retrospective and unavailable online;
- required-tool labels can be policy-relative, non-unique, redundant, or noisy;
- ranked-prefix optimization is not unrestricted subset optimization;
- tool count is not complete cost or privacy accounting;
- catalog acquisition, tool registration, invocation, result consumption, and
  external mutation are separate actions;
- transparent acquisition policies are mandatory comparators before router or
  Jacobian superiority claims;
- no privacy, sealed-data, verifier, provenance, derivative, GPU, intervention,
  or production gate is weakened; and
- Q35Q remains blocked.

## Unproven

- independent reproduction of arXiv `2607.27083v1`;
- immutable admission of implementation, data, labels, models, and dependency
  closure;
- correctness or completeness of required-tool annotations;
- robustness to alternative acceptable sets and policy-generated labels;
- global subset optimality of a ranked-prefix controller;
- proportional privacy benefit from reduced acquisition depth;
- robustness under catalog, schema, permission, policy, and distribution shift;
- safe operation with write, action, metered, or irreversible tools;
- transfer to Agents-A1 or architectural MoEs;
- objective tool-utility value from hidden-state, router, expert, semantic-
  workspace, or Jacobian features;
- incremental Jacobian-Lens value beyond transparent acquisition controls;
- complete Q35Q runtime and derivative admission; and
- safe production acquisition, early exit, retry, repair, routing intervention,
  steering, or external-action execution.

The research program remains unfinished.
