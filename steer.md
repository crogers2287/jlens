# steer.md — close transactional-install, cadence, finiteness, and provenance false-pass paths before live Agents-A1 smoke

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `65c76ecf0cd44fe08f6dc4fa4df1107921c2eda5` only where explicitly
amended below. Every sealed-data, verifier, privacy, claim-boundary, resource,
production, and repository-hygiene gate from steers `8eb2e9e`, `cccf40a`,
`fe6fcf2`, `821e430`, and `65c76ec` remains binding by incorporation. No
scientific threshold, feature family, prompt, task, checkpoint, cadence, top-k
value, resource ceiling, or production gate is relaxed.

## Current established state

- M36T development remains frozen at 96/96 with 65 positive and 31 negative
  labels. Its task sets, comparators, decision step, tool budget, hypotheses,
  verifier, power gate, and evaluator remain unchanged.
- At pushed heartbeat `c4858641d311602369ea7aed33910cff975ded6e`, M36T
  sealed capture was healthy at 108/192, with 52/52 fresh core tests and no
  operational blocker. Do not interrupt, split, migrate, tune, or shorten it.
- The only authorized M36T evaluator remains
  `0285ec3531d40faac286424661f610ade677d3ec`. It may run exactly once after all
  192 sealed rows are durably present and its full preflight succeeds.
- M37J-A remains closed. Completed-error prediction was not established and its
  truncation arm was underpowered. Do not reopen or tune it.
- Commit `13b81078b402dfc27b185f6799fd19c33dc6c4f3` executed steer
  `65c76ec`: per-prompt all-rank identity, nonempty readouts, exact final-slot
  handling, strict gate maps, exception blocker artifacts, and exact serving
  reply checks are now staged. Its synthetic suite reported 318 green tests.
  No live M37J-C prompt has been issued.
- A fresh source audit found additional implementation paths that can leak hooks
  after a failed install, accept structurally wrong cadence data or infinite
  semantic values, and record false source provenance. These are technical
  blockers, not scientific outcomes.
- M38E remains queued behind the M36T sealed window and bounded M37J-C smoke.

## Binding corrections before any live M37J-C prompt

### 1. Make worker installation transactional and cleanup idempotent

The current worker installation methods attach hooks before allocation and only
store worker state after allocation succeeds. If allocation raises, hooks can
remain attached while the state pointer stays `None`, making normal uninstall
unable to find them. The driver also sets `installed = True` only after both
bridge and telemetry installation RPCs return. If bridge installation succeeds
but telemetry installation raises, the exception path skips cleanup entirely.

Correct this without changing the model or capture behavior:

- In both `jlens_bridge_install` and `jlens_install_telemetry`, treat hook
  attachment plus buffer allocation as one transaction.
- Hold local handles immediately after attachment. If any later operation
  raises, remove every handle already attached, clear provisional state, and
  re-raise. Never leave a hook installed without discoverable state.
- Make both uninstall RPCs idempotent: the postcondition "component absent" is
  success whether or not state existed when cleanup began.
- Mark installation as attempted before the first install RPC. On any exception
  after engine construction, run ordered cleanup on every rank even if only one
  component or one rank may have installed successfully.
- Continue all cleanup steps after individual errors. Verify the exact rank set
  and the final absent/disabled postcondition for both bridge and telemetry on
  every rank.
- Add a bounded status RPC if needed. It may expose only rank plus booleans for
  installed/enabled state; no prompts, tokens, routes, activations, paths, or
  model data.
- Any rollback, uninstall, rank-coverage, or postcondition failure writes the
  aggregate blocked outcome and prohibits the live smoke.

### 2. Validate the actual frozen cadence and projection-call schedule

The staged harness checks that the metadata field says `cadence == 32`, but it
can still accept arbitrary strictly increasing steps such as `[5, 10, final]`.
It also checks cross-rank equality of slot and call counts without checking that
those counts are mathematically implied by the frozen schedule.

For each frozen layer with `N = decode_steps`:

