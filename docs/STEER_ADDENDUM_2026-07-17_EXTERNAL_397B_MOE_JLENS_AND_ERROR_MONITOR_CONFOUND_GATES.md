# Steer addendum — external large-MoE Jacobian-lens precedents and correctness-monitor confound gates

Date: 2026-07-17

This addendum is binding program control. It incorporates every existing sealed-data,
privacy, provenance, verifier, exact-set, resource, retry, production-gating, and
claim-boundary rule. It does not alter an M38E task or result, relax any Q35Q
Phase-0 prerequisite, authorize Q35Q weight staging, release the dual-3090 resource
window, authorize M39 capture, or permit an Agents-A1 intervention.

## New public evidence

A public Hugging Face artifact, `praxagent-org/jacobian-lens-qwen3.5-397b-a17b`,
reports a fitted Anthropic-format Jacobian lens for
`Qwen/Qwen3.5-397B-A17B`, a 397B-total / 17B-active MoE. The model card reports:

- a BF16 fit over 59 source layers on 8 H200 GPUs;
- 24 WikiText prompts, sequence length 128, and eager attention;
- an exact text-backbone layout under `model.language_model`;
- public FP32 and FP16 lens artifacts, checksums, fit receipts, and evaluation files;
- a CPU consumer-path reproduction of the reported band statistic; and
- separate ignition and behavioral-intervention claims.

The base model's official card independently identifies it as a 397B-total,
17B-active, 60-layer Qwen3.5 MoE with Gated DeltaNet, routed experts, a shared
expert, vision, and MTP components.

A second public Hugging Face artifact,
`stanleytheli/qwen3.6-35B-A3B-jlens`, at immutable repository revision
`7a5dc7a6c770c272226a321409b30d7e6d773bba`, reports a fitted
Anthropic-format Jacobian lens for `Qwen/Qwen3.6-35B-A3B`. This is a materially
closer architecture and scale comparator for the Agents-A1-35B path than the
397B artifact. Its model card reports:

- source layers 0 through 38 with target layer 39 on the 40-layer,
  `d_model=2048` text decoder;
- one 1000-prompt WikiText-103 fit and one 100-prompt fit, with the author claiming
  agreement within noise;
- two approximately 327 MB FP16 PyTorch-pickle lens files;
- fitting on 8 H200 GPUs with `dim_batch=16`, approximately 101 GiB peak memory per
  GPU, and approximately 55 to 80 seconds per prompt;
- a pure-PyTorch autograd path claimed to propagate through the 256-expert sparse
  MoE dispatch and hybrid gated-linear-attention blocks; and
- final-output-token rank comparisons against the classic logit lens plus a small
  two-hop factual-readout demonstration.

The 35B model card does not freeze the exact base-model revision, Transformers
revision, Jacobian-lens source revision, dependency lock, corpus example identities,
per-shard fit receipts, merge receipts, or artifact digests. Its published files are
pickle-bearing artifacts. These omissions and the unsafe serialization format are
admission blockers, not clerical details.

A separate open campaign in `solarkyle/jspace` reports that workspace-derived
signals can improve some family-specific hallucination detectors but do not support
a universal correctness gate. At immutable public commit
`50fc677f0a107b5dae84dbac6d30eb4dcee8ff2d`, the campaign corrected its earlier
operation-level sign-inversion interpretation: its prospective universal-transfer
gate missed, and several apparent favorable or inverted veracity slices were
entangled with answer-identity or fixed-truth confounding. The bounded evidence is
task-conditional reliability and transfer failure, not a clean cross-operation sign
reversal. The campaign still reports answer-readout confounding, weak signal for
some tool-call argument errors, and materially different results across model and
task families.

These are external public claims. They have not been independently reproduced in
this repository. Paper, model-card, repository, and author-supplied results remain
lead evidence until their immutable artifacts, code, receipts, and evaluation
procedures are independently audited.

## Binding interpretation

The public 397B artifact changes one narrow feasibility classification:

> Fitting and publishing a BF16 Jacobian lens on a Qwen3.5-family MoE at roughly
> 0.4T total parameters is no longer purely hypothetical; it has a concrete public
> implementation and artifact claim.

