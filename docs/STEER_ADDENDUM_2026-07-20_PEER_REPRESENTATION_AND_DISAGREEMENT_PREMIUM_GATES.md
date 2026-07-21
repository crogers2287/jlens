# Steer addendum — peer-representation baselines and disagreement-premium gates

Date: 2026-07-20

This addendum is binding program control. It inherits every existing privacy,
sealed-data, verifier, provenance, resource, derivative-parity, intervention, and
production-gating rule. It does not reopen M38E, advance Q35Q, authorize weights,
model execution, GPU work, hidden-state or router capture, Jacobian fitting, sealed
evaluation, intervention, or production use.

## New primary evidence

Ashuach et al., “Masked by Consensus: Disentangling Privileged Knowledge in LLM
Correctness,” ACL 2026 / arXiv `2604.12373`, compares probes trained on a target
model's own hidden states with probes trained on representations from peer models
processing the same question.

The main experiments use Llama-3.1-8B, Qwen2.5-7B, and Gemma-2-9B, with
Qwen3-Embedding-8B as an external representation baseline and Qwen3-32B in an
appendix. The evaluated domains are factual recall (Mintaka, TriviaQA, HotPotQA)
and mathematical reasoning (MATH, GSM1K). Probes use the final question token from
every fifth layer, with linear and MLP probe families.

On ordinary full test sets, self probes generally do not outperform peer-model probes.
High inter-model agreement lets a peer representation encode shared question
difficulty and the peer model's own success pattern, which can predict the target
model's outcome without access to the target model's private state.

The paper therefore evaluates a pairwise disagreement subset in which the target and
peer model have opposite correctness labels. Probes are trained on the full training
population and only filtered to disagreement examples at test time; training on the
disagreement subset would create a trivial inverse-label shortcut.

On disagreement subsets, a modest self-over-peer premium appears consistently in the
reported factual tasks, while no consistent premium appears in mathematical
reasoning. The factual premium emerges from early-to-mid layers and strengthens with
depth. The evidence is correlational, mainly 7B–9B, limited to factual recall and
math, and does not establish agentic, MoE, causal, online, or production validity.

No attributable public implementation was located. The paper and project page remain
primary methodological evidence, not a reproduced result in this repository.

## Binding claim separation

A hidden-state, router, sparse-feature, semantic-workspace, or Jacobian feature may
support three different claims:

1. it predicts target-model correctness;
2. it improves over prompt, metadata, output, and confidence baselines; or
3. it contains model-specific correctness information unavailable from comparable
   external representations.

Passing the first or second claim does not establish the third.

The phrase “privileged,” “private,” “model-specific,” “introspective,” or equivalent
may be used only when a frozen self representation outperforms all admitted peer and
embedding representation baselines under the disagreement-premium protocol below.

If peer representations match a self monitor, the result must be classified as shared
difficulty, task, semantic, or public-representation evidence unless a separate sealed
analysis establishes otherwise.

## Mandatory peer-representation comparator

Every future correctness study using internal model features must include, when
technically compatible:

- prompt-text and transparent metadata baselines;
- a frozen embedding-model representation baseline;
- at least one independently admitted peer-model representation baseline;
- the target model's own passive hidden-state baseline;
- final logits, confidence, entropy, and answer/output baselines;
- the proposed router, workspace, sparse-feature, transcoder, or Jacobian features.

Separate probes may be trained over different representation dimensions. No
cross-model coordinate alignment is required merely to test predictive value.
Architecture or dimension mismatch is not grounds for omitting a peer-representation
baseline.

Peer models, checkpoints, processors, layers, pooling rules, probe families,
regularization, calibration, and selection budgets must be frozen using training-only
data. The strongest peer baseline is selected without sealed-label access.

## Disagreement-premium protocol

Report both:

1. full-population performance; and
2. pairwise disagreement performance where the target and each peer model have
   opposite frozen outcome labels.

Disagreement strata are evaluation strata only. Do not train, select layers, tune
probes, calibrate thresholds, or choose peer models using disagreement-test labels.
Training exclusively on a disagreement subset is prohibited because peer correctness
then becomes a deterministic inverse shortcut.

