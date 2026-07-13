# steer.md — make the M38E one-retry controller crash-consistent and identity-exact; leave attempt 1 untouched

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `3f422ade15370faf34b1034e17bf99110537fef8` only where explicitly
amended below. That steer and every predecessor remain incorporated in full,
including all sealed-data, verifier, privacy, provenance, exact-set,
cap-escalation, resource, claim-boundary, retry-limit, production-gating,
repository-hygiene, and stop rules. No frozen result may be re-evaluated or
tuned. No M38E task, family, band, seed, count, threshold, verifier, sampling
setting, output-cap rule, power gate, comparator gate, retry limit, or
production gate may be weakened.

## Current state

- Remote `master` before this steer was
  `815a70a25647318609f6034586b13f7aca6135c5`.
- The active first M38E attempt remains valid and must continue undisturbed. The
  latest heartbeat reports 29 official rows, uniform official identity, recent
  progress, a live driver, and 52/52 fresh core tests. This is an in-progress
  development capture, not a scientific result.
- Commit `a7249a2816be10af6a06b7673e04cd1afdc154a7` correctly removed
  host-global process discovery, added an owned `setsid`/`exec` process group,
  preserved the original attempt as attempt one of a two-total budget, added an
  exclusive run-ID lock, and kept the active attempt untouched.
- Those corrections close the defects named by `3f422ad`, but source inspection
  finds remaining false-retry paths in the newly committed controller. No retry
  is authorized until the corrections below are implemented and tested.
- M36T remains scoped exactly as frozen: T-H3 establishes verifier-backed
  adaptive tool/compute allocation only on its deterministic population. T-H1
  and T-H2 are not established, and no router, hidden-state, semantic, or
  Jacobian mechanism was established by M36T.
- M37J-C remains blocked by its frozen disabled-path parity result. Its resource
  and overhead measurements are descriptive technical observations only.
- M38E has no outcome yet. No completed-error predictor, safe truncation rule,
  early-exit rule, semantic monitor, causal repair, activation steering, route
  intervention, or production utility is established.

## Remaining retry-control defects

The active first attempt is not affected by these defects. They apply only to a
possible retry after attempt one has actually failed.

### 1. Retry-budget consumption is not crash-consistent

The controller currently launches the retry with `Popen`, waits for the launcher
to become the driver, and only then increments `attempts_launched` and writes the
private record. If the controller exits, is killed, or the host fails after
`Popen` but before that write completes, the flock is released while an
unrecorded retry driver may remain alive. A later controller invocation sees the
old attempt count and no recorded retry PID, and can launch another process.
That creates more than two total attempts and can create concurrent writers.

The retry authorization must be durably consumed before any process creation.
A crash may conservatively waste the one retry; it may never recreate or refund
that authorization based on inference.

### 2. The model pointer is not verified against the original launch record

`verify_runtime_identity()` compares the current control-checkout pointer bytes
with the current execution-checkout pointer bytes. It does not compare either
value with an immutable value or digest captured in the original private launch
record, despite the amendment claiming that it does. Both current files can
change together and still pass. The retry launch argument is then derived from
the changed execution pointer.

The original private record must contain a model-pointer digest or exact private
identity captured from attempt one. Both current pointers and the exact launch
argument must match that recorded identity. Missing original evidence blocks.

### 3. Unreadable process identity is treated as dead instead of ambiguous

`proc_identity()` returns `None` for `PermissionError` as well as for a missing
process. `driver_alive()` then continues as though no process exists. This
contradicts the binding rule that partial or unreadable evidence blocks. An
existing recorded PID whose `/proc` identity cannot be fully read must block a
retry; only a proven nonexistent process may be treated as dead.

### 4. Protocol-environment absence is not reconstructed exactly

The current verification uses `os.environ.get(key, want)`, so a missing current
variable silently passes when `want` is non-null. More importantly, variables
recorded as absent are skipped when the retry environment is built, allowing a
new ambient value to leak into the retry. The retry environment must be built
from a frozen explicit protocol-key schema: recorded values are set exactly and
keys recorded as absent are explicitly removed. Missing keys or schema fields in
the original record block.

## Binding handling of the active first attempt

1. Do not stop, signal, restart, reparent, attach a new supervisor to, or mutate
   the active first-attempt driver or its execution tree.
2. Do not invoke `scripts/m38e_retry_controller.py` or the superseded shell
   supervisor while attempt one is alive.
3. Continue aggregate-only heartbeat monitoring. A heartbeat may report row
   count, freshness, test count, aggregate process health, and aggregate phase
   only.
4. If attempt one completes, finalize only through the existing exact-set,
   cap-escalation, verifier, privacy, cleanup, and result gates.
5. If attempt one exits nonzero, preserve the private ledger byte-for-byte and
   block until the corrected one-retry controller passes every requirement
   below.

## Required controller correction

This is control-plane-only. It may not alter the executing driver, scientific
source, task generation, private rows, manifest, thresholds, verifier, sampling
settings, output caps, cap-escalation logic, eligibility arithmetic, power gate,
result gate, or claim boundary.

A retry is authorized only if all of the following hold:

- Acquire the existing exclusive nonblocking run-ID lock before preflight and
  keep it for the controller lifetime.
- Validate the immutable execution checkout, exact ledger, original process
  death, runtime identity, model identity, protocol environment, worker
  override, tensor-parallel configuration, sampling settings, and remaining
  retry budget before process creation.
