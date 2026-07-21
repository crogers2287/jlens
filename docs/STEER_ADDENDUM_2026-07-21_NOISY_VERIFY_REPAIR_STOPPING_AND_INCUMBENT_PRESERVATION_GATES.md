# STEER ADDENDUM — noisy verify-repair stopping and incumbent-preservation gates

Date: 2026-07-21

Parent remote head: `30715d2555dca73613fb1109e099101b25e7526e`

Status: binding future-protocol correction; no current execution authorization

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, the canonical
protocol index, and the existing complexity-aware execution-scope and
verify-expand addendum. It changes the minimum future comparator, calibration,
and safety requirements for verifier-driven repair, retry, escalation, and
stopping policies. It does not change the active Q35Q milestone or authorize any
later phase.

Q35Q remains `q35q_artifact_admission_blocked`. No weight staging,
tensor-payload retrieval, model execution, GPU execution, hidden-state capture,
router capture, Jacobian fitting, sealed scientific evaluation, repair policy,
retry policy, intervention, or production use is authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-gradient, parity,
resource, cleanup, commit-safety, production-gating, and stop rule remains
binding. GitHub currently reports this repository as public; aggregate-only
commit restrictions continue to apply.

## External evidence and narrow interpretation

Wu, Shen, Yang, Peng, and Hu, “Verify, Repair, Repeat, or Stop? Robust Stopping
for Noisy Verify-Repair Loops in LLM Agents,” arXiv `2607.17641v1`, submitted
2026-07-20, formalize verifier-driven repair when both the verifier and the
repairer are noisy.

The paper separates four quantities:

- verifier false acceptance of an invalid candidate;
- verifier false rejection of a valid candidate;
- repair success, meaning invalid-to-valid transition probability `alpha`;
- repair damage, meaning valid-to-invalid transition probability `beta`.

Its central result is that observed verifier acceptance can improve while true
candidate validity declines. Continued repair is beneficial only when the
expected invalid-to-valid gain exceeds the expected valid-to-invalid damage.
With committed-validity belief `b`, the one-step gain is
`G = (1-b) * alpha - b * beta`, and the zero-cost boundary is
`b* = alpha / (alpha + beta)`.

The stopping decision therefore requires reliable identification of the sign of
marginal repair gain, not merely a high verifier score, a fixed retry budget, or
an increasing pass rate. When verifier discrimination or the decision margin is
too small, calibration error can reverse the sign. The paper pairs its
model-based rule with a conservative incumbent-preserving fallback that replaces
the current best candidate only under sufficient verification margin.

On the authors’ GSM8K stress setting, the reported method improves final true
validity by 60.6 percentage points over fixed five-round repair while averaging
0.72 repair rounds. This is an authors’ result, not independent reproduction.
The paper assumes conditionally independent repeated verifier votes given the
true state and locally stable verifier and repair-transition parameters. It
explicitly treats those assumptions as local approximations and notes repeated
vote correlation and instance heterogeneity as limitations.

The binding interpretation is limited:

1. Verifier pass rate is not a valid substitute for objective task validity.
2. Repair is a state-changing intervention that can destroy an already-correct
   incumbent.
3. Verifier quality, repair efficacy, repair damage, candidate selection, and
   stopping policy are separate experimental objects.
4. A fixed number of retries or repairs is not a safe default.
5. A stopping guarantee applies only under the admitted calibration,
   dependence, stationarity, and coverage assumptions.
6. The evidence does not establish hidden-state correctness awareness, router
   quality, semantic-workspace monitoring, Jacobian-Lens value, Agents-A1
   transfer, or safe production repair.

## Required decomposition of verify-repair systems

Every future verify-repair experiment must freeze and report separately:

1. **Generator:** produces the initial candidate.
2. **Verifier:** produces observations about a candidate.
3. **Repairer:** mutates a candidate using frozen feedback and context.
4. **Candidate store:** retains incumbents and candidate lineage.
5. **Selection rule:** chooses which candidate is considered incumbent.
6. **Stopping rule:** decides commit, repair, retry, escalate, or abstain.
7. **Objective outcome rule:** determines true validity independently of the
   operational verifier where technically possible.
8. **Fallback:** applies when calibration, verification, repair, or stopping is
   unavailable or uncertified.

A method may not receive a stronger verifier, repairer, candidate-selection rule,
and stopping rule while attributing the combined gain solely to an internal
hidden-state, route, workspace, sparse-feature, transcoder, directional-JVP, or
Jacobian signal.

## Mandatory repair-transition accounting

Every admitted repairer must be evaluated on all four before-after transition
cells under the frozen objective outcome rule:

- invalid to valid: repair success;
- invalid to invalid: ineffective repair;
- valid to valid: incumbent preservation;
- valid to invalid: repair damage.

Report transition counts, rates, cluster-aware uncertainty, severity-weighted
outcomes, and stratification by task family, repair round, verifier state,
trajectory phase, model, checkpoint, runtime, and distribution shift.

Pooled post-repair accuracy is insufficient because it can hide a high damage
rate on already-valid candidates. Success-only repair statistics are prohibited.
A repairer with high invalid-to-valid conversion but unacceptable valid-to-
invalid damage is not admitted for automatic use.

## Objective validity versus verifier acceptance

Operational verifier acceptance, confidence, score, or vote count must not be
represented as true validity.

Future evaluations must report separately:

- objective validity by canonical executable, benchmark, or independently
  admitted outcome evidence;
- operational verifier acceptance;
- false acceptance and false rejection;
- acceptance-validity divergence over repair rounds;
- calibration and discrimination within every claimed deployment stratum;
- final committed validity, not merely best-seen or accepted-candidate validity.

A rising verifier score or pass rate with flat or declining objective validity is
negative evidence for the loop. It cannot be reported as successful refinement.
When no independent outcome rule exists, the result must be scoped as verifier
optimization rather than correctness improvement.

## Incumbent preservation and candidate lineage

Every automatic repair loop must preserve the pre-repair incumbent until the
replacement rule has been satisfied. A repair operation may not destructively
overwrite the only retained candidate.

The candidate store must bind, in private controlled storage where necessary:

- immutable candidate identity and parent identity;
- generator, verifier, repairer, prompt, tool, runtime, and source-state identity;
- repair round and feedback identity;
- objective and verifier evidence freshness;
- replacement, rollback, escalation, and retention decisions.

Only aggregate results and permitted immutable protocol identities may enter this
public repository. Raw prompts, code, plans, tool outputs, verifier transcripts,
per-candidate labels, hidden states, routes, and predictions remain prohibited.

The default under unidentifiable stopping sign, verifier unavailability,
repairer failure, malformed evidence, stale evidence, candidate-store failure,
or distribution drift is to retain the incumbent and invoke the frozen fallback.
It is not to overwrite, continue repairing indefinitely, or treat the newest
candidate as best.

## Mandatory stopping-policy comparators

Future compatible evaluations must compare at least:

- no repair;
- exactly one repair;
- fixed multi-round repair budgets, including three and five rounds where
  affordable;
- stop on first verifier acceptance;
- consecutive-pass or repeated-vote thresholding;
- keep-latest candidate;
- keep-best-by-verifier candidate;
- incumbent-preserving verifier-margin fallback;
- a calibrated marginal-gain stopping policy when its assumptions are admitted;
- a guarded fallback when marginal-gain sign is not identifiable;
- bounded escalation or human-review fallback;
- simpler external checks, confidence, answerability, capability, and trajectory
  baselines;
- internal hidden-state, route, workspace, sparse-feature, transcoder, or
  Jacobian policies only after their separate admission gates.

All policies must use the same generator, repairer, verifier stream, candidate
store, objective outcome rule, repair budget, and intervention semantics during
matched comparisons. Total cost and all-run utility must be reported.

## Calibration, leakage, and certification gates

Use distinct populations for:

1. verifier calibration and discrimination estimation;
2. repair-transition estimation, including `alpha` and `beta`;
3. stopping-rule, threshold, and fallback selection;
4. post-selection certification;
5. sealed evaluation.

The following may not cross those boundaries:

- repeated or near-duplicate tasks and trajectories;
- shared templates, repositories, environments, users, tenants, or rollouts;
- candidate lineages or before-after repair pairs;
- verifier labels, objective outcomes, future repair outcomes, canonical answers,
  or post-hoc error localization;
- stopping-policy outcomes or best-round identities.

A failed certification population may not be reused to recalibrate the verifier,
repairer, stopping boundary, replacement margin, or fallback. Candidate damage
observed after deployment requires recertification or fail-closed suspension, not
silent threshold adjustment.

## Dependence, heterogeneity, and drift

Repeated verifier queries on one candidate are not independent merely because
they are separate calls. Repair rounds on one lineage are not independent tasks.

Future reports must test or explicitly bound:

- repeated-vote correlation;
- candidate- and task-level difficulty heterogeneity;
- repair-transition dependence on verifier feedback and trajectory history;
- model, verifier, repairer, prompt, decoding, tool, source-state, runtime, and
  workload drift;
- repeated rollouts, retries, branches, and shared environments;
- adaptive querying and stopping-induced selection;
- cluster-aware uncertainty at task or episode level.

When conditional independence, local stationarity, calibration coverage, or
sign identifiability is not defensible, model-based guarantees must be withdrawn.
The policy becomes an empirical comparator and must fall back to the admitted
incumbent-preserving rule.

## Cost, harm, and full-population reporting

Report complete end-to-end cost and harm across the full population, including:

- generator, verifier, repairer, judge, and fallback calls;
- repeated verification votes;
- all failed, discarded, and rolled-back candidates;
- source inspection, retrieval, context, tool, storage, and synchronization cost;
- time to first candidate, first verification, accepted result, and final commit;
- false acceptance, false rejection, false completion, abandonment, timeout,
  escalation, and verifier unavailability;
- invalid-to-valid repairs and valid-to-invalid damage;
- irreversible external effects caused before stopping;
- rollback success and failures;
- accelerator, host-memory, network, storage, and energy cost where measurable.

A cheap loop that commits a damaged candidate is not an efficiency gain. Best-of-
trajectory validity cannot replace final committed validity. A repair policy must
be evaluated against no-repair and incumbent-preserving baselines at equal total
budget.

## Correctness and intervention boundary

A useful stopping signal does not authorize repair. A useful repairer does not
authorize repeated repair. A verifier does not authorize destructive candidate
replacement. A retrospective identification of the best round is not an online
stopping result.

Repair, retry, escalation, tool suppression, early exit, reasoning truncation,
model switching, expert skipping, forced routing, activation steering, and
production deployment remain separate intervention classes with separate
preregistration, safety, privacy, verifier, resource, and production gates.

No internal monitor may be claimed to improve correctness unless it adds sealed
objective-outcome value after conditioning on verifier state, repair history,
incumbent state, repair-transition risk, confidence, answerability, capability,
context envelope, and cheaper external controls.

## Agents-A1 scaling consequence

For Agents-A1 or comparable large MoE agents, the technically credible order is:

1. complete Q35Q production-path provenance and exact derivative admission on a
   frozen static runtime;
2. define immutable task contracts, objective outcome rules, and irreversible-
   action boundaries;
3. establish no-repair, fixed-repair, verifier-threshold, and incumbent-
   preservation baselines;
4. estimate verifier false acceptance, false rejection, and discrimination on
   independent calibration data;
5. estimate repair success and repair damage on independent before-after
   transitions;
6. evaluate sign-aware and guarded stopping policies on Agents-A1-4B with full
   candidate lineage and rollback controls;
7. separately admit and evaluate the same decomposition on Agents-A1-35B;
8. add passive hidden-state and bounded trajectory signals only after the
   external loop is frozen;
9. add direct route telemetry only if it provides residual sealed objective-
   outcome value under the identical stopping and repair policy;
10. add sparse-feature, transcoder, or Jacobian-Lens signals only after exact
    parity and incremental value over every cheaper comparator;
11. keep automatic repair, retry, escalation, truncation, route modification,
    activation steering, and production enforcement under separate gates.

Calibration and stopping artifacts do not transfer automatically between
Agents-A1-4B and Agents-A1-35B. Shared gains are task-, harness-, verifier-, or
repair-policy evidence, not MoE-specific evidence. Route- or Jacobian-specific
claims require residual value on the full population and on cases where cheaper
signals prescribe the wrong stopping action.

## Program status after this addendum

Established:

- noisy verifiers and noisy repairers can compound rather than correct errors;
- verifier acceptance can rise while objective validity falls;
- valid-to-invalid repair damage is a required first-class endpoint;
- stopping should depend on prospective marginal repair value rather than fixed
  round count or pass rate when the required quantities are identifiable;
- incumbent preservation is the safe default when stopping sign or evidence is
  not reliable;
- the noisy verify-repair stopping, lineage, transition, calibration, dependence,
  full-cost, and Agents-A1 comparator gates in this document are now binding.

Unproven:

- independent reproduction of the reported VRR-Stop results;
- validity of its independence, stationarity, and calibration assumptions on
  natural long-horizon agents;
- stable verifier and repair-transition estimates under model, task, tool, and
  runtime drift;
- safe automatic repair on coding, web, multimodal, tool-using, or adversarial
  workloads;
- transfer to Agents-A1-4B or Agents-A1-35B;
- incremental hidden-state, router, semantic-workspace, sparse-feature,
  transcoder, directional-JVP, or Jacobian-Lens value after the complete external
  verify-repair stopping baseline;
- safe retry, repair, escalation, early exit, truncation, routing intervention,
  activation steering, or production deployment.

The active engineering blocker remains production-path upstream/runtime
provenance composition as defined in `steer.md`. This addendum changes future
comparator, calibration, candidate-preservation, stopping, and policy-evaluation
requirements only. It does not authorize advancement past the current gate, and
the research program remains unfinished.
