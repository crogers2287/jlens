# STEER ADDENDUM — Evidence-grounding, copy-selectivity, and distractor controls

Date: 2026-07-22

Parent remote head: `e1aa24d1ee602865e4a8db56f789dec26cad6c24`

Status: binding future-protocol correction; no current execution authorization

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- GitHub currently reports this repository as public. Aggregate-only commit restrictions remain binding.
- No weight staging, tensor-payload retrieval, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, model post-training, intervention, or production use is authorized by this document.
- Every privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, cleanup, commit-safety, comparator, nuisance-control, production-gating, and stop rule remains binding.

## New primary evidence and narrow interpretation

Fang et al., **Copy Less, Ground More: Overcoming Repetitive Copying in Long-Context Reasoning via Evidence-Aware Reinforcement Learning**, arXiv `2607.19345v1`, submitted 2026-07-21, studies lexical copying and evidence selectivity in long-context reasoning.

The public paper reports the following bounded facts:

1. Output-to-input n-gram overlap increased with context length across seven tested long-context models.
2. On the reported GSM-Infinite experiments, high prompt-copy overlap was associated with lower answer accuracy even after grouping examples by the stated number of reasoning operations.
3. The authors partitioned context into task-relevant key evidence and irrelevant distractors, then reported that correct samples generally had higher key-evidence overlap, lower distractor overlap, and a higher grounding ratio.
4. The pattern was reported across multiple dense and sparse models, with exceptions and weaker separation on some systems.
5. The proposed GEAR reward combines an accuracy reward, key-evidence overlap, and a distractor-overlap penalty.
6. The reported training used Qwen3.5-9B, Qwen3.5-27B, and Qwen3.5-35B-A3B, including a sparse MoE close in broad backbone scale to the intended Agents-A1 comparison family.
7. The authors report held-out improvements over accuracy-only GSPO on several long-context benchmarks, with larger gains at 128k context in the reported runs.
8. Grounding-only and distractor-only reward ablations were not sufficient; grounding-only could increase copying and degrade accuracy.
9. The study concerns post-training and long-context QA/reasoning. It does not establish prospective agent-error prediction, hidden-state correctness awareness, router telemetry value, safe truncation, or Agents-A1 transfer.
10. No attributable public implementation or immutable training package was located during this review.

These results make a cheap surface-level evidence-selectivity baseline mandatory. They do not establish that lexical copying is intrinsically wrong, that low copying is sufficient for correctness, or that the reported reward should be applied to this program.

## Binding claim separation

Future long-context studies must distinguish:

1. **Copy volume:** literal or near-literal overlap between generated content and available context.
2. **Key-evidence use:** overlap or semantic support attributable to prospectively identified task-relevant evidence.
3. **Distractor use:** overlap or semantic dependence attributable to prospectively identified irrelevant or misleading context.
4. **Grounding selectivity:** preferential use of relevant evidence relative to distractors.
5. **Reasoning quality:** whether intermediate operations are valid and sufficient.
6. **Objective outcome:** whether the final answer or action passes the canonical verifier.
7. **Internal-monitor signal:** hidden-state, route, workspace, sparse-feature, transcoder, or Jacobian information beyond cheaper observable features.
8. **Intervention:** post-training, context mutation, suppression, truncation, retry, abort, routing changes, or steering.

Passing one level does not establish the next. High evidence overlap can reflect correct extraction, needless repetition, quotation, code reuse, or benchmark formatting. Low overlap can reflect paraphrase, unsupported synthesis, omission, or hallucination.

## Mandatory evidence-grounding comparator

For every technically compatible long-context correctness-monitor study, include a frozen passive comparator containing at least:

- total output-to-context overlap;
- overlap with prospectively admitted key evidence;
- overlap with prospectively admitted distractor context;
- key-minus-distractor selectivity;
- response and reasoning length;
- context length and utilization;
- truncation and maximum-token indicators;
- evidence position and distance from the decision boundary;
- retrieval rank, source count, and evidence redundancy when retrieval is used;
- requirement-ledger and checklist state when tasks have enumerable requirements.

At least one literal overlap family and one semantic-support family should be included when technically feasible. Literal n-gram overlap alone cannot support an open-vocabulary grounding claim.

