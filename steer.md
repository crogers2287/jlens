# steer.md — freeze M38E retry fail-closed; finish the active sweep; prioritize forward-only Agents-A1 scaling

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `0e812c16616251a9326207fa8e7191b8d92284cd` only where explicitly
amended below. Every predecessor remains incorporated in full, including all
sealed-data, verifier, privacy, provenance, exact-set, cap-escalation, resource,
claim-boundary, retry-limit, production-gating, repository-hygiene, and stop
rules. No frozen scientific result may be re-evaluated or tuned. No M38E task,
family, band, seed, count, threshold, verifier, sampling setting, output-cap
rule, power gate, comparator gate, or production gate may be weakened.

## Current state

- Remote `master` before this steer was
  `66698439beca24a41e7aeef52e2f2f3a6a376ce7`.
- M38E official attempt one remains valid and must continue undisturbed. The
  latest aggregate heartbeat reports 83 rows: 69 official-2048 plus 14
  pilot-4096; `mod_chain` band 3 at 21/24; uniform official identity; a live
  driver with fresh progress; and 52/52 fresh core suites. This is incomplete
  development capture, not a scientific result.
- Commit `a77fede0d605376f04852b6db842e10385755ffd` correctly fixed the audit
  git-slot wiring and honestly made automatic retry permanently fail-closed on
  the current runtime because the required fd-bound execution and trustworthy
  process-tree kill scope are unavailable. It launched no retry and did not
  touch attempt one.
- The active attempt has no runtime blocker. Retry and finalization blockers
  remain separate and must continue to be reported separately.
- M36T remains scoped exactly as frozen: T-H3 establishes verifier-backed
  adaptive tool/compute allocation only on its deterministic population. T-H1
  and T-H2 are not established.
- M37J-C remains blocked by its frozen disabled-path parity result. Its memory,
  runtime, and observability measurements are descriptive technical facts only.
- M38E has no outcome. No completed-error predictor, safe truncation rule,
  early-exit rule, semantic monitor, causal repair, activation steering, route
  intervention, or production utility is established.

## Binding decision: stop retry-controller expansion for this run

The retry-control investigation has reached the correct operational conclusion:
automatic retry is unavailable under the current execution boundary and must
remain fail-closed. Do not continue adding increasingly complex automatic retry
machinery while attempt one is healthy.

1. Do not invoke the retry controller or any superseded supervisor while attempt
   one is alive.
2. Do not stop, signal, restart, reparent, attach to, mutate, or otherwise disturb
   attempt one, its process tree, worktree, model cache, environment, or private
   ledger.
3. Preserve the permanent two-attempt ceiling. The fail-closed controller does
   not authorize attempt two; it blocks it.
4. If attempt one exits nonzero, preserve the private ledger byte-for-byte,
   record M38E as interrupted and blocked, and require private operator review.
   Do not infer that a retry is safe, do not refund the retry authorization, and
   do not launch a replacement automatically.
5. Any future rerun after a failed attempt one must be treated as a separately
   authorized execution under a fresh immutable execution environment and an
   explicit amendment. It may not be presented as a continuation merely because
   some rows are reusable.
6. Public status may describe the two aggregate retry blockers, but must not
   expose PIDs, paths, executable identities, environment values, model pointers,
   private hashes, or other secret-linked evidence.

This decision closes the automatic-retry engineering loop for the active M38E
run. It does not weaken any scientific gate.

## M38E completion and finalization

Continue aggregate-only heartbeat monitoring until attempt one exits normally or
fails.

A normal process exit is not by itself a scientific pass. Before any result is
reported, require all frozen M38E finalization checks:

1. exact expected task and row set;
2. exact run, source, model, task-set, seed, index, cap, and run-kind identities;
3. deterministic 2048-to-4096 escalation accounting and complete eligible-band
   arithmetic;
4. verifier, privacy, cleanup, resource, and commit-safety gates;
5. fresh reusable import/execution-root audit;
6. fresh external-root, virtual-environment, loader, package, native-library,
   `.pth`, editable-install, namespace, entry-point, and command-origin audit;
7. proof that no private task text, operands, outputs, tokens, telemetry arrays,
   states, routes, per-example predictions, paths, environment data, model
   pointers, or secret-linked digests entered committed artifacts.

Do not manufacture stronger launch provenance after the fact. If the required
original evidence for a finalization gate is absent or cannot be verified, the
correct outcome is `provenance-blocked` or `inconclusive`, not pass. Preserve the
rows privately for audit and report only the aggregate block reason.

## New external evidence and the next forward-only comparator

External review on 2026-07-14 found two useful primary-source methods that refine
the technically credible path without changing M38E.

### Expert contribution, not router selection alone

`The Expert Strikes Back: Interpreting Mixture-of-Experts Language Models at
Expert Level` (arXiv:2604.02178; code `jerryy33/MoE_analysis`) distinguishes
router selection from actual expert impact. Its useful measurement is the norm
of the routed residual write:

`contribution_i(l,t) = router_weight_i(l,t) * ||expert_output_i(l,t)||_2`.

Router weight means an expert was selected; it does not prove that the expert
made a large residual-stream contribution. The paper also uses expert-output
logit projections and sparse probes, but its semantic labels are not evidence of
completed-error prediction on Agents-A1.

