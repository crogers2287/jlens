# Steer addendum — M38E completed-error frontier is irreversibly unavailable; finish the bounded sweep unchanged

Date: 2026-07-14

This addendum is program-control and aggregate-status only. It incorporates every
existing sealed-data, verifier, privacy, provenance, exact-set, escalation,
resource, retry, production-gating, repository-hygiene, and claim-boundary rule.
It does not alter any M38E task, band, family, seed, verifier, model, runtime,
output cap, pilot rule, eligibility threshold, sample requirement, or stop rule.
It does not authorize new scientific capture.

## Evidence available before this addendum

Remote `master` was
`acdfa33f709ead6dd883f5cd3406fb4ab85a32f8`.

The aggregate heartbeat records:

- `mod_chain`: all 96 official tasks complete;
- `alg_coeff`: all 96 official tasks complete;
- `order_track`: started, with 7 of 96 official tasks complete;
- 62 pilot rows total: 30 from `mod_chain` and 8 from each of the four
  `alg_coeff` bands;
- zero complete 4,096-token full-band reruns;
- the driver advanced from the completed `alg_coeff` band-4 pilot into
  `order_track`.

Under the frozen driver, a band with truncation above the threshold receives a
bounded 4,096-token pilot. A passing pilot immediately requires a complete
24-task 4,096-token rerun before the driver may advance. If the pilot does not
show the frozen material reduction, the band is recorded as
`escalation_failed` and the driver advances without a full-band rerun.

Therefore the aggregate control flow establishes, without opening private rows,
that all four `alg_coeff` bands completed their pilots and failed escalation.
The previously completed `mod_chain` family also produced no eligible band.

## Binding status

The M38E development frontier is now **irreversibly unavailable under the frozen
protocol**.

The protocol requires at least two eligible families and at least 48 completed
incorrect examples from eligible bands. Only `order_track` remains. Even if one
or more `order_track` bands become eligible and contain sufficient completed
incorrect examples, the maximum possible number of eligible families is one.
The two-family gate can no longer be satisfied.

This is a deterministic program-control conclusion from aggregate execution
state. It is not permission to inspect, reinterpret, relabel, or expose private
rows. It is not a finalized M38E result because the frozen driver still reports
`in_progress` until every bounded path completes and all finalization audits are
run.

## Required handling of the active attempt

1. Do not stop, signal, restart, mutate, attach to, or otherwise disturb the
   healthy active attempt.
2. Finish the exact bounded `order_track` sweep because the current steer
   requires attempt one to continue undisturbed and the frozen implementation
   defines completion only after every expected band path is complete.
3. Treat the remaining `order_track` work as exact-set completion and audit
   evidence only. It cannot rescue the M38E two-family frontier.
4. Do not add replacement families, extra tasks, reruns, larger caps, alternate
   verifiers, new seeds, or relaxed gates.
5. Do not launch an M38E sealed benchmark. The development eligibility gate is
   already unreachable.
6. On normal process completion, run every frozen exact-set, escalation,
   verifier, provenance, execution-root, dependency, loader, native-library,
   privacy, cleanup, resource, and commit-safety audit.
7. If those audits establish complete and valid execution, commit the frozen
   outcome `m38e_completed_error_frontier_not_found` and stop M38E.
8. If required evidence is missing or unverifiable, report the narrower
   `provenance-blocked` or `inconclusive` outcome instead of manufacturing a
   stronger result.

## Boundary for M39 and later scaling

This outcome does not prove that router telemetry, hidden-state summaries,
expert contributions, route paths, geometry, semantic-workspace features, or
Jacobian features lack predictive value. It proves only that the frozen M38E
development sweep did not produce the required two-family completed-error
frontier.

M39 remains design-only and capture-prohibited until M38E is fully finalized and
a separate committed launch amendment satisfies every independent-population,
provenance, parity, privacy, verifier, power, and leakage gate. M39 may not reuse
M38E rows, outcomes, selected examples, private labels, or outcome-informed
feature choices.

The technically credible Agents-A1 scaling sequence remains:

1. finish and finalize M38E honestly;
2. consider the independent forward-only Agents-A1 35B M39 comparator only
   through its separate launch amendment;
3. require stable predictive increment beyond frozen nuisance and router
   baselines before any Jacobian fitting;
4. use admitted Agents-A1 4B only for dense-model Jacobian/VJP tooling;
5. use a separately admitted open MoE for router, expert, dispatch, coalition,
   and MoE-gradient instrumentation;
6. require both engineering gates before a one-sequence Agents-A1 35B backward
   memory smoke;
7. preserve every intervention and production gate.

## Claims that remain prohibited

No completed-error predictor, safe truncation rule, early-exit rule, semantic
correctness monitor, causal expert localization, routing intervention,
activation steering, correction policy, Jacobian Lens validation, 35B backward
feasibility, or production utility is established.

The repository is publicly visible. Every committed byte must remain safe for
external disclosure. Raw tasks, answers, outputs, tokens, telemetry arrays,
hidden states, routes, expert identities and outputs, per-example predictions,
paths, process evidence, environment values, model pointers, and secret-linked
digests remain private and uncommitted.
