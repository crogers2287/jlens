# steer.md — harden M38E retry process ownership and attempt accounting; leave the active attempt untouched

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `a726b352ffc375aef4a96adc0995aebed8059346` only where explicitly
amended below. That steer and every predecessor remain incorporated in full,
including all sealed-data, verifier, privacy, provenance, exact-set,
cap-escalation, resource, claim-boundary, production-gating,
repository-hygiene, and stop rules. No frozen result may be re-evaluated or
tuned. No M38E task, family, band, seed, count, threshold, verifier, sampling
setting, output-cap rule, power gate, comparator gate, retry limit, or
production gate may be weakened.

## Current state

- Remote `master` before this steer was
  `83a9866b6fc3719ec9e3c56cb54af70e2f06b67c`.
- The active first M38E attempt remains valid and must continue undisturbed. The
  latest heartbeat reports 18 official rows, uniform official row identity,
  recent progress, and 52/52 fresh core tests. This is an in-progress
  development capture, not a scientific result.
- Commit `e147de6dfe584d9be1f3c8f7e3d32e8c917df6fa` correctly separated the
  mutable control checkout from an immutable detached execution worktree and
  added exact source/ledger preflight checks. That closes the moving-`master`
  identity defect identified by `a726b35`.
- M36T remains scoped exactly as frozen: T-H3 establishes verifier-backed
  adaptive tool/compute allocation only on its deterministic population. T-H1
  and T-H2 are not established, and no router, hidden-state, semantic, or
  Jacobian mechanism was established by M36T.
- M37J-C remains blocked by its frozen disabled-path parity result. Its resource
  and overhead measurements are descriptive technical observations only.
- M38E has no outcome yet. No completed-error predictor, safe truncation rule,
  early-exit rule, semantic monitor, causal repair, activation steering, or
  production utility is established.

## Newly identified retry-control defects

Source review of the control supervisor landed in `e147de6` found that the
immutable-source preflight is necessary but not sufficient. The active first
attempt is not affected. The replacement retry controller is not authorized to
launch until the defects below are corrected and tested.

### 1. The supervisor does not own a uniquely identified driver process group

The supervisor starts the driver through a background subshell:

`( cd "$EXEC_DIR" && setsid "$PY" src/m38e_dev_sweep.py ... ) &`

The recorded `$!` is the background shell process, not a proven driver PID and
process-group identity. The stall path then discards that PID and uses
host-global `pgrep -f "m38e_dev_sweep.py" | head -1`. This can select an
unrelated process, including the still-running original attempt, another test,
or another user's process, and then signal that process group. This directly
violates the binding rule that the active first attempt must not be disturbed.

No production or research supervisor may use `pgrep`, `pkill`, process-name
matching, `head -1`, or another host-global search to identify the process it
owns.

### 2. The repaired supervisor resets the attempt counter

The original official attempt has already consumed attempt one. The replacement
supervisor still loops over `1 2`. If invoked after the original process exits,
it could launch two additional executions, producing three total attempts. The
frozen policy authorizes the original attempt plus at most one retry. A control
rewrite may not reset that budget.

### 3. There is no exclusive single-writer gate

The current supervisor does not prove that the original driver is dead before a
retry, and it does not acquire an exclusive run lock bound to the official run
identity and ledger. A mistaken invocation could create two writers against the
same private JSONL ledger. Exact row validation before launch does not prevent a
concurrent append race after validation.

### 4. Runtime identity is not fully enforced by the new preflight

The preflight verifies detached source identity, tracked provenance files, the
model pointer's existence, and exact row identity. The incorporated steer also
requires the same environment identity, runtime, worker override,
tensor-parallel configuration, sampling settings, and immutable model revision
as the first attempt. The preflight docstring says the frozen model pointer is
compared with the control checkout, but the implementation only checks that the
execution pointer exists. Row validation binds the model revision and override
hash, but it does not by itself prove the complete runtime/environment identity.

If the original launch identity cannot be reconstructed from an existing
private launch record without exposing private data, retry must block. Do not
invent, infer loosely, or silently substitute an environment.

## Binding handling of the active first attempt

1. Do not stop, signal, restart, reparent, attach a new supervisor to, or mutate
   the active first-attempt driver or its execution tree.
2. Do not invoke `scripts/m38e_supervisor.sh` while the first attempt is alive.
3. Continue aggregate-only heartbeat monitoring. A heartbeat may report row
   count, freshness, test count, and aggregate process health only.
4. If the first attempt completes, finalize only through the existing exact-set,
   cap-escalation, verifier, privacy, cleanup, and result gates.
5. If the first attempt exits nonzero, preserve the private ledger byte-for-byte
   and block until the corrected one-retry controller passes every requirement
   below.

## Required retry-controller correction

The correction is control-plane-only. It may not alter the executing driver,
scientific source, task generation, private rows, manifest, thresholds,
verifier, sampling settings, output caps, cap-escalation logic, or result gates.

A retry controller is authorized only if all of the following are implemented:

