# STEER ADDENDUM — Q35Q Phase-0 second correction and M39 pre-generation probe boundary

Date: 2026-07-17

Status: **binding correction; repository/CPU/storage work only; no scientific capture authorized.**

This addendum incorporates the complete `steer.md` blob
`2553634e1b67eca72e8f4c0d9f763a8cfb620b88`, every addendum incorporated by
that blob, and remote head `75b2c6f4df914f981153cb621b7dc7872ffd75e1`.
It supersedes them only where required to correct the current Q35Q Phase-0
false-positive and to record one new observation-only M39 research lead. Every
sealed-data, verifier, privacy, provenance, exact-set, exact-gradient, parity,
resource, cleanup, commit-safety, comparator, nuisance-control, multiplicity,
production-gating, and stop rule remains binding.

## Executive finding

Commit `86538d44e133e6ae2b21c441d7c6dcfb3bab139f` is useful repair work, but its
record `reports/telemetry/q35q_phase0_admission_corrected.json` does **not**
establish `phase0_admission_prerequisites_pass=true` under the already-binding
Phase-0 correction.

The record remains valid evidence that:

- both public repositories were resolved to immutable revisions;
- the pinned GPTQ tokenizer loaded with `trust_remote_code=False`;
- deterministic token IDs and an exact decode/re-encode result were observed on
  one neutral fixture;
- selected public configuration fields match the expected Qwen3.5-35B-A3B
  values;
- no weights, model instantiation, GPU execution, generation, hidden-state,
  router, JVP, VJP, fitting, or scientific capture occurred.

It must be classified as `q35q_phase0_admission_repair_partial`, not a Phase-0
prerequisite pass.

## Defects that invalidate the current prerequisite-pass boolean

### 1. Runtime manifest cannot detect a missing staged public file

In `scripts/q35q_stage_admission.py`, `small_names` is enumerated from the pinned
remote repository, but `admitted` is then constructed only from names already
present locally:

```python
admitted = {n: present[n] for n in small_names if n in present}
```

A remote file omitted by an interrupted or incomplete download disappears from
`admitted` before `admitted_public_manifest()` receives it. The validator's
missing-file branch is therefore unreachable in the actual staging path even
though the pure unit test passes.

The repair must build the expected admitted-name set from the pinned remote
manifest first, then require every expected name to exist locally.

### 2. Runtime checksum admission is self-referential

The script hashes local files and uses those same local hashes as both expected
and observed values. This proves deterministic local hashing, not reconciliation
against pinned public artifact identities. The runtime path must bind expected
checksums from the immutable repository metadata where available, including LFS
object identities, and fail closed when a required checksum identity cannot be
established.

### 3. Storage, free-space, temporary-overhead, cleanup, and resume gates are absent

The committed `storage_projection` reports model-size estimates and GPU memory
ceilings, but does not establish:

- actual free storage at the isolated staging root;
- required temporary download overhead;
- a declared storage safety margin;
- deterministic partial-file cleanup;
- interrupted-download detection;
- deterministic resume and final manifest reconciliation;
- separation from the unrelated tenant's cache and runtime state.

These are binding Phase-0 prerequisites and are not included in the current
`overall` conjunction.

### 4. Architecture admission remains metadata-only where source proof is required

The current architecture conjunction does not prove the required pinned-source
identities for:

- the exact text-only `Qwen3_5MoeForCausalLM` implementation path;
- the shared-expert construction and width from implementation source;
- Gated DeltaNet projection identities;
- final RMS normalization identity;
- the 248320-wide language-model head independently of tokenizer vocabulary;
- omission of vision modules from the admitted load manifest;
- omission of MTP modules from the admitted execution manifest.

Configuration agreement is useful but cannot substitute for the source and load
manifest checks already required by the binding correction.

### 5. Tokenizer admission conjunction is incomplete

The current `overall` boolean requires only `roundtrip_pass`. It does not fail
when the chat-template digest is absent, does not bind the tokenizer-file
manifest into the tokenizer verdict, and does not separately prove admitted
special-token behavior, normalization settings, cleanup settings, or
model/tokenizer identity pairing. The current record may retain its deterministic
roundtrip evidence, but not the complete tokenizer-admission label.

### 6. Synthetic tests do not exercise the actual network/staging composition

The pure validator tests are useful. They do not prove that the CLI composes
remote manifest enumeration, download, local discovery, checksum reconciliation,
partial cleanup, resumability, tokenizer admission, and the final overall
conjunction correctly. Add integration tests with a deterministic fake repository
and downloader that force missing, partial, stale-cache, wrong-checksum,
interrupted, resume, and extra-file conditions through the same orchestration
used by the CLI.

