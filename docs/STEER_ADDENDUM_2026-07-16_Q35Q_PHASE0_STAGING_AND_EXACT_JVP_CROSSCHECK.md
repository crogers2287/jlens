# STEER ADDENDUM — Q35Q Phase-0 public-artifact staging and exact JVP cross-check

Status: **binding Q35Q operational clarification; not GPU execution authorization.**

This addendum incorporates the current `steer.md` blob
`52227ac18f3f1712b0909e2b8c282d12cf7dfc91`,
`docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md`, and
`docs/STEER_ADDENDUM_2026-07-15_Q35Q_ROUTE_REGIME_AND_EXACT_SHARDING.md`.
It supersedes them only where it resolves the Phase-0 staging ambiguity below.
Every sealed-data, verifier, privacy, provenance, exact-gradient, resource,
parity, cleanup, commit-safety, production-gating, and stop rule remains binding.

## Decision basis

Remote head `ee3654d29b300884591fe51cb18912c95d2de01d` records that M38E is
terminally closed at `inconclusive`, the unrelated dual-RTX-3090 tenant remains
untouched, Q35Q is the active milestone, and Q35Q remains CPU/storage/repository-
side only. That status also says model/tokenizer download is not yet authorized.

The binding Q35Q protocol already authorizes CPU-side implementation, artifact-
admission work, and download staging before GPU execution. The phrase "download
not yet authorized" is therefore an operational ambiguity, not a scientific or
privacy gate. Leaving it unresolved would prevent the only currently permitted
work and create repeated status-only heartbeats.

This addendum authorizes the bounded public-artifact staging sequence below. It
does not release the GPU window, restore Agents-A1 serving, authorize model
execution, or convert `q35q_artifact_admission_blocked` into a pass.

## Immediate authorized Phase-0 sequence

The next host-capable Q35Q cycle must perform, in order:

1. Pin immutable revisions for the official public repositories
   `Qwen/Qwen3.5-35B-A3B-Base` and
   `Qwen/Qwen3.5-35B-A3B-GPTQ-Int4`. A mutable branch name may be used only to
   discover an immutable revision; it may not appear as the admitted identity.
2. Stage public repository metadata and the smallest files needed for admission:
   license, model card, configuration, tokenizer, tokenizer configuration,
   processor configuration, chat template, generation configuration, custom-code
   source, and public file manifests. Do not execute custom code during discovery.
3. Review and hash every custom-code source file before any later
   `trust_remote_code` execution. Unreviewed, mutable, missing, or identity-
   mismatched custom code records `q35q_artifact_admission_blocked`.
4. Produce a genuine deterministic tokenizer roundtrip record from a neutral,
   public, non-outcome-bearing fixture. Bind exact tokenizer revision, file
   hashes, normalization, special-token behavior, chat-template identity,
   encoded-length summary, and roundtrip result. Raw fixture text and token IDs
   remain private and uncommitted; commit only aggregate pass/fail and hashes.
5. Produce a text-only configuration and architecture admission record without
   loading weights. Verify the expected language-model class, hidden dimension,
   layer count, routed/shared expert layout, attention/DeltaNet layout,
   vocabulary/output dimensions, omitted vision modules, and MTP exclusion.
6. Generate deterministic public file manifests, expected download sizes,
   storage projections, cache-isolation rules, checksum procedures, and
   resumability checks for the GPTQ and BF16/NF4 candidate paths.
7. Storage-only weight staging is authorized after the preceding repository,
   free-space, cache-isolation, immutable-revision, and checksum procedures pass.
   Weight staging may use CPU, storage, and network resources only. It may not
   instantiate a model, allocate GPU memory, run a forward pass, invoke a
   quantization kernel, or inspect Agents-A1 artifacts.
8. Regenerate and test the Q35Q admission and driver manifests, synthetic
   validation suite, privacy scan, and commit-safety checks. Persist only public
   identities and aggregate outcomes.

No additional operator ruling is required for this exact Phase-0 sequence. Any
step outside this sequence remains unauthorized unless already permitted by the
incorporated protocol.

## Hard resource and execution boundary

Until the dual-RTX-3090 resources are legitimately available and the applicable
resource/serving transition is verified:

- do not signal, stop, inspect, reconfigure, or displace the unrelated
  `llama-server` / llama-swap / MCP tenant;
- do not load Q35Q weights onto a GPU;
- do not run generation, hidden-state capture, router capture, JVP, VJP,
  backward, micro-fit, lens fitting, transfer, or M39 scientific capture;
- do not use CPU or disk offload to disguise a GPU execution path;
- do not access, copy, hash, or stage private Agents-A1 prompts, outputs,
  telemetry, routes, states, weights, caches, or ledgers;
- do not describe successful download, tokenizer load, config parsing, or model
  construction as evidence of exact autograd support.

