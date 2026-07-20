# Steer addendum — external Jacobian-lens precedents, official global-workspace primary source, and correctness-monitor confound gates

Date: 2026-07-17
Updated: 2026-07-20 — official Anthropic paper and reference implementation bound

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

The primary source for the Jacobian lens is now public: Gurnee et al.,
“Verbalizable Representations Form a Global Workspace in Language Models,” arXiv
`2607.15495v1`, submitted 2026-07-16. The companion implementation is
`anthropics/jacobian-lens` at immutable commit
`581d398613e5602a5af361e1c34d3a92ea82ba8e`.

The paper reports extensive mechanistic experiments primarily on proprietary Claude
Sonnet 4.5, with selected corroboration on Haiku 4.5, Opus 4.5, and Opus 4.6. The
exact production-model architecture, checkpoint bytes, training data, runtime, and
full fitted-lens artifacts are not publicly reproducible. The public repository is a
one-commit, explicitly unmaintained reference implementation for open-weight
Hugging Face decoder models; it does not reproduce the proprietary-model results by
itself.

The official method computes, for each source layer, an average linear transport into
a target residual basis. The released estimator:

- runs one forward pass and `ceil(d_model / dim_batch)` backward passes per prompt;
- injects one-hot cotangents for output dimensions at every valid current-and-future
  target position simultaneously;
- averages source-position gradients after excluding the first sixteen positions and
  the final no-target position;
- accumulates one full `d_model x d_model` matrix per fitted source layer in FP32;
- fits by default against the final residual layer, while allowing a different frozen
  target layer; and
- merges independently fitted prompt shards by an `n_prompts`-weighted mean.

The reference README states that the paper's lenses use 1000 sequences of 128 tokens
from a pretraining-like corpus and that roughly 100 prompts can be usable. That is a
method-author claim and a resource-planning lead, not an imported convergence result.

The paper's key scientific evidence is broader than next-token prediction. It reports
that J-lens directions can expose known latent intermediates and produce stronger
causal ablation or concept-swap effects than logit- and tuned-lens directions on its
selected tasks. It also reports that the ordinary logit lens captures much of the
same workspace-like structure, especially in later layers, while the tuned lens is
best at matching the final output distribution but can skip over latent
intermediates.

The paper also contains alignment-audit and automated-audit demonstrations. Those
must be interpreted narrowly:

- the evaluation-awareness proof-of-concept score uses two preselected target words
  minus one hundred preselected control words and averages over a chosen workspace
  layer band;
- its automated auditing benchmark contains six transcripts and eighteen claims,
  with claim ground truth inherited from a prior NLA analysis and final quality
  scored by an LLM judge;
- the investigator receives a completed transcript and queries readouts at selected
  positions, so the demonstration is retrospective auditing rather than prospective
  failure prediction or online stopping; and
- the paper's single-token J-lens degrades on multi-token concepts. Its template-lens
  extension depends on a predefined roughly 12,700-word dictionary and
  model-generated continuation templates, while its oracle extension adds learned
  reconstruction and proposal models.

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

The official paper and reference implementation change a third classification:

> The estimator, reference code, methodological comparisons, and core functional
> workspace claims are now available as a primary public source. The program no
> longer needs to infer the canonical method from secondary implementations.

This does **not** establish:

- exact GPTQ, AWQ, NF4, or other quantized autograd;
- equality between a quantized Jacobian and a BF16 Jacobian;
- equality between the public Qwen3.6 base-model Jacobian and an Agents-A1
  checkpoint Jacobian after agentic post-training;
- feasibility on two 24 GiB GPUs or the present host;
- correctness prediction, completed-error detection, safe early exit, or repair;
- transfer from either public base model or any proprietary Claude result to
  Agents-A1;
- multimodal, long-context, tool-trajectory, or production-path validity;
- privacy or production suitability;
- causal expert localization;
- target-blind semantic monitoring;
- prospective online auditing from the paper's retrospective audit examples;
- validity of the reported ignition, latent-hop, ablation, swap, or steering effects
  in this program; or
- any claim about phenomenal consciousness.

The reported workspace-band, final-token-rank, latent-hop, global-workspace,
alignment-audit, and automated-audit statistics are geometry, readout, mechanism, or
retrospective-audit evidence. They are not correctness monitors. No threshold,
source layer, direction, target word, control-word list, performance number,
prompt-count claim, or intervention from any public artifact may be imported into
an Agents-A1 claim.

A lens fitted to the public Qwen3.6 base checkpoint may not be treated as an admitted
Agents-A1 lens. Post-training can change residual bases, routing, attention dynamics,
normalization, calibration, and the input-output Jacobian. Any proposed reuse must be
a prospectively frozen transfer experiment with separate checkpoint admission and
without sealed-label retuning. A failed transfer requires a checkpoint-specific fit
or termination of that branch; it may not be repaired after viewing sealed outcomes.

## Canonical-estimator and implementation gate