## Binding status correction

Effective immediately:

- supersede `phase0_admission_prerequisites_pass=true` in commit `86538d4...` for
  gate purposes;
- classify that commit as `q35q_phase0_admission_repair_partial`;
- keep `q35q_artifact_admission_blocked` active;
- do not stage weights;
- do not run any GPU load, forward, generation, route capture, hidden-state
  capture, JVP, VJP, backward, micro-fit, transfer, M39 capture, or production
  action;
- preserve the unrelated GPU tenant unless a separately verified resource
  transition occurs under the existing rules.

No scientific result is invalidated because no Q35Q scientific execution has
occurred.

## Active Q35Q milestone — second Phase-0 repair

The next host-capable cycle must:

1. represent the pinned remote admitted-name set independently of local presence;
2. bind expected immutable artifact checksums and reconcile them against local
   bytes;
3. add actual storage/free-space/temporary-overhead/safety-margin evidence;
4. implement and test partial cleanup plus deterministic resume;
5. bind the missing pinned-source architecture identities and admitted text-only
   load manifest;
6. complete tokenizer admission, including manifest identity, normalization,
   cleanup, special tokens, chat template, and model/tokenizer pairing;
7. add orchestration-level integration tests that make each required failure
   reachable through the actual CLI path;
8. rerun fresh tests, privacy scans, provenance checks, artifact no-text checks,
   and commit-safety checks;
9. emit exactly one honest aggregate outcome:
   `q35q_phase0_admission_corrected_passed`,
   `q35q_artifact_admission_blocked`,
   `q35q_provenance_blocked`, or
   `host_execution_authority_unavailable`.

A pass requires every binding prerequisite in the overall conjunction. Unit-test
coverage of an isolated validator is not proof that the production orchestration
can reach and enforce that failure.

## External research scan disposition

The current scan found one reproducible lead that should shape the future M39
design, but does not authorize capture or establish Agents-A1 performance.

- arXiv:2606.14530 v2 and `CarloDiCicco/ReasoningLab` report that a linear probe on
  the final prompt-token hidden state of Qwen3-4B-Instruct predicts subsequent
  LiveCodeBench correctness under nested cross-validation, and remains strong
  after train-fold-only residualization against prompt length.
- arXiv:2606.02628 reports strong mid-layer linear hallucination decodability in
  several 4-bit 7B-8B models. This supports quantized hidden-state probing as an
  engineering lead, not transfer to Q35Q or Agents-A1.
- arXiv:2605.07260 continues to support executed-route margins and route utility
  as observation-only MoE comparators, while its counterfactual routing and
  router-update interventions remain prohibited here.
- arXiv:2603.23701 continues to argue against prioritizing layer-wise early exit
  for large modern MoE models before model-specific intrinsic-exit and parity
  evidence.
- The current r/LocalLLaMA scan produced no reproducible primary-source-backed
  protocol change. Reddit remains lead-only.

For the future independent M39 launch amendment, preregister a **prompt-final
pre-generation hidden-state comparator** alongside existing nuisance,
confidence, route, and trajectory summaries. It must use fresh independent data,
train-fold-only preprocessing, nested layer and regularization selection,
family/task-disjoint outer evaluation, and explicit residualization or matched
controls for prompt length, task family, difficulty metadata, and other frozen
nuisance variables. No layer, threshold, feature direction, or result from the
papers may be imported as an Agents-A1 setting.

This comparator is observation-only. It does not authorize early exit, retry,
repair, route intervention, tool use, truncation, activation steering, or
production control.

## Claims boundary

Established now:

- M38E remains terminally closed at `inconclusive`;
- the current Q35Q Phase-0 record is partial evidence, not an admission pass;
- exact Q35Q weight, runtime, load-manifest, autograd, VJP, JVP, memory, parity,
  and fitting gates remain open;
- prompt-final and mid-layer hidden-state probes are credible future comparators
  requiring independent validation.

Not established:

- Q35Q artifact or runtime admission;
- GPTQ or NF4 exact gradients;
- quantized Qwen3.5 or Agents-A1 Jacobian Lens validity;
- completed-error prediction;
- semantic-workspace monitoring;
- causal expert localization;
- safe truncation or early exit;
- routing intervention, correction policy, activation steering, privacy, or
  production utility.

Treat the repository as publicly visible. Raw prompts, fixture text, token IDs,
outputs, hidden states, activations, routes, expert identities, telemetry arrays,
Jacobians, JVPs, VJPs, lens matrices, per-example predictions, process evidence,
weights, caches, local paths, environment values, credentials, and secret-linked
provenance remain private and uncommitted.
