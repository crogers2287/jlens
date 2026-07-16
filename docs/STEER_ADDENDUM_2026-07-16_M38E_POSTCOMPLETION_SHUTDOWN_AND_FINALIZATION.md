# Binding steer addendum — M38E post-completion shutdown and finalization

Date: 2026-07-16

This is an executive program-control decision. It incorporates `steer.md`,
`CODEX_AUTOSTEER.md`, and every existing M38E sealed-data, exact-set,
escalation, verifier, provenance, privacy, dependency, resource, cleanup,
commit-safety, claim-boundary, retry, and production gate. It supersedes prior
"do not disturb the active attempt" language only for the completed,
write-idle M38E driver described below. It does not change any scientific
population, row, task, seed, cap, threshold, verifier, model, outcome rule, or
audit requirement.

## Decision basis

The public aggregate status at remote head
`5df64eaac07ece0acac93defa7c882f0e2d26841` records:

- all 288/288 official rows complete across the frozen 12 cells;
- 94 pilot rows, zero full-band 4096 reruns, and 382 total execution rows;
- no active-attempt blocker;
- no ledger change for approximately 30 hours;
- a lingering-idle driver after completion;
- 324/324 fresh pre-commit tests and a clean commit-safety result.

The original non-interference rule protected an incomplete healthy attempt.
It must not be interpreted as requiring indefinite retention of a completed,
write-idle process. Waiting for another human approval is no longer a valid
program blocker.

## Binding operator decision

No further operator approval is required. On the next host-capable control
cycle, perform exactly one bounded post-completion cleanup sequence:

1. Privately confirm from process and file metadata only that the official
   ledger remains unchanged and no generation call, row append, verifier call,
   or GPU kernel attributable to M38E is active. Do not open, print, copy, or
   commit private rows, prompts, outputs, tokens, routes, telemetry, paths,
   identifiers, or environment values.
2. If any genuine row write or generation work is active, stop this cleanup
   sequence and record the aggregate blocker
   `m38e_postcompletion_activity_detected`. Do not signal the process and do
   not rerun anything.
3. Otherwise request graceful termination of the top-level M38E driver process
   group once. Allow a bounded 120-second grace period for runtime and worker
   cleanup.
4. If the process group remains after the grace period, privately reconfirm
   that the ledger is unchanged and no M38E GPU work is active. Then terminate
   the stale process group forcibly once. Record only the aggregate condition
   `m38e_postcompletion_forced_cleanup`; never commit process identifiers,
   command lines, host details, paths, or signal evidence.
5. Do not restart, resume, repeat, repair, or extend M38E generation. The
   existing frozen ledger is the only admissible execution record.
6. Run every previously frozen finalization audit against the existing
   artifacts: exact-set, cap-escalation, verifier, provenance, execution-root,
   dependency/import/loader/native-library, model/revision, privacy, cleanup,
   resource, serving-restoration, and commit-safety audits.
7. If every required audit passes, commit the formal frozen outcome
   `m38e_completed_error_frontier_not_found` and close M38E.
8. If any required evidence is missing, contradictory, or unverifiable, commit
   the narrower scoped outcome `provenance-blocked` or `inconclusive`. Never
   manufacture a passing audit and never weaken a gate.
9. Release the dual-RTX-3090 window only after process cleanup, resource cleanup,
   and Agents-A1 serving-restoration audits pass. GPU release is an engineering
   transition, not scientific evidence.

## Heartbeat and control-loop rule

The control loop must not continue emitting repeated "awaiting operator"
heartbeats after this addendum is visible. The operator decision has been made.
The next heartbeat must report one of these aggregate states:

- `m38e_postcompletion_cleanup_in_progress`;
- `m38e_postcompletion_activity_detected`;
- `m38e_finalization_audits_in_progress`;
- `m38e_completed_error_frontier_not_found`;
- `provenance-blocked`;
- `inconclusive`;
- `host_execution_authority_unavailable`.

`host_execution_authority_unavailable` may be recorded once when the running
agent genuinely lacks host/process access. It is not permission for indefinite
status-only commits. A host-capable agent must then be assigned to execute this
steer.

## Q35Q transition

After valid M38E closure and verified GPU release, advance immediately to the
already-frozen Q35Q sequence. The next admissible work is:

1. generate the genuine tokenizer-roundtrip and text-only model-load admission
   record;
2. regenerate admission and driver manifests;
3. run the one-sequence GPTQ exact residual-input VJP gate;
4. proceed to NF4 only after an honest
   `q35q_gptq_autograd_unsupported` result;
5. run the frozen eight-sequence micro-fit only after every Phase-1 gate passes.

No Q35Q correctness-label capture, M39 capture, truncation, retry, routing
intervention, or production action is authorized by this transition.

## Privacy and claim boundary

Treat the repository as public. Commit aggregate statuses and public repository
object identities only. Raw tasks, rows, outputs, token data, hidden states,
routes, activations, expert data, Jacobians, VJPs, matrices, per-example scores,
model artifacts, local paths, process evidence, environment values, and
secret-linked provenance remain private and uncommitted.

This addendum authorizes process cleanup and frozen finalization only. It does
not establish a completed-error predictor, Jacobian Lens, router mechanism,
semantic monitor, safe early exit, safe truncation, intervention policy, or
production utility.