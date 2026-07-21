# STEER ADDENDUM — Hardware Route Telemetry, Side-Channel, and Privacy Gates

Date: 2026-07-21
Status: binding; cumulative with `steer.md` and every more restrictive addendum
Scope: future MoE route monitoring, hardware-derived telemetry, safety auditing, privacy claims, and Agents-A1 scaling

## Why this addendum exists

`RouteScan: A Non-Intrusive Approach to Auditing MoE LLMs Safety via Expert Routing Telemetry` (arXiv:2605.24817v1) reports that request-level GPU execution telemetry can act as a proxy for MoE routing. The reported system uses active GPU-thread allocation during prefilling, derives per-expert load distributions and layer-level statistics, and trains a lightweight harmful-risk detector. The authors report AUROC above 0.93 on unseen harmful domains and above 0.96 under novel jailbreak wrappers on DeepSeek-V2-Lite-Chat and Qwen1.5-MoE-A2.7B-Chat across two NVIDIA GPU platforms.

This is not evidence of correctness prediction, latent error awareness, safe intervention, or Agents-A1 transfer. It is evidence that a useful MoE monitoring signal may exist below the model API, in hardware and kernel execution traces.

The same architectural surface is also a privacy attack surface. `MoEcho: Exploiting Side-Channel Attacks to Compromise User Privacy in Mixture-of-Experts LLMs` (arXiv:2508.15036; CCS 2025) reports prompt inference, response reconstruction, visual inference, and visual reconstruction attacks using CPU cache/page channels and GPU performance-counter/TLB channels. Therefore, aggregate execution telemetry is neither semantically empty nor presumptively privacy-preserving.

No attributable public RouteScan implementation was found during this review. Its measurements and privacy claims remain external and unverified.

## Telemetry-class separation

Future work must distinguish at least four different signal classes:

1. **Direct router state** — router logits, selected experts, selected weights, margins, entropy, or token-level route paths.
2. **Executed-route aggregates** — per-expert token counts, expert-load histograms, occupancy, union size, or request-level route summaries derived inside the serving process.
3. **Hardware-proxy telemetry** — GPU thread activity, performance counters, kernel timing, memory transactions, cache/TLB behavior, page activity, or other execution traces used to infer routing behavior.
4. **Serving-state telemetry** — batch composition, queue state, KV pressure, expert placement, precision state, page residency, scheduler state, or topology variables that affect execution without necessarily encoding task semantics.

A result from one class may not be represented as a result from another. Agreement between hardware telemetry and route aggregates must be measured prospectively for the admitted runtime. A hardware proxy that fails to track the executed route under a changed kernel, topology, quantization, batch, or scheduler is not admitted route telemetry.

## Claim separation

The following claims are separate and require separate evidence:

1. The hardware signal predicts harmful prompt intent.
2. The hardware signal predicts unsafe model output.
3. The hardware signal predicts task correctness or eventual agent failure.
4. The hardware signal predicts route identity or expert workload.
5. The hardware signal supplies an auditable record resistant to provider tampering.
6. The hardware signal preserves user privacy better than content or internal-state monitoring.
7. A policy acting on the signal improves full-population utility and safety.

Passing one claim does not authorize another. Harmful-intent classification is not correctness prediction. Prefill auditing is not long-horizon trajectory monitoring. A detector that separates benchmark prompt classes does not establish detection before an irreversible tool action.

## Runtime and measurement provenance

Every hardware-telemetry experiment must freeze and bind:

- model and checkpoint identity;
- tokenizer, processor, prompt formatting, and sequence-length policy;
- quantization and dynamic-precision state;
- serving backend, compiler, kernel implementation, and kernel launch policy;
- GPU model, firmware, driver, CUDA/runtime, profiler, counter source, and sampling cadence;
- tensor, expert, pipeline, and data-parallel topology;
- expert placement, replication, paging, prefetch, and cache policy;
- batch size, batch composition, request ordering, scheduler, and concurrent tenants;
- prefill/decode boundary and aggregation window;
- raw-counter-to-feature transformation;
- feature selection, normalization, detector, calibration, and thresholds;
- telemetry access permissions, transport, retention, and audit-store identity.