- Before `Popen`, atomically replace and `fsync` the private launch record with a
  state that permanently consumes attempt two, includes a unique private launch
  nonce, and marks the retry `reserved` or `launching`. Also `fsync` the parent
  directory. Once written, this budget is never rolled back or reused.
- A record showing attempt two as `reserved`, `launching`, `running`, `exited`,
  or otherwise consumed must block every later launch. If a crash leaves
  `reserved` without a PID, the run is blocked; do not infer that no process was
  created and do not refund the retry.
- After successful `setsid`/`exec` identity proof, atomically update the same
  record to `running` with the exact owned PID/PGID, command identity, execution
  directory, source identity, and private nonce. Crash-safe atomic replacement
  and `fsync` remain required.
- Distinguish a proven missing PID from unreadable or partial `/proc` evidence.
  Missing may be dead; unreadable, inconsistent, or partial evidence blocks.
- Bind the exact model pointer or its cryptographic digest in the original
  private launch record. Verify the control pointer, execution pointer, and
  launch argument against that original value. Comparing only two current files
  is insufficient.
- Define the complete protocol-relevant environment-key set in code or a frozen
  private schema. Validate that the original record contains every key. Build a
  clean retry environment in which recorded values are set exactly and recorded
  absences are removed explicitly; do not inherit protocol-relevant ambient
  values.
- Preserve the existing owned-PGID launcher, exact signal targeting, immutable
  source worktree, exact-ledger preflight, and permanent two-total attempt cap.
- Preserve the private ledger in place. Do not copy, normalize, rewrite, compact,
  sort, redact in place, or regenerate rows.
- Commit only aggregate operational status. PIDs, nonpublic paths, environment
  values, model pointers, rows, prompts, outputs, task IDs, cap-pilot membership,
  token data, and telemetry remain uncommitted.

## Required tests before any retry

Add deterministic tests proving:

1. a simulated crash immediately after `Popen` cannot permit another launch;
2. attempt two is durably consumed before process creation and is never refunded
   after launcher failure, controller failure, or ambiguous recovery;
3. `reserved` or `launching` without a PID blocks permanently rather than
   launching again;
4. atomic record replacement survives interruption without producing a partial
   JSON record, and file plus parent-directory durability steps are exercised;
5. an unreadable live recorded PID blocks while a proven nonexistent PID may be
   treated as dead;
6. changing both current model-pointer files together still blocks when they do
   not match the original recorded identity;
7. the actual retry launch argument is verified against the original model
   identity;
8. protocol keys recorded as absent are removed from an ambient environment;
9. missing protocol schema fields block before engine construction;
10. the launched process PID remains the exact owned PGID through `exec`, decoys
    are never selected or signaled, and a stall targets only that group;
11. two simultaneous controllers cannot both acquire the lock or consume the
    retry;
12. the existing attempt one is counted and no state permits a third launch;
13. source, ledger, model, runtime, environment, override, tensor-parallel, or
    sampling mismatch blocks before engine construction;
14. the full repository test suite, recursive privacy audit, and
    `check_commit_safe.py` remain green.

Commit the corrected controller, tests, and an aggregate-only amendment. Do not
launch a retry merely because the code is committed. Verify the exact remote
head, then use the controller only if attempt one has actually failed and the
single remaining authorization was not already consumed.

## Agents-A1 scaling path

The official InternScience repository still announces a forthcoming Agents-A1
4B model, while the official organization currently exposes the 35B Agents-A1
variants. Do not substitute Agents-K1 or an unofficial checkpoint under the
Agents-A1 name.

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
   hardware with frozen abort thresholds and no scientific claims;
6. advance from the smoke only through a separately frozen fit and validation
   protocol. A memory success is not an interpretability, prediction, stopping,
   or production result.

Jacobian Scopes (`arXiv:2601.16407`) remains the strongest concrete engineering
lead for reduced-target VJPs and finite-difference Jacobian quadratic-form
estimation. Hidden Error Awareness (`arXiv:2605.09502`) supports diagnostic
hidden-state prediction while explicitly failing to establish causal repair.
When Are Experts Misrouted? (`arXiv:2605.07260`) supports counterfactual router
analysis, not treating router confidence or expert identity as a correctness
label. The Diminishing Returns of Early-Exit Decoding (`arXiv:2603.23701`)
continues to caution that modern MoEs are generally less early-exit-friendly
than dense transformers. None changes M38E or authorizes intervention, stopping,
or production use. No actionable r/LocalLLaMA lead has been verified against a
primary source.

## Claim, privacy, and production boundary

GitHub reports this repository as public. Treat every committed byte as
externally visible. Never commit private prompts, answers, operands, outputs,
token text or IDs, per-task labels or predictions, raw telemetry, hidden states,
activations, gradients, Jacobians, lens matrices, model weights, caches, stack
traces, local paths, private task IDs, cap-pilot membership, PIDs, environment
values, or model pointers. Public artifacts remain aggregate-only.

The research program is not finished. M38E is in progress, M37J-C remains
blocked, the official Agents-A1 4B checkpoint is unavailable, and full 35B
backward/Jacobian feasibility is unproven. No observation, classifier, tool
policy, route edit, activation intervention, semantic monitor, truncation rule,
or early-exit rule is authorized for production by this directive.