- Compute periodic checkpoints exactly as `31, 63, 95, ... < N`.
- Append `N - 1` exactly once only when it is not already a periodic checkpoint.
- Require the returned `steps` vector to equal that expected vector exactly,
  not merely be monotone and in range.
- Require `captured_slots` to equal the number of periodic checkpoints retained.
- Under this 256-token smoke with 80 slots per layer, require `dropped == 0`.
- Require `projection_calls` to equal the exact sum of
  `ceil(len(expected_steps_for_layer) / PROJECTION_CHUNK_SLOTS)` across the five
  frozen layers.
- Require these exact vectors and counts on every rank. Any mismatch blocks.

This is conformance-only. The frozen cadence, final-position rule, five layers,
80-slot capacity, chunk size, token cap, and top-k remain unchanged.

### 3. Enforce true numerical finiteness and the exact semantic schema

The current semantic check rejects NaN via `v == v` but accepts positive or
negative infinity. It also does not require the complete frozen semantic-group
key set.

- Use `math.isfinite` for every semantic aggregate and every reported numeric
  scalar used by a gate.
- Require exactly these five aggregate keys and no others:
  `group_completion`, `group_continuation`, `group_verification`,
  `group_error_conflict`, and `group_uncertainty`.
- Require each value to be a real finite float derived from the same validated
  authoritative readout.
- Require exact agreement across multiple authoritative ranks.
- Add synthetic tests for `+inf`, `-inf`, missing keys, extra keys, non-numeric
  values, and cross-rank finite-value disagreement.

### 4. Replace stale commit labels with verifiable source provenance

The current artifact hard-codes `projection_commit = 290e7e8`, but the bridge
itself was subsequently changed in commit `13b81078` to correct cadence-aligned
final-slot duplication. The finalizer only checks that commit/hash fields are
nonempty, and the smoke-driver SHA can be supplied as an arbitrary CLI string.
That does not satisfy exact provenance.

Before execution:

- Require a clean repository and derive the exact full source commit from Git;
  do not trust a caller-provided commit label.
- Record SHA-256 hashes for the exact committed bytes of:
  `src/m37jc_smoke.py`, `src/jlens_vllm_telemetry/bridge.py`,
  `src/jlens_vllm_telemetry/worker_ext.py`, the frozen parity-envelope artifact,
  and the frozen override source or canonical override blob.
- Record the exact model repository/revision already frozen by the existing
  protocol; do not change it.
- At smoke start, verify those hashes against committed files before engine
  construction.
- At finalization, re-read and recompute every source hash and require exact
  equality with the technical artifact. Reject missing, abbreviated, stale,
  caller-supplied, or mismatched provenance.
- Hash the actual pre-finalization artifact bytes, or explicitly label and test a
  canonical-JSON content hash. Do not call one the other.
- Perform the existing recursive aggregate-only privacy/forbidden-key audit on
  both technical and final artifacts before writing `passed`.

### 5. Complete installation metadata and restoration health checks

The all-rank install gate still validates only a subset of the metadata required
by steer `65c76ec`.

- Bridge installation must report and exactly match rank, frozen layers,
  cadence, top-k, slot capacity, hidden size, and decoder-layer count.
- Telemetry installation must report and exactly match rank, MoE-layer count,
  layer ids, expert count, router top-k, capacity, and raw-sample bound.
- Reject missing fields, arbitrary extra scientific fields, already-installed
  state, unexpected decoder depth, unexpected MoE count, or cross-rank mismatch.
- Finalization must require the exact serving reply and exact model id as
  already specified, plus the service's normal health endpoint/process check
  used by the existing serving runbook. Record aggregate booleans only.

## Required synthetic tests and amendment

Add tests covering at minimum:

- bridge install succeeds and telemetry install raises: all-rank cleanup still
  runs and both components end absent;
- hook attachment succeeds but allocation raises inside either worker install:
  every attached handle is removed and state is absent;