The public 35B artifact changes a second, narrower feasibility classification:

> Fitting an Anthropic-format BF16 Jacobian lens through the same broad
> Qwen3.6-35B-A3B sparse/hybrid backbone used as the nearest public base-family
> comparator for Agents-A1 is no longer purely hypothetical.

This does **not** establish:

- exact GPTQ, AWQ, NF4, or other quantized autograd;
- equality between a quantized Jacobian and a BF16 Jacobian;
- equality between the public Qwen3.6 base-model Jacobian and an Agents-A1
  checkpoint Jacobian after agentic post-training;
- feasibility on two 24 GiB GPUs or the present host;
- correctness prediction, completed-error detection, safe early exit, or repair;
- transfer from either public base model to Agents-A1;
- multimodal, long-context, tool-trajectory, or production-path validity;
- privacy or production suitability;
- causal expert localization; or
- validity of the reported ignition, latent-hop, or steering effects in this program.

The reported workspace-band, final-token-rank, and latent-hop statistics are geometry
or readout evidence, not correctness monitors. No threshold, source layer, direction,
performance number, prompt-count claim, or intervention from either public artifact
may be imported into an Agents-A1 claim.

A lens fitted to the public Qwen3.6 base checkpoint may not be treated as an admitted
Agents-A1 lens. Post-training can change residual bases, routing, attention dynamics,
normalization, calibration, and the input-output Jacobian. Any proposed reuse must be
a prospectively frozen transfer experiment with separate checkpoint admission and
without sealed-label retuning. A failed transfer requires a checkpoint-specific fit
or termination of that branch; it may not be repaired after viewing sealed outcomes.

## Q35Q order remains unchanged

Q35Q remains `q35q_artifact_admission_blocked`. The active order remains:

1. wire strict immutable weight-index admission into the committed production CLI;
2. commit and pass the real source-to-artifact reconciliation composition;
3. establish exact load-manifest semantics, including every quantization auxiliary
   tensor, shape, dtype, multiplicity, ordering, fusion rule, and numbered-to-packed
   loader transformation;
4. bind the full config, Transformers package, source file, class, loader, kernel,
   and runtime identities;
5. run one adversarial aggregate Phase-0 conjunction;
6. stage weights only after that conjunction passes;
7. obtain an independently authorized resource transition; and
8. test exact quantized forward and VJP/JVP parity before fitting any quantized
   Jacobian lens.

The external BF16 precedents may not be used to skip exact quantized parity. They do
reduce the value of spending Q35Q effort merely to prove that a large MoE lens can
exist in BF16. Q35Q's unique purpose is now sharper: determine whether an admitted,
locally feasible quantized path preserves the derivatives needed for a credible
Agents-A1 scaling route.

## External-replication lane

A separate launch amendment is required before downloading or executing either
public lens or either base-model tensor payload. That amendment must freeze:

- the public lens repository revision and every artifact identity;
- the base-model revision and exact lm-head shard identity;
- the public GitHub or Hugging Face source revision and dependency lock;
- corpus identity, source-position policy, estimator, shard boundaries, merge rule,
  and expected fit receipts;
- a CPU-only consumer-check implementation and expected aggregate outputs;
- storage, network, cleanup, and resource limits;
- a prohibition on private prompt, output, token, activation, route, or label use;
- a statement that reproducing a rank or band statistic does not validate behavioral
  or correctness claims;
- stop conditions and a public-safe aggregate record; and
- serialization safety.

The two Qwen3.6 lens files are PyTorch pickles. They may not be loaded directly in an
ordinary research or production process. Before deserialization, the lane must either
convert them through a separately admitted, network-isolated, credential-free,
read-only sandbox into a non-executable tensor format with independently verified
schema and digests, or reject the artifacts. A file being hosted on Hugging Face does
not satisfy this gate.

Before such a launch, metadata and source inspection only are permitted. No public
behavioral steering trial is authorized by this addendum.

## Prompt-count convergence gate

The public 35B card's claim that a 100-prompt fit matches a 1000-prompt fit within
noise is useful only as a lead for a resource-saving pilot. It is not an imported
sample-size result.

