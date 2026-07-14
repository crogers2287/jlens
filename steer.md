# steer.md — close M38E launch, audit, and descendant-termination gaps; preserve attempt one

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `32d5918cc371aaf373f1fe3c52d4dade5cc1bf7a` only where explicitly
amended below. That steer and every predecessor remain incorporated in full,
including every sealed-data, verifier, privacy, provenance, exact-set,
cap-escalation, resource, claim-boundary, retry-limit, production-gating,
repository-hygiene, and stop rule. No frozen scientific result may be
re-evaluated or tuned. No M38E task, family, band, seed, count, threshold,
verifier, sampling setting, output-cap rule, power gate, comparator gate, retry
limit, or production gate may be weakened.

## Current state

- Remote `master` before this steer was
  `c7393461f3286f9fec452a445ee79d3991dc614b`.
- M38E official attempt one remains valid and must continue undisturbed. The
  latest aggregate heartbeat reports 66 rows, uniform official identity, a live
  driver with fresh progress, and 52/52 fresh core suites. This is in-progress
  development capture, not a scientific result.
- Commit `164b3fff238a436f0cc2ef8a9ee84b9faf778c80` correctly moved the importing
  preflight and package probes under the recorded environment and bound
  executable, added a reusable audit script, compared `torch`/`vllm` origins,
  made liveness more fail-closed, and replaced bare process-group signals with
  pidfd-based signaling. It launched no retry and did not touch attempt one.
- Source inspection finds remaining discrepancies between the claimed retry
  envelope and the code that would actually execute. They do not invalidate
  attempt one. They block only a possible retry and, where stated, M38E
  finalization.
- M36T remains scoped exactly as frozen: T-H3 establishes verifier-backed
  adaptive tool/compute allocation only on its deterministic population. T-H1
  and T-H2 are not established.
- M37J-C remains blocked by its frozen disabled-path parity result. Its memory,
  runtime, and observability measurements are descriptive technical facts only.
- M38E has no outcome. No completed-error predictor, safe truncation rule,
  early-exit rule, semantic monitor, causal repair, activation steering, route
  intervention, or production utility is established.

## Remaining control-plane defects

The active first attempt must not be modified. Every item below applies to a
possible retry. Items 4 and 5 also apply to scientific finalization.

### 1. The one-way barrier does not prove that the child established its owned session

The parent calls `Popen`, then immediately reads `/proc/<pid>` and records the
result. The launcher performs `chdir()` and `setsid()` asynchronously before it
waits on the existing one-way GO pipe. The parent does not wait for a child
READY signal and does not require, before durable registration, that PID = PGID
= SID, cwd equals the immutable execution directory, the command is the pinned
launcher phase, and `/proc/<pid>/exe` is the bound interpreter. A scheduler race
can therefore record the pre-`setsid` parent session or the pre-`chdir` working
directory and still release GO.

Replace the one-way barrier with a two-way launch handshake:

1. the child starts under the bound interpreter, performs `chdir`, `setsid`, and
   its descriptor audit;
2. the child writes exactly one READY record through a dedicated inherited pipe
   or socket and then blocks;
3. the parent waits with a bounded timeout and verifies exact PID, PGID, SID,
   cwd, command phase, kernel start time, executable identity, nonce, and open-FD
   allowlist;
4. only after that proof is durably written, fsynced, reread, and validated may
   the parent send GO;
5. EOF, timeout, malformed READY, or any mismatch consumes the retry and exits
   without scientific exec; parent death before GO must still cause child exit.

The child must not touch the scientific ledger before GO.

### 2. The executable remains pathname-racy and is not fully re-proven behind the barrier

`bind_executable()` verifies a canonical target but returns the original invoked
pathname. The preflight, probes, launcher, and driver are then started through
that alias. The guarded launcher rechecks only SHA256 and calls `execv()` on the
pathname. A symlink retarget or same-byte replacement can therefore change the
actual inode after validation while still passing the SHA-only check. The
current launcher also does not prove that the interpreter already running the
launcher is the bound executable.

Before any retry:

- invoke every subprocess by the canonical bound executable, never by the
  original alias;
- after `Popen` and before READY acceptance, verify `/proc/<pid>/exe` canonical
  target, device, inode, mode, size, and digest against the private original
  identity;
