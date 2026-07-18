# STEER ADDENDUM — Layer localization, sign reversal, and incremental geometry gates

Date: 2026-07-18

Status: binding protocol addendum. This file does not reopen M38E, advance Q35Q, authorize scientific execution, or weaken any privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, production, or stop rule.

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- No weight staging, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized.
- GitHub currently reports this repository as public. Commits remain restricted to aggregate program-control records and public-source engineering code or tests.

## New public evidence

At immutable public commit `45a7908cf81b5487ba2b386fc5c577bae710aaa8`, `solarkyle/jspace` added a PopQA replication and per-layer analysis combining contextual residual-stream curvature with output-logprob and Jacobian-workspace features on Gemma-4-E4B.

The reported bounded findings are:

1. Contextual curvature can carry a substantial correctness-associated signal at selected late-middle layers.
2. The direction changes across depth: layers below the transition were below chance for the chosen label direction, while later layers rose above chance.
3. A broad layer-band average cancelled opposing signs and materially obscured the localized signal.
4. After localization, curvature added approximately no incremental discrimination over output-logprob plus workspace entropy in the reported nested-CV comparison.
5. A favorable confident-slice result from the first dataset did not replicate after pooling a second dataset.

The underlying curvature paper, arXiv `2604.23985`, establishes a relation between contextual curvature and next-token entropy in GPT-2 XL and Pythia-2.8B and reports trajectory-aligned perturbation effects. It does not establish correctness prediction, large-MoE transfer, Agents-A1 transfer, or incremental value over simpler monitor features.

These are public implementation and preprint results, not admitted results of this repository.

## Binding correction: pooled depth summaries are not default-admissible

Future hidden-state, curvature, Jacobian-Lens, router, attention, sparse-feature, and trajectory monitors must not treat a fixed broad layer mean as the default scientific representation.

Each feature family must preserve enough depth resolution to detect:

- sign reversals;
- narrow informative bands;
- architecture-specific depth shifts;
- task-family-specific depth shifts;
- cancellation introduced by averaging;
- apparent performance created by post-hoc layer selection.

Required reporting includes:

1. Per-layer or pre-registered depth-block performance.
2. The sign and scale of each layer-level association.
3. A broad pooled summary as a comparator, not as the only representation.
4. A sign-aware summary that cannot silently cancel opposite directions.
5. Stability of the selected depth region across folds, seeds, datasets, task families, model revisions, quantizations, and serving paths.
6. Performance after nuisance controls and against all simpler baselines.

## Layer selection and multiplicity

Layer localization is model selection. It must be confined to training data or an explicitly designated inner validation partition.

Before opening outer-validation or sealed-test labels, freeze:

- candidate layers and depth blocks;
- feature definitions and signs;
- any smoothing, pooling, normalization, or dimensionality reduction;
- the selection rule;
- the maximum number of retained layers or blocks;
- the classifier and regularization family;
- all thresholds and calibration rules.

The outer test must evaluate the entire frozen selection procedure. Reporting the best layer on the same examples used for scientific scoring is inadmissible. Correct for multiplicity when presenting layer-wise inferential claims.

Required negative controls include:

- shuffled labels;
- random layers or matched-size random layer subsets;
- reversed or permuted depth order;
- broad-band averages expected to expose cancellation;
- sign-flipped features;
- equal-capacity models using only logits, entropy, metadata, and hidden-state norms.

## Incremental-value gate

A geometric or Jacobian-derived feature may be individually predictive and still be operationally redundant.

No claim of monitor value may be based on single-feature AUROC alone. The primary claim must be the sealed incremental value over a frozen comparator stack containing, where available:

- output logprob and entropy;
- prompt-final and decision-boundary hidden-state probes;
- hidden-state norms and simple trajectory deltas;
- metadata, action history, finish reason, latency, and tool-state features;
- route paths, margins, entropy, persistence, and expert-transition summaries;
- sparse-feature or transcoder comparators;
- previously admitted workspace/Jacobian summaries.

Report at minimum:

- delta AUROC and delta AUPRC;
- calibration change;
- selective-risk or abstention utility;
- right-to-wrong and wrong-to-right policy transitions;
- confidence intervals under task- or cluster-aware resampling;
- end-to-end latency, accelerator, memory, transfer, storage, and privacy cost.