A storage, identity, license, checksum, source-review, privacy, or commit-safety
failure stops staging and records the narrow aggregate blocker. It does not
permit substitution of a different model, revision, tokenizer, quantization, or
runtime.

## Rapid-MLX Jacobian-lens implementation disposition

The public `raullenchai/Rapid-MLX` implementation added a `jlens` command at
commit `f0c754337fc282a0e957e4550fc57ed74bd8e2f4`; the reviewed source identity
was `d5741f1c0667688e01f1db5494c981c627210e42`. It is a useful independent
engineering lead because it applies forward-mode `mx.jvp` through quantized MLX
models and exposes layerwise rank trajectories.

It is not adopted as Q35Q evidence or as an Agents-A1 method because:

- its MLX runtime and Apple-hardware execution path do not establish the
  admitted PyTorch GPTQ or NF4 path;
- its implementation falls back to finite differences when forward-mode
  autodiff fails;
- its fixed corpus, "workspace signal," answer-crystallization layer, and
  reported early-exit headroom are heuristic and are not verifier-backed
  correctness, causality, safe truncation, or production evidence;
- no finite-difference result may satisfy Q35Q's exact-gradient gate.

After, and only after, a Q35Q candidate passes the existing genuine reverse-mode
VJP gate, a separately preregistered diagnostic may attempt an exact forward-mode
JVP on the same admitted model, quantization, route regime, sequence, source,
target, runtime, and device placement. The diagnostic must:

1. prohibit finite differences, straight-through estimators, detached
   dequantize/requantize paths, manually substituted derivatives, and runtime or
   model substitution;
2. freeze deterministic probe vectors, precision, reduction order, and numerical
   tolerance before execution;
3. test the adjoint identity `u^T (J v) = v^T (J^T u)` against the already-passing
   reverse-mode VJP;
4. require finite, nonzero, repeatable JVP and VJP values, output parity, route
   parity, frozen weights, no hidden offload, resource compliance, and cleanup;
5. record only aggregate discrepancy, timing, memory, identities, and pass/fail.

Forward-mode unsupported records `q35q_exact_jvp_crosscheck_unsupported` and does
not invalidate an otherwise passing exact reverse-mode VJP. A numerical mismatch,
detachment, substitution, or approximate fallback records
`q35q_exact_jvp_crosscheck_failed` and blocks any strengthened exact-gradient or
implementation-correctness claim pending a separate preregistered resolution.
Neither outcome authorizes fitting, transfer, correctness prediction, early exit,
or production use.

## Router-trajectory research disposition

`Polysemantic Experts, Monosemantic Paths: Routing as Control in MoEs`
(arXiv:2604.17837) supports treating routing trajectories and router-visible
subspaces as candidate interpretability objects rather than assigning semantic
meaning to isolated expert identities. `The Myth of Expert Specialization in
MoEs` (arXiv:2604.09780) cautions that routing similarity can largely follow
hidden-state geometry and that prompt-level routes may poorly represent deeper
rollout routing.

These results reinforce, but do not expand, the existing M39 design:

- preserve executed-route margins, loads, transitions, and temporal summaries;
- preserve train-fold-only nuisance conditioning and hidden-state comparators;
- do not commit expert identities or token-level route trajectories;
- do not add a new outcome-bearing feature, selected layer, threshold, route
  intervention, or expert-specialization claim from this scan;
- do not infer semantic workspace, correctness, causal control, or safe stopping
  from route-path coherence alone.

## Required next operational record

The next Q35Q operational commit must record one of:

- immutable tokenizer/config identities staged and the genuine tokenizer plus
  text-only architecture admission sequence in progress or complete;
- a narrow exact blocker from repository identity, license, source review,
  storage, checksum, dependency, privacy, or commit-safety evidence;
- `host_execution_authority_unavailable` once if the executing agent cannot
  access the authorized CPU/storage/network path.

Repeated unchanged claims that download staging is not authorized are no longer
an admissible steady state. `q35q_artifact_admission_blocked` remains binding
until every required admission record is genuinely present and committed.

## Privacy, claims, and completion boundary

Treat the repository as publicly visible. Never commit raw fixture text, token
IDs or text, prompts, outputs, hidden states, activations, expert identities,
routes, router logits, telemetry arrays, Jacobians, JVPs, VJPs, lens matrices,
per-example scores, process evidence, weights, caches, local paths, environment
values, credentials, or secret-linked provenance.

This addendum establishes only an executable Phase-0 staging path and an optional
future exact-autodiff consistency diagnostic. No Q35Q artifact is admitted by
this commit. No exact GPTQ or NF4 VJP or JVP has passed. No quantized Qwen3.5 or
Agents-A1 lens has been fitted or validated. No transfer, completed-error
prediction, semantic-workspace monitoring, truncation, early exit, routing
intervention, activation steering, privacy, or production utility is
established. The research program remains incomplete.