This comparator must precede expensive internal instrumentation. Router, workspace, sparse-feature, transcoder, directional-JVP, or Jacobian features must demonstrate residual sealed objective-outcome value after the evidence-grounding comparator and existing context-envelope controls are included.

## Evidence ontology and provenance

Key evidence and distractors are experimental labels requiring their own provenance. Freeze before outer validation:

- the evidence unit: token span, sentence, line, document, tool result, code hunk, requirement, or event;
- the support ontology and allowed relations;
- annotation source and adjudication procedure;
- deterministic extraction or judge identity;
- evidence boundaries and document identities;
- distractor construction and sampling policy;
- treatment of partially relevant, redundant, contradictory, and multi-hop evidence;
- treatment of evidence revealed only after tool use;
- handling of missing, unavailable, stale, or verifier-dependent evidence;
- tokenization, normalization, overlap metric, semantic encoder, thresholds, and aggregation;
- selection, calibration, certification, and sealed-test populations.

Evidence labels derived from the canonical answer, future trajectory steps, sealed verifier outcomes, or post-intervention information unavailable at the monitored boundary are leakage unless the study is explicitly retrospective and labeled as such.

Model-generated evidence labels remain model evidence rather than ground truth until validated against an independently admitted source. Annotation disagreement and uncertain evidence must not be silently converted to key evidence or distractor.

## Mandatory nuisance and adversarial controls

Future evaluations must include, when compatible:

1. Exact-copy versus paraphrase controls.
2. N-gram size and tokenization controls.
3. Response-length and context-length matching.
4. Evidence-position and recency matching.
5. Relevant and irrelevant length-matched contexts.
6. Redundant-evidence and duplicate-distractor controls.
7. Quotation-required tasks where copying is correct.
8. Code, command, identifier, citation, and structured-data tasks where literal reuse may be required.
9. Tasks requiring synthesis with little lexical overlap.
10. Contradictory, stale, adversarial, or poisoned evidence.
11. Multi-hop tasks where no single span is sufficient.
12. Evidence absent from the current context but available through a permitted tool.
13. Output truncation, context truncation, compaction, cache, retry, and resume controls.
14. Language, script, tokenizer, and modality controls.
15. Correct and incorrect examples matched on copy volume.
16. Correct and incorrect examples matched on key-evidence and distractor overlap.

A result that disappears after length, truncation, task type, evidence position, quotation requirements, or evidence availability is controlled must be described as context or process telemetry rather than privileged correctness information.

## Surface correlation is not causal localization

Correlation between distractor copying and final failure does not establish that copying caused the failure or identify the first erroneous step.

Future reports must separate:

- pre-answer evidence selection;
- intermediate evidence citation or copying;
- the first invalid reasoning operation;
- final-answer correctness;
- output truncation;
- failure before an irreversible external action;
- retrospective explanation after the complete trajectory.

Sequence-level correctness labels cannot establish when grounding failed. A copied distractor may be a symptom of earlier confusion, a consequence of length pressure, or an irrelevant byproduct.

## Adapted-model and intervention boundary

GEAR is a post-training method. Any model trained with an evidence-grounding reward is a new adapted artifact and cannot inherit checkpoint, runtime, calibration, monitor, router, derivative, safety, or production admission from its base model.

Any future training or control study must separately evaluate:

- accuracy-only training;
- key-evidence reward only;
- distractor penalty only;
- the combined reward;
- no-training passive monitoring;
- fixed decoding and context-management baselines;
- verifier-backed external evidence selection;
- full-population quality and tail failures;
- off-domain, multilingual, tool-use, coding, multimodal, and adversarial regressions;
- reward hacking and evidence-label exploitation;
- total training, inference, annotation, retrieval, and verification cost.

No result in the cited paper authorizes early exit, reasoning truncation, content deletion, tool suppression, retry, abort, forced routing, activation steering, or production deployment.

## Privacy and public-repository boundary

Raw prompts, contexts, evidence spans, distractors, outputs, trajectories, overlap traces, per-example scores, annotations, verifier labels, hidden states, routes, expert traces, Jacobians, and model weights remain prohibited from this public repository.

Only prospectively specified aggregate summaries may be committed, including aggregate overlap statistics, uncertainty intervals, evidence-label disagreement rates, and comparator outcomes after privacy review.

