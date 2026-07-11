# M36V Phase 1 — dispatch-validated router telemetry (result: full_telemetry)

Steer: 0be9d84. Checkpoint: `cyankiwi/Agents-A1-AWQ-INT4` @
`3e522d4e46438c782789b73c8ff4503e0edd037c`, isolated vLLM 0.24.0
(compressed-tensors, WNA16 Marlin MoE, TP=2, enforce-eager, max_model_len
1024). Gate artifact: `reports/telemetry/m36v_phase1_router_telemetry.json`.

## Mechanism (no vLLM source patch)

- **Expert ids** ride vLLM's native `enable_return_routed_experts` path:
  `RequestOutput.routed_experts` gives per-token, per-layer top-8 ids,
  captured by vLLM inside `BaseRouter._select_experts` — the exact
  boundary between router score production and fused dispatch.
- **Weights, entropy/mass scalars, raw validation sample** come from a
  registered `worker_extension_cls` override
  (`jlens_vllm_telemetry.worker_ext.JlensWorkerExtension`): at install it
  wraps each MoE layer's `router.select_experts` (records returned top-8
  ids, dispatch weights, full-softmax entropy and top-8 mass computed
  device-side, plus full router logits for the first 64 rows) and
  `routed_experts.forward_modular` (records what fused dispatch actually
  receives). Wrappers only read; uninstall restores class methods.
- Data plane: workers write per-prompt npz files under
  `reports/shadow/private/`; collective_rpc carries scalar counters only.
- Override hash is recorded in the artifact; vLLM tree verified unpatched.

## Gate results (all passed)

| Gate | Evidence |
|---|---|
| stock_parity | within baseline envelope (see below) |
| observation_parity | enabled-vs-disabled diverged on 3/8 prompts vs baseline 5/8, same earliest onset (token 13) |
| architecture_identity | qwen3_5_moe, 40 routed layers, 256 experts, top-8, pinned revision |
| dispatch_identity | 0 id mismatches over 2,609 rows x 40 layers; native path, both TP ranks, early/middle/late layers exact |
| weight_identity | router-return vs dispatch-entry maxdiff 0.0; normdev 2.4e-7; finite, nonnegative |
| feature_availability | schema features derived for 2,389 decode rows without hidden states; raw-recompute deviations ~1e-6 |
| bounded_overhead | 1.33x generation time enabled vs disabled; 40.47 GiB combined peak (< 44) |
| privacy | aggregate-only public artifact (guard-enforced); per-token data private |

## Material finding: baseline runtime nondeterminism

Two identical greedy passes in the same **unpatched stock engine**
diverge on 5/8 smoke prompts (first divergence at token 13, mean 122.8).
`VLLM_BATCH_INVARIANT=1` rejects this deployment config
("No WNA16 MoE backend supports the deployment configuration"), so
deterministic kernels are unavailable without changing quantization —
which the steer forbids. Token-identity parity is therefore unmeasurable
for any configuration of this runtime, including stock.

Parity gates consequently use a frozen envelope (declared in the
artifact): a leg passes when it diverges on no more than baseline+2
prompts and no earlier than the floor (token 8). The observation-only
property rests on the exact dispatch/weight identity, the read-only
wrapper audit, and divergence indistinguishable from baseline.

**Consequence for M36:** paired decision capture must treat a single
deterministic AWQ original per task as *one draw* from a nondeterministic
runtime, captured once and frozen — reruns will not reproduce token
sequences bit-for-bit. Verifier-level outcomes, not token identity, are
the unit of comparison.

## Tie behavior at the k-boundary

142 of 512 raw-validation row-layers picked a different 8th expert than a
numpy recompute — every one with tie-equivalent mass gap 0.0 (the
captured set carries identical probability mass). The binding
summary-vs-raw criterion is mass equivalence; exact-set mismatch is
recorded informationally.

## Feature schema coverage

Per decode token and routed layer, derivable with no hidden-state and no
raw-tensor capture at benchmark scale: top-8 expert ids, dispatch weights
(= schema `topk_probs`; the router renormalizes), full-softmax entropy,
pre-renormalization top-8 mass, and the schema-v3 weighted usage/drift
signatures. `entropy_final_logits` / `selected_token_prob` come from vLLM
logprobs as before.
