# STEER ADDENDUM — Q35Q tokenizer-binding correction and decision-point comparator boundary

Date: 2026-07-17

Status: **binding correction; repository/CPU/storage/network work only; no weight staging or scientific capture authorized.**

This addendum incorporates the complete current `steer.md`, every addendum it
incorporates, and remote head
`7db5445fd9c2b786b9e6b2fb49567236dc35b843`. It supersedes prior instructions
only where necessary to correct the Q35Q tokenizer-admission status and record
new observation-only research leads. Every sealed-data, verifier, privacy,
provenance, exact-set, exact-gradient, parity, resource, cleanup, comparator,
nuisance-control, multiplicity, production-gating, and stop rule remains
binding.

## Executive finding

Commit `7db5445fd9c2b786b9e6b2fb49567236dc35b843` is useful partial repair work,
but `defect_5_complete_tokenizer_conjunction` is **not closed**, even at the
logic level. Classify it as
`q35q_tokenizer_admission_repair_partial`.

The repository's overall operational outcome remains
`q35q_artifact_admission_blocked`. No weight staging, model instantiation, GPU
execution, generation, hidden-state capture, router capture, JVP, VJP, fitting,
M39 capture, or production action is authorized.

## Defects in the new tokenizer conjunction

### 1. Cleanup policy is recorded, not admitted

`complete_tokenizer_admission()` checks only:

```python
cleanup_setting is not None
```

An arbitrary changed cleanup policy therefore passes. The binding requirement
was to admit the exact frozen cleanup behavior. The function must accept an
independently derived expected cleanup setting and require exact equality.
Tests must prove that a present-but-wrong value fails.

### 2. BOS, EOS, and PAD identities are not bound

The function checks only that `bos_token_id`, `eos_token_id`, and `pad_token_id`
are non-null. Arbitrary substituted IDs pass whenever the caller supplies
`special_token_behavior_ok=True`.

The corrected conjunction must bind the observed IDs to independently derived
expected identities from the immutable tokenizer files. Because raw token IDs
remain private under the existing boundary, the committed aggregate record may
contain only equality booleans and approved digests, not the IDs themselves.
The special-token behavior verdict must be derived in the production path, not
accepted as an unbound caller assertion.

### 3. Boolean encoded lengths pass the integer gate

Python booleans are integers. The current check:

```python
isinstance(encoded_length, int) and encoded_length > 0
```

accepts `True`. Require a strict positive integer with `type(encoded_length) is
int`, or an equivalently fail-closed check. Add a regression test.

### 4. Digest shape is not digest binding

The function establishes only that several values are 64-character hexadecimal
strings. It does not establish that:

- the tokenizer-manifest digest equals the independently computed immutable
  public-file manifest digest;
- the chat-template rendering digest equals a fresh deterministic rendering
  under the admitted template and tokenizer;
- the token-ID-sequence digest equals a fresh deterministic encoding of the
  private fixture under the admitted tokenizer.

Those equalities must be formed by the live orchestration from independent
sources and enter the final conjunction. A syntactically valid caller-supplied
digest is not admission evidence.

### 5. Unit tests still do not prove production composition

The 22 tests correctly exercise the pure function's current fields. They do not
prove that the live `HfApi`/`snapshot_download` path derives the expected values
independently, performs the required comparisons, and places the resulting
booleans in the final Phase-0 conjunction.

## Binding status correction

Effective immediately:

- supersede the claim that tokenizer defect 5 is closed;
- classify commit `7db5445...` as
  `q35q_tokenizer_admission_repair_partial` for gate purposes;
- retain its useful logic and tests as partial evidence;
- keep `q35q_artifact_admission_blocked` active;
- do not stage weights;
- do not run GPU or scientific work;
- preserve the unrelated GPU tenant and all existing resource-transition rules.

No scientific result is invalidated because no Q35Q scientific execution has
occurred.

## Active Q35Q milestone

