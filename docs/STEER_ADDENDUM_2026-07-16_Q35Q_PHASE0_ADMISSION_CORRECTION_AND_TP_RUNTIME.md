# STEER ADDENDUM — correct Q35Q Phase-0 admission and bind a viable tensor-parallel runtime

Status: **binding Q35Q correction; repository/CPU/storage work only; no GPU authorization.**

This addendum incorporates the current `steer.md` blob
`52227ac18f3f1712b0909e2b8c282d12cf7dfc91`,
`docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md`,
`docs/STEER_ADDENDUM_2026-07-15_Q35Q_ROUTE_REGIME_AND_EXACT_SHARDING.md`, and
`docs/STEER_ADDENDUM_2026-07-16_Q35Q_PHASE0_STAGING_AND_EXACT_JVP_CROSSCHECK.md`.
It supersedes them only where required to correct the Phase-0 false-positive
boundary and to bind an upstream tensor-parallel runtime requirement. Every
sealed-data, verifier, privacy, provenance, exact-gradient, parity, resource,
cleanup, commit-safety, production-gating, and stop rule remains binding.

## Decision basis

Remote head `7c91af53ad8c5b5b934e66ea68ecf6dd514a85ca` records useful partial
staging for `Qwen/Qwen3.5-35B-A3B-GPTQ-Int4` at immutable revision
`3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b`. The tokenizer was genuinely
loaded with `trust_remote_code=False`, deterministic token IDs were observed,
and no GPU, weight load, model instantiation, hidden-state capture, or
scientific capture occurred.

That work is valid staging evidence, but it does **not** satisfy the binding
Phase-0 tokenizer and architecture admission gates:

1. The committed record explicitly reports `shared_experts: false` while also
   reporting `architecture_text_only_admitted: true`.
2. `scripts/q35q_stage_admission.py` omits shared-expert layout from
   `architecture_match`, and its final admission boolean checks only hidden
   size, layer count, and vocabulary size. Routed-expert count, top-k,
   MoE-intermediate width, shared-expert structure, model class, hybrid layer
   layout, output head, vision omission, and MTP exclusion cannot fail that
   boolean.
3. The tokenizer check accepts a decoded string when only the first sentence of
   the fixture appears as a substring. It does not bind the required
   normalization, special-token behavior, chat-template behavior, or full
   deterministic roundtrip semantics.
4. The file-manifest loop walks the complete local staging directory without
   excluding `.cache` or downloader metadata. The committed digest is therefore
   not proven to be a deterministic manifest of public repository files only.
5. Only the GPTQ repository is pinned. The required immutable base-checkpoint
   identity, storage projections, checksum procedures, and remaining Phase-0
   steps are absent.

The historical commits and aggregate record must remain intact. Their admission
labels are superseded for gate purposes by this correction.

## Executive decision

Effective immediately:

- classify commit `1123561ed4f360c14cf424bc0156842d2947b353` as
  `q35q_admission_staging_partial` only;
- do not treat its `architecture_text_only_admitted` field as an admission pass;
- do not treat its tokenizer result as the complete binding tokenizer-admission
  record, although it remains evidence that the pinned tokenizer genuinely
  loaded and produced deterministic IDs on one neutral fixture;
- keep `q35q_artifact_admission_blocked` active;
- do not begin storage-only weight staging until corrected Phase-0 steps 1-6 all
  pass, including both immutable repository identities, deterministic
  public-file manifests, storage/free-space projections, checksum procedures,
  and resumability checks;
- do not run any GPU load, forward, generation, router capture, hidden-state
  capture, JVP, VJP, backward, micro-fit, fitting, transfer, or M39 capture;
- do not signal, inspect, reconfigure, or displace the unrelated GPU tenant.

No scientific result is invalidated because no Q35Q scientific execution has
occurred. This correction prevents partial metadata checks from being promoted
into a false artifact-admission pass.

## Required Phase-0 repair