The next separately preregistered forward-only Agents-A1 study must therefore
include, where technically observable without changing outputs:

- router weights and margins;
- selected-expert output norms;
- router-weight times expert-output-norm contribution;
- layer-level sums, maxima, dispersion, entropy, and concentration of those
  contributions;
- contribution changes and route transitions across layers;
- separate prefill and autoregressive-decode summaries;
- contribution-path features across multiple layers.

Measure router weight, output norm, and their product separately so predictive
increment cannot be attributed to the wrong component. Do not retain unnecessary
full expert activations when aggregate features suffice.

### Privacy-minimal aggregated routing-load baseline

`RouteScan: A Non-Intrusive Approach to Auditing MoE LLMs Safety via Expert
Routing Telemetry` (arXiv:2605.24817) shows that prefill expert-load patterns can
be represented using normalized per-expert load, active-expert coverage,
entropy-derived effective expert count, coverage gap, and concentration. Its
published result concerns harmful-input auditing on other MoEs, not answer-error
prediction or Agents-A1.

Use its aggregate feature construction only as a low-cost, privacy-minimal
baseline in the next study:

- normalized expert-load distribution by layer;
- active expert fraction;
- entropy and effective expert count;
- coverage gap and concentration;
- prefill-only and decode-only variants where the runtime permits exact phase
  separation.

Do not claim prompt non-invertibility or privacy safety from the paper alone.
Run a project-specific leakage and inversion audit under the frozen privacy
threat model before any such claim.

No r/LocalLLaMA item in this scan produced an actionable method that survived
primary-source verification.

## Preregistered sequence toward Agents-A1 scaling

The official Agents-A1 repository still lists only the released 35B-A3B model
and retains its 2026-07-08 statement that a 4B model is coming. The official
Hugging Face collection still contains only 35B variants. Do not substitute
Agents-K1 or an unofficial checkpoint under the Agents-A1 name.

The required sequence is now:

1. finish and finalize M38E unchanged, or record it honestly as blocked;
2. before collecting any new scientific rows, create and commit a separate
   preregistration for a forward-only 35B comparator;
3. use the exact pinned Agents-A1 35B runtime and observation-only capture;
4. compare frozen nuisance baselines against incremental blocks for:
   - router logits, margins, loads, and route-count summaries;
   - hidden-state summaries and router-visible/router-blind energy;
   - router-expert geometry and multi-layer route paths;
   - expert-output norms and router-weighted contribution norms;
   - RouteScan-style aggregate load/coverage/entropy features;
5. separate prefill from autoregressive decode;
6. stream only preregistered aggregate features to private storage unless a
   stronger raw signal is explicitly necessary and privacy-approved;
7. use leakage-free nested cross-validation, train-fold-only preprocessing and
   feature selection, frozen nuisance covariates, family-aware splits, and a
   locked held-out evaluation set;
8. report raw and nuisance-residualized predictive increment over confidence,
   prompt/completion length, task family, difficulty, cap, truncation status,
   latency, verifier category, and route count;
9. treat semantic expert labels as exploratory and sealed. Do not use LLM-made
   expert labels as scientific predictors, stopping rules, or interventions
   without a separate preregistration and held-out validation;
10. advance only if a forward-only feature block adds stable, calibrated,
    verifier-labeled completed-error prediction beyond all frozen baselines;
11. then compare full Jacobians, reduced-target VJPs, and bounded
    finite-difference probes on a smaller comparable MoE or the official
    Agents-A1 4B checkpoint if released;
12. require approximation-error, rank-stability, finite-value, phase-localized
    parity, memory, runtime, privacy, and predictive-increment gates;
13. only then run a frozen one-sequence 35B backward memory smoke on rented
    high-memory hardware with no scientific claim;
14. advance to fitting only through a separately frozen fit and validation
    protocol.

`Jacobian Scopes` remains the strongest concrete engineering lead for
reduced-target VJPs and finite-difference Jacobian estimates. `When Are Experts
Misrouted?` continues to support counterfactual routing analysis while warning
that ordinary router scores can be uninformative on fragile reasoning tokens.
Current hidden-state error-prediction work supports diagnostic probing but not
causal repair, and current early-exit evidence remains unfavorable for modern
MoEs without direct verifier-backed validation.

## Claim and stop boundary

- M38E remains in progress and has no result.
- Automatic retry is permanently fail-closed for the current runtime. This is a
  safety decision, not a scientific failure and not authorization for a manual
  retry.
- M38E finalization remains blocked until every frozen scientific and provenance
  audit passes; unverifiable evidence produces a blocked or inconclusive result.
- No router, hidden-state, geometry, expert-contribution, load, path, semantic,
  or Jacobian feature has demonstrated incremental completed-error prediction on
  Agents-A1.
- No Jacobian Lens has been fitted or validated on Agents-A1.
- No safe truncation, early exit, semantic correctness, causal repair, routing
  intervention, activation steering, or production utility is established.
- Full 35B backward feasibility remains unproven.
- GitHub reports this repository as public. Treat every committed byte as
  externally visible and keep all raw tasks, outputs, token data, telemetry,
  states, routes, expert outputs, paths, per-example predictions, process
  evidence, environment data, model pointers, and secret-linked digests private.
- The research program is not complete. Do not mark it complete until every
  frozen milestone and final stop rule in `CODEX_AUTOSTEER.md` is satisfied.
