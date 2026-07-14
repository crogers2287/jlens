# steer.md — close M38E preflight and runtime-identity fail-open paths; preserve attempt one

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `e2d5b5e92a62259651b1159e50bc7fc22ce535ae` only where explicitly
amended below. That steer and every predecessor remain incorporated in full,
including every sealed-data, verifier, privacy, provenance, exact-set,
cap-escalation, resource, claim-boundary, retry-limit, production-gating,
repository-hygiene, and stop rule. No frozen scientific result may be
re-evaluated or tuned. No M38E task, family, band, seed, count, threshold,
verifier, sampling setting, output-cap rule, power gate, comparator gate, retry
limit, or production gate may be weakened.

## Current state

- Remote `master` before this steer was
  `5f70e4172ebc2fdb52b20e2c1e669226e9f31f8f`.
- M38E official attempt one remains valid and must continue undisturbed. The
  latest aggregate heartbeat reports 56 rows, with `mod_chain` band 2 complete
  at 2,048 tokens and its deterministic 4,096-token pilot underway, uniform
  official identity, a live driver, and 52/52 fresh core suites. This remains
  in-progress development capture, not a scientific result.
- Commit `f102e904fa71352dc8afc00c61e4afd629ab0d2b` correctly closed the
  explicit-unlock, permissive-termination, broad-descriptor-inheritance, and
  one-time untracked-import-audit findings from the prior steer. It did not
  launch a retry and did not touch attempt one.
- Source inspection finds remaining discrepancies between the claimed retry
  identity envelope and the code that would actually execute. These findings
  do not invalidate attempt one and do not authorize interruption of it. They
  block only a possible retry and, where stated, M38E finalization.
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
possible retry. Item 5 also applies to finalization of attempt one.

### 1. The executable preflight still runs under the ambient controller runtime

The controller invokes `m38e_exec_preflight.py` through `sys.executable` before
reconstructing the complete attempt-one environment. The preflight is not a
pure byte-level shell check: it imports `m38e_dev_sweep`, `m36v_phase1`, task
generators, verifier code, and their transitive Python dependencies, and it
executes run-identity and row-validation logic. Running it under the controller
interpreter and ambient environment can validate different imports and package
resolution than the retry driver will use.

The retry order must be:

1. load and validate the private attempt-one record under the run lock;
2. reconstruct and digest-verify the complete attempt-one environment;
3. establish the exact invoked Python executable identity;
4. run the pinned preflight with that exact executable and environment;
5. run package/runtime probes under the same executable and environment;
6. reverify source, control artifacts, model identity, ledger identity, and
   executable identity immediately before reservation and process creation.

No Python-importing preflight may run through `sys.executable` or ambient
`os.environ`. A byte-only bootstrap check may use the controller runtime only
if it imports no execution-tree module and its scope is explicitly limited.

### 2. The hashed executable is not necessarily the executable invoked

`verify_runtime_identity()` hashes `exe_resolved` but launches probes and the
scientific driver using `original["python"]`. If `original["python"]` is a
symlink, wrapper, relative path, or otherwise retargetable pathname, the hashed
file and the invoked file can differ after validation. The guarded launcher is
also started with the mutable controller `sys.executable`.

Before any retry:

- bind the original executable by canonical resolved path, device, inode, mode,
  size, and SHA256 in the private record;
- prove that every configured Python pathname resolves to that exact identity;
- invoke the preflight, runtime probes, guarded launcher, and scientific driver
  by the exact bound executable, not by an unchecked alias or mutable symlink;
- re-prove the executable identity immediately before every subprocess creation
  and again behind the launch barrier before scientific exec;
- treat any missing field, resolution change, wrapper insertion, symlink
  retarget, inode change, or byte change as a permanent block.

No private path, inode, device number, or executable digest may be committed.

### 3. Package origin is read but not compared

The runtime probe prints each module version and `__file__`, but the controller
currently checks only the version line. Two installations can report the same
version while resolving different code. The amendment's claim that module
origin is compared is therefore not established by the implementation.

Capture privately and verify, under the exact bound executable and complete
attempt-one environment, at minimum for `torch`, `vllm`, and every locally
imported execution package:

- exact version or distribution identity;
- canonical module origin;
- origin file identity and SHA256;
- distribution metadata origin and a stable digest of the installed-file
  manifest when available.