The next host-capable Q35Q cycle must repair the staging implementation and its
synthetic tests before rerunning the aggregate record.

### Repository and manifest identity

1. Pin immutable revisions for both:
   - `Qwen/Qwen3.5-35B-A3B-Base`;
   - `Qwen/Qwen3.5-35B-A3B-GPTQ-Int4`.
2. Enumerate admitted repository files from the pinned public repository
   manifest. Hash only explicitly admitted files. Exclude local cache folders,
   lock files, downloader metadata, timestamps, temporary files, partial files,
   symlinks outside the staging root, and host-specific paths.
3. Commit only aggregate counts, public relative-path manifest hashes, total
   public byte counts, immutable repository identities, and pass/fail. Do not
   commit raw tokenizer IDs, fixture text, weights, caches, or local paths.
4. Add synthetic tests proving that cache metadata, an extra unapproved file, a
   missing file, a mutable revision, a path escape, a hash mismatch, and an
   interrupted partial download all fail closed.

### Exact text architecture record

The corrected aggregate record must fail unless all applicable public metadata
and pinned implementation-source checks pass:

- outer architecture class `Qwen3_5MoeForConditionalGeneration` and the exact
  admitted text-only class/source mapping;
- outer model type `qwen3_5_moe` and text model type `qwen3_5_moe_text`;
- hidden size 2048;
- 40 text layers;
- vocabulary and language-model output width 248320;
- 256 routed experts and top-8 routing;
- MoE intermediate size 512;
- one shared-expert path with shared-expert intermediate size 512, verified from
  the pinned model implementation rather than inferred from a nonexistent
  `num_shared_experts` field;
- the exact 40-entry hybrid layout: three `linear_attention` layers followed by
  one `full_attention` layer, repeated ten times, with
  `full_attention_interval=4` and the admitted Gated DeltaNet projection fields;
- final RMS normalization identity and untied 248320-wide language-model head;
- vision modules present in the source repository but omitted from the admitted
  text-only load path;
- MTP metadata present (`mtp_num_hidden_layers=1`) but MTP modules excluded from
  the admitted text-only execution path;
- GPTQ configuration identity, including 4-bit GPTQ, group size 128, and every
  skipped/dynamic module rule.

A missing, contradictory, inferred, or source-unverified field records
`q35q_artifact_admission_blocked`. Do not collapse all checks into a small subset
boolean. The aggregate artifact must expose a pass/fail boolean for every frozen
field and an overall conjunction over every required field.

The tokenizer vocabulary reported by the tokenizer may differ from the padded
248320 language-model output dimension. Record both values and their meaning;
do not silently equate them or treat the difference as failure without the
pinned tokenizer/model contract.

### Binding tokenizer record

Use the same immutable tokenizer files and neutral public fixture. The corrected
record must bind:

- exact tokenizer repository revision and file-manifest digest;
- tokenizer class and `trust_remote_code` setting;
- normalization and cleanup settings;
- `add_special_tokens=False` and the separately tested admitted special-token
  behavior;
- BOS/EOS/PAD and chat-template identities;
- deterministic encoded length and private ID-sequence digest;
- exact deterministic decode/re-encode behavior under a preregistered
  normalization rule, not a substring-only check;
- deterministic chat-template rendering digest on a neutral fixture, while raw
  rendered text and token IDs remain private.

Synthetic tests must prove that substring-only reconstruction, changed
normalization, changed special tokens, changed chat template, tokenizer/model
identity mismatch, or nondeterministic IDs fail closed.

## Tensor-parallel runtime requirement

Upstream Hugging Face Transformers commit
`259711a042c5858d8c48edf04aa97b7021fee4b3` corrected the Qwen3.5-MoE
base tensor-parallel plan by adding the five Gated DeltaNet projections
`in_proj_qkv`, `in_proj_z`, `in_proj_b`, `in_proj_a`, and `out_proj` as
`colwise_gather_output`. The upstream change states that without these entries,
linear-attention weights remain unsharded and Qwen3.5-MoE can OOM at tensor
parallel degree greater than one.

