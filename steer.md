# steer.md — close remaining M38E retry identity and audit gaps; preserve attempt one

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `4cb5caac0c4a26458213f0337a3afd8bfc6b864c` only where explicitly
amended below. That steer and every predecessor remain incorporated in full,
including every sealed-data, verifier, privacy, provenance, exact-set,
cap-escalation, resource, claim-boundary, retry-limit, production-gating,
repository-hygiene, and stop rule. No frozen scientific result may be
re-evaluated or tuned. No M38E task, family, band, seed, count, threshold,
verifier, sampling setting, output-cap rule, power gate, comparator gate, retry
limit, or production gate may be weakened.

## Current state

- Remote `master` before this steer was
  `7ab643553bdb2d22c33dafd12b398b2a1ee1b348`.
- M38E official attempt one remains valid and must continue undisturbed. The
  latest aggregate heartbeat reports 75 rows, `mod_chain` band 3 at 13/24,
  uniform official identity, a live driver with fresh progress, and 52/52 fresh
  core suites. This is in-progress development capture, not a scientific result.
- Commit `7f51bf5db6a3ea63a02d419c8a4ffde43888344c` correctly added a READY/GO
  handshake, stronger process checks, a pinned NUL-safe audit, dependency-origin
  checks, and fail-closed stall handling. It launched no retry and did not touch
  attempt one.
- Source inspection finds remaining discrepancies between the frozen retry and
  finalization requirements and the code that would actually execute. These do
  not invalidate attempt one. They block only a possible retry and, where
  stated, M38E finalization.
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

### 1. The executable is still invoked by pathname, not by an identity-bound descriptor

The prior steer required fd-bound execution through `fexecve`, `execveat`, or an
equivalent kernel mechanism, with failure closed if unavailable. The current
code does not implement that boundary:

- `bind_executable()` still returns the original invoked pathname;
- the preflight, audit, probes, and guarded launcher are started through that
  pathname;
- the launcher re-hashes a canonical path and then calls `execv()` on that path.

A path or inode can still be replaced after the final identity check and before
the kernel resolves `execv()`. Canonical-path execution narrows the race but
does not close it.

Before any retry:

1. open the exact bound interpreter before reservation using a descriptor mode
   suitable for execution;
2. bind canonical path, device, inode, mode, size, digest, and descriptor
   metadata into the private record;
3. run every importing preflight and package probe through that bound executable
   identity;
4. pass the bound executable descriptor through the READY/GO launcher using an
   exact descriptor allowlist;
5. execute through `execveat(..., AT_EMPTY_PATH)`, `fexecve`, or a proven
   equivalent that performs no final pathname lookup;
6. fail closed if the platform or Python runtime cannot provide that primitive.

Do not claim the alias, symlink, wrapper, inode-replacement, or final path-lookup
race is closed until a deterministic replacement-race test proves that the
checked descriptor, not a later pathname target, is executed.

### 2. READY is not fully nonce-bound or exactly framed

The launcher READY record currently contains PID, PGID, SID, cwd, and a
self-executable identity. It does not contain the reserved retry nonce or the
observed open-descriptor inventory. The parent accepts the first newline from a
single bounded read, does not require exactly one complete framed record with no
trailing bytes, checks only the canonical path and digest from the child's
self-executable identity, and checks only a command-line prefix rather than the
exact launcher argv.

Before GO:

- READY must include the exact reserved nonce, run ID, attempt number, command
  phase, complete expected argv digest or exact argv, and sorted open-FD role
  inventory;
- the parent must require exactly one length-bounded framed record, reject
  truncation and trailing data, and verify EOF/closure semantics explicitly;
- parent and child views must match on PID = PGID = SID, start time, cwd, nonce,
  state, phase, full argv, full executable identity (canonical path, device,
  inode, mode, size, digest), and descriptor roles;
- the durable launching record must contain the same nonce and identity, be
  fsynced and reread, and only then authorize GO;
- malformed, partial, duplicated, oversized, stale-nonce, wrong-run, or
  wrong-descriptor READY evidence permanently consumes the retry and exits
  without scientific exec.

Add direct tests for stale nonce replay, two JSON records, trailing bytes,
partial reads, oversized READY, wrong descriptor role, full-identity mismatch,
and exact-argv mismatch.

### 3. The retry controller wires the Python executable into the audit's git slot

`m38e_untracked_audit.py` requires four arguments after its script name:
checkout, recorded environment, bound Python executable, and bound git
executable. The current controller passes the Python executable for both the
Python and git arguments. The audit then attempts to execute Python with git
arguments. This should fail closed, but it means the committed retry path is not
usable and the claimed end-to-end audit wiring has not been tested.

Before any retry:

- bind the original git executable by canonical path, device, inode, mode, size,
  and digest in the private attempt-one record;
- invoke it through an identity-bound descriptor or a fail-closed equivalent;
- pass that exact git identity to the audit, never the Python executable and
  never ambient `PATH` lookup;
- add an integration test that executes the controller preflight wiring through
  the real argument boundary with a planted shadow file and proves both clean
  PASS and contaminated BLOCK behavior.