Any checkpoint-specific Agents-A1 lens proposal must first preregister a training-only
prompt-count convergence study using independently fitted shards at multiple frozen
corpus sizes. Stability must be evaluated on public or training-only readout metrics,
artifact-to-artifact distance, and held-out public prompts. Sealed correctness labels,
private trajectories, verifier outcomes, and production telemetry may not select the
fit size. The smallest stable fit may advance only if it also passes all derivative,
provenance, privacy, and artifact-admission gates.

## M39 and Agents-A1 correctness-monitor gates

Any future M39 or Agents-A1 monitor protocol must treat correctness prediction as
family-conditional unless a sealed cross-family result establishes otherwise. It
must include all of the following before capture:

1. **Answer-readout control.** Compare every workspace or hidden-state feature set
   with transparent answer-identity, answer-format, response-length, finish-reason,
   confidence, and metadata baselines.
2. **Varying-truth construction.** Correct labels and target answers must vary
   within every primary family and split. Fixed-answer or fixed-truth slices may
   not support a correctness claim.
3. **Family-disjoint evaluation.** Hyperparameters, layers, directions, calibration,
   and thresholds are selected without access to the held-out family or task group.
4. **Sign-stability reporting.** Report per-family effect direction and confidence
   intervals. Pooled improvement may not conceal a family-level sign reversal.
5. **Tool-error separation.** Tool-call argument errors, verifier failures,
   completed reasoning errors, truncations, and malformed outputs are distinct
   populations. A signal in one does not license a claim in another.
6. **No universal-gate claim by default.** Universal correctness awareness requires
   positive sealed transfer across independently weighted families and model/task
   domains; average in-domain gain is insufficient.
7. **Detection before control.** Retry, abort, early exit, forced routing,
   activation steering, and correction remain prohibited until a separately powered
   intervention protocol demonstrates benefit without right-to-wrong regressions.
8. **Nuisance residualization.** Prompt length, response length, answer token,
   family, difficulty, tool count, latency, and finish reason must be controlled
   using development-only procedures.
9. **Comparator parity.** Prompt-final hidden state, trajectory delta, router/path
   summaries, confidence, metadata, and Jacobian-space features must use the same
   examples, outer splits, calibration budget, and selection budget.
10. **Privacy boundary.** Only predeclared aggregate telemetry may be committed.
    Raw prompts, outputs, labels, tokens, hidden states, routes, expert identities,
    Jacobians, per-example predictions, and secret-linked digests remain private.

## Technically credible scaling sequence

The current credible sequence is:

1. finish Q35Q Phase-0 honestly;
2. establish exact quantized derivative parity on the admitted Qwen3.5 MoE path;
3. audit the public Qwen3.6-35B-A3B lens metadata, serialization, source path, and
   claimed fit receipts through a separate bounded amendment, treating it as the
   nearest public same-backbone feasibility comparator rather than an Agents-A1 lens;
4. independently audit the public 397B BF16 artifact through a separate bounded
   amendment only if its additional scale comparison remains decision-relevant;
5. run an independent forward-only correctness-monitor benchmark with the confound
   gates above;
6. require stable incremental prediction beyond nuisance, confidence, hidden-state,
   router/path, external-check, and trajectory comparators;
7. preregister a public/training-only prompt-count convergence pilot before any
   checkpoint-specific Agents-A1 lens fit;
8. only then design an Agents-A1-native derivative or telemetry capture; and
9. keep every intervention and production gate separate.

If quantized derivative parity fails, the program must report that result and choose
between a separately resourced BF16/FP8 path, a smaller admitted dense engineering
model, or stopping the Jacobian branch. It may not substitute either external claim
for local parity evidence.

## Status and claims

M38E remains closed at terminal `inconclusive`. Q35Q remains
`q35q_artifact_admission_blocked`. M39 remains design-only and capture-prohibited.
The research program is not finished.

No completed-error predictor, universal hidden-state correctness signal, semantic
workspace correctness monitor, safe early-exit rule, truncation policy, causal
expert localization, routing intervention, correction policy, activation steering,
Agents-A1 transfer, or production utility is established.