The retry preflight and launch barrier must compare these values exactly.
Missing metadata, namespace ambiguity, editable-install drift, origin change,
or equal-version/different-origin resolution blocks. Tests must prove that two
same-version packages at different origins cannot pass.

### 4. Recorded-process identity mismatch can authorize a retry

`driver_alive()` currently returns `False` when a readable process exists at a
recorded PID but its command line or cwd differs from the record. That treats an
identity mismatch as equivalent to proven death and can authorize attempt two
without evaluating the recorded start time, session, process group, executable,
or command phase.

For every recorded attempt carrying a PID:

- proven PID nonexistence means dead;
- a different `/proc/<pid>/stat` start time proves PID reuse and means the
  recorded process is dead, while the unrelated current process remains
  untouched;
- the same start time with any command, cwd, executable, SID, PGID, or phase
  mismatch is ambiguous and blocks;
- unreadable or partial evidence blocks;
- missing original identity fields block rather than being skipped;
- only exact full identity may count as the recorded process alive.

Add tests for same-PID/same-start-time command mutation, cwd mutation, executable
mutation, SID/PGID mutation, PID reuse, missing fields, and unreadable evidence.
No mismatch path may silently fall through to `False`.

### 5. The reusable untracked-import audit was not added to executable preflight

A one-time read-only audit of attempt one's execution tree passed, which is a
valid aggregate observation. The committed preflight still uses
`git status --porcelain --untracked-files=no`, and no committed reusable audit
enumerates all untracked files and symlinks against the exact import and
execution roots. The one-time observation does not prove that a future retry or
finalization rerun is protected from later untracked importable content.

Implement a pinned, deterministic, read-only audit used by both retry preflight
and M38E finalization that:

- enumerates all untracked files, directories, and symlinks;
- derives import and executable search roots from the exact recorded
  environment and bound executable;
- resolves symlinks and rejects traversal into import or execution roots;
- allows only an explicit private operational-data allowlist outside those
  roots;
- rejects Python modules, packages, extension modules, executable scripts,
  path-configuration files, startup hooks, editable-install pointers, and any
  artifact capable of changing import or execution resolution;
- records only an aggregate pass/block publicly.

Run this audit freshly after attempt one exits and immediately before scientific
finalization. Preserve any blocking file and the ledger byte-for-byte for
private forensic review; do not delete or normalize evidence.

### 6. The pidfd is opened but does not participate in the safety proof

`terminate_owned()` opens a pidfd but performs liveness checks and both signals
through numeric PID/PGID operations. Merely holding an unused pidfd does not
make `killpg()` resistant to leader exit and process-group reuse between proof
and signal. The code and amendment must not claim pidfd protection that is not
actually used.

Before any retry, use a termination design with an enforceable ownership
boundary. Acceptable implementations are:

- a dedicated pinned cgroup/process scope whose membership and identity are
  recorded before barrier release and whose kill operation is scoped to that
  identity; or
- pidfd-based leader signaling and waiting plus a separately proven mechanism
  for enumerating and terminating only descendants belonging to the recorded
  session/group without numeric-ID reuse exposure.

If the platform cannot establish that boundary, fail closed and do not
terminate automatically. Never signal a numeric process group after its leader
identity is unavailable or ambiguous. Tests must simulate leader exit and
PID/PGID reuse between proof and escalation and prove that no decoy is touched.

### 7. Ambiguous stall termination can block forever in `wait()`

After a stall, the controller records the return from `terminate_owned()`,
breaks the supervision loop, and unconditionally calls `proc.wait()`. When the
termination result is `ambiguous`, the process may still be alive by design;
waiting indefinitely prevents a durable terminal block from being surfaced and
retains controller ownership without resolving the condition.

If termination is ambiguous:

- durably record an `ambiguous` terminal block with complete private evidence;
- do not signal again;
- do not call an unbounded wait;
- close only the controller's lock duplicate and exit blocked, leaving any
  surviving child to retain its inherited run lock;
- require private operator review before any later action.

Bounded waiting is permitted only after exact owned termination or proven
natural exit. Add a deterministic test in which termination becomes ambiguous
and the controller returns blocked without hanging or releasing a surviving
child's lock.

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
   cap-escalation completion, verifier gates, privacy audit, cleanup gates, and
   a fresh passing reusable untracked-import audit.
6. If attempt one exits nonzero, preserve its private ledger byte-for-byte and
   block until every retry correction and test below passes.

## Required correction and tests before any retry