Any future jLens fit or replication must bind the exact estimator rather than merely
claiming “Anthropic-format” compatibility. Freeze at least:

- official source commit and dependency lock;
- model, tokenizer/processor, checkpoint, precision, attention implementation, and
  distributed runtime identities;
- source and target layers;
- source-position policy and `skip_first` value;
- target-position policy, including whether current and future positions are summed;
- prompt corpus, sequence lengths, truncation, sharding, ordering, and exclusions;
- `dim_batch`, gradient precision, accumulation precision, checkpoint cadence, and
  merge weighting;
- normalization, unembedding, sparse decomposition, ranking, and calibration rules;
- stop-gradient choices and any Q/K, attention, router, or cache modifications; and
- exact lens tensor schema, dtype, layer keys, digests, and serialization path.

A change to any item is a different estimator or runtime condition and requires
separate reporting. Agreement on a few visual examples is not estimator parity.

The reference implementation's generic residual hooks do not prove compatibility
with a quantized, multimodal, sharded, expert-parallel, offloaded, fused, or
production-serving model. Forward, activation-VJP, activation-JVP, finite-difference,
route, cache, and tensor-consumption parity remain model/runtime-specific gates.

## Logit-lens and method-comparison gate

Because the primary paper reports that the ordinary logit lens captures much of the
workspace-like structure, every future workspace or correctness study must include a
same-boundary logit-lens baseline unless technically impossible. It must also include
final logits/confidence and passive hidden-state baselines.

Any claim that the Jacobian lens is operationally necessary must demonstrate sealed
incremental value over:

- final logits, entropy, margins, and calibrated confidence;
- the ordinary logit lens at identical layers and positions;
- prompt-final and decision-boundary hidden-state probes;
- the tuned lens or another output-predictive linear map when available;
- target-word and control-word readouts using development-only selection; and
- the previously admitted metadata, trajectory, external-check, router, sparse-feature,
  and transcoder comparators.

Superior recovery of a curated latent intermediate or larger causal swap effect does
not establish superior error prediction. Next-token KL, latent-intermediate recovery,
causal intervention, audit quality, and correctness monitoring are distinct endpoints.

## Target-conditioned and multi-token concept gate

A monitor built from preselected words, phrases, templates, or concept dictionaries is
target-conditioned. It may be useful for known-policy auditing, but it cannot be
reported as a target-blind semantic monitor.

Freeze concept vocabulary, synonyms, tokenizer decomposition, control words,
layer bands, aggregation, thresholds, template generator, template prompts, phrase
reconstructor, oracle proposer, and all post-hoc filtering using training-only data.
Evaluate at least:

- literal target mentions and innocent discussion of the target;
- paraphrases, synonyms, translations, homoglyphs, spacing, and tokenization changes;
- multi-token concepts and concepts absent from the predefined dictionary;
- semantically matched correct and incorrect cases;
- target-blind open-set conditions; and
- a no-concept-list baseline.

The template lens and oracle lens are separate learned or constructed feature systems.
Their performance cannot be attributed to the original single-token Jacobian lens,
and their generation, training, storage, inference, privacy, and selection costs must
be included.

## Retrospective-audit and label-independence gate

The paper's automated auditing result is a retrospective diagnosis comparator, not an
online monitor. Future audit claims must separate:

1. completed-transcript retrospective interpretation;
2. localization of a known phenomenon within a completed transcript;
3. prefix-only anomaly detection;
4. prospective eventual-failure prediction;
5. pre-action detection before irreversible tool execution; and
6. online intervention utility.

Claims, target concepts, human ground truth, NLA-derived labels, investigator prompts,
readout-query budget, judge identity, scoring rubric, and transcript selection must be
frozen independently of sealed evaluation. A monitor may not be trained or tuned on
claims extracted from the same transcripts used to score it.

A tiny curated claim set cannot establish prevalence, false-positive rate, calibration,
open-set coverage, or controller utility. Full-population evaluation must include
successful episodes, ordinary non-target cognition, ambiguous cases, recoverable
errors, terminal failures, tool failures, malformed outputs, and verifier failures.

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

The external BF16 precedents and official reference implementation may not be used to
skip exact quantized parity. They reduce the value of spending Q35Q effort merely to
prove that a large MoE lens can exist in BF16. Q35Q's unique purpose is now sharper:
determine whether an admitted, locally feasible quantized path preserves the
derivatives needed for a credible Agents-A1 scaling route.

## External-replication lane

A separate launch amendment is required before downloading or executing any public
lens or base-model tensor payload. That amendment must freeze:

- the public lens repository revision and every artifact identity;
- the base-model revision and exact lm-head shard identity;
- the official or third-party GitHub/Hugging Face source revision and dependency lock;
- corpus identity, source-position policy, target-position policy, estimator, shard
  boundaries, merge rule, and expected fit receipts;
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

