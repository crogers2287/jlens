# STEER ADDENDUM — Experience-memory termination and contamination gates

Date: 2026-07-18

Status: binding protocol addendum. This file does not reopen M38E, advance Q35Q, authorize scientific execution, or weaken any privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, production, or stop rule.

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- No weight staging, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized.
- GitHub currently reports this repository as public. Commits remain restricted to aggregate program-control records and public-source engineering code or tests.

## New public evidence

The ACL 2026 Findings paper **EET: Experience-Driven Early Termination for Cost-Efficient Software Engineering Agents** evaluates an external-memory early-termination system on SWE-bench Verified across Agentless, Mini-SWE-Agent, and Trae Agent with GPT-5-mini and DeepSeek-V3.2 backends.

The associated public implementation was inspected at immutable commit:

`91d9936afaaead424c0f5ce90880905cfa81adf4`

Bounded public findings include:

1. EET constructs structured experience objects from historical issue-resolution trajectories and successful outcomes.
2. It retrieves one similar experience using TF-IDF and injects it into patch-generation or patch-selection workflows.
3. It uses model-produced confidence with fixed reported thresholds, including approximately 90 for confident termination and approximately 40 for low-confidence difficulty termination.
4. The paper reports 19.3%–55.1% total-cost reduction, 31.8% on average, with resolution-rate change no worse than -0.2 percentage points across its six agent-model configurations.
5. The paper reports a 50-issue cross-repository subset with unchanged 14% resolution and a 24.4% cost reduction.
6. Experience-generation cost is reported separately and amortized rather than included in per-task headline cost.
7. The study is limited to SWE-bench Verified and depends on historical experience; cold-start and non-programming transfer remain open.

These are external public results, not admitted results of this repository. They establish neither Agents-A1 transfer nor internal correctness awareness. They do establish that external experience retrieval is a credible, potentially cheaper comparator for agent termination and routing policies.

## Binding comparator correction

Future Agents-A1 monitoring work must compare internal telemetry against an external-memory baseline when historical trajectories are available.

The comparator stack must distinguish at least:

1. No memory and no internal monitor.
2. Metadata-only history.
3. Raw-trajectory retrieval.
4. Structured-experience retrieval without early termination.
5. Structured-experience retrieval with confidence-only termination.
6. Decision-boundary hidden-state monitoring without memory.
7. Router-path monitoring without memory.
8. Jacobian-Lens monitoring without memory.
9. Frozen combinations of memory and internal telemetry.

A Jacobian, router, or hidden-state monitor cannot be described as operationally necessary when a cheaper frozen experience-memory policy provides equal sealed utility under equal-cost accounting.

External-memory benefit and internal-state benefit must be reported separately. Improvement from their combination does not establish that both components contribute independently.

## Experience-base provenance

Every experience object used in training, validation, certification, or sealed evaluation must have an immutable provenance record covering, where applicable:

- source benchmark, repository, issue, pull request, and source commit;
- agent and backbone identities;
- generation settings and tool environment;
- trajectory identity and capture time;
- success or failure determination and verifier identity;
- summarizer or judge model, prompt identity, decoding settings, and software version;
- fields retained, discarded, or transformed;
- retrieval representation and index identity;
- confidence-generation procedure;
- threshold, ranking, and tie-breaking rules;
- deletion, retention, and refresh policy.

Caller-supplied prose summaries without immutable source linkage are inadmissible as scientific experience records.

Experience objects derived from sealed examples, sealed labels, hidden tests, future trajectory outcomes, or post-decision verifier information may not enter monitor features, retrieval indexes, threshold tuning, policy selection, or calibration.

## Contamination and near-duplicate controls

Removing exact issue-ID overlap is insufficient.

Before any experience-memory comparison, perform training-only and independently audited decontamination across:

- exact issue and pull-request identity;
- repository and fork lineage;
- source commit and patch ancestry;
- duplicate or cherry-picked patches;
- issue title and description paraphrases;
- stack traces, exception messages, test names, function names, and API symbols;
- shared benchmark templates;
- repeated bug families and generated variants;
- upstream/downstream package mirrors;
- semantically equivalent fixes across repositories;
- public solution text, patch discussions, or derived summaries.

Cross-repository evaluation does not by itself establish non-memorization. Different repositories can share copied code, common dependencies, duplicate defects, benchmark templates, or semantically identical fixes.

Required reporting includes exact-match, normalized-match, semantic-neighbor, code-clone, patch-similarity, and repository-lineage audit results. Any uncertain overlap must be quarantined from the primary sealed claim.

## Success-only memory bias

A memory containing only successful trajectories changes the task from neutral monitoring to retrieval from a positively selected archive.

Future studies must report separately:

- success-only experience bases;
- outcome-balanced or outcome-stratified bases;
- retrieval without outcome fields;
- retrieval with confidence fields removed;
- matched negative or misleading experiences;
- irrelevant but lexically similar experiences;
- contradictory experiences;
- no-retrieval conditions.

A confidence score produced retrospectively from a successful trajectory is not a calibrated online probability of current-task success without independent prospective validation.

## Decision-time and outcome-time separation

Experience-guided control must identify the exact boundary at which a decision is made:

1. Before any action generation.
2. During action generation.
3. After a candidate action is generated but before execution.
4. After tool execution.
5. After a patch is generated.
6. During patch selection.
7. After tests or verifier output.
8. Retrospective replay.

Savings may be credited only for work that occurs after the actual decision boundary and would otherwise have been executed.