This work is control-plane-only. It may not alter the scientific driver, task
generation, private rows, manifest, thresholds, verifier, sampling, output
caps, cap-escalation logic, eligibility arithmetic, power gate, result gate, or
claim boundary.

Implement and deterministically test all prior requirements plus:

1. the executable preflight imports execution code only under the exact bound
   attempt-one executable and complete recorded environment;
2. ambient `PATH`, `PYTHONPATH`, library paths, sitecustomize/usercustomize,
   virtual-environment variables, and controller interpreter cannot affect
   preflight or probes;
3. mutable aliases, wrappers, relative paths, and symlink retargets cannot cause
   a different executable to run after the bound executable was hashed;
4. preflight, probes, launcher, and driver all use the exact bound executable;
5. same-version packages at different origins or with changed origin bytes
   block;
6. process identity mismatch is fail-closed except for PID reuse proven by a
   different start time;
7. the reusable all-untracked/import-root audit blocks importable, executable,
   symlinked, startup-hook, editable-install, and path-configuration artifacts;
8. the reusable audit passes only the explicit private non-importable
   operational allowlist and runs freshly before finalization;
9. leader exit and PID/PGID reuse between TERM and KILL cannot target a decoy;
10. ambiguous termination records a permanent block and returns without an
    unbounded wait or explicit lock release;
11. two simultaneous controllers cannot reserve, register, release, signal, or
    supervise the same run;
12. every attempt-two state permanently consumes the sole retry and no crash or
    exception permits a third launch;
13. full repository tests, recursive privacy audit, and
    `check_commit_safe.py` remain green.

Commit the corrected controller, preflight, guarded launcher, reusable audit,
tests, and an aggregate-only amendment. Do not launch a retry merely because
the code is committed. Verify the exact remote head, then use the retry only if
attempt one has actually failed and every private identity check passes.

## Agents-A1 scaling path

No new primary source in this scan changes the frozen scientific sequence. The
official Agents-A1 repository still reports only the released 35B-A3B model and
its 2026-07-08 notice that a 4B model is forthcoming; the official Hugging Face
organization still lists only 35B variants. Do not substitute Agents-K1 or an
unofficial checkpoint under the Agents-A1 name.

The observation-only router-control/path comparator from the prior steer
remains the cheapest technically credible next scaling step after M38E. The
sequence remains:

1. finish M38E unchanged;
2. retain observation-only router and hidden-state telemetry on the pinned 35B
   runtime;
3. preregister the router-visible/router-blind control-subspace and path
   comparator, separating prefill from autoregressive decode;
4. test only verifier-labeled predictive increment and calibration over frozen
   router-logit and hidden-state baselines;
5. compare full Jacobians, reduced-target VJPs, and bounded finite-difference
   probes on a smaller comparable MoE or the official Agents-A1 4B checkpoint
   if released;
6. require approximation-error, rank-stability, finite-value, phase-localized
   parity, memory, runtime, privacy, and predictive-increment gates;
7. only then run a one-sequence 35B backward memory smoke on rented high-memory
   hardware with frozen abort thresholds and no scientific claims;
8. advance only through a separately frozen fit and validation protocol.

`Jacobian Scopes` remains the strongest concrete engineering lead for
reduced-target VJPs and finite-difference Jacobian estimates, but its current
public implementation remains small-model-oriented and is not a drop-in
Agents-A1 lens. `Polysemantic Experts, Monosemantic Paths` supports the
parameter-free router-control/path comparator but establishes no Agents-A1
result. `Hidden Error Awareness` supports diagnostic prediction but not causal
repair. `When Are Experts Misrouted?` supports counterfactual router analysis
while showing that ordinary routing can be uninformative on fragile reasoning
tokens. `The Diminishing Returns of Early-Exit Decoding in Modern LLMs`
continues to argue against assuming that a modern MoE is naturally suitable for
layer truncation. `SoftMoE` is a training-time differentiable-routing result;
it does not authorize modifying the frozen Agents-A1 router and adds no current
observation-only or production claim.

No r/LocalLLaMA item found in this scan produced an actionable technique that
could be substantiated by a primary source.

## Claim and stop boundary

- M38E remains in progress and has no result.
- The retry path is blocked until every correction above is implemented and
  tested. Attempt one remains valid and must continue.
- No router, hidden-state, path, semantic, or Jacobian feature has demonstrated
  incremental completed-error prediction on Agents-A1.
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