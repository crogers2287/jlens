# steer.md — pin M38E execution source across retries; do not disturb the active first attempt

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `a9b91f71a4258a6e43cca49e2133ed3d61b536c2` only where explicitly
amended below. That steer and every predecessor are incorporated in full,
including all sealed-data, verifier, privacy, provenance, exact-set, cap-
escalation, resource, claim-boundary, production-gating, repository-hygiene,
and stop rules. No frozen result may be re-evaluated or tuned. No M38E task,
family, band, seed, count, threshold, verifier, sampling setting, output-cap
rule, power gate, comparator gate, or production gate may be weakened.

## Current established state

- Remote `master` before this steer was
  `3e4bceab74c2d3784d3f5cfcd3a42789f4d67e30`.
- The M38E smoke/official identity and explicit task-provenance corrections
  required by `a9b91f7` landed at
  `4469b100842732cb68ffbc0cec7270ccf240cf40`. Smoke rows are content-marked
  `run_kind=m38e_driver_smoke` and `attempt_kind=smoke_2048`; official rows are
  content-marked `run_kind=m38e_official_dev`; every task and row binds an
  explicit `task_index` and `generator_seed_id=m38e-dev-v1`. The commit reports
  23 driver tests, 351 green repository-wide tests, commit-safe clean, and zero
  official rows before launch.
- The corrected two-row nonofficial smoke passed without touching the official
  ledger. The official 288-task M38E development sweep was launched at
  2026-07-13T18:46Z from source commit `4469b10`.
- The latest pre-steer heartbeat reports four official rows captured and 52/52
  fresh core tests. This is an in-progress development sweep, not a result.
- M36T remains interpreted exactly as frozen: T-H3 establishes only verifier-
  backed adaptive tool/compute allocation on its deterministic population.
  T-H1 and T-H2 are not established. No router, hidden-state, semantic, or
  Jacobian mechanism was established by M36T.
- M37J-C remains blocked by its frozen disabled-path parity outcome. Seven of
  eight technical gates passed, but 11 of 16 prompts differed against the
  absolute allowance of seven. Its 40.04 GiB peak and 1.313x overhead are
  descriptive technical observations only.

## Newly identified operational false-resume path

The current first M38E attempt must not be interrupted. Its source identity is
valid as launched. The automatic retry path is not valid after repository head
movement.

`src/m38e_dev_sweep.py` derives `source_commit` from `git rev-parse HEAD`, hashes
provenance files from that HEAD, includes the source commit in `run_id`, and
requires resumed rows to match that exact identity. The committed supervisor,
however, changes into the ordinary repository checkout and launches the driver
again on attempt two. Since launch, status-only commits have advanced `master`
from `4469b10` through `0d64fc5`, `a527652`, and `3e4bce`. A retry from the
mutable checkout would therefore derive a new source identity and reject the
existing official rows. The validator would fail safely, but the supervisor's
claim that it provides a usable provenance-valid retry is false.

This is a control-plane defect, not permission to alter rows, regenerate tasks,
relax provenance, or restart under a new source commit.

## Binding handling of the active attempt

1. Do not stop, signal, restart, pull into, checkout over, patch, or otherwise
   mutate the running first-attempt process or its execution tree.
2. Record the supervisor PID, child process-group PID, execution working tree,
   exact `HEAD`, environment identity, model pointer, and private-ledger byte
   count without exposing private values in a public artifact.
3. Prevent the supervisor from launching attempt two from the mutable checkout.
   If necessary, terminate only the waiting supervisor shell after verifying the
   `setsid` child remains alive and unchanged. Never kill or reparent the active
   generation process merely to correct the retry controller.
4. Allow the first attempt to complete under `4469b10`. If it completes, finalize
   only through the existing exact-set, cap-escalation, verifier, privacy,
   cleanup, and result gates.
5. If the first attempt exits nonzero, do not launch a second attempt from
   `master`, the current checkout, or any source tree whose exact identity differs
   from the rows already captured.
6. Preserve the private ledger byte-for-byte. Do not copy any private row,
   prompt, answer, output, task id, cap-pilot membership, token data, or telemetry
   into a committed artifact or log excerpt.

## Required immutable retry architecture

A retry is authorized only as a resume of the same official run identity. It
must execute from an immutable execution checkout satisfying every condition
below before engine construction:

- detached `HEAD` exactly
  `4469b100842732cb68ffbc0cec7270ccf240cf40`, or the exact full source commit
  recorded in the official rows if the launch record proves a different value;
- clean tracked tree and byte-identical provenance files;
- exact frozen model repository, immutable model revision, runtime, worker
  override, tensor-parallel configuration, sampling settings, and environment
  identity used by the first attempt;
- byte-for-byte preserved private ledger placed in the expected private location
  with no row transformation;
- recomputed run identity exactly equal to every existing row before GPU engine
  construction;
- no status, heartbeat, steer, documentation, or control-plane commits written
  from the execution checkout.

Use two physically separate Git worktrees or source trees:

1. a control checkout that may receive status, steer, tests, and operational
   supervisor changes; and
2. an execution checkout permanently pinned to the official source identity.