For every target-peer pair report:

- total sealed population size;
- agreement and disagreement counts;
- target and peer accuracies;
- self-probe and peer-probe AUC, AUPRC, calibration, and selective-risk metrics;
- the self-minus-best-peer premium with cluster-aware confidence intervals;
- per-family, per-modality, per-action, and per-boundary results;
- the exact independent unit used for uncertainty estimation.

Disagreement filtering can create a harder and shifted population. Report both
absolute performance and the premium; do not present a positive premium with
near-chance absolute performance as an operational monitor.

## Long-horizon and agent boundary

For agent trajectories, endpoint disagreement does not identify when models diverged
or when an error became irreversible. Freeze the prediction boundary and distinguish:

- prompt-time admissibility or answerability;
- pre-action eventual-failure prediction;
- post-action but pre-execution prediction;
- post-execution diagnosis;
- terminal outcome prediction.

A target-peer disagreement at the episode outcome cannot by itself establish
step-local privileged information, causal error localization, or safe intervention.

Repeated rollouts, common tasks, templates, environments, tool states, and users must
be treated as clusters. Episode-level examples may not be treated as independent when
that assumption is unsupported.

## Agents-A1 bridge

After separate artifact and runtime admission, Agents-A1-4B becomes the minimum
same-family peer-representation baseline for predicting Agents-A1-35B outcomes under
matched tasks, harnesses, prompts, tools, decoding, decision boundaries, verifier
rules, and outcome taxonomies.

This comparison does not assume aligned layers or semantic coordinates. It trains
separate frozen probes and asks whether the 35B model's own representations provide
sealed predictive value beyond representations produced by the 4B sibling.

At least one non-sibling peer or embedding baseline should be included when resource
and privacy constraints permit, because a same-family peer may share unusually strong
difficulty and task features.

The future Agents-A1 comparator order is:

1. external deterministic checks and metadata;
2. logits, confidence, and output baselines;
3. embedding and peer-model representations;
4. target-model hidden-state probes;
5. bounded trajectory summaries;
6. minimal conditional route telemetry;
7. sparse-feature or transcoder streams;
8. Jacobian-Lens streams after exact derivative parity.

Router or Jacobian features must demonstrate sealed incremental value over the best
peer representation on both the full population and the disagreement population.
A gain only on agreement cases is not evidence of model-specific correctness access.

## Cost, privacy, and verifier rules

Peer-model execution, hidden-state extraction, replay, storage, calibration, and
serving overhead are part of total monitoring cost. Equal-cost black-box or verifier
baselines remain mandatory.

Raw prompts, outputs, hidden states, routes, Jacobians, per-example outcomes,
peer-model predictions, and disagreement membership remain private. Only predeclared
aggregate statistics may be committed.

Outcome labels and disagreement strata inherit all canonical verifier and sealed-data
rules. Verifier disagreement, unavailability, or benchmark-label uncertainty must be
quarantined rather than silently converted into target-peer disagreement.

## Active blocker and status

Q35Q remains `q35q_artifact_admission_blocked`. The active engineering blocker is
unchanged: production-path upstream/runtime provenance composition, followed by the
immutable GPTQ runtime tuple, strict synthetic loading, tensor-consumption and expert
ordering proof, quantized forward/VJP/JVP/finite-difference parity, the complete
Phase-0 conjunction, weight staging, and a separately authorized GPU transition.

Established from the cited primary source:

- ordinary probe accuracy can be matched by peer-model representations;
- inter-model correctness agreement is a material confound;
- disagreement-only evaluation must not be used for probe training;
- the reported factual tasks show a modest self-over-peer premium under disagreement;
- the reported math tasks show no consistent self-over-peer premium;
- the premium is domain- and depth-dependent.

Unproven:

- independent reproduction;
- a privileged correctness signal in coding, tool use, long-horizon agents, MoEs, or
  Agents-A1;
- prospective or step-local error prediction;
- causal correctness control;
- incremental router or Jacobian-Lens value over peer representations;
- safe early exit, abort, retry, escalation, routing intervention, activation
  steering, or production deployment.

The research program is not finished.