Therefore:

1. No Transformers source lacking the equivalent five Qwen3.5-MoE
   linear-attention TP-plan entries is admissible for the dual-GPU Q35Q path.
2. The eventual runtime must pin an exact immutable Transformers source commit,
   package build identity, PyTorch/CUDA identities, and generated configuration
   source hashes. A mutable release name or an unreviewed later branch is not
   sufficient.
3. Before GPU execution, synthetic source inspection must prove that the selected
   immutable runtime contains the required TP plan and has not substituted the
   model class, expert path, quantization path, or linear-attention kernels.
4. The explicit dual-3090 placement plan must account for the full-channel
   all-gather required before depthwise convolution. The existing 23.0 GiB per
   GPU and 46.0 GiB aggregate ceilings are unchanged.
5. A source/runtime mismatch, missing TP entry, hidden offload, OOM, placement
   mismatch, or kernel substitution remains a hard stop. Do not work around it
   by weakening the resource gate or using `device_map="auto"` as proof.

The reviewed upstream implementation also exposes a text-only
`Qwen3_5MoeForCausalLM` path and optional `router_logits`. These are credible
engineering leads for omitting vision/MTP weights and obtaining direct
executed-router telemetry without semantic expert labels. They are not admitted
until the exact runtime source is pinned, the load manifest proves which modules
were omitted, output and route parity pass, resource use passes, raw router
arrays remain private, and only aggregate route summaries are committed.

## Research-scan disposition

The current external scan found no new paper or r/LocalLLaMA lead that warrants
an outcome-bearing feature, threshold, selected layer, stopping rule, route
intervention, or production policy.

- Current routing-signature, routing-control, misrouting, and hardware-telemetry
  papers continue to support route margins, loads, transitions, entropy, and
  hidden-state comparators as candidate observation-only summaries.
- They do not establish Agents-A1 correctness prediction, semantic workspace,
  causal routing, safe truncation, or privacy.
- Current early-exit evidence remains unfavorable for prioritizing layer
  truncation in a large modern MoE before model-specific intrinsic-exit and
  final-output-parity gates.
- Reddit produced no reproducible primary-source-backed change beyond leads
  already reviewed. Reddit remains lead-only.

The upstream Transformers TP fix is the only new evidence in this cycle that
changes the executable scaling plan. It strengthens, rather than weakens, the
existing explicit-sharding gate.

## Required next operational record

The next Q35Q operational commit must record exactly one of:

1. the staging script and synthetic tests repaired, both model repositories
   immutably pinned, and a corrected aggregate tokenizer/architecture/manifest
   rerun whose overall admission conjunction is honest;
2. a narrow blocker from repository identity, source review, tokenizer contract,
   architecture mismatch, dependency identity, storage projection, checksum,
   privacy, or commit safety;
3. `host_execution_authority_unavailable` once if the executing agent cannot
   access the already-authorized CPU/storage/network path.

Do not repeat the superseded architecture-admission pass. Do not stage weights
before the corrected prerequisite record. Fresh repository tests, privacy scan,
and commit-safety checks are required for the next operational commit.

## Privacy, claims, and completion boundary

Treat the repository as publicly visible. Never commit raw prompts, fixture text,
token IDs or text, outputs, hidden states, activations, expert identities,
routes, router logits, telemetry arrays, Jacobians, JVPs, VJPs, lens matrices,
per-example scores, process evidence, model weights, caches, local paths,
environment values, credentials, or secret-linked provenance.

This addendum establishes a corrected admission boundary and a technically
credible tensor-parallel dependency requirement only. It does not admit a model
artifact or runtime. No exact GPTQ or NF4 VJP/JVP has passed. No quantized
Qwen3.5 or Agents-A1 lens has been fitted or validated. No transfer,
completed-error prediction, semantic-workspace monitoring, truncation, early
exit, routing intervention, activation steering, privacy, or production utility
is established. The research program remains incomplete.