The control supervisor must accept an explicit pinned execution directory and
explicit expected source SHA. It must refuse symbolic refs such as `master`,
`main`, `HEAD`, or an unverified current directory. It must verify the detached
execution SHA and provenance hashes immediately before each launch. It must not
silently create, reset, clean, or update the execution checkout.

If the exact execution source, environment, model revision, or private ledger
cannot be reconstructed and verified, commit only an aggregate blocked status
and stop M38E. Do not regenerate completed rows under a new source identity and
do not call a fresh run a resume.

## Required control-plane tests and audit

Before any retry or future long-running sealed/development capture, add tests or
a deterministic operational preflight proving:

1. status-only commits after launch do not change the execution checkout SHA;
2. a retry launches from the row-bound source commit, not the control checkout;
3. a newer control `master` cannot satisfy or replace the expected execution SHA;
4. a source mismatch blocks before model loading or engine construction;
5. existing rows are exact-validated before resume and no row-count shortcut can
   satisfy completion;
6. the supervisor has no automatic fallback to the current directory, branch
   tip, or latest commit;
7. heartbeat and steer writes occur only in the control checkout;
8. a simulated first-attempt failure followed by control-head advancement either
   resumes from the immutable original source or blocks cleanly;
9. public artifacts remain aggregate-only and pass the recursive privacy audit
   and `check_commit_safe.py`.

An operational supervisor correction may be committed in the control checkout
while the first attempt runs, but it may not change the executing driver,
scientific code, private rows, or frozen M38E identity. No official row may be
produced by revised scientific source code as part of this repair.

## M38E completion order remains frozen

- Finish every complete 2,048-token band and every deterministically triggered
  4,096 pilot/full-band path under one validated run identity.
- Never mix 2,048 rows, pilot rows, and full-band 4,096 rows in a primary band
  estimate.
- Apply exact rational eligibility arithmetic and count completed errors only
  from eligible final-cap bands.
- A completed-error frontier-not-found result is legal only after all required
  paths and exact-set checks finish.
- If the frontier gates pass, fit transparent development comparators only on
  eligible completed, nontruncated rows; complete the preregistered power
  calculation; freeze and commit the sealed manifest before generating sealed
  outcomes.
- Stop after the M38E result for operator-level scientific interpretation. Do not
  promote a policy automatically.

## Agents-A1 scaling path

As of 2026-07-13, the official InternScience organization still exposes the 35B
Agents-A1 BF16, FP8, and GGUF variants. The official repository's 2026-07-08
notice says a 4B model is coming, but no official Agents-A1 4B checkpoint is
listed. `InternScience/Agents-K1` is a separate 4B model and may not be
substituted under the Agents-A1 name.

The technically credible sequence is:

1. complete M38E without changing its in-flight protocol;
2. retain observation-only router and hidden-state telemetry on the pinned 35B
   runtime as the near-term full-model path;
3. after M38E, preregister a separate scaling study comparing full Jacobian
   construction against low-rank target-space VJPs and bounded finite-difference
   probes, using a smaller comparable open MoE or an official Agents-A1 4B model
   if released;
4. require approximation-error, rank-stability, finite-value, memory, runtime,
   parity, privacy, and predictive-increment gates before attempting the 35B
   backward path;
5. only then run a one-sequence 35B memory smoke on rented high-memory hardware,
   with frozen abort thresholds and no scientific outcome claims.

Jacobian Scopes (`arXiv:2601.16407`) provides relevant engineering comparators:
its Fisher low-rank path computes only top-k target-space batched VJPs, while its
finite-difference path estimates Jacobian quadratic forms without materializing
the full Jacobian. These methods may reduce probe count or memory, but they are
token-attribution methods, not a validated Jacobian Lens, semantic monitor, or
error predictor. They may be evaluated only in a fresh preregistered study.

The Diminishing Returns of Early-Exit Decoding (`arXiv:2603.23701`) reports that
modern MoE models are generally less early-exit-friendly than dense models.
Hidden Error Awareness (`arXiv:2605.09502`) reports strong hidden-state error
prediction but failed steering and correction interventions. When Are Experts
Misrouted? (`arXiv:2605.07260`) reports that standard routes can be
uninformative on fragile reasoning tokens. Together these support empirical
prediction tests while prohibiting semantic-only stopping, causal repair claims,
or trust in router confidence as a correctness label.

ICA Lens (`arXiv:2606.11722`) is a low-cost activation-geometry comparator for a
future semantic study, not a substitute for Jacobians or verifier-backed error
prediction. No actionable r/LocalLLaMA implementation lead has been verified by
a primary source.

## Claim, privacy, and production boundary

GitHub currently reports this repository as public. Treat every committed byte
as externally visible. Never commit private prompts, answers, operands, outputs,
token text or ids, per-task labels or predictions, raw telemetry, hidden states,
activations, gradients, Jacobians, lens matrices, model weights, caches, stack
traces, local paths, private task ids, or cap-pilot membership. Public artifacts
remain aggregate-only.

M36T does not establish an internal telemetry mechanism. M37J-C remains blocked.
M38E is in progress. No Jacobian Lens on Agents-A1, semantic correctness,
completed-error prediction, safe truncation, early exit, causal repair,
activation steering, or production utility is established.

Production remains gated. No observation, classifier, tool policy, route edit,
activation intervention, semantic monitor, truncation rule, or early-exit rule
is authorized for production by this directive.