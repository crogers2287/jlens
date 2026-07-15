# steer.md — prioritize an architecture-matched quantized Qwen3.5 MoE Jacobian path without disturbing M38E

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
prior steer only where explicitly amended below. Every predecessor remains
binding by incorporation, including all sealed-data, verifier, privacy,
provenance, exact-set, cap-escalation, resource, claim-boundary, retry,
production-gating, repository-hygiene, and stop rules. No frozen scientific
result, task, family, seed, threshold, verifier, sampling setting, token cap,
power gate, comparator, or production gate may be weakened or retuned.

## Current established state

- The latest pre-steer heartbeat was
  `15b880bcbaa272c1ceeed5c6d1d1eb99b8f2ef94`: M38E attempt one was healthy at
  226/288 official tasks, `order_track` band 2 at 10/24, 62 official tasks
  remaining, and 52/52 fresh core tests passing.
- Do not interrupt, inspect private rows from, signal, restart, reconfigure,
  contend with, or otherwise disturb the active M38E process, environment,
  worktree, cache, or ledger.
- The M38E two-family completed-error frontier is already irreversibly
  unavailable under the frozen protocol. Remaining execution and finalization
  are still mandatory for exact-set, escalation, verifier, provenance, privacy,
  dependency, resource, cleanup, and commit-safety evidence.
- The prospective M38E terminal outcome remains
  `m38e_completed_error_frontier_not_found` after successful completion and
  audits, or the narrower `provenance-blocked` / `inconclusive` outcome if an
  original finalization requirement cannot be verified.
- M36T T-H3 remains established only as verifier-backed adaptive tool and compute
  allocation on its frozen deterministic population. It does not establish a
  router, hidden-state, semantic, or Jacobian mechanism.
- M37J-C remains blocked by its frozen disabled-path parity gate. Its memory,
  runtime, and observability measurements remain descriptive technical facts.
- M39 remains the independently preregistered forward-only test of incremental
  completed-error prediction on Agents-A1 35B. Scientific M39 capture remains
  prohibited until M38E is formally finalized and the complete launch amendment
  is committed.
- No Jacobian Lens has been fitted or validated on Agents-A1. No safe truncation,
  early exit, causal repair, activation steering, route intervention, or
  production utility is established.

## Binding decision: adopt Q35Q as the primary architecture-matched engineering surrogate

Commit `35ea8ab80880466534e4e2f33d00312067637ef1` added
`docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md`. That protocol is now binding.

The official `Qwen/Qwen3.5-35B-A3B-Base` and
`Qwen/Qwen3.5-35B-A3B-GPTQ-Int4` checkpoints provide a substantially closer
engineering surrogate than an unrelated MoE because the official model cards
identify the same Qwen3.5 MoE structure used by the Agents-A1 lineage:

- hidden dimension 2048;
- 40 language-model layers;
- 256 routed experts;
- 8 routed plus 1 shared expert per token;
- expert intermediate dimension 512;
- hybrid Gated DeltaNet / Gated Attention layout;
- padded vocabulary and language-model output dimension 248320.

The official GPTQ artifact is an INT4 Safetensors checkpoint intended primarily
for inference. Its recommended vLLM/SGLang path uses `moe_wna16` quantized serving
kernels. A successful load or generation is not evidence that exact input
Jacobians are available.

The official bitsandbytes documentation states that 8-bit and 4-bit training is
supported only for extra parameters. QLoRA demonstrates useful gradient flow
through quantized frozen weights, but it does not prove that every Qwen3.5 hybrid
attention and MoE kernel exposes the exact residual-input VJPs required by
Jacobian Lens. Therefore the exact one-sequence VJP smoke in Q35Q is mandatory
and may not be skipped by analogy to LoRA training.

## What may begin immediately

While M38E continues, authorize only CPU-side and storage-side Q35Q work:

1. pin exact immutable model revisions;
2. download/stage official artifacts without changing the M38E cache or host;
3. build artifact-admission, architecture, quantization, device-placement,
   provenance, privacy, and commit-safety checks;
4. implement synthetic tests and aggregate artifact schemas;
5. stage a Transformers/eager GPTQ path and a runtime-NF4 fallback path;
6. build explicit training-compatible multi-GPU placement rather than relying on
   inference-only `device_map="auto"` behavior;
7. commit the aggregate-only admission amendment before any backward call.

