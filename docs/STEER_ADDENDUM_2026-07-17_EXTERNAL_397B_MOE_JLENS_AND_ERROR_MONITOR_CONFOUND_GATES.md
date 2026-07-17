# Steer addendum — external 397B MoE Jacobian-lens precedent and correctness-monitor confound gates

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

A separate open campaign in `solarkyle/jspace` reports that workspace-derived
signals can improve some family-specific hallucination detectors but do not support
a universal correctness gate. Its reported negative controls include sign reversal
or failure on some veracity families, answer-readout confounding, weak signal for
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

It does **not** establish:

- exact GPTQ, AWQ, NF4, or other quantized autograd;
- equality between a quantized Jacobian and a BF16 Jacobian;
- feasibility on two 24 GiB GPUs or the present host;
- correctness prediction, completed-error detection, safe early exit, or repair;
- transfer from Qwen3.5-397B-A17B to Agents-A1;
- privacy or production suitability;
- causal expert localization; or
- validity of the reported ignition or steering effects in this program.

The reported workspace-band statistic is geometry evidence, not a correctness
monitor. The model card itself reports family confounding and a small fitting
sample relative to larger published lens collections. No threshold, source layer,
direction, performance number, or intervention from the public artifact may be
imported into an Agents-A1 claim.

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

The external BF16 precedent may not be used to skip exact quantized parity. It does
reduce the value of spending Q35Q effort merely to prove that a large MoE lens can
exist in BF16. Q35Q's unique purpose is now sharper: determine whether an admitted,
locally feasible quantized path preserves the derivatives needed for a credible
Agents-A1 scaling route.

## External-replication lane

A separate launch amendment is required before downloading or executing the public
397B lens or base-model tensor payloads. That amendment must freeze:

- the public lens repository revision and every artifact identity;
- the base-model revision and exact lm-head shard identity;
- the public GitHub source commit and dependency lock;
- a CPU-only consumer-check implementation and expected aggregate outputs;
- storage, network, cleanup, and resource limits;
- a prohibition on private prompt, output, token, activation, route, or label use;
- a statement that reproducing a band statistic does not validate behavioral claims;
- stop conditions and a public-safe aggregate record.

Before such a launch, metadata and source inspection only are permitted. No public
behavioral steering trial is authorized by this addendum.

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
3. independently audit the public 397B BF16 artifact through a separate bounded
   amendment, using it only as an external large-MoE comparator;
4. run an independent forward-only correctness-monitor benchmark with the confound
   gates above;
5. require stable incremental prediction beyond nuisance, confidence, hidden-state,
   and router/path comparators;
6. only then design an Agents-A1-native derivative or telemetry capture;
7. keep every intervention and production gate separate.

If quantized derivative parity fails, the program must report that result and choose
between a separately resourced BF16/FP8 path, a smaller admitted dense engineering
model, or stopping the Jacobian branch. It may not substitute the external 397B
claim for local parity evidence.

## Status and claims

M38E remains closed at terminal `inconclusive`. Q35Q remains
`q35q_artifact_admission_blocked`. M39 remains design-only and capture-prohibited.
The research program is not finished.

No completed-error predictor, universal hidden-state correctness signal, semantic
workspace correctness monitor, safe early-exit rule, truncation policy, causal
expert localization, routing intervention, correction policy, activation steering,
Agents-A1 transfer, or production utility is established.