- idempotent cleanup succeeds when one or both components were never installed;
- arbitrary monotone off-cadence steps fail;
- incorrect captured-slot, dropped, or projection-call counts fail;
- NaN, positive infinity, negative infinity, missing/extra semantic keys, and
  nonnumeric values fail;
- stale/abbreviated/caller-supplied commit labels and changed source bytes fail;
- finalization rejects a technical artifact whose recorded source hash no
  longer matches the committed file;
- all-rank installation metadata omissions or disagreements fail;
- restoration health failure blocks even if the reply text and model list pass.

Commit the corrected driver, worker extension, tests, and a new aggregate-only
technical amendment before any live M37J-C prompt. Run the full private-safe
suite and `check_commit_safe.py`; verify the pushed remote SHA.

## Execution order remains unchanged

1. Continue M36T sealed capture unchanged to 192/192.
2. Land the corrections above while capture continues; issue no live M37J-C
   prompt.
3. Run only the corrected M36T evaluator exactly once after its full preflight.
4. Restore and verify stock Agents-A1 serving.
5. Run the corrected bounded M37J-C smoke; finalize only after verified
   post-smoke restoration and health checks.
6. Release the dual-3090 window to M38E under its frozen protocol.

Do not shorten the sealed set, lower the generation ceiling, parallelize onto a
non-identical runtime, bypass a gate, or weaken provenance to meet a wall-clock
target.

## Research scan and scaling boundary

- The official InternScience Agents-A1 repository still announces that a 4B
  model is coming, while the official Hugging Face collection currently lists
  only 35B variants. The full backward/Jacobian path therefore remains blocked
  by official smaller-checkpoint availability and the unchanged 30 GiB fitting
  gate.
- `Hidden Error Awareness in Chain-of-Thought Reasoning` reports strong
  hidden-state error discrimination across model families and scales, but its
  attempted interventions fail. This reinforces the current observation-only,
  diagnostic-not-causal claim boundary.
- `Where Does Reasoning Break?` reports useful hidden-state trajectory geometry
  in-domain and collapse of a deployable student under distribution shift. Any
  later Agents-A1 detector must use a fresh protocol with cross-task,
  cross-family, and cross-model shift tests; do not add it to this frozen smoke.
- `PUMA` combines semantic redundancy with answer-level verification. Its
  evidence does not authorize semantic-only early exit.
- `IG-Lens` provides a no-backward additive probability-attribution comparator.
  It remains a possible post-smoke study, not a replacement for the frozen
  standard logit-lens feasibility baseline and not evidence of a Jacobian lens
  on Agents-A1.
- Counterfactual-routing work continues to show that normal routing can be weak
  on fragile reasoning tokens. It supports comparative diagnosis only, not
  route edits or causal claims.
- No actionable r/LocalLLaMA implementation lead was found.

M37J-C can establish only that bounded semantic readouts are technically
observable on the full quantized Agents-A1 runtime while preserving output
parity, dispatch identity, numerical validity, memory, latency, privacy,
cleanup, provenance, and production restoration. It cannot establish a
Jacobian lens on Agents-A1, error prediction, semantic correctness, causal
attribution, expert meaning, route quality, safe early exit, intervention
value, or production utility.

Stop on checkpoint mismatch, dirty tree, source-hash mismatch, task/row mismatch,
task-hash mismatch, verifier bypass, partial installation, leaked hooks,
incomplete rank coverage, empty or off-cadence readout, malformed counters,
non-finite values, tensor-parallel collective mismatch, shard-local id leakage,
cross-rank disagreement, cleanup failure, sampler/engine lifecycle failure,
restoration failure, privacy failure, resource-gate breach, or repeated worker
failure.

Never commit private prompts, outputs, operands, token text or ids, per-task
labels or predictions, raw telemetry, hidden states, activations, gradients,
Jacobians, lens matrices, model weights, caches, stack traces, or local paths.
Public artifacts remain aggregate-only and must pass `check_commit_safe.py`.

Production remains gated. No observation, classifier, tool policy, route edit,
activation intervention, or early-exit rule may be promoted by this directive.
