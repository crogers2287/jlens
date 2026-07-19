# STEER ADDENDUM — canonical protocol index and no-milestone-drift rule

Date: 2026-07-18
Parent remote head: `739ff23fe4b8676eaacc3f022ea9dbdcaa5bc6e0`

This is a binding addendum to `CODEX_AUTOSTEER.md` and `steer.md`.
It changes no scientific result, privacy rule, sealed-data rule, verifier rule,
production gate, exact-gradient requirement, resource boundary, or stop rule.

## Reason for correction

`steer.md` identifies itself as the canonical milestone source but states that it
consolidates protocol only through parent head
`7ca183e039ac9b4da45aee7bb3d88c3c404ad066`. Twelve later comparator and
nuisance-control addenda are present at the parent head of this correction.
Leaving those documents unindexed creates avoidable ambiguity for an autonomous
executor deciding which controls are binding.

This correction makes the post-consolidation addenda explicitly cumulative and
prevents research scanning from displacing the unresolved engineering milestone.

## Binding post-consolidation protocol index

The following documents are cumulative and binding:

1. `docs/STEER_ADDENDUM_2026-07-17_WORKSPACE_MONITOR_TARGET_CONDITIONING_AND_FINAL_LOGIT_CONFOUND.md`
2. `docs/STEER_ADDENDUM_2026-07-17_TRANSCODER_COMPARATOR_AND_FEATURE_SELECTION_LEAKAGE_GATES.md`
3. `docs/STEER_ADDENDUM_2026-07-18_AGENTS_A1_MULTIMODAL_ROUTING_AND_MODALITY_MATCHED_CONTROLS.md`
4. `docs/STEER_ADDENDUM_2026-07-18_GNOSIS_TRAJECTORY_COMPARATOR_AND_END_TO_END_COST_GATES.md`
5. `docs/STEER_ADDENDUM_2026-07-18_MULTI_HEAD_LATENT_CONTROL_AND_POLICY_EVALUATION_GATES.md`
6. `docs/STEER_ADDENDUM_2026-07-18_RECALL_CONTROLLED_AGENT_ABORT_AND_SEQUENTIAL_CERTIFICATION_GATES.md`
7. `docs/STEER_ADDENDUM_2026-07-18_LAYER_LOCALIZATION_SIGN_REVERSAL_AND_INCREMENTAL_GEOMETRY_GATES.md`
8. `docs/STEER_ADDENDUM_2026-07-18_CROSS_LAYER_ROUTING_ANCESTRY_AND_ROUTE_SEMANTIC_CONFOUND_GATES.md`
9. `docs/STEER_ADDENDUM_2026-07-18_EXPERIENCE_MEMORY_TERMINATION_AND_CONTAMINATION_GATES.md`
10. `docs/STEER_ADDENDUM_2026-07-18_ROUTER_COALITION_GENERALIST_CORE_AND_EXPERT_IDENTITY_GATES.md`
11. `docs/STEER_ADDENDUM_2026-07-18_EXPERT_SCATTERING_SERVING_COST_AND_ROUTER_PREDICTOR_GATES.md`
12. `docs/STEER_ADDENDUM_2026-07-18_EXTERNAL_INVARIANT_CHECKER_AND_RETROSPECTIVE_LOCALIZATION_GATES.md`

Where a general statement and a later specific correction differ, the more
specific and more restrictive requirement controls. No indexed addendum
constitutes Phase-0 admission, a scientific result, a resource release, or
permission to execute a later phase.

## Canonical current state