Evidence annotations may themselves reveal sensitive task content. Hashes, offsets, snippets, document identities, or reconstruction-enabling aggregates are not automatically safe.

## Agents-A1 scaling directive

The technically credible long-context sequence is now:

1. Complete Q35Q production-path provenance and exact derivative admission on one frozen static runtime.
2. Define matched long-horizon task contracts, evidence ontologies, and immutable requirement ledgers without sealed-outcome access.
3. Establish minimal, relevant-long, irrelevant-length-matched, position, compaction, progressive-disclosure, retrieval, and truncation controls.
4. Establish deterministic checks, detailed checklists, and passive copy/key-evidence/distractor-selectivity baselines.
5. Evaluate the separately admitted Agents-A1-4B dense sibling under the same tasks, evidence boundaries, and context envelopes.
6. Evaluate confidence, self-judgement, peer representations, passive hidden states, bounded trajectory summaries, and evidence-grounding features on full-population and residual failures.
7. Capture minimal executed-route telemetry on Agents-A1-35B only after evidence, context, checklist, and truncation controls are frozen.
8. Require route features to add sealed objective-outcome value after conditioning on copy volume, evidence selectivity, trajectory length, truncation, requirement state, verifier history, and dense-sibling representations.
9. Add sparse-feature or transcoder streams when admitted.
10. Add Jacobian-Lens features only after exact derivative parity and sealed incremental value over every cheaper comparator.
11. Keep evidence-aware post-training, context mutation, retrieval changes, early exit, truncation, retry, abort, tool suppression, forced routing, activation steering, and production deployment under separate intervention gates.

A route or Jacobian signal that primarily tracks indiscriminate copying, context length, evidence position, or truncation pressure is useful serving or process telemetry, not evidence of privileged model-internal correctness awareness.

## Current blocker and execution order

This addendum does not change the active blocker.

The next admissible engineering work remains one clean-subprocess, fail-closed production adapter that:

1. verifies the frozen upstream Transformers artifact;
2. binds the live import to its owning installed distribution and `RECORD`;
3. derives complete live source closure for dispatch, converters, nested operations, model/configuration classes, and loader objects;
4. rejects shadow packages, editable installs, monkeypatches, forged identities, incomplete closure, wrong ownership, and unadmitted loaders;
5. invokes and binds the actual GPTQModel/Defuser loader entry point;
6. freezes the complete immutable runtime tuple;
7. passes the full adversarial integration conjunction;
8. emits only the permitted aggregate result.

After that remain strict synthetic loading, exact quantization-tensor consumption and expert-ordering proof, forward/VJP/JVP/finite-difference parity, Phase-0 admission, weight staging, and a separately authorized GPU transition.

## Established versus unproven

Established only as external public evidence:

- Repetitive output-to-context copying increased with context length across the reported models.
- In the reported long-context experiments, indiscriminate or distractor-heavy copying was associated with lower accuracy.
- Correct samples generally showed stronger selectivity toward prospectively identified key evidence in the authors' evaluated settings.
- The reported combined evidence-and-distractor reward improved several held-out long-context benchmarks over accuracy-only training.
- Grounding-only and distractor-only reward ablations were insufficient, showing that one-dimensional anti-copy objectives can be harmful.
- Qwen3.5-35B-A3B was included in the reported post-training experiments.
- Passive evidence-grounding features are therefore a mandatory future cheap comparator for compatible long-context monitoring claims.

Unproven for this program:

- independent reproduction or an immutable public training package;
- causal attribution of failure to repetitive copying;
- universal evidence-grounding metrics across tasks, languages, modalities, tokenizers, and runtimes;
- reliable evidence annotations for open-ended tool-using agents;
- prospective error-onset localization;
- transfer to Agents-A1-4B or Agents-A1-35B;
- incremental hidden-state, router, workspace, sparse-feature, transcoder, or Jacobian value after evidence-grounding controls;
- safe evidence-aware post-training, context mutation, early exit, truncation, retry, escalation, route intervention, activation steering, or production deployment;
- completion of Q35Q provenance, strict loading, forward parity, or derivative admission.

The research program remains unfinished. Q35Q remains blocked at production-path upstream/runtime provenance composition.
