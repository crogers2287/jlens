# STEER ADDENDUM — complexity-aware execution scope and verify-expand gates

Date: 2026-07-19

Parent remote head: `88e13ea226a64b93cbbf80c9e0c9663dca8c88cd`

Status: binding future-protocol correction; no current execution authorization

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and the
canonical protocol index. It changes the minimum future comparator set for
agent efficiency, early-exit, truncation, escalation, and internal-monitor
claims. It does not change the active Q35Q milestone or authorize any later
phase.

Q35Q remains `q35q_artifact_admission_blocked`. No weight staging,
tensor-payload retrieval, model execution, GPU execution, hidden-state capture,
router capture, Jacobian fitting, sealed scientific evaluation, intervention,
or production use is authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-gradient, parity,
resource, cleanup, commit-safety, production-gating, and stop rule remains
binding. GitHub currently reports this repository as public; aggregate-only
commit restrictions continue to apply.

## External evidence and narrow interpretation

Yin and Feng, “Do AI Agents Know When a Task Is Simple? Toward
Complexity-Aware Reasoning and Execution,” arXiv `2607.13034v1`, submitted
2026-07-14, introduce minimum-sufficient execution and the E3 policy:
Estimate an initial operating point, Execute a minimum viable path, and Expand
scope only when verification fails.

The associated public implementation was inspected at immutable commit
`44e2bfd438a39ad81e6135851f5c691c61179460` in
`eejyin/Do-AI-Agents-Know-When-a-Task-Is-Simple-Toward-Complexity-Aware-Reasoning-and-Execution`.
The released estimator is intentionally simple: prompt lexical features plus at
most one search probe produce an estimated difficulty, scope, risk, and
confidence. The policy then performs a bounded minimum execution and expands
through broader inspection and verification only after failure.

On the authors’ deterministic 121-task MSE-Bench simulator, E3 reportedly
matches the fully successful baselines at 100% success while reducing mean cost
by about 85% versus max-context-first and about 16% versus an adaptive retrieval
baseline, with about 91% fewer tokens and 92% fewer fully inspected files than
max-context-first. Under held-out paraphrasing, estimator accuracy reportedly
falls from 85.1% to 66.9%, while verify-and-expand preserves 100% simulator
success at higher cost. A companion live GPT-4o case on one open-source library
reports the same qualitative over-reading pattern, but is too narrow to
establish broad agent or Agents-A1 transfer.

The binding interpretation is limited:

1. A harness-level task-scope estimator with verifier-backed expansion is a
   credible cheap comparator for agent-efficiency and early-control claims.
2. It is not evidence of hidden-state correctness awareness, semantic-workspace
   monitoring, MoE router quality, Jacobian-Lens value, or safe reasoning
   truncation.
3. MSE-Bench equalizes editing capability in a synthetic simulator. Its result
   isolates execution redundancy but does not establish behavior on naturally
   distributed repositories, tools, multimodal environments, or long-horizon
   agents.
4. The verifier-backed expansion policy can preserve success despite an
   imperfect initial estimate only when the verifier is available, independent,
   sufficiently sensitive, and correctly bound to fresh source state.
5. Task difficulty, execution scope, answerability, capability, correctness,
   and failure risk are separate endpoints. Success on one does not establish
   another.

## Mandatory minimum-sufficient-execution comparator

Before an internal hidden-state, router, workspace, or Jacobian monitor may be
claimed necessary for reducing agent effort, the future comparator stack must
include, when technically compatible, a frozen external policy with these
components:

1. a prompt- and metadata-only initial scope estimate;
2. an optional bounded cheap probe whose permitted tools and cost are frozen;
3. a minimum viable execution path;
4. a fresh deterministic or mechanically grounded verifier;
5. a bounded expansion ladder after failure, ambiguity, timeout, or verifier
   unavailability;
6. a frozen terminal fallback when the expansion budget is exhausted.

Compare at least:

- max-context-first or maximum-budget execution;
- fixed-budget execution without scope adaptation;
- adaptive retrieval without an explicit initial scope estimate;
- estimate-execute without expansion;
- execute-expand without an estimator;
- full estimate-execute-expand;
- admitted answerability, capability, confidence, and hidden-state policies;
- route telemetry and Jacobian-Lens policies only after their existing gates.

An internal monitor has no operational necessity claim when the admitted
external scope policy achieves equal sealed task utility at lower total cost.
Mechanistic interest may still be reported separately.

## Oracle, label, and task-construction leakage gates

The minimum-sufficient oracle, benchmark task level, hidden dependency graph,
canonical edit sites, expected patch, test outcome, and eventual expansion
requirement must not enter policy features or threshold selection.

Freeze before outer validation or sealed evaluation:

- estimator inputs, features, model, prompt, and artifact identity;
- permitted cheap probes and their result serialization;
- scope classes, risk classes, and expansion ladder;
- initial operating-point rule and confidence thresholds;
- verification commands, timeout semantics, and parser;
- retry, escalation, fallback, and terminal-stop rules;
- cost weights and utility function.

Split by repository, task family, template, dependency pattern, and generated
benchmark seed where applicable. Near-duplicate edits, paraphrases, shared
oracles, cloned dependency graphs, and repeated source states may not cross
training, tuning, certification, and sealed-test partitions.