No Q35Q GPU process may run on the active M38E resources. GPU execution is
permitted only after M38E releases the dual-3090 window or on a proven independent
host.

## Mandatory candidate order and exact-gradient boundary

Q35Q must test candidates in this order:

1. official `Qwen/Qwen3.5-35B-A3B-GPTQ-Int4` through a genuine
   Transformers/PyTorch autograd path;
2. the exact admitted BF16 base checkpoint loaded at runtime with bitsandbytes
   NF4 under an explicit training-compatible shard plan.

For the passing path:

- all weights remain frozen;
- weight gradients remain absent;
- the residual-to-target VJP must be non-`None`, nonzero, finite, repeatable, and
  connected through genuine autograd;
- straight-through estimators, detached dequantize/requantize approximations,
  finite differences, fake gradients, or manually substituted derivatives may
  not be called an exact Jacobian;
- no hidden CPU or disk offload may occur in the primary passing fit path;
- observation hooks must preserve token outputs and the frozen logit-parity
  tolerance;
- peak memory must remain at or below 23.0 GiB per RTX 3090 and 46.0 GiB total;
- exact model, quantization, package, kernel, source, layer, and placement
  identities must match the committed admission amendment.

If GPTQ lacks exact backward support, record
`q35q_gptq_autograd_unsupported` and proceed to NF4. Do not patch an approximate
gradient into the GPTQ path and call it exact. If NF4 also fails, record
`q35q_local_exact_vjp_blocked`. That blocks the local quantized path only; it does
not reject a later BF16 fit on rented high-memory hardware.

## Scientific claim boundary for quantized lenses

A lens fitted under GPTQ, NF4, AWQ, FP8, or another quantization is a lens for
that exact quantized mathematical model. Quantization changes weights, routing
margins, expert writes, and local derivatives.

Therefore:

- do not describe a quantized Qwen3.5 lens as a BF16 lens;
- do not describe a transferred Qwen3.5 lens as an Agents-A1-native lens;
- do not pool rows, calibration, power, or validation across quantizations;
- use each target checkpoint's own final normalization and output head;
- compare transfer against target-native identity transport and standard logit
  lens at identical tokens and layers;
- keep raw Jacobians, VJPs, states, routes, lens matrices, prompts, outputs, and
  per-example readouts private and uncommitted.

A successful native quantized Agents-A1 fit may establish a Jacobian Lens for the
exact quantized Agents-A1 checkpoint. Native BF16 Agents-A1 fitting remains the
reference target.

## Program order

The binding execution order is:

1. finish M38E unchanged and complete every frozen finalization audit;
2. stage Q35Q Phase 0 while M38E runs, without GPU contention or scientific
   capture;
3. after M38E releases the dual-3090 window, run only the Q35Q one-sequence VJP
   gate and, if it passes, the frozen eight-sequence micro-fit;
4. commit and review aggregate technical outcomes before any larger fit;
5. if the micro-fit passes, preregister the selected-layer quantized
   Qwen3.5-35B-A3B-Base lens fit before capture;
6. use the validated base-model lens for separately preregistered transfer tests
   onto post-trained Qwen3.5 derivatives and Agents-A1;
7. fit a native quantized Agents-A1 lens only after exact target artifact and
   quantization admission and a separate pre-outcome manifest;
8. independently launch M39 only through its existing fresh-population,
   leakage, nuisance, power, parity, provenance, and privacy gates;
9. do not evaluate Q35Q correctness prediction, stopping, or intervention value
   until M39's confirmatory program permits an independent outcome-bearing study;
10. use an unrelated open MoE only for a specific expert/dispatch operation that
    remains technically impossible on the admitted Qwen3.5 quantized paths;
11. retain native BF16 Agents-A1 exact VJPs and fitting on rented high-memory
    hardware as the final reference comparison under a separate frozen protocol.

Q35Q engineering feasibility may run before M39 because it uses a neutral corpus
and no correctness labels. It does not replace M39 and cannot borrow M38E/M39
rows, outcomes, families, difficulty observations, feature discoveries, layers,
or thresholds.

## Binding M39 metacognition and temporal-state amendment

Commit `ced86a9e3b0a23eced18aa82490936541b341dd8` added
`docs/STEER_ADDENDUM_2026-07-15_M39_METACOGNITION_TEMPORAL_AND_EARLY_EXIT_BOUNDARY.md`.
That addendum is now binding and amends the M39 design before capture.