- pass the complete executable identity to the guarded launcher, not only a
  digest;
- behind the barrier, re-prove the running interpreter via `/proc/self/exe` and
  the target executable via canonical path, device, inode, mode, size, and
  digest;
- eliminate the final path lookup race by executing a pre-opened, identity-bound
  executable descriptor through a kernel-supported fd/`execveat` path, or fail
  closed if that mechanism is unavailable;
- treat alias change, symlink retarget, same-byte inode replacement, wrapper
  insertion, or any missing identity field as a permanent block.

No private path, inode, device number, or executable digest may be committed.

### 3. Recorded-process liveness is still not the full recorded identity

`driver_alive()` currently checks only command line, cwd, and start time. It does
not compare the recorded executable, SID, PGID, command phase, or state, despite
the binding requirement and the amendment's statement that liveness is exact.
A same-start-time process that execs a different binary with the same argv, or
changes process-group/session state, can be treated as the original driver.

For every record carrying a PID, require exact comparison of:

- kernel start time;
- canonical executable identity and digest;
- full argv;
- cwd;
- SID and PGID;
- expected command phase and durable state;
- run nonce and execution directory identity where applicable.

Only proven PID nonexistence or a different kernel start time may count as dead.
Any same-start-time mismatch, missing field, unreadable field, or phase/state
inconsistency is ambiguous and blocks. Add direct tests for executable, SID,
PGID, phase, and state mutation; do not satisfy this requirement with source
inspection alone.

### 4. The reusable untracked/import audit has multiple false-pass paths

The new audit is useful but is not yet the pinned deterministic boundary claimed
by the amendment:

- its own bytes are not included in `control_artifact_sha256` or checked by
  `verify_control_artifacts()`;
- it ignores return codes from both `git status` and the bound-interpreter
  `sys.path` probe, so command failure can produce an empty PASS;
- porcelain output is parsed as newline-delimited text rather than NUL-delimited
  records, so quoted, escaped, newline-containing, or unusual filenames can be
  misresolved;
- ignored files are not enumerated, even though ignored Python modules, `.pth`
  files, startup hooks, extension modules, or executables can change resolution;
- it derives Python import roots but not executable roots from `PATH` and related
  loader variables;
- it executes `git` through the recorded ambient `PATH` without binding the git
  executable identity;
- allowlisting uses broad prefix matching and can permit similarly prefixed
  names; allowlisted executable/importable artifacts outside the derived Python
  roots can still affect commands if an allowlisted directory is on `PATH`;
- external import and execution roots outside the checkout are not inventoried
  or bound.

Before retry and again immediately before finalization:

1. pin and verify the audit script itself with the launcher and preflight;
2. require successful return codes and parse machine-safe NUL-delimited output;
3. inventory tracked, untracked, ignored, symlinked, and special files in every
   checkout import or execution root;
4. derive and verify Python roots, `PATH`, library-loader paths, startup hooks,
   editable installs, namespace packages, and command resolution under the exact
   recorded environment;
5. bind every external tool used by preflight/audit by canonical executable
   identity or replace it with a byte-level implementation that needs no ambient
   command lookup;
6. use exact path allowlist entries or component-bound directory rules, never
   raw string-prefix matching;
7. fail closed on command failure, undecodable filename, permission error,
   disappearing file, symlink cycle, external root, or incomplete inventory;
8. publish only aggregate pass/block counts and preserve blocking evidence
   privately byte-for-byte.

The current one-time PASS remains a descriptive observation only. It does not
satisfy the fresh finalization audit.

### 5. Package/runtime provenance remains incomplete

`verify_runtime_identity()` compares only `torch` and `vllm` version, module
origin, and origin-file digest. It does not verify distribution metadata,
installed-file manifests, namespace/editable-install state, or the other local
and third-party packages imported by the driver, verifier, task generators, and
telemetry hooks. The prior steer explicitly required every locally imported
execution package. The amendment must not claim broader package identity than
is implemented.

A retry is permitted only if the private attempt-one record contains sufficient
original evidence to reconstruct and verify the complete execution dependency
closure. At minimum bind:

- module canonical origins and file digests for every imported execution module;
- distribution name/version, metadata origin, and installed-file manifest digest
  for every distribution in that closure;
- namespace-package roots, editable-install pointers, `.pth` effects, and native
  extension/shared-library origins;