- M38E remains terminally closed as `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active milestone remains **production-path upstream/runtime provenance
  composition** exactly as defined in `steer.md`.
- The repository remains public according to GitHub metadata; aggregate-only
  commit restrictions remain binding.
- No weight staging, tensor-payload retrieval, model execution, GPU execution,
  hidden-state capture, router capture, Jacobian fitting, sealed evaluation,
  intervention, or production use is authorized.

## No-milestone-drift rule

External research review is subordinate to execution of the active engineering
milestone.

Do not create another steering addendum merely because a new paper, repository,
or discussion provides an additional example of a comparator or confound already
covered by the indexed controls. A new protocol correction is warranted only
when primary evidence materially changes at least one of:

1. the current engineering admission sequence;
2. a preregistered scientific claim boundary;
3. a privacy, provenance, verifier, resource, or production-safety gate;
4. the minimum comparator set in a way not subsumed by the indexed documents.

Otherwise record the source as a lead outside sealed evidence and make no commit.
Status-only heartbeats remain prohibited as a substitute for executing the active
milestone.

## Official Agents-A1 dense-sibling bridge

InternScience released `Agents-A1-4B` on 2026-07-14. The public Hugging Face
artifact inspected for this correction is revision
`945c40a4aa6f534d434a353207b8d42ecf7a5293`. Its configuration identifies
`Qwen3_5ForConditionalGeneration` with model type `qwen3_5`, rather than the
35B model's MoE architecture. It is therefore an official dense member of the
same Agents-A1 family and materially changes the minimum future comparator set.

This artifact does not change the active Q35Q milestone and authorizes no weight
retrieval, model execution, GPU use, hidden-state capture, Jacobian capture,
scientific evaluation, or production use. Before any use, the dense sibling must
receive its own immutable artifact, processor, vision path, runtime, forward, and
derivative admission. No layer, feature, token, Jacobian, calibration, or semantic
coordinate may be assumed aligned with the 35B MoE.

After Q35Q passes its existing gates and establishes sealed incremental monitor
value, the first Agents-A1-family scaling bridge must include the admitted 4B
dense sibling under matched task partitions, harness, tool schemas, prompts,
decoding, decision boundaries, verifier rules, and outcome taxonomy. Required
paired comparisons are:

1. external checks, metadata, confidence, hidden-state, and trajectory monitors on
   the dense sibling and the 35B MoE;
2. identical full-population and family-disjoint evaluation where both models can
   execute the task;
3. equal-cost reporting and separate calibration for each model;
4. explicit classification of signals shared by both models as general
   agent-family, task, or representation evidence rather than MoE-specific
   evidence;
5. explicit classification of route-only effects as 35B-MoE evidence requiring
   occupancy, parent-route, semantic, topology, and checkpoint controls;
6. prospective, preregistered transfer tests rather than fitting an alignment on
   sealed outcomes.

The dense sibling is a bridge and negative control for MoE-specific claims. It is
not a substitute for Agents-A1-35B route telemetry, derivative parity, or sealed
replication.

## Passive-readout versus representation-adapting monitor boundary

Zeng et al., `ReLope: KL-Regularized LoRA Probes for Multimodal LLM Routing`,
arXiv `2603.24787v2` dated 2026-07-14, report that fixed last-token probes lose
correctness-prediction AUC when visual inputs are introduced. They report stronger
routing AUC from a passive learned token-attention readout and from ReLope, which
optimizes correctness-supervised LoRA parameters at a selected transformer layer
plus a variational bottleneck. The inspected public repository
`Spinozaaa/ReLope` at commit `3e56817b18f05d6b15820e6a6c4a61a940259429`
contains only a two-line README, so no implementation or execution semantics are
currently reproducible from the claimed code release.

This evidence changes the scientific claim boundary. Future monitor reports must
classify the instrumentation as exactly one of:

1. a passive readout from the unmodified admitted model;
2. a learned sidecar transformation of captured states that is mutation-isolated
   from the answer-generation path;
3. an in-path representation-adapted model whose LoRA, adapter, bottleneck, or
   other learned transform can alter downstream computation.

Only category 1 can support a claim that correctness is decodable from the
original model representation. Category 2 can establish performance of a trained
sidecar monitor, not natural correctness legibility in the unmodified state.
Category 3 is a new model artifact and cannot be reported as passive monitoring.
A correctness-supervised transformation may construct a label-predictive
coordinate; its performance is not evidence that the original model already
contained the same directly readable signal.

For category 2, the protocol must prove fail-closed sidecar isolation. With the
monitor enabled versus disabled under deterministic matched execution, the
answer-generation path must preserve exact model parameters, logits, generated
tokens, KV state, router assignments, tool calls, and verifier inputs. The
adapter must consume an immutable captured boundary without writing into the
backbone, caches, router state, or generation buffers. Any replay or second
forward pass must be declared and charged in full.

For category 3, separately freeze and admit the complete adapted artifact,
including base revision, adapter bytes and digest, injection points, layer, rank,
scaling, precision, processor, runtime, and serving path. Re-run outcome,
calibration, safety, privacy, forward-path, and where applicable derivative and
router-telemetry validation on the exact adapted model. Labels generated by an
unadapted model may not be silently used as labels for an adapted model's output,
and adapted-model performance may not be attributed to monitoring alone.

For all learned representation transforms, select the layer, token boundary,
pooling, adapter type, rank, scaling, bottleneck dimension, regularization,
training schedule, label source, classifier, threshold, and calibration using
training data only. Freeze them before outer validation, certification, or sealed
labels are opened. Report passive last-token, passive token-aggregation, and
confidence baselines under equal end-to-end cost; report cross-dataset,
modality-matched, perturbation, and full-population results. Supervised adapter
training, artifact storage, capture, replay, memory, latency, and recertification
costs are part of total monitor cost.

For Agents-A1, passive decision-boundary and token-aggregation probes remain the
first internal comparators. A representation-adapting monitor may be studied only
after those passive baselines and under the classification and admission rules
above. It does not authorize retry, escalation, truncation, expert forcing,
activation steering, or any other policy intervention, and it does not reduce the
Jacobian-Lens derivative-parity or incremental-value gates.

Established from the public source is limited to the authors' reported routing
results on Qwen2.5-VL-7B-Instruct, Gemma3-12B, and Phi-4-Multimodal-Instruct, plus
the methodological fact that ReLope optimizes a correctness-supervised
representation transform. Independent reproduction, generation-path isolation,
base-versus-adapted output parity, long-horizon agent utility, and transfer to
Agents-A1 remain unproven.

## Canonical future comparator order for Agents-A1

After Q35Q runtime admission, strict loading, forward parity, derivative parity,
and sealed incremental-value evidence, Agents-A1-native monitoring must proceed
from cheaper and more observable controls toward more expensive internal
instrumentation:

1. deterministic schema, permission, ordering, provenance, and relational checks;
2. action, tool, finish, latency, modality, and trajectory metadata;
3. calibrated logits, entropy, margins, and confidence;
4. selected decision-boundary hidden-state probes and fixed-budget trajectory
   summaries;
5. independently certified sequential abort, capability, and resolution heads;
6. provenance-bound experience-memory comparators under contamination and
   cold-start controls;
7. matched execution on the separately admitted Agents-A1-4B dense sibling as an
   official same-family control for every compatible non-routing monitor;
8. minimal executed-route identities, weights, margins, entropy, occupancy, and
   parent-route innovations at frozen boundaries on the 35B MoE;
9. coalition, ancestry, semantic-nuisance, expert-footprint, and serving-topology
   controls when route telemetry is evaluated;
10. frozen sparse-feature or transcoder comparators when technically available;
11. Jacobian-Lens features only after exact derivative parity, bounded capture
    cost, and sealed incremental value over every admitted cheaper baseline.

Detection remains separate from abort, retry, escalation, truncation, tool
suppression, speculative selection, expert skipping, forced routing, activation
steering, and production deployment. Each intervention requires its own protocol
and authorization.

## Immediate required work

The next admissible repository progress is implementation or evidence for one
clean-subprocess production adapter that:

1. verifies the frozen upstream Transformers artifact;
2. derives expected source identities from that verified artifact;
3. binds the imported package to its owning installed distribution and ownership
   records;
4. derives the complete source closure from the actual live dispatch, converter,
   nested-operation, model, configuration, and loader objects;
5. invokes the real conversion dispatch and eventual loader entry point;
6. compares exact expected and observed identities and structures;
7. rejects shadow packages, editable installs, monkeypatches, forged identity
   bundles, incomplete closure, wrong ownership, and unadmitted loaders;
8. emits one aggregate fail-closed result.

Until that work lands and passes the required adversarial integration tests, the
research program is not finished and no later Q35Q or Agents-A1 phase may advance.