A localized feature that adds no sealed value over the comparator stack must be classified as mechanistically interesting but operationally redundant. It must not justify Agents-A1 instrumentation by itself.

## Cross-domain sign stability

The existing program already requires family-disjoint evaluation and reporting of sign reversals. This addendum makes the disposition explicit.

If the feature-to-error mapping reverses across task families, modalities, action types, or environment states:

1. A universal scalar threshold is prohibited.
2. Pooled performance cannot mask per-family harm.
3. Any task-conditioned calibration must use only information available before the monitored decision.
4. The task-condition classifier becomes part of the monitor and must be included in cost, privacy, robustness, and error accounting.
5. Unrecognized or out-of-distribution families default to no intervention.
6. Transfer claims require a frozen prospective test on never-seen families.

## Quantization and runtime portability

Public claims that one fitted lens can read multiple quantizations do not waive parity requirements.

For every admitted model/runtime/quantization combination, separately establish:

- exact model and tokenizer identity;
- forward equivalence within the frozen tolerance;
- activation, Jacobian, JVP, and VJP parity where those quantities are used;
- per-layer feature agreement and sign stability;
- selected-depth stability;
- monitor calibration and sealed incremental value;
- no new privacy or telemetry-reconstruction failure.

A lens fitted in one precision may be tested on another only as a preregistered transfer condition. It is not presumed portable.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence remains derivative-first and detection-before-intervention. After Q35Q admission and derivative parity, use a staged depth-resolution design:

1. Capture the cheapest decision-boundary metadata, logits, confidence, and selected hidden-state summaries.
2. Capture compact per-layer route margins, entropy, expert identity, persistence, and transition summaries without averaging across depth.
3. Fit layer-sparse and sign-aware probes using nested selection on training data only.
4. Compare them against broad-band averages to quantify cancellation.
5. Add low-cost trajectory geometry such as contextual curvature only if its complete capture cost is bounded.
6. Add Jacobian-Lens features only after exact derivative parity and only if they show sealed incremental value over the preceding stack.
7. Require prospective task-family, modality, quantization, and runtime transfer tests.
8. Keep abort, truncation, retry, escalation, forced routing, expert intervention, and activation steering under separate policy and safety gates.

For a large MoE, depth-sparse instrumentation is preferable to full all-layer capture only after the selected layer set is frozen and validated prospectively. Post-hoc selection of a cheap layer from the sealed test is prohibited.

## Current blocker and execution order

This addendum does not change the active blocker. The required order remains:

1. Production-path upstream/runtime provenance composition.
2. Freeze the complete GPTQModel/Defuser/Optimum/Accelerate/PyTorch/CUDA/backend tuple.
3. Run a strict synthetic Qwen3.5-MoE GPTQ loader fixture.
4. Prove exact tensor consumption, expert ordering, and fusion identity.
5. Prove forward, activation-VJP, activation-JVP, and finite-difference parity.
6. Pass the complete adversarial Phase-0 conjunction.
7. Stage weights only after admission.
8. Obtain a separately authorized GPU-resource transition.
9. Prove full-model derivative parity.
10. Fit Q35Q under the frozen protocol.
11. Run sealed detection-only comparisons with the layer-localization and incremental-value gates above.
12. Begin Agents-A1-native instrumentation only if Q35Q establishes incremental monitor value.

## Established versus unproven

Established only as external public evidence:

- Internal geometric signals can be strongly layer-localized.
- Their label direction can reverse across depth.
- Broad depth averaging can destroy a real localized signal.
- An individually predictive geometric feature can add essentially no value over simpler uncertainty features.
- Favorable subgroup findings can fail to replicate on a second dataset.

Unproven for this program:

- Q35Q admission or derivative parity.
- The location, direction, stability, or utility of curvature features in Qwen3.5-MoE.
- The location, direction, stability, or utility of Jacobian or router features in Agents-A1.
- Quantization-invariant lens behavior.
- Incremental correctness value over logits, hidden states, metadata, trajectory, and route summaries.
- Safe early exit, abort, retry, escalation, routing intervention, steering, or production utility.