In particular:

- M39 must preserve a strict separation between monitoring and control;
- the launch amendment must include an isolated pre-solve/post-solve behavioral
  metacognition comparator or record it unsupported through a pre-capture gate;
- internal telemetry must be tested against nuisance, router, and behavioral
  self-assessment comparators under a frozen hierarchical multiplicity rule;
- nuisance residualization or an equivalent conditional comparison must be fit
  inside training folds only;
- one separately identifiable aggregate temporal hidden-state dynamics block may
  be admitted only after parity, privacy, phase-attribution, and resource smokes;
- counterfactual routing, router updates, retries, tool invocation, truncation,
  and early exit remain outside M39;
- do not prioritize a TIDE-style early-exit integration for Agents-A1 before
  observation-only monitoring and model-specific intrinsic-exit feasibility are
  established;
- every borrowed external method must pin the exact paper version, immutable code
  commit, formula, deviations, license, dependencies, and synthetic tests.

This amendment strengthens comparators and confound controls. It does not
establish an Agents-A1 predictor, metacognitive controller, causal router result,
or safe early exit.

## Binding Q35Q route-regime and exact-sharding amendment

Commit `e609fa547b4505a64e3adc38131f3ce6faff3daf` added
`docs/STEER_ADDENDUM_2026-07-15_Q35Q_ROUTE_REGIME_AND_EXACT_SHARDING.md`.
That addendum is now binding before any Q35Q live backward call.

In particular:

- an exact sparse-MoE VJP is claimed only as the local autograd derivative through
  the executed top-k route regime, not across counterfactual expert assignments;
- the Phase-1-passing path must produce an aggregate-only route-regime artifact
  covering route parity, selected-boundary margins, load/transition summaries,
  hook parity, resource use, cleanup, provenance, and privacy before micro-fitting;
- cross-checkpoint transfer must report aggregate route overlap, route-change
  frequency, and source/target margin distributions; architecture compatibility
  alone is not sufficient for a route-conditioned portability claim;
- Phase 1 must produce an exact backward-cost, wall-time, and storage projection
  before Phase 2 or Phase 3 begins;
- Phase 3 and a later native Agents-A1 fit may use only preregistered horizontal
  prompt sharding across identically admitted workers with deterministic fp32
  weighted merging and cross-worker agreement smokes;
- sharding may change wall-clock parallelism only. It may not reduce the frozen
  corpus, omit dimensions, replace exact VJPs with sketches, adapt shards after
  outcomes, pool quantizations, or weaken any existing gate;
- counterfactual routing, straight-through route estimators, route updates, and
  production use remain prohibited.

This amendment creates a scalable exact-fitting path and a stricter MoE claim
boundary. It does not establish a passing VJP, route mechanism, fitted lens,
Agents-A1 transfer, correctness predictor, stopping policy, or production utility.

## Required stop outcomes

Use only the scoped outcomes defined by the Q35Q protocol, including:

- `q35q_gptq_exact_vjp_passed`;
- `q35q_gptq_autograd_unsupported`;
- `q35q_nf4_exact_vjp_passed`;
- `q35q_local_exact_vjp_blocked`;
- `q35q_microfit_passed` / `q35q_microfit_blocked`;
- `q35q_quantized_base_lens_validated`;
- `q35q_transfer_feasible` / `q35q_transfer_not_established`;
- `q35q_native_quantized_agents_lens_validated`;
- `q35q_artifact_admission_blocked`;
- `q35q_provenance_blocked`.

None authorizes production use.

## Privacy, production, and completion boundary

Stop on model or revision mismatch, dirty source provenance, unsupported
backward, detached/zero/nonfinite gradients, approximate gradients represented as
exact, parity failure, hidden offload, model substitution, quantization mismatch,
device-placement mismatch, kernel mismatch, OOM, resource breach, instability,
checkpoint corruption, cleanup failure, privacy failure, or commit-safety
failure.

Treat the repository as publicly visible. Never commit raw tasks, corpus text,
prompts, outputs, token IDs or text, hidden states, activations, expert outputs,
routes, Jacobians, VJPs, lens matrices, per-example scores, model weights, caches,
local paths, environment values, process evidence, or secret-linked provenance.

Production remains gated. The research program is not complete. Do not mark it
complete until every frozen milestone and final stop rule in
`CODEX_AUTOSTEER.md` is satisfied.
