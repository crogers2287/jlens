# steer.md — post-M32R-Phase-0 resource gate

M1 through M31 are complete. M32 (structured repair) was superseded before
execution and is preserved as a never-executed historical artifact. M32R
(Agents-A1 counterfactual expert routing) stopped at its Phase-0 feasibility
gate under the protocol's Branch 4 before any preregistration, generation, or
capture.

`CODEX_AUTOSTEER.md` remains the operating contract. The M32R protocol
remains `docs/M32R_AGENTS_A1_COUNTERFACTUAL_ROUTING_AUTOLOOP.md`.

## Why M32R stopped (Branch 4 — resource/loader failure)

Measured with a config-only meta-device audit; no weights were downloaded:

- `InternScience/Agents-A1` is `qwen3_5_moe` with 40 text layers, 256 experts,
  top-8 — 34.66B parameters, of which 32.21B (93%) sit in fused 3D expert
  tensors (`mlp.experts.gate_up_proj/down_proj`).
- bitsandbytes quantizes `nn.Linear` only, so the preferred NF4 research load
  leaves the experts in BF16: ~61.9 GiB estimated versus the hard 44 GiB
  dual-3090 ceiling. Plain BF16 is ~64.6 GiB. Both fail the gate. This
  reproduces the repository's earlier Qwen3.6-35B-A3B NF4 audit exactly.
- `InternScience/Agents-A1-FP8` uses compressed-tensors, which is not in the
  approved stack (adding it is a new-dependency gate), and RTX 3090/Ampere
  (sm86) has no FP8 kernel path, so the installed loader cannot run it within
  the ceiling without decompressing toward BF16.
- BF16 with bounded CPU offload loads this geometry but ran at ~5.3 minutes
  per prompt on this hardware in earlier milestones — infeasible for a
  branched counterfactual screen and excluded from causal timing by the
  protocol anyway.

Public record: `reports/telemetry/hf_m32r_feasibility_gate.json`.
No model substitution was made; no decision data exist; nothing was captured.

## Required operator decision before resuming

Choose exactly one:

### A. FP8 preflight attempt

Approve installing `compressed-tensors` into the research venv and a bounded
preflight: load `InternScience/Agents-A1-FP8`, measure real memory and
router-hook availability, and stop again with data if Ampere forces
decompression past the gate. Honest prognosis: low odds, small cost
(~37 GiB download to Thor, one dependency).

### B. Offload-scoped M32R

Explicitly amend the protocol to allow BF16 + bounded CPU offload as the
research mode, with branch budgets cut to what ~5 min/prompt permits (a
screen over a handful of failures, not 192 tasks). Changes the preregistered
scope materially; slow but runs today.

### C. Proxy-model routing methodology (fastest to causal evidence)

Approve the already-local `Qwen1.5-MoE-A2.7B-Chat` (24 layers × 60 experts,
top-4) as an explicit research proxy: build the route-override hook, fake-MoE
tests, and the full M32R causal-screen methodology on the proxy, with every
claim scoped to the proxy model. Agents-A1 conclusions would wait for
hardware or checkpoint availability, but the machinery and the
route-recoverability question get real answers now.

### D. Wait for a viable Agents-A1 checkpoint

Park expert-routing work until an official pre-quantized (GPTQ/AWQ-class or
unfused) Agents-A1 checkpoint exists or hardware changes; return to the
superseded structured-repair/tool-routing track in the meantime.

Do not resume M32R until the operator selects A–D. Any download or new
dependency stays gated on that choice.

## Standing evidence (unchanged)

- M30: telemetry error-detection increment over difficulty metadata
  ESTABLISHED (+.099 [+.042,+.156], n=192 once-read holdout).
- M31: frozen trigger ~89% precision on fresh tasks; naive resample repair
  rescues only ~4.5% — repair operator, not detection, is the open problem.
- Full suite green at 151 tests; candidate-only and production gates active;
  agents-a1 GGUF serving unaffected throughout.

## Repository hygiene

Do not commit model weights, caches, local model paths, prompts, outputs,
operands, per-task routes, token ids/text, raw router tensors, or detailed
records. Public artifacts remain aggregate-only. No candidate becomes gold
and production remains gated until explicit audited unlock criteria are
defined.