The official reference implementation loads lens files with
`torch.load(..., weights_only=True)`, which reduces arbitrary-object loading risk but
does not establish artifact identity, schema correctness, non-malleability, or
production suitability. The existing isolated-conversion and immutable-digest rules
continue to apply to third-party artifacts.

Before such a launch, metadata and source inspection only are permitted. No public
behavioral steering trial is authorized by this addendum.

## Prompt-count convergence gate

Public claims that approximately 100 prompts are usable or that a 100-prompt fit
matches a 1000-prompt fit within noise are useful only as leads for a resource-saving
pilot. They are not imported sample-size results.

Any checkpoint-specific Agents-A1 lens proposal must first preregister a training-only
prompt-count convergence study using independently fitted shards at multiple frozen
corpus sizes. Stability must be evaluated on public or training-only readout metrics,
artifact-to-artifact distance, held-out public prompts, logit-lens comparisons, and
estimator diagnostics. Sealed correctness labels, private trajectories, verifier
outcomes, and production telemetry may not select the fit size. The smallest stable
fit may advance only if it also passes all derivative, provenance, privacy, and
artifact-admission gates.

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
9. **Comparator parity.** Prompt-final hidden state, trajectory delta, logit lens,
   router/path summaries, confidence, metadata, and Jacobian-space features must use
   the same examples, outer splits, calibration budget, and selection budget.
10. **Privacy boundary.** Only predeclared aggregate telemetry may be committed.
    Raw prompts, outputs, labels, tokens, hidden states, routes, expert identities,
    Jacobians, per-example predictions, and secret-linked digests remain private.

## Technically credible scaling sequence

The current credible sequence is:

1. finish Q35Q Phase-0 honestly;
2. establish exact quantized derivative parity on the admitted Qwen3.5 MoE path;
3. audit the official Anthropic paper and reference implementation at immutable
   commit `581d398613e5602a5af361e1c34d3a92ea82ba8e` as the canonical method source;
4. reproduce estimator mechanics, logit-lens comparisons, serialization, and resource
   accounting on a separately admitted small open model or the Agents-A1-4B dense
   sibling before attempting the 35B MoE;
5. audit the public Qwen3.6-35B-A3B lens metadata, serialization, source path, and
   claimed fit receipts through a separate bounded amendment, treating it as the
   nearest public same-backbone feasibility comparator rather than an Agents-A1 lens;
6. independently audit the public 397B BF16 artifact only if its additional scale
   comparison remains decision-relevant;
7. run an independent forward-only correctness-monitor benchmark with external
   checks, metadata, confidence, logit-lens, hidden-state, trajectory, and routing
   comparators;
8. require stable incremental prediction beyond every cheaper comparator;
9. preregister a public/training-only prompt-count convergence pilot before any
   checkpoint-specific Agents-A1 lens fit;
10. only then design an Agents-A1-native derivative or telemetry capture; and
11. keep every intervention and production gate separate.

If quantized derivative parity fails, the program must report that result and choose
between a separately resourced BF16/FP8 path, a smaller admitted dense engineering
model, or stopping the Jacobian branch. It may not substitute any external claim for
local parity evidence.

## Status and claims

M38E remains closed at terminal `inconclusive`. Q35Q remains
`q35q_artifact_admission_blocked`. M39 remains design-only and capture-prohibited.
The research program is not finished.

Established from public primary sources:

- the canonical Jacobian-lens estimator and a reference implementation are public;
- the official implementation exposes the dominant fitting-cost structure: one
  forward plus `ceil(d_model / dim_batch)` backward passes per prompt;
- the paper reports mechanistic evidence that selected J-lens directions support
  verbal report, modulation, latent intermediate computation, flexible use, and
  selective causal effects in the tested proprietary models;
- the ordinary logit lens captures a substantial fraction of the reported
  workspace-like structure and is therefore a mandatory baseline;
- the paper's automated audit is retrospective and small, and its proof-of-concept
  evaluation-awareness score is target-conditioned;
- the single-token J-lens does not provide an open-vocabulary semantic monitor; and
- the public large-MoE lens artifacts establish feasibility leads, not admitted
  Agents-A1 evidence.

Unproven:

- independent reproduction of the proprietary-model global-workspace experiments;
- exact architecture, checkpoint, runtime, and artifact provenance for those results;
- quantized or production-runtime estimator parity;
- target-blind, open-set semantic monitoring;
- prospective error prediction, completed-error detection, or online controller
  utility;
- incremental correctness value over logits, logit lens, hidden states, external
  checks, trajectory summaries, router telemetry, sparse features, and transcoders;
- safe early exit, truncation, retry, escalation, routing intervention, correction,
  activation steering, Agents-A1 transfer, or production utility; and
- any conclusion about phenomenal consciousness.

No completed-error predictor, universal hidden-state correctness signal, semantic
workspace correctness monitor, safe early-exit rule, truncation policy, causal expert
localization, routing intervention, correction policy, activation steering,
Agents-A1 transfer, or production utility is established.