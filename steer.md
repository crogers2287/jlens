# steer.md — close remaining M38E retry ownership and source-identity gaps; preserve attempt 1

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `0821351f75d1eff144112b26a75f65ed3b71ed7c` only where explicitly
amended below. That steer and every predecessor remain incorporated in full,
including every sealed-data, verifier, privacy, provenance, exact-set,
cap-escalation, resource, claim-boundary, retry-limit, production-gating,
repository-hygiene, and stop rule. No frozen scientific result may be
re-evaluated or tuned. No M38E task, family, band, seed, count, threshold,
verifier, sampling setting, output-cap rule, power gate, comparator gate, retry
limit, or production gate may be weakened.

## Current state

- Remote `master` before this steer was
  `a20870898df6b2939573c2be851c49f5fbb152b6`.
- M38E official attempt one remains valid and must continue undisturbed. The
  latest aggregate heartbeat reports 47 rows: 41 official-2048 rows and the
  frozen six-row 4096 pilot, with `mod_chain` band 2 at 17/24, uniform official
  identity, a live driver, recent progress, and 52/52 fresh core suites. This is
  in-progress development capture, not a scientific result.
- Commit `fa000fd3162dff8d7e6126db5bbf3c5682cb6cc6` correctly added a
  pre-exec barrier, durable nonce-bound launching record, inherited run lock,
  pinned launcher/preflight bytes, complete private attempt-one environment
  capture, and consumed terminal states. It did not launch a retry and did not
  touch attempt one.
- Source inspection finds additional fail-open or false-resume paths in the
  retry control plane and one source-provenance gap that must be audited before
  M38E finalization. These findings do not authorize interruption of attempt one.
- M36T remains scoped exactly as frozen: T-H3 establishes verifier-backed
  adaptive tool/compute allocation only on its deterministic population. T-H1
  and T-H2 are not established.
- M37J-C remains blocked by its frozen disabled-path parity result. Its memory,
  runtime, and observability measurements are descriptive technical facts only.
- M38E has no outcome. No completed-error predictor, safe truncation rule,
  early-exit rule, semantic monitor, causal repair, activation steering, route
  intervention, or production utility is established.

## Remaining control-plane defects

The active first attempt must not be modified. Items 1–4 apply to any possible
retry. Item 5 is a read-only integrity audit required before finalizing attempt
one or launching a retry.

### 1. Explicit `LOCK_UN` defeats inherited-lock survival

The child inherits the same open file description that holds the run-ID
`flock`. Closing the controller's duplicate descriptor preserves the lock while
the child survives, which the current test covers. The controller's `finally`
block instead calls `flock(..., LOCK_UN)` before closing. An explicit unlock on
one duplicate releases the shared lock, including for the inherited child.

This is safe only on the narrow normal path where the child has already exited.
It is unsafe after an exception or ambiguous termination path: a surviving
launcher or driver can be left alive with an unlocked run identity. The current
lock-survival test does not exercise explicit unlock semantics.

After the lock descriptor is inherited, the controller must never call
`LOCK_UN`. It must close only its own descriptor. The lock must remain held by
the child until the child's last inherited descriptor closes. If the child is
not proven dead, no cleanup path may unlock the run identity.

### 2. `terminate_owned(..., expected=None)` can signal an unrelated process group

The current failure paths call `terminate_owned(pid, None)`. That permissive
mode accepts any readable process at the numeric PID and sends group signals
without proving the expected launcher or driver command, cwd, session, process
start time, or `PGID == PID`. PID/PGID reuse between checks can therefore target
an unrelated process group. The second SIGKILL is sent after a five-second sleep
without re-proving ownership.

There must be no permissive termination mode. Immediately after `Popen`, capture
and durably bind the child PID, PGID, SID, `/proc/<pid>/stat` start time,
nonce, exact guarded-launcher command, cwd, and pinned launcher digest while the
child is still behind the barrier. Use a pidfd for liveness and PID-reuse
resistance where supported. Before every signal, including escalation from TERM
to KILL, re-prove the exact start time, session, group, command phase
(pre-exec launcher or post-exec driver), and cwd. Any mismatch, unreadable
field, vanished leader with an unproven group, or unavailable required evidence
is an ambiguous permanent block; do not signal.

### 3. `close_fds=False` leaks the controller's inheritable descriptor table

The guarded launch intentionally needs only the barrier descriptor and run-lock
descriptor in addition to standard streams. `close_fds=False` allows every other
inheritable controller descriptor to cross into the launcher and then the
scientific driver. That violates the claimed complete execution envelope and can
carry unrelated locks, sockets, pipes, or files into the retry.

Launch with `close_fds=True` and an exact `pass_fds=(barrier_fd, lock_fd)`
allowlist. Standard streams may be supplied only through explicit
`stdin`/`stdout`/`stderr` arguments. Before exec, the guarded launcher must verify
that no unexpected descriptor is open beyond standard streams, the barrier, the
run lock, and any explicitly documented interpreter-internal descriptor. Close
the barrier before exec. Commit no descriptor numbers or private paths.

### 4. Preflight and runtime checks use the wrong interpreter/environment

The retry environment is reconstructed from attempt one only after the pinned
preflight has already run. The preflight and `verify_runtime_identity()` are
invoked through the controller's `sys.executable` and ambient environment.
`verify_runtime_identity()` imports `vllm` and `torch` without passing the
recorded retry environment. It can therefore validate one package resolution
while the retry driver loads another through the exact recorded `PATH`,
`PYTHONPATH`, library path, or environment prefix.

Reconstruct and digest-verify the complete attempt-one environment before any
Python or package-dependent preflight. Run the pinned preflight and every runtime
probe with the original recorded Python executable and that exact environment.
Bind the original executable by resolved `/proc/<attempt-one-pid>/exe`, file
identity, and private SHA256 captured read-only while attempt one is alive.
Missing or conflicting executable evidence blocks. Runtime probes must record
and compare package version plus resolved module/distribution origin under the
same interpreter and environment that will launch the retry. The controller's
ambient interpreter may orchestrate file I/O only; it may not establish
scientific runtime identity.

### 5. Tracked-clean provenance ignores untracked importable files

Both `source_provenance()` and the immutable retry preflight use
`git status --porcelain --untracked-files=no`. The scientific driver executes
with `src/` on `sys.path`; an untracked module or package in an importable path
can shadow a tracked module or installed dependency while every committed-file
hash still passes.

Do not mutate the active execution worktree. Perform a read-only audit while
attempt one runs or immediately after it exits:

- enumerate all untracked files and symlinks in the execution checkout;
- resolve every import root supplied by the exact attempt-one environment;
- prove that no untracked file is importable or executable by the driver;
- allow only an explicit private operational-data allowlist outside import and
  execution roots, including the exact official ledger and approved private
  launch records;
- publish only an aggregate pass/block result.

If any untracked importable/executable path exists, preserve it and the ledger
unchanged, block M38E finalization, and require private forensic review. Do not
delete or normalize evidence. A retry preflight must use
`--untracked-files=all` plus a filesystem/import-root audit and fail on every
unapproved path or symlink.

## Binding handling of active attempt one

1. Do not stop, signal, restart, reparent, attach a new supervisor to, or mutate
   the active first-attempt driver, environment, worktree, model cache, ledger,
   or process tree.
2. Do not invoke the retry controller or any superseded supervisor while attempt
   one is alive.
3. Continue aggregate-only heartbeat monitoring. Public status may contain row
   count, aggregate phase, freshness, aggregate process health, test count, and
   aggregate integrity-audit pass/block state only.
4. Read-only capture of retry identity evidence is permitted only into the
   existing private operational record. Never commit PIDs, process start times,
   descriptor numbers, paths, environment values, executable hashes, model
   pointers, or digest-to-secret mappings.
5. Before scientific finalization, require exact-set validation, cap-escalation
   completion, verifier gates, privacy audit, cleanup gates, and the new
   aggregate untracked-import audit.
6. If attempt one exits nonzero, preserve its private ledger byte-for-byte and
   block until every retry correction and test below passes.

## Required correction and tests before any retry

This work is control-plane-only. It may not alter the scientific driver, task
generation, private rows, manifest, thresholds, verifier, sampling, output caps,
cap-escalation logic, eligibility arithmetic, power gate, result gate, or claim
boundary.

Implement and deterministically test all prior requirements plus:

1. explicit `LOCK_UN` is never executed after the lock descriptor has been
   inherited; injected controller failure after barrier release leaves the lock
   held while the child survives;
2. closing the parent's duplicate preserves the lock, while the final child
   close releases it;
3. no termination path accepts `expected=None` or equivalent permissive
   ownership;
4. PID reuse, PGID reuse, SID mismatch, start-time mismatch, command-phase
   mismatch, cwd mismatch, and unreadable process evidence all block without a
   signal;
5. ownership is re-proved immediately before both TERM and KILL; a decoy process
   created between the two signals is untouched;
6. `close_fds=True` with an exact pass-fd allowlist prevents an injected
   inheritable decoy descriptor from reaching the launcher or driver;
7. the pinned preflight and package probes execute under the original Python and
   complete recorded environment, and ambient `PATH`, `PYTHONPATH`, or library
   injection cannot affect their result;
8. changing the original Python binary identity, resolved package origin,
   launcher bytes, preflight bytes, source, ledger, model pointer, override,
   tensor-parallel setting, worker mode, or sampling identity blocks before
   scientific exec;
9. untracked importable files and symlinks block, while only the explicit private
   non-importable allowlist passes;
10. two simultaneous controllers cannot reserve, register, release, signal, or
    supervise the same run;
11. every attempt-two state permanently consumes the sole retry and no crash or
    exception permits a third launch;
12. full repository tests, recursive privacy audit, and
    `check_commit_safe.py` remain green.

Commit the corrected controller, guarded launcher, preflight, tests, and an
aggregate-only amendment. Do not launch a retry merely because the code is
committed. Verify the exact remote head, then use the retry only if attempt one
has actually failed and every private identity check passes.

## Agents-A1 scaling path

The official Agents-A1 repository still reports the released 35B-A3B model and
its 2026-07-08 notice that a 4B model is forthcoming. The official Hugging Face
collection still lists only 35B BF16/FP8/GGUF variants. Do not substitute
Agents-K1 or an unofficial checkpoint under the Agents-A1 name.

A newly incorporated primary-source comparator is `Polysemantic Experts,
Monosemantic Paths: Routing as Control in MoEs` (`arXiv:2604.17837`). It derives
a parameter-free orthogonal decomposition of each MoE residual state into the
subspace spanned by router weights, which is causally sufficient for the current
routing logits, and a router-blind complement. Its evidence suggests that
multi-layer routing trajectories and rotating control subspaces are more useful
units than human-labeled individual experts.

This supports a technically cheap, observation-only Agents-A1 comparator before
full Jacobian fitting, but it establishes no Agents-A1 result and authorizes no
intervention. After M38E is complete, preregister a separate study that:

1. computes router-visible and router-blind projection summaries at frozen
   selected layers without backpropagation;
2. records phase-localized prefill versus autoregressive-decode features;
3. compares path/transition features, control-subspace energy, adjacent-layer
   control rotation, router logits, and existing hidden-state baselines;
4. tests only verifier-labeled predictive increment and calibration under frozen
   train/validation separation;
5. retains raw hidden states, routes, paths, token data, and per-example features
   privately and publishes aggregates only;
6. prohibits semantic labels for individual experts and treats path semantics as
   an empirical hypothesis requiring independent validation;
7. requires parity, finite-value, memory, runtime, privacy, and predictive-
   increment gates before the feature family can inform the later Jacobian
   approximation study.

The broader scaling sequence remains:

1. finish M38E unchanged;
2. retain observation-only router and hidden-state telemetry on the pinned 35B
   runtime;
3. preregister the router-control/path comparator above;
4. compare full Jacobians, reduced-target VJPs, and bounded finite-difference
   probes on a smaller comparable MoE or the official Agents-A1 4B checkpoint if
   released;
5. require approximation-error, rank-stability, finite-value, phase-localized
   parity, memory, runtime, privacy, and predictive-increment gates;
6. only then run a one-sequence 35B backward memory smoke on rented high-memory
   hardware with frozen abort thresholds and no scientific claims;
7. advance only through a separately frozen fit and validation protocol.

Jacobian Scopes (`arXiv:2601.16407`) remains the strongest concrete engineering
lead for reduced-target VJPs and finite-difference Jacobian estimates. Hidden
Error Awareness (`arXiv:2605.09502`) supports diagnostic prediction but not
causal repair. When Are Experts Misrouted? (`arXiv:2605.07260`) supports
counterfactual router analysis, not router confidence as a correctness label.
The Diminishing Returns of Early-Exit Decoding (`arXiv:2603.23701`) continues to
require direct verifier-backed stopping evidence for modern MoEs. No actionable
r/LocalLLaMA implementation lead has been verified against a primary source.

## Claim, privacy, and production boundary

GitHub reports this repository as public. Treat every committed byte as
externally visible. Never commit private prompts, answers, operands, outputs,
token text or IDs, per-task labels or predictions, raw telemetry, hidden states,
activations, gradients, Jacobians, lens matrices, model weights, caches, stack
traces, local paths, private task IDs, pilot membership, PIDs, process start
times, environment values, descriptor numbers, model pointers, executable
hashes, or private launch evidence. Public artifacts remain aggregate-only.

The research program is not finished. M38E is in progress, M37J-C remains
blocked, the official Agents-A1 4B checkpoint is unavailable, and full 35B
backward/Jacobian feasibility is unproven. No observation, classifier, tool
policy, route edit, activation intervention, semantic monitor, truncation rule,
or early-exit rule is authorized for production by this directive.