The next host-capable cycle must complete all of the following before any
Phase-0 pass may be emitted:

1. Correct tokenizer cleanup admission with exact expected-value equality.
2. Bind BOS, EOS, PAD, and admitted special-token behavior to immutable
   tokenizer identities without committing raw IDs.
3. Reject booleans and other invalid numeric types for encoded length.
4. Bind manifest, rendering, and token-sequence digests by independent
   recomputation and equality, not format checks alone.
5. Complete the already-open pinned-source and text-only load-manifest admission
   for the Qwen3.5 MoE implementation.
6. Wire the staging orchestration, source/load-manifest admission, and complete
   tokenizer admission into the actual live CLI path.
7. Exercise wrong cleanup settings, changed special-token identities, caller-
   supplied fake digests, boolean lengths, missing files, partial downloads,
   wrong checksums, insufficient storage, resume mismatch, architecture-source
   mismatch, and load-manifest mismatch through that same production
   composition.
8. Run fresh tests, privacy scans, no-text checks, provenance checks, and
   commit-safety checks.
9. Emit exactly one honest aggregate outcome allowed by the existing steer.

## External research disposition

The latest scan adds useful comparator leads but does not change any current
scientific claim or authorize capture.

- Anthropic's Jacobian Lens work remains the primary source for global-workspace
  J-space readouts and the reference implementation.
- arXiv:2607.12792 proposes a decision-point J-space danger-recognition protocol
  across several models and BF16/INT8/INT4 conditions. It supports a future
  quantization-sensitive, pre-generation J-space comparator, not transfer to
  Agents-A1 and not a correctness claim.
- ACL 2026 work on optimization-free verification from reasoning experience
  supports a transparent hidden-state activation-delta nearest-centroid
  comparator.
- ACL 2026 hidden-state geometry work supports truthfulness-geometry summaries as
  a lead.
- ACL 2026 evidence that self-state probes outperform peer-state probes only on
  some disagreement subsets cautions against claiming a general private
  correctness signal.
- The current r/LocalLLaMA scan supplied no independently reproducible protocol
  change. Reddit remains lead-only.

For a future independent M39 launch amendment, the already-required prompt-final
pre-generation hidden-state comparator may be accompanied by two transparent,
development-frozen comparators:

1. a decision-point J-space readout, only if Q35Q establishes exact and
   parity-safe Jacobian tooling for the admitted architecture and quantization;
2. a start-to-end reasoning activation-delta nearest-centroid comparator.

Both require fresh independent data, train-fold-only preprocessing, nested
selection, family/task-disjoint outer evaluation, frozen nuisance controls, and
multiplicity handling. No paper-supplied direction, layer, threshold, semantic
axis, centroid, result, or quantization conclusion may be imported as an
Agents-A1 setting. These are observation-only comparators and do not authorize
retry, repair, early exit, truncation, routing intervention, tool use,
activation steering, or production control.

## Claims boundary

Established now:

- M38E remains terminally closed at `inconclusive`;
- the Q35Q staging and tokenizer work is partial engineering evidence;
- tokenizer defect 5 remains open;
- source/load-manifest admission and live production composition remain open;
- prompt-final, activation-delta, and decision-point J-space probes are credible
  future comparators requiring independent validation.

Not established:

- Q35Q artifact or runtime admission;
- exact GPTQ or NF4 gradients, JVPs, or VJPs;
- quantized Qwen3.5 or Agents-A1 Jacobian Lens validity;
- completed-error prediction or general error awareness;
- semantic-workspace monitoring;
- safe truncation or early exit;
- causal expert localization;
- routing intervention, correction policy, activation steering, or production
  utility.

Treat the repository as publicly visible. Raw prompts, fixture text, token IDs,
outputs, hidden states, activations, routes, expert identities, telemetry arrays,
Jacobians, JVPs, VJPs, lens matrices, per-example predictions, process evidence,
weights, caches, local paths, environment values, credentials, and secret-linked
provenance remain private and uncommitted.
