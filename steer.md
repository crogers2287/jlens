# steer.md — close the M38E post-launch ownership gap; freeze the complete retry envelope; leave attempt 1 untouched

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `02a483b6a74687ccf31b87e491e68a563e9a8398` only where explicitly
amended below. That steer and every predecessor remain incorporated in full,
including all sealed-data, verifier, privacy, provenance, exact-set,
cap-escalation, resource, claim-boundary, retry-limit, production-gating,
repository-hygiene, and stop rules. No frozen result may be re-evaluated or
tuned. No M38E task, family, band, seed, count, threshold, verifier, sampling
setting, output-cap rule, power gate, comparator gate, retry limit, or
production gate may be weakened.

## Current state

- Remote `master` before this steer was
  `049c033a7c3d92d1287e9b70e08e2898b6d7ef14`.
- M38E official attempt one remains valid and must continue undisturbed. The
  latest aggregate heartbeat reports 38 rows, a live driver, 52/52 fresh core
  tests, and the first live execution of the frozen cap-escalation rule:
  `mod_chain` band 1 exceeded the 2048 truncation threshold, ran the exact
  deterministic six-task 4096 pilot, and advanced according to the frozen
  rule. This is in-progress development capture, not a scientific result.
- Commit `71f04c5413bb837524fd54a5b9fb38460c74ed83` correctly made retry-budget
  reservation crash-consistent, bound the model pointer to attempt-one
  evidence, distinguished unreadable process evidence from death, and removed
  the five explicitly recorded protocol variables when they were originally
  absent. It did not launch a retry and did not touch attempt one.
- Source inspection finds remaining post-launch ownership and execution-envelope
  defects. They do not invalidate attempt one. They block any possible retry
  until corrected and tested.
- M36T remains scoped exactly as frozen: T-H3 establishes verifier-backed
  adaptive tool/compute allocation only on its deterministic population. T-H1
  and T-H2 are not established.
- M37J-C remains blocked by its frozen disabled-path parity result. Its memory,
  runtime, and observability measurements are descriptive technical facts only.
- M38E has no outcome. No completed-error predictor, safe truncation rule,
  early-exit rule, semantic monitor, causal repair, activation steering, route
  intervention, or production utility is established.

## Remaining retry-control defects

The active first attempt is not affected. These defects apply only if attempt
one actually fails and the single remaining retry authorization is still
available.

### 1. Durable budget reservation does not yet provide durable process ownership

The controller durably writes attempt two as `reserved`, then calls `Popen`,
but does not durably record the child PID/PGID until after up to ten seconds of
`/proc` polling and exec recognition. If the controller dies after `Popen` and
before the `running` record, the child may continue while the private record
contains no PID. The controller lock is then released. The retry budget remains
correctly consumed, but the possible official writer is unowned, unmonitored,
and not safely signalable.

The same gap occurs when exec recognition times out. The code returns blocked
without proving the child is dead, without terminating its exact process group,
and without recording a terminal process state. A slow or unexpected-but-live
child may therefore survive after the controller exits.

Budget conservatism is necessary but insufficient. A retry process must never
be allowed to reach the scientific driver unless its PID/PGID, nonce, exact
launcher identity, expected exec identity, and lock ownership are already
recorded durably.

### 2. The retry launcher is taken from the mutable control checkout

The retry command invokes `CONTROL/scripts/m38e_launch.py`. The immutable-source
preflight validates the detached execution checkout, but the launcher that
performs `chdir + setsid + exec` is neither loaded from that checkout nor bound
to a frozen cryptographic digest. A later control-plane edit can therefore
change executable path, arguments, environment, process-group behavior, or
working directory after the scientific source preflight has passed.

The launcher and preflight artifacts used for a retry must be immutable or
cryptographically pinned and reverified immediately before process creation.
Control-branch agreement or a clean working tree is not sufficient.

### 3. The five-key environment schema is not a complete execution envelope

`build_retry_environment()` inherits the entire current ambient environment and
only overwrites or removes five named keys. This does not establish exact
runtime identity. Variables outside that tuple can change CUDA, NCCL, PyTorch,
vLLM, tokenization, threading, library loading, determinism, cache behavior, or
model resolution. Examples include `VLLM_*`, `CUDA_*`, `NCCL_*`, `TORCH_*`,
`PYTORCH_*`, `CUBLAS_*`, `OMP_*`, `MKL_*`, `HF_*`, `TRANSFORMERS_*`,
`TOKENIZERS_*`, `PYTHONHASHSEED`, and `LD_LIBRARY_PATH`.

