# Binding steer addendum — M38E orphaned post-completion compute resolution

Date: 2026-07-16

Status: **binding executive amendment; immediate host execution authorized.**

This addendum incorporates `steer.md`, `CODEX_AUTOSTEER.md`, the M38E frozen
protocols, and
`docs/STEER_ADDENDUM_2026-07-16_M38E_POSTCOMPLETION_SHUTDOWN_AND_FINALIZATION.md`.
It supersedes only the earlier rule that any observed GPU activity must halt
post-completion cleanup. Every sealed-data, exact-set, escalation, verifier,
provenance, dependency, privacy, resource, cleanup, commit-safety,
claim-boundary, retry, and production gate remains binding. No task, row, seed,
cap, threshold, model, verifier, outcome rule, or scientific population changes.

## Decision basis

Remote head `c970d7add7c88f019f8eb739cedd9926d5126c5e` records all of the following:

- the official ledger is byte-stable for approximately 30.5 hours;
- no ledger write file descriptor is open;
- all 288/288 official rows are present across the frozen 12 cells;
- all 94 required pilot rows are present;
- zero full-band 4096 reruns were triggered;
- the frozen execution record contains 382 total rows;
- an M38E-driver-named process remains present;
- one RTX 3090 remains at sustained high utilization while the two-GPU model is
  resident;
- no process was signalled and no row was rerun;
- 324/324 fresh tests pass and the repository is commit-safe clean.

The committed driver admits generation only for missing `(task_id,
attempt_kind)` keys. Once every official band and every triggered escalation
path has exact-set completion, no further generation attempt is authorized by
the frozen program. Sustained compute after that point can be a stalled kernel,
worker, runtime teardown, or orphaned process. GPU utilization alone is not
proof that valid scientific work remains.

## Binding classification rule

On the next host-capable cycle, perform one private metadata-only classification.
The process may be classified as `m38e_orphaned_postcompletion_compute` only if
all conditions below hold simultaneously:

1. The existing M38E validator accepts every ledger row against the frozen run
   identity, task-set digest, manifest digest, source commit, model revision,
   override hash, attempt kind, cap, task hash, and duplicate constraints.
2. Exact set equality confirms all 288 official keys and every deterministically
   required pilot/full-band escalation key are present, with no unknown or
   extra attempt keys.
3. The public aggregate counts remain 288 official, 94 pilot, zero full-band
   4096, and 382 total, and all 12 band paths are complete.
4. The ledger has no open writer and remains byte-for-byte unchanged during a
   fresh bounded observation interval of at least 10 minutes.
5. No authorized M38E task key remains missing. Do not infer this from row count
   alone; derive it from the frozen task identities and escalation rules.
6. The active GPU process is privately attributable by process-group or
   parent-child identity to the top-level M38E driver. Do not signal an
   unrelated model server or workload.
7. No finalization audit or serving-restoration operation is currently writing
   an authorized artifact.

If any exact-set, identity, writer, attribution, or activity condition fails,
do not signal anything. Record only the narrow aggregate blocker
`m38e_postcompletion_classification_blocked` and the blocker class. Never commit
process identifiers, command lines, host details, paths, environment values, or
private row evidence.

## Authorized cleanup after positive classification

When all classification conditions pass, active GPU utilization is no longer a
reason to wait. It is classified as orphaned post-completion compute and the
following one-shot sequence is mandatory:

1. Record aggregate state `m38e_orphaned_postcompletion_compute`.
2. Request graceful termination of the attributable M38E process group once.
3. Allow a bounded 120-second grace period for runtime and worker teardown.
4. Reconfirm privately that the ledger is unchanged and has no writer.
5. If the attributable process group remains, terminate that process group
   forcibly once and record only
   `m38e_postcompletion_forced_cleanup` in aggregate status.
6. Do not restart, resume, repair, retry, or extend M38E. Discard any uncommitted
   in-memory output. The frozen validated ledger is the sole admissible
   execution record.
7. Run the complete frozen finalization audit set against the existing
   artifacts: exact-set, escalation, verifier, provenance, execution-root,
   dependency/import/loader/native-library, model/revision, privacy, resource,
   cleanup, serving-restoration, and commit-safety.
8. If every audit passes, commit
   `m38e_completed_error_frontier_not_found` and close M38E.
9. If any required evidence is missing, contradictory, or unverifiable, commit
   only `provenance-blocked` or `inconclusive`. Never manufacture evidence or
   weaken a gate.
10. Release the dual-RTX-3090 window only after process cleanup, GPU-memory
    cleanup, and Agents-A1 serving restoration pass.

## Control-loop rule

After this addendum is visible, repeated
`m38e_postcompletion_activity_detected` heartbeats are not an admissible steady
state when the exact classification conditions can be evaluated. The next
host-capable heartbeat must report one of:

- `m38e_postcompletion_classification_in_progress`;
- `m38e_postcompletion_classification_blocked`;
- `m38e_orphaned_postcompletion_compute`;
- `m38e_postcompletion_cleanup_in_progress`;
- `m38e_finalization_audits_in_progress`;
- `m38e_completed_error_frontier_not_found`;
- `provenance-blocked`;
- `inconclusive`;
- `host_execution_authority_unavailable`.

`host_execution_authority_unavailable` may be recorded once by an agent that
cannot inspect or signal host processes. It is not permission for indefinite
status-only commits. A host-capable agent must execute this decision.

## Research-scan disposition

The current external evidence does not justify changing the frozen scientific
program:

- leakage-controlled hidden-state correctness work supports M39's existing
  nested selection, train-fold-only nuisance control, and behavioral/router
  comparator requirements, but does not establish an Agents-A1 predictor;
- counterfactual MoE-routing results support treating executed-route margins,
  loads, transitions, and fragile-token correlates as serious observation-only
  comparators, but do not authorize alternative-route sampling, router updates,
  or expert intervention in M39;
- current early-exit evidence remains unfavorable for prioritizing layer-wise
  exit on modern large MoE models before observation-only monitoring and
  model-specific intrinsic-exit feasibility are established.

The existing M39 and Q35Q amendments already encode these boundaries. No new
outcome-bearing feature, layer, threshold, intervention, or stopping rule is
added here.

## Privacy and claim boundary

Treat the repository as publicly visible. Commit aggregate states and public
repository object identities only. Raw tasks, rows, prompts, answers, outputs,
token data, telemetry, routes, expert identities, hidden states, activations,
Jacobians, VJPs, lens matrices, per-example scores, process evidence, model
artifacts, local paths, environment values, and secret-linked provenance remain
private and uncommitted.

This addendum resolves an engineering deadlock. It does not establish a
completed-error predictor, Jacobian Lens, router mechanism, semantic monitor,
causal repair, safe early exit, safe truncation, intervention policy, or
production utility.