Unit-testing the audit helper separately does not satisfy this requirement.

### 4. The audit still excludes roots that are not actually closure-bound

The audit removes every external import root, every external executable root,
and the in-repository virtual environment from inspection on the assertion that
they are protected by dependency-closure digests. The implemented closure is a
small list of module origin files. It does not bind entire external roots,
commands resolved from `PATH`, distribution manifests, native libraries,
`.pth` effects, editable-install pointers, startup hooks, or dynamic loader
inputs. The assertion is therefore broader than the evidence.

The current allowlist is also not the exact component-bound boundary claimed by
the amendment. It accepts entire top-level directories by their first path
component, while several configured multi-component entries can never match the
implemented test. An allowlisted directory could contain an importable,
executable, or symlinked artifact and bypass the block.

Before retry and again immediately before finalization:

1. inventory every effective Python import root, executable root, loader root,
   virtual-environment root, startup hook, `.pth` target, editable-install
   target, namespace-package root, and native-library search root under the
   exact recorded environment;
2. either byte-manifest and verify each external root relevant to the execution
   closure or run inside a content-addressed immutable environment image whose
   identity was captured at attempt one; otherwise block;
3. replace broad top-level allowlisting with exact files and explicitly bounded
   directories whose contents are recursively classified;
4. never exempt an importable, executable, special, or symlinked artifact merely
   because an ancestor directory is operationally allowlisted;
5. bind every external command used by preflight or audit independently of
   `PATH`;
6. fail closed on ignored files, special files, permission failures, races,
   disappearing files, undecodable names, symlink traversal, incomplete
   manifests, or unbound external roots.

The prior aggregate audit PASS remains descriptive only and cannot satisfy the
fresh finalization gate.

### 5. Dependency provenance remains a module-file sample, not a complete closure

The new private closure records origin and digest for eleven named modules. The
retry verifier re-imports those names and compares their main module files. This
is useful evidence but does not satisfy the frozen requirement for a complete
execution dependency closure. It omits distribution metadata and installed-file
manifests, transitive modules imported after startup, native extensions and
shared libraries, namespace roots, editable-install mappings, import hooks,
entry points, generated code, and the exact import graph.

Before retry:

- require the original private record to contain the complete import and native
  dependency graph observed for attempt one, including canonical origins and
  digests;
- bind distribution name/version, metadata origin, RECORD or installed-file
  manifest digest, editable and namespace state, `.pth` effects, and native
  shared-library origins for every dependency in that graph;
- enforce subprocess return codes and strict machine-readable output for every
  probe;
- verify the entire closure under the exact recorded environment and fd-bound
  executable immediately before reservation and again behind the barrier where
  applicable;
- block when original launch evidence is missing rather than reconstructing a
  stronger identity claim after the fact.

The amendment and status must call the current eleven-module check a
`named-module origin sample`, not a complete dependency closure, until these
requirements pass.

### 6. Full liveness identity is still incomplete

`driver_alive()` requires recorded command line, cwd, start time, and SID. It
checks executable canonical path only when an optional executable field is
present. It does not require or verify full executable file identity, retry
nonce, run ID, attempt, durable state, expected command phase, environment
identity, execution-directory identity, or the lock owner. Therefore the
amendment's claim of full-identity liveness is stronger than the implementation.

For every PID-bearing record, liveness must require and exactly compare:

- kernel start time;
- full executable identity and digest;
- full argv;
- cwd and execution-directory identity;
- SID and PGID;
- run ID, attempt number, nonce, durable state, and expected phase;
- environment and source identities;
- owned lock identity where applicable.

Only proven PID absence or a changed kernel start time may count as dead. Missing
fields, same-start mismatch, unreadable evidence, invalid state transition, or
lock inconsistency are ambiguous and block. Add mutation tests for every field.

### 7. Post-GO failure termination still lacks a trustworthy owned scope

Automatic stall termination is correctly disabled. However, launch-handshake and
exec-recognition failure paths still call the session-enumerating termination
helper. Before GO, a proven launcher can be terminated through its pidfd. After
GO, the scientific driver may already have created descendants. The helper can
skip unreadable descendants and can report leader death without proving zero
surviving workers. That is the same ownership gap that required fail-closed stall
handling.

- Before GO, termination may target only the exact proven launcher through its
  pidfd after confirming no descendants and re-proving full identity.
- After GO, automatic termination is prohibited unless attempt two was launched
  inside a dedicated, identity-bound cgroup-v2/systemd scope and zero members are
  proven after escalation.
- Without that scope, exec-recognition or later ambiguity must record a permanent
  block, return without unbounded wait, preserve the inherited lock boundary,
  and require private operator review.
- No status may say `failed_terminated` or `dead` based only on leader exit.

Add tests where the driver forks before recognition, the leader exits while a
worker survives, descendant evidence is unreadable, and an unrelated decoy
shares similar argv. No worker may be mislabeled dead and no decoy may be
signaled.

## Status-reporting correction

Public heartbeats may continue to report that the active first attempt has no
runtime blocker. They must separately report persistent control-plane blockers:

- `active_attempt_blockers`: aggregate status for attempt one;
- `retry_blockers`: aggregate count or short non-sensitive description;
- `finalization_blockers`: aggregate count or short non-sensitive description.

A single `Blockers: none` line is misleading while retry and finalization remain
blocked. Do not publish private paths, identities, hashes, PIDs, environment
values, or secret-linked evidence.

## Binding handling of active attempt one

1. Do not stop, signal, restart, reparent, attach a new supervisor to, or mutate
   the active first-attempt driver, environment, worktree, model cache, ledger,
   or process tree.
2. Do not invoke the retry controller or any superseded supervisor while attempt
   one is alive.
3. Continue aggregate-only heartbeat monitoring.
4. Read-only capture of missing retry identity evidence is permitted only into
   the existing private operational record. Never commit PIDs, process start
   times, descriptor numbers, paths, environment values, executable or package
   hashes, model pointers, or digest-to-secret mappings.
5. Before scientific finalization, require exact-set validation,
   cap-escalation completion, verifier gates, privacy audit, cleanup gates, and a
   fresh passing corrected import/execution audit.
6. If attempt one exits nonzero, preserve its private ledger byte-for-byte and
   block until every retry correction and deterministic test in this steer
   passes.

## Required correction and tests before any retry

This work is control-plane-only. It may not alter the scientific driver, task
generation, private rows, manifest, thresholds, verifier, sampling, output caps,
cap-escalation logic, eligibility arithmetic, power gate, result gate, or claim
boundary.

Implement and deterministically test all prior requirements plus:

1. fd-bound executable invocation closes the final pathname race;
2. READY is exactly framed and binds nonce, run, attempt, state, phase, full
   executable identity, exact argv, and descriptor roles;
3. controller-to-audit git wiring uses an independently bound git executable;
4. the audit inventories or immutable-manifest-binds every effective external
   import, execution, loader, virtual-environment, and native-library root;
5. allowlists cannot exempt importable, executable, special, or symlinked
   artifacts by broad ancestor prefix;
6. complete distribution, import, and native dependency closure is verified or
   the retry blocks for missing original evidence;
7. liveness requires every recorded identity, state, nonce, and lock field;
8. no post-GO process is automatically terminated without an identity-bound
   cgroup or equivalent zero-member scope;
9. two simultaneous controllers cannot reserve, register, release, signal, or
   supervise the same run;
10. every attempt-two state permanently consumes the sole retry and no crash or
    exception permits a third launch;
11. full repository tests, recursive privacy audit, and
    `check_commit_safe.py` remain green.

Commit the corrected controller, launcher, preflight, audit, provenance logic,
tests, status-schema change, and an aggregate-only amendment. Do not launch a
retry merely because the code is committed. Verify the exact remote head, then
use the retry only if attempt one has actually failed and every private identity
check passes.

## Agents-A1 scaling path

No new external evidence in this scan warrants changing the frozen scientific
sequence. The official Agents-A1 repository still has no release after its
2026-07-08 statement that a 4B model is coming, and the official Hugging Face
collection still lists only 35B variants. Do not substitute Agents-K1 or an
unofficial checkpoint under the Agents-A1 name.

The technically credible sequence remains:

1. finish M38E unchanged;
2. preregister a forward-only 35B comparator using observation-only router
   logits, hidden-state summaries, router-visible/router-blind energy,
   router-expert geometry, route transitions, and multi-layer path features;
3. separate prefill from autoregressive decode and stream only preregistered
   aggregate features into private storage rather than retaining unnecessary
   full activations;
4. test verifier-labeled predictive increment over frozen confidence, length,
   family, difficulty, cap, truncation, latency, and route-count baselines using
   leakage-free nested cross-validation and train-fold-only preprocessing;
5. report raw and nuisance-residualized increment; correlation without frozen
   incremental value is not a mechanistic monitor;
6. compare full Jacobians, reduced-target VJPs, and bounded finite-difference
   probes on a smaller comparable MoE or the official Agents-A1 4B checkpoint if
   released;
7. require approximation-error, rank-stability, finite-value, phase-localized
   parity, memory, runtime, privacy, and predictive-increment gates;
8. only then run a frozen one-sequence 35B backward memory smoke on rented
   high-memory hardware with no scientific claim;
9. advance only through a separately frozen fit and validation protocol.

`Jacobian Scopes` remains the strongest concrete engineering lead for
reduced-target VJPs and finite-difference Jacobian estimates. `When Are Experts
Misrouted?` continues to support counterfactual router analysis while warning
that ordinary router scores can be uninformative on fragile reasoning tokens.
Current hidden-state error-prediction work supports diagnostic probing but not
causal repair, and current early-exit evidence remains unfavorable for modern
MoEs without direct verifier-backed validation. No r/LocalLLaMA item in this scan
produced a new actionable technique that survived primary-source verification.

## Claim and stop boundary

- M38E remains in progress and has no result.
- The retry path is blocked until every correction above is implemented and
  tested. Attempt one remains valid and must continue.
- M38E finalization requires the corrected fresh import/execution and dependency
  provenance audits.
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