While attempt one is alive and its `/proc` identity is still proven, capture its
complete process environment privately, with exact bytes or a canonical map and
cryptographic digest. Do not commit it. A retry must be launched from that
recorded environment rather than from `dict(os.environ)`. Missing, unreadable,
non-reconstructable, or conflicting evidence blocks. Do not guess a smaller
schema after attempt one has exited.

## Binding handling of active attempt one

1. Do not stop, signal, restart, reparent, attach a new supervisor to, or mutate
   the active first-attempt driver or its execution tree.
2. Do not invoke the retry controller or any superseded supervisor while attempt
   one is alive.
3. Continue aggregate-only heartbeat monitoring. Public status may contain row
   count, aggregate phase, freshness, aggregate process health, and test count
   only.
4. Capture any additional retry identity evidence only by read-only inspection
   of the already-running process and store it only in the existing private
   operational record. No private value or digest-to-secret mapping may be
   committed.
5. If attempt one completes, finalize only through the existing exact-set,
   cap-escalation, verifier, privacy, cleanup, and result gates.
6. If attempt one exits nonzero, preserve the private ledger byte-for-byte and
   block until every correction and test below passes.

## Required retry-controller correction

This is control-plane-only. It may not alter the executing driver, scientific
source, task generation, private rows, manifest, thresholds, verifier, sampling
settings, output caps, cap-escalation logic, eligibility arithmetic, power gate,
result gate, or claim boundary.

A retry is authorized only if all prior requirements and all of the following
hold:

- Acquire the exclusive nonblocking run-ID lock before loading mutable launch
  state, then reload and validate the private record under the lock.
- Preserve the permanent two-total-attempt cap and pre-`Popen` durable
  reservation. A consumed retry is never refunded.
- Replace the unguarded launch window with a parent/child handshake. The child
  may create its dedicated session/process group but must block on a private
  inherited pipe, socketpair, eventfd, or equivalent barrier before executing
  the scientific driver.
- Immediately after process creation, durably update the consumed attempt-two
  record to `launching` with the exact child PID/PGID, nonce, expected command,
  execution directory, pinned launcher digest, pinned preflight digest, source
  identity, and environment digest. File and parent-directory `fsync` remain
  mandatory.
- Release the child barrier only after that durable `launching` record is
  reread and exact-validated. If the parent dies before release, the child must
  exit without exec and without touching the private scientific ledger.
- Keep the run-ID lock alive across controller failure by transferring or
  inheriting a dedicated lock descriptor into the guarded launcher/driver, or
  use an equivalent kernel-enforced guardian whose death semantics are tested.
  A surviving driver may not be accompanied by an unlocked run identity.
- After exec, prove exact PID/PGID, command, cwd, interpreter, source, model,
  launcher, environment, tensor-parallel, worker override, and sampling
  identity; then atomically advance the same nonce-bound record to `running`.
- On exec timeout, launcher error, ambiguous `/proc` evidence, or controller
  exception after process creation, do not simply return. Re-prove and terminate
  only the exact owned process group, wait for confirmed death, and durably
  record a consumed terminal or ambiguous state. If exact ownership cannot be
  proved, leave the PID/PGID recorded, block permanently, and require manual
  private investigation; never signal by name or host-global search.
- Invoke only a launcher and preflight artifact whose exact bytes are pinned by
  digest in the private amendment and reverified immediately before `Popen`.
  Prefer an immutable detached control-plane worktree. Any mismatch blocks.
- Capture the complete attempt-one process environment privately while it is
  still readable. Build retry `env` solely from that exact recorded map. Do not
  inherit ambient keys. Exact reconstruction failure blocks.
- Preserve the immutable scientific execution worktree and exact-ledger
  preflight. Preserve the private ledger in place; never copy, normalize,
  rewrite, compact, sort, redact in place, or regenerate rows.
- Commit only aggregate operational status. PIDs, paths, environment values,
  model pointers, rows, prompts, outputs, task IDs, pilot membership, token data,
  and telemetry remain uncommitted.

## Required tests before any retry

Add deterministic tests proving:

1. parent death after `Popen` but before durable PID registration cannot allow
   the child to exec the scientific driver or touch the ledger;
2. the child remains behind the barrier until a nonce-bound `launching` record
   with exact PID/PGID is durably written and reread;
3. a controller crash after barrier release leaves the run-ID lock held while
   the driver survives;
4. exec-recognition timeout kills and reaps only the exact owned process group,
   or records an ambiguous permanent block when ownership cannot be proved;
5. no failure path leaves a live unrecorded or PID-less child;
6. changing the mutable control launcher or preflight bytes blocks even when the
   immutable scientific checkout and ledger are unchanged;
7. the retry environment equals the complete recorded attempt-one environment,
   ambient injection cannot leak, and missing private evidence blocks;
8. reserved, launching, running, exited, failed, or ambiguous attempt-two state
   permanently consumes the sole retry and no state permits a third launch;
9. two simultaneous controllers cannot both reserve, register, release, or
   supervise a child;
10. source, ledger, model, runtime, environment, launcher, preflight, override,
    tensor-parallel, or sampling mismatch blocks before driver exec;
11. the full repository test suite, recursive privacy audit, and
    `check_commit_safe.py` remain green.

Commit the corrected controller, launcher/guardian, tests, and an aggregate-only
amendment. Do not launch a retry merely because the code is committed. Verify
the exact remote head, then use it only if attempt one has actually failed.

## Agents-A1 scaling path

The official Agents-A1 repository still reports only the 35B-A3B release and
its 2026-07-08 notice that a 4B model is forthcoming. The official model card
identifies the released architecture as `qwen3_5_moe`. Do not substitute
Agents-K1 or an unofficial checkpoint under the Agents-A1 name.

The technically credible sequence remains:

1. complete M38E without changing its in-flight scientific protocol;
2. retain observation-only router and hidden-state telemetry on the pinned 35B
   runtime as the near-term full-model path;
3. preregister a separate scaling study comparing full Jacobian construction,
   low-rank target-space VJPs, and bounded finite-difference probes on a smaller
   comparable MoE or the official Agents-A1 4B checkpoint if released;
4. explicitly phase-localize future telemetry and probes into prefill versus
   autoregressive decode. `Behavioral Steering in a 35B MoE Language Model via
   SAE-Decoded Probe Vectors` (`arXiv:2603.16335`) reports that Qwen3.5-35B-A3B
   behavioral commitments were steerable during prefill while decode-only
   steering had no effect. Treat this as a comparator-generating observation,
   not an Agents-A1 result. Require independent replication and verifier-backed
   predictive-increment tests before any claim;
5. require approximation-error, rank-stability, finite-value, phase-localized
   parity, memory, runtime, privacy, and predictive-increment gates;
6. only then run a one-sequence 35B backward memory smoke on rented high-memory
   hardware with frozen abort thresholds and no scientific claims;
7. advance from the smoke only through a separately frozen fit and validation
   protocol. Memory success is not an interpretability, prediction, stopping,
   intervention, or production result.

Jacobian Scopes (`arXiv:2601.16407`) remains the strongest concrete engineering
lead for reduced-target VJPs and finite-difference Jacobian quadratic-form
estimation. Hidden Error Awareness (`arXiv:2605.09502`) supports diagnostic
hidden-state prediction while failing to establish causal repair. When Are
Experts Misrouted? (`arXiv:2605.07260`) supports counterfactual router analysis,
not treating router confidence or expert identity as a correctness label. The
Diminishing Returns of Early-Exit Decoding (`arXiv:2603.23701`) cautions that
modern MoEs are generally less early-exit-friendly than dense transformers.
None changes M38E or authorizes intervention, stopping, or production use. No
actionable r/LocalLLaMA implementation lead has been verified against a primary
source.

## Claim, privacy, and production boundary

GitHub reports this repository as public. Treat every committed byte as
externally visible. Never commit private prompts, answers, operands, outputs,
token text or IDs, per-task labels or predictions, raw telemetry, hidden states,
activations, gradients, Jacobians, lens matrices, model weights, caches, stack
traces, local paths, private task IDs, pilot membership, PIDs, environment
values, model pointers, or private launch evidence. Public artifacts remain
aggregate-only.

The research program is not finished. M38E is in progress, M37J-C remains
blocked, the official Agents-A1 4B checkpoint is unavailable, and full 35B
backward/Jacobian feasibility is unproven. No observation, classifier, tool
policy, route edit, activation intervention, semantic monitor, truncation rule,
or early-exit rule is authorized for production by this directive.