- Launch the driver through a dedicated minimal launcher that performs
  `chdir`, `setsid`, and `exec` so that one exact PID is also the exact owned
  process-group ID. Record that PID/PGID in a private operational record before
  monitoring begins.
- Signal only the negative of that recorded PGID after proving it still belongs
  to the expected executable, execution directory, source SHA, and run identity.
  Never rediscover it by process name.
- Acquire an exclusive nonblocking lock keyed to the row-bound run ID before
  preflight and hold it for the full lifetime of the retry. Refuse launch if the
  lock is held.
- Prove no original or other driver for the same run identity is alive before
  launch. Ambiguity blocks.
- Read an explicit persisted attempt record showing that the original launch
  consumed attempt one. Permit zero or one additional launch only. A second
  retry request must block permanently for this run.
- Run immutable-source and exact-ledger validation after acquiring the lock and
  immediately before engine construction.
- Verify the exact model pointer, immutable model revision, Python executable,
  runtime/library identity, worker override, tensor-parallel configuration,
  sampling environment, and all protocol-relevant environment variables against
  the original private launch record. Missing evidence blocks.
- Preserve the private ledger in place. Do not copy, normalize, rewrite, compact,
  sort, redact in place, or regenerate rows.
- Write only aggregate operational status to committed files. PID values,
  private paths, environment values, rows, prompts, outputs, task IDs, and
  telemetry remain uncommitted.

## Required tests before any retry

Add deterministic tests proving:

1. the launched process PID is the owned process-group ID and remains stable
   through `exec`;
2. a decoy `m38e_dev_sweep.py` process is never selected or signaled;
3. a stall terminates only the exact owned process group;
4. a live original attempt blocks a retry before model loading;
5. two simultaneous supervisors cannot both acquire the run lock;
6. the existing original attempt is counted, so the replacement controller can
   launch at most one additional attempt;
7. an already-consumed retry budget blocks permanently;
8. source, ledger, model, runtime, environment, override, tensor-parallel, or
   sampling identity mismatch blocks before engine construction;
9. newer control-checkout commits do not move or alter the execution checkout;
10. a simulated interrupted run resumes from the exact row-bound source and
    exact ledger or blocks cleanly;
11. no private value enters logs, test output, diffs, status files, or committed
    artifacts;
12. the full repository test suite, recursive privacy audit, and
    `check_commit_safe.py` remain green.

Commit the corrected controller, launcher, tests, and an aggregate-only
operational amendment. Do not launch a retry merely because the code was
committed. Verify the exact remote head, then execute the corrected preflight
only if the original attempt has actually failed and the single remaining retry
is required.

## Agents-A1 scaling path remains unchanged

The official InternScience repository still announces a forthcoming Agents-A1
4B model, while the official organization currently exposes only the 35B BF16,
FP8, and GGUF Agents-A1 variants. Do not substitute Agents-K1 or an unofficial
model under the Agents-A1 name.

The technically credible sequence remains:

1. complete M38E without changing its in-flight scientific protocol;
2. retain observation-only router and hidden-state telemetry on the pinned 35B
   runtime as the near-term full-model path;
3. preregister a separate scaling study comparing full Jacobian construction,
   low-rank target-space VJPs, and bounded finite-difference probes on a smaller
   comparable MoE or the official Agents-A1 4B checkpoint if released;
4. require approximation-error, rank-stability, finite-value, parity, memory,
   runtime, privacy, and predictive-increment gates;
5. only then run a one-sequence 35B backward memory smoke on rented high-memory
   hardware with frozen abort thresholds and no scientific claims.

Jacobian Scopes (`arXiv:2601.16407`) remains the strongest concrete engineering
lead for top-k target-space VJPs and finite-difference Jacobian quadratic-form
estimation. When Are Experts Misrouted? (`arXiv:2605.07260`) and Awakening
Dormant Experts (`arXiv:2604.14246`) support counterfactual router analysis as a
future comparator, not treating router confidence or expert identity as a
correctness label. The Diminishing Returns of Early-Exit Decoding
(`arXiv:2603.23701`) continues to argue against assuming that a modern MoE is
naturally early-exit-friendly. None of these sources changes M38E or authorizes
intervention, stopping, or production use. No actionable r/LocalLLaMA lead was
verified by a primary source in this scan.

## Claim, privacy, and production boundary

GitHub reports this repository as public. Treat every committed byte as
externally visible. Never commit private prompts, answers, operands, outputs,
token text or IDs, per-task labels or predictions, raw telemetry, hidden states,
activations, gradients, Jacobians, lens matrices, model weights, caches, stack
traces, local paths, private task IDs, cap-pilot membership, PIDs, or environment
values. Public artifacts remain aggregate-only.

The research program is not finished. M38E is in progress, M37J-C remains
blocked, the official Agents-A1 4B checkpoint is unavailable, and full 35B
backward/Jacobian feasibility is unproven. No observation, classifier, tool
policy, route edit, activation intervention, semantic monitor, truncation rule,
or early-exit rule is authorized for production by this directive.