- the exact import graph produced by the pinned preflight under the recorded
  environment.

Evidence captured after launch is not automatically equivalent to original
launch evidence. If original identity cannot be established without attaching
to or perturbing attempt one, do not attach or perturb it; block the retry.

### 6. Descendant termination can return `dead` while workers remain alive

The pidfd change protects the leader signal from PID reuse, but the current
algorithm still does not establish complete process-tree termination:

- descendants are selected only by numeric SID and a start-time inequality, not
  by a durable process-tree or cgroup membership boundary;
- unreadable descendant evidence is silently skipped;
- after TERM, if the leader exits, the KILL phase breaks before signaling
  descendants that ignored TERM;
- the final result checks only the leader and can return `dead` while surviving
  workers retain the ledger, model, GPU, or run lock.

Do not use leader death as proof that the run is dead. Preferred correction:
launch attempt two inside a dedicated cgroup-v2/systemd scope whose identity and
membership are privately bound before GO, signal through that scope, and verify
zero surviving members before reporting termination. If a trustworthy scope is
unavailable, disable automatic stall termination and record an ambiguous
permanent block for private review. A hand-enumerated session is acceptable only
if every member is durably tied to the owned process tree, every permission or
race failure blocks, TERM and KILL are applied independently of leader survival,
and zero remaining members is proven before `dead` is returned.

Tests must include a leader that exits on TERM while a child ignores TERM, a
child that forks during escalation, unreadable descendant evidence, and a decoy
outside the scope. No surviving child may be mislabeled dead or lose the run
lock boundary.

## Binding handling of active attempt one

1. Do not stop, signal, restart, reparent, attach a new supervisor to, or mutate
   the active first-attempt driver, environment, worktree, model cache, ledger,
   or process tree.
2. Do not invoke the retry controller or any superseded supervisor while attempt
   one is alive.
3. Continue aggregate-only heartbeat monitoring. Public status may contain row
   count, aggregate phase, freshness, aggregate process health, test count, and
   aggregate integrity-audit pass/block state only.
4. Read-only capture of missing retry identity evidence is permitted only into
   the existing private operational record. Never commit PIDs, process start
   times, descriptor numbers, paths, environment values, executable or package
   hashes, model pointers, or digest-to-secret mappings.
5. Before scientific finalization, require exact-set validation,
   cap-escalation completion, verifier gates, privacy audit, cleanup gates, and a
   fresh passing corrected import/execution audit.
6. If attempt one exits nonzero, preserve its private ledger byte-for-byte and
   block until every retry correction and deterministic test below passes.

## Required correction and tests before any retry

This work is control-plane-only. It may not alter the scientific driver, task
generation, private rows, manifest, thresholds, verifier, sampling, output caps,
cap-escalation logic, eligibility arithmetic, power gate, result gate, or claim
boundary.

Implement and deterministically test all prior requirements plus:

1. a child READY/parent GO handshake proves post-`setsid`, post-`chdir` ownership
   before durable launch registration;
2. PID = PGID = SID, exact cwd, command phase, start time, nonce, and running
   interpreter identity are required before GO;
3. canonical/fd-bound executable invocation prevents alias, symlink, wrapper,
   inode-replacement, and final path-lookup races;
4. `driver_alive()` checks executable, SID, PGID, phase, state, argv, cwd, and
   start time and treats every same-start mismatch as ambiguous;
5. the audit script is pinned, all subprocess return codes are enforced, and
   filename parsing is NUL-safe;
6. ignored files, symlinks, special files, PATH roots, loader roots, startup
   hooks, editable installs, and external roots cannot escape the audit;
7. audit/preflight tool executables are identity-bound and ambient PATH cannot
   substitute a fake `git`, Python, shell, or helper;
8. complete package/distribution/import-closure identity is verified or the
   retry blocks for missing original evidence;
9. leader exit before escalation cannot prevent worker KILL or produce a false
   `dead` result;
10. termination proves zero owned-scope members and leaves every decoy untouched;
11. ambiguous launch, audit, import, process, or termination evidence durably
    consumes the retry and returns without an unbounded wait or explicit lock
    release;
12. two simultaneous controllers cannot reserve, register, release, signal, or
    supervise the same run;
13. every attempt-two state permanently consumes the sole retry and no crash or
    exception permits a third launch;
14. full repository tests, recursive privacy audit, and
    `check_commit_safe.py` remain green.

Commit the corrected controller, launcher, preflight, audit, dependency-closure
logic, tests, and an aggregate-only amendment. Do not launch a retry merely
because the code is committed. Verify the exact remote head, then use the retry
only if attempt one has actually failed and every private identity check passes.

## Agents-A1 scaling path

The official Agents-A1 repository still reports only the released 35B-A3B model
and its 2026-07-08 notice that a 4B model is forthcoming. The official Hugging
Face collection was updated recently but still lists only 35B BF16, FP8, and
GGUF variants. Do not substitute Agents-K1 or an unofficial checkpoint under the
Agents-A1 name.

The observation-only router-control/path comparator remains the cheapest
technically credible next scaling step after M38E. The sequence remains:

1. finish M38E unchanged;
2. retain observation-only router and hidden-state telemetry on the pinned 35B
   runtime;
3. preregister the router-visible/router-blind control-subspace, router-expert
   geometry, and multi-layer path comparator, separating prefill from
   autoregressive decode;
4. test only verifier-labeled predictive increment and calibration over frozen
   router-logit, hidden-state, length, family, cap, and runtime baselines;
5. use leakage-free nested cross-validation for layer, feature, and
   regularization selection, and fit every scaler, projection, residualizer, and
   calibrator on training folds only;
6. preregister nuisance-covariate residualization for prompt/completion length,
   task family, difficulty/band, truncation/cap status, verifier category,
   latency, route count, and any feature mechanically determined by the label;
7. report both raw and residualized predictive increment; a signal that does not
   survive its frozen controls remains a correlate, not a mechanistic monitor;
8. compare full Jacobians, reduced-target VJPs, and bounded finite-difference
   probes on a smaller comparable MoE or the official Agents-A1 4B checkpoint
   if released;
9. require approximation-error, rank-stability, finite-value, phase-localized
   parity, memory, runtime, privacy, and predictive-increment gates;
10. only then run a one-sequence 35B backward memory smoke on rented high-memory
    hardware with frozen abort thresholds and no scientific claims;
11. advance only through a separately frozen fit and validation protocol.

`Code Correctness Signals in LLM Hidden States` (arXiv:2606.14530, v2 dated
2026-07-10) is methodological evidence for nested-CV layer selection and
train-fold-only residualization; it does not establish an Agents-A1 predictor.
`Routers Learn the Geometry of Their Experts` (arXiv:2605.12476) supports a
forward-only router/expert-activation geometry comparator, but its public code
repository currently contains only a placeholder stating that code is coming.
`Path-Constrained Mixture-of-Experts` (arXiv:2603.18297) supports path-level
analysis as a design axis, not a frozen-model intervention claim. `Jacobian
Scopes` remains the strongest concrete engineering lead for reduced-target VJPs
and finite-difference Jacobian estimates. `When Are Experts Misrouted?` supports
counterfactual router analysis while showing ordinary routing can be
uninformative on fragile reasoning tokens. `The Diminishing Returns of
Early-Exit Decoding in Modern LLMs` continues to argue against assuming a modern
MoE is naturally suitable for layer truncation.

No r/LocalLLaMA item found in this scan produced an actionable technique that
could be substantiated by a primary source.

## Claim and stop boundary

- M38E remains in progress and has no result.
- The retry path is blocked until every correction above is implemented and
  tested. Attempt one remains valid and must continue.
- M38E finalization requires the corrected fresh import/execution audit.
- No router, hidden-state, geometry, path, semantic, or Jacobian feature has
  demonstrated incremental completed-error prediction on Agents-A1.
- No Jacobian Lens has been fitted or validated on Agents-A1.
- No safe truncation, early exit, semantic correctness, causal repair, routing
  intervention, activation steering, or production utility is established.
- Full 35B backward feasibility remains unproven.
- GitHub reports this repository as public. Treat every committed byte as
  externally visible and keep all raw tasks, outputs, token data, telemetry,
  states, routes, paths, per-example predictions, process evidence, environment
  data, model pointers, and secret-linked digests private.
- The research program is not complete. Do not mark it complete until every
  frozen milestone and final stop rule in `CODEX_AUTOSTEER.md` is satisfied.