A patch-selection termination policy is not an early token-exit result. A post-test confidence judgment is not a verifier-blind monitor. A policy using completed patch content or test feedback must be evaluated as a downstream workflow controller, not as pre-error prediction.

## Threshold and model-selection gates

Similarity thresholds, top-k, experience schema, summarizer, confidence prompt, confidence thresholds, patch-generation limits, selection limits, retrieval method, and fallback behavior are model-selection choices.

They must be selected using training and validation data only, frozen before certification or sealed evaluation, and versioned as one policy artifact.

Required controls include:

- threshold sweeps reported only on non-sealed data;
- random-experience retrieval;
- similarity-matched wrong experiences;
- shuffled confidence values;
- confidence-only without retrieved content;
- retrieval-only without confidence termination;
- fixed turn or token budgets;
- task-difficulty and issue-type baselines;
- no-memory policies matched for additional context length and inference calls.

A failed sealed evaluation may not be used to revise the experience base, summarizer, thresholds, retrieval rules, or policy and then be reported as the same preregistered test.

## Full-population policy evaluation

Resolution rate and average cost are insufficient for safety or production claims.

Future experience-guided termination studies must report:

- right-to-wrong and wrong-to-right transitions relative to the no-memory baseline;
- correct patches discarded by low-confidence stopping;
- incorrect patches accepted by high-confidence stopping;
- malformed, empty, partial, or non-applying patches;
- tool failures and environment failures;
- verifier failures and flaky-test cases;
- unnecessary continuation and premature termination;
- performance by task family, difficulty, repository, issue type, tool state, and retrieval-similarity band;
- conditional outcomes when no experience clears the retrieval threshold;
- cold-start outcomes with an empty or nonmatching experience base;
- calibration and selective-risk curves for each termination action.

Policy utility must include the cost of false termination, incorrect acceptance, retries, fallback agents, and recovery from harmful actions.

## End-to-end and amortized cost accounting

Headline per-task savings must not exclude material system costs without explicit amortization.

Required accounting includes:

- historical trajectory generation;
- successful-patch verification;
- summarizer or judge inference;
- experience extraction and quality control;
- index construction and refresh;
- retrieval computation;
- injected-context tokens;
- confidence-estimation calls;
- storage, privacy filtering, and deletion;
- drift detection and recertification;
- failed retrievals and fallback execution;
- monitor and policy engineering cost where quantified;
- latency, accelerator time, memory, and throughput effects.

Report both marginal online cost and total amortized cost under explicit workload volumes. Include a break-even analysis showing the number and distribution of future tasks required to recover experience-generation and maintenance cost.

A one-time cost is not zero cost. Generated-token, API-price, latency, and accelerator-time savings are separate claims.

## Privacy and sealed-data boundary

Experience memories are compressed trajectory records and may retain issue text, code, tool outputs, patch content, user data, secrets, verifier information, or latent benchmark labels.

The existing public-repository boundary remains binding. Raw or summarized per-example experiences, issue descriptions, trajectories, patches, confidence rationales, retrieval neighbors, verifier results, and private repository identifiers may not be committed here.

Before any external experience store is authorized, require:

1. A frozen data inventory and threat model.
2. Secret, credential, personal-data, proprietary-code, and hidden-test filtering.
3. Membership, reconstruction, and nearest-neighbor disclosure tests.
4. Tenant and repository isolation.
5. Retention limits and deletion propagation.
6. Access logging and provenance-preserving redaction.
7. Aggregate-only scientific records in this repository.

Retrieval utility does not override privacy, sealed-data, or verifier-blindness rules.

## Agents-A1 scaling directive

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q runtime provenance and derivative admission.
2. Establish sealed metadata, confidence, and selected hidden-state baselines.
3. Establish an experience-free sequential abort or escalation baseline.
4. Build a training-only, provenance-bound external-memory comparator from admissible historical trajectories.
5. Evaluate no-memory, raw-memory, and structured-memory conditions under contamination and cold-start controls.
6. Add minimal route identity, margin, entropy, and parent-route innovation at frozen decision boundaries.
7. Compare memory-only, telemetry-only, and combined policies under equal end-to-end cost.
8. Add Jacobian-Lens features only after exact derivative parity and after cheaper memory and telemetry systems fail the frozen incremental-value gate.
9. Require family-, repository-, template-, and environment-disjoint sealed evaluation.
10. Keep abort, retry, escalation, tool selection, patch acceptance, forced routing, expert intervention, and activation steering under separate policy and safety gates.

This sequence tests whether historical experience solves the operational problem before authorizing expensive all-layer or derivative instrumentation.

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
11. Run sealed detection-only comparisons including the experience-memory gates above.
12. Begin Agents-A1-native instrumentation only if Q35Q establishes incremental monitor value.

## Established versus unproven

Established only as external public evidence:

- Structured historical experience can reduce reported SWE-bench agent cost in the evaluated EET configurations.
- Retrieval and confidence-guided termination can act at patch-generation and patch-selection boundaries.
- External memory is a credible comparator for internal monitoring.
- Experience quality, selection, contamination, cold start, and amortized cost are material confounds.

Unproven for this program:

- Independent reproduction of EET.
- Non-memorization under semantic, code-clone, patch, and benchmark-template decontamination.
- Calibrated prospective meaning of EET confidence scores.
- Transfer beyond SWE-bench software-engineering agents.
- Transfer to Agents-A1.
- Incremental value of hidden states, router telemetry, or Jacobian-Lens features over a frozen experience-memory policy.
- Safe early termination, patch acceptance, abort, retry, escalation, forced routing, expert intervention, steering, or production utility.