Include deceptive localized wording, indirect dependencies, cross-file aliases,
missing search hits, stale indexes, tool failures, flaky tests, verifier false
negatives, verifier false positives, and tasks whose cheapest safe path is not
the shortest path.

## Verifier independence and failure semantics

Verification is a separate admitted component, not free ground truth.

Every verifier-backed expansion experiment must bind:

- source revision and workspace state;
- verifier code, dependencies, command, environment, and immutable identity;
- test selection and exclusion rules;
- timeout, crash, flaky, partial, skipped, and unavailable outcomes;
- evidence freshness and invalidation after every edit or environment change.

A verifier crash, timeout, stale result, malformed output, or unavailable check
must not count as success. It becomes `verifier_unavailable` and triggers the
frozen expansion or fallback rule. A passing partial check cannot authorize a
completion claim outside its proved scope.

The estimator and policy must not receive sealed verifier labels, canonical
answers, future trajectory states, post-hoc failure localization, or outcomes
from work that had not occurred at the claimed decision boundary.

## Cost and utility accounting

Report complete end-to-end cost, not only successful-run redundancy.

Include:

- scope-estimation and probe tokens, latency, and tool calls;
- retrieved, inspected, transferred, and retained context;
- minimum-path execution;
- every verifier invocation;
- failed attempts, discarded work, retries, and expansions;
- fallback execution and handoff construction;
- model, accelerator, host-memory, storage, network, and energy cost where
  measurable;
- time to first action, time to first verification, and time to accepted result;
- success, regression, false-completion, abandonment, and failure severity.

ACRR or another success-only efficiency statistic may be reported, but it must
be accompanied by all-run expected utility and cost. A cheap failed run is not
an efficiency gain. Cost weights must be frozen, and sensitivity across
plausible deployment weights must be reported.

Claims of savings may count only work occurring after the scope decision. A
retrospective estimate based on the completed trajectory, final patch, eventual
file set, or verifier result is not an online scope-control result.

## Correctness and intervention boundary

Execution-scope prediction is not correctness prediction. A low-scope estimate
may be correct while the edit is wrong; a high-scope estimate may be wrong while
the task succeeds. Report scope calibration and task outcome separately.

A verify-expand policy may be evaluated as a harness intervention only after its
components are frozen and admitted. It does not authorize token-level early
exit, reasoning truncation, tool suppression, model escalation, expert
skipping, forced routing, activation steering, or production deployment. Each
of those remains a separate intervention class with its own preregistration and
safety gate.

## Agents-A1 scaling consequence

For Agents-A1 or comparable large MoE agents, the technically credible order is
now:

1. deterministic schema, permission, provenance, ordering, and relational
   checks;
2. a frozen prompt/metadata scope estimator with bounded cheap probes;
3. minimum viable execution with fresh verifier-backed expansion;
4. calibrated confidence, answerability, capability, and resolution baselines;
5. selected passive hidden-state and bounded trajectory summaries;
6. matched execution on the separately admitted Agents-A1-4B dense sibling;
7. minimal conditional route telemetry on Agents-A1-35B;
8. sparse-feature or transcoder comparators when admitted;
9. Jacobian-Lens features only after exact derivative parity and sealed
   incremental value over every cheaper baseline.

The same scope-policy implementation, task partitions, verifier rules, cost
model, and outcome ontology must be used on the dense sibling and MoE model
where technically compatible. Shared gains are harness- or task-level evidence,
not MoE-specific evidence. Router or Jacobian features must show residual sealed
value after conditioning on the frozen scope estimate, probes, verification
history, expansion state, and simpler internal baselines.

Use bounded aggregate telemetry only. This addendum does not authorize retaining
raw prompts, source code, patches, tool outputs, trajectories, verifier labels,
hidden states, router paths, or per-example predictions in this public
repository.

## Program status after this addendum

Established:

- a public deterministic E3/MSE-Bench implementation exists at the inspected
  commit;
- its released policy explicitly separates initial scope estimation from
  verifier-triggered expansion;
- the authors report large simulator cost reductions at matched success and a
  smaller advantage over adaptive retrieval;
- imperfect paraphrase-time estimation can be recovered by expansion in the
  released simulator;
- a frozen minimum-sufficient-execution policy is now a mandatory future
  comparator for compatible agent-efficiency, early-control, and truncation
  claims.

Unproven:

- independent reproduction of the reported results;
- broad validity beyond the controlled simulator and one narrow live-model case;
- reliable scope estimation on natural long-horizon, multimodal, adversarial, or
  distribution-shifted agent workloads;
- verifier completeness, independence, latency, and stability on Agents-A1;
- transfer to Agents-A1-4B or Agents-A1-35B;
- correctness prediction from task-scope estimates;
- incremental hidden-state, router, semantic-workspace, or Jacobian-Lens value
  after the admitted scope-policy baseline;
- safe early exit, reasoning truncation, tool suppression, escalation, routing
  intervention, activation steering, or production deployment.

The active engineering blocker remains production-path upstream/runtime
provenance composition as defined in `steer.md`. This addendum changes future
comparator, verifier, leakage, cost, and policy-evaluation requirements only. It
does not authorize advancement past the current gate, and the research program
remains unfinished.