Changes to any of these fields require recertification or an explicitly preregistered invariance test. Hardware-platform calibration is not transferable by default.

## Required nuisance controls

Before describing hardware route telemetry as semantic, safety, or correctness information, future studies must control or stratify at least:

- prompt length and token count;
- padding, truncation, packing, and batch position;
- task family, topic, language, modality, and template;
- benign discussion of harmful subjects versus malicious instruction;
- jailbreak wrapper, encoding, formatting, and tokenization;
- layer, expert count, top-k, occupancy, and load balance;
- batch composition and neighboring-request workload;
- KV pressure, page residency, cache state, and dynamic precision;
- expert placement, kernel version, GPU architecture, and clock/power state;
- queueing, concurrency, retries, cancellation, and preemption;
- tool phase, trajectory phase, and environment state for agent workloads.

Required negative controls include length-matched benign prompts, topic-matched benign and harmful pairs, shuffled expert labels preserving load, shuffled request labels within matched runtime strata, fixed-route or synthetic-load controls where safe, and serving-state-only predictors.

A signal that disappears after conditioning on prompt length, batch state, topology, or serving state must be classified as execution-state telemetry, not model-internal semantic or correctness information.

## Privacy and side-channel gate

The phrase `non-intrusive` may refer only to whether model code or user content is directly read. It must not imply low privacy risk, low overhead, low privilege, or absence of a side channel.

Before any hardware-derived telemetry leaves the admitted execution boundary, require a frozen threat model covering:

- trusted operator, external auditor, malicious auditor, compromised collector, and malicious co-tenant;
- direct counter access, profiler access, shared-library access, same-GPU access, same-host access, and remote timing access;
- repeated observations of the same user, task, template, or trajectory;
- known-profile and chosen-prompt attacks;
- prompt-class, topic, language, tool, user, tenant, and sensitive-attribute inference;
- prompt and response reconstruction;
- membership, linkage, and re-identification attacks;
- cross-request and cross-tenant leakage;
- covert channels and intentional route encoding;
- model, architecture, expert-placement, and workload fingerprinting.

Exact-text inversion failure under one attacker is insufficient to establish privacy. Privacy evaluation must report the strongest admitted attacker, attack training data, auxiliary information, query budget, repeated-observation budget, target attributes, reconstruction metric, and confidence interval.

A telemetry stream cannot be described as privacy-preserving merely because it is aggregated. RouteScan-style useful discrimination and MoEcho-style leakage are two uses of the same input-dependent execution surface. Utility itself is evidence that the signal carries semantic information and therefore triggers privacy review.

Raw request-level counter traces, expert-load vectors, route paths, prompts, outputs, token IDs, hidden states, Jacobians, tenant identifiers, verifier labels, and attack reconstructions must not be committed to this public repository. Public records remain aggregate-only.

## Auditor integrity and least privilege

A hardware auditing channel is a separate production subsystem and requires:

- least-privilege counter access;
- authenticated, integrity-protected telemetry transport;
- replay and omission detection;
- collector and auditor artifact identity;
- bounded retention and access logging;
- tenant isolation;
- fail-closed handling of missing, malformed, delayed, or inconsistent telemetry;
- explicit behavior when counters are unavailable or virtualized;
- independent tests for provider forgery, selective reporting, and calibration drift.

Hardware-backed does not automatically mean tamper-proof. A provider-controlled collector, scheduler, kernel, or aggregation layer can still manipulate or omit evidence. Claims of objective auditing require a separately admitted integrity design.

## Minimum comparator stack

For a compatible safety-auditing study, compare at equal decision boundaries and full cost:

1. prompt and metadata baselines;
2. deterministic policy and schema checks;
3. content classifier or external guard model where privacy policy permits;
4. logits, confidence, entropy, and output features;
5. passive hidden-state features;
6. direct executed-route aggregates;
7. hardware-proxy telemetry;
8. combinations of hardware, route, and cheaper signals;
9. Jacobian-Lens or other derivative features only after exact derivative admission.

Hardware telemetry must show incremental value over direct route aggregates to justify its additional side-channel surface. Direct route aggregates must show incremental value over cheaper external and forward-only baselines before Jacobian-scale instrumentation is considered.

Privacy comparisons must use matched threat models. Comparing a restricted hardware attacker against an unrestricted content reader does not establish an intrinsic privacy advantage.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q production-path provenance and exact forward/VJP/JVP/finite-difference admission on one frozen static runtime.
2. Establish external checks, metadata, confidence, peer-representation, hidden-state, trajectory, and minimal direct-route baselines.
3. On the separately admitted Agents-A1-4B dense sibling, establish the same non-route safety and correctness baselines.
4. For Agents-A1-35B, measure request-level executed-route aggregates at frozen boundaries and fixed serving topology.
5. Only if direct route aggregates are useful, evaluate hardware-proxy telemetry as a lower-access or independent-audit channel.
6. Prove proxy-to-route agreement, calibration, and stability across admitted hardware and runtime strata.
7. Run the full privacy and malicious-auditor threat model before any telemetry export.
8. Evaluate residual safety or correctness value after prompt length, topic, batch, topology, precision, and serving-state controls.
9. Add sparse-feature, transcoder, or Jacobian-Lens streams only after cheaper signals fail the incremental-value gate.
10. Keep alarm, block, retry, escalation, abort, truncation, expert intervention, routing changes, and production enforcement under separate policy gates.

Hardware telemetry is optional. If it cannot satisfy privacy, tenant-isolation, provenance, and cross-runtime stability gates, the branch terminates and the admitted direct-route or forward-only path remains the maximum allowed instrumentation.

## Active blocker unchanged

This addendum does not advance Q35Q and does not authorize weights, model execution, GPU work, telemetry capture, sealed evaluation, intervention, or production use.

The active blocker remains production-path upstream/runtime provenance composition:

1. bind the live import to its owning installed distribution and `RECORD`;
2. derive complete live source closure for dispatch, converters, nested operations, model/configuration classes, and loader objects;
3. reject shadow packages, editable installs, and monkeypatching in a clean subprocess;
4. invoke and bind the actual GPTQModel/Defuser loader entry point;
5. freeze the complete immutable runtime tuple;
6. pass the full adversarial integration conjunction;
7. emit only the permitted aggregate result.

## Established

- MoE routing can leave measurable hardware execution footprints.
- RouteScan reports harmful-risk discrimination from prefilling GPU thread-allocation telemetry on two small open MoE models and two GPU platforms.
- MoEcho demonstrates that related CPU and GPU execution channels can leak prompt, response, and visual information under stronger attack models.
- Hardware-proxy telemetry is scientifically and operationally distinct from direct router state and executed-route aggregates.
- A useful hardware audit signal is not presumptively private.
- Hardware telemetry, side-channel, auditor-integrity, nuisance-control, and matched-threat-model gates are now binding.

## Unproven

- Independent RouteScan reproduction or a public attributable implementation.
- RouteScan transfer to Qwen3.5/Qwen3.6 MoE or Agents-A1.
- Correctness or long-horizon agent-failure prediction from prefilling hardware telemetry.
- Privacy under malicious auditors, co-tenants, repeated observations, known-profile attacks, or stronger inversion models.
- Tamper-resistant provider-to-auditor evidence.
- Stable calibration across kernels, hardware, topology, batching, dynamic precision, and serving drift.
- Incremental hardware-telemetry value over direct route aggregates and cheaper baselines.
- Q35Q provenance, strict loading, tensor consumption, expert ordering, or derivative admission.
- Safe online intervention or production deployment.
