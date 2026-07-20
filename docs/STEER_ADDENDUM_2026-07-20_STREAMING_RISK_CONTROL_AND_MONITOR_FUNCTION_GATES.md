# STEER ADDENDUM — streaming risk-control baseline and monitor-function separation gates

Date: 2026-07-20
Parent remote head: `9c7a2281b235e168457c452ad1c47a96934b27d2`

This is a binding future-protocol correction to `CODEX_AUTOSTEER.md`,
`steer.md`, and the cumulative post-consolidation addenda.

It changes the minimum comparator and certification requirements for any future
streaming error, safety, early-abort, truncation, escalation, retry, tool-use,
router-telemetry, semantic-workspace, hidden-state, or Jacobian-Lens monitor.
It does not change the active engineering milestone.

Q35Q remains `q35q_artifact_admission_blocked`. No weight staging,
tensor-payload retrieval, model execution, GPU execution, hidden-state capture,
router capture, Jacobian fitting, sealed scientific evaluation, intervention,
or production use is authorized by this document.

GitHub currently reports the repository as public. This addendum contains only
aggregate public-source program-control information. It does not authorize
committing prompts, outputs, token IDs, verifier labels, per-task predictions,
hidden states, router traces, Jacobians, weights, caches, credentials, private
logs, or local paths.

## External evidence and narrow interpretation

Schirmer et al., “Online Safety Monitoring for LLMs,” arXiv
`2607.02510v1`, submitted 2026-07-02, study a streaming monitor that observes a
per-step proxy safety signal and raises an alarm at the first threshold crossing.
The associated public implementation was inspected at immutable commit
`897e19a798bac59ef08a4d4dbc1c69cdea82286c` in `monasch/llm-monitor`.

The paper evaluates two threshold-calibration procedures:

1. conformal risk control (CRC), which controls expected risk over calibration
   draws under the stated exchangeability and monotonicity assumptions;
2. a high-probability upper-confidence-bound procedure using a
   Hoeffding-Bentkus bound.

The same frozen proxy streams are also evaluated with e-valuator sequential
hypothesis-testing baselines. On the authors’ MATH and harmfulness experiments,
the simple calibrated threshold monitors are reported as competitive with the
more complex e-valuator monitor functions and often raise successful alarms
earlier. The signal ablation reports that an external process-reward model is
substantially more powerful than generator token log-probability at matched
false-alarm rates.

The binding interpretation is narrow:

- this is evidence about a monitor function applied to a proxy stream, not
  evidence that any particular hidden-state, route, workspace, or Jacobian
  signal is informative;
- the reported statistical guarantees depend on the specified loss,
  calibration procedure, exchangeability assumptions, and the quality of the
  proxy signal;
- sequence-level correctness or harmfulness labels do not by themselves locate
  the first causally actionable error inside a trajectory;
- the experiments do not establish long-horizon agent monitoring, MoE-specific
  value, Agents-A1 transfer, adversarial robustness, or safe intervention;
- an external verifier can dominate cheaper internal signals while imposing a
  second-model execution cost at every scored boundary;
- a time-invariant threshold ignores temporal structure and may fail under
  model, task, horizon, verifier, or workload drift.

## Signal-versus-monitor-function separation

Every future online-monitor report must separate at least three components:

1. **signal construction** — external verifier score, logits, confidence,
   hidden-state readout, trajectory summary, route telemetry, semantic-workspace
   score, sparse feature, transcoder feature, or Jacobian-Lens feature;
2. **monitor function** — fixed threshold, risk-calibrated threshold,
   sequential test, temporal model, ensemble, or learned stopping policy;
3. **intervention policy** — alarm only, human review, retry, escalation,
   tool suppression, abort, truncation, or another action.

A stronger final policy does not establish that its internal signal is stronger
unless monitor functions and intervention rules are matched. A stronger signal
does not establish safe stopping unless the intervention study passes
separately.

Claims of incremental router, workspace, hidden-state, or Jacobian value must
report both:

- signal quality under a common frozen monitor function; and
- monitor-function quality using the same frozen signal stream.

No method may receive both a stronger signal and a stronger monitor function
while attributing the combined gain solely to the signal.

## Mandatory streaming monitor-function baselines

For each technically compatible frozen signal stream, evaluate at least:

1. a preregistered time-invariant threshold selected on tuning data only;
2. CRC when the target loss is monotone in the threshold and the stated
   assumptions are defensible;
3. a high-probability UCB threshold when a high-probability risk claim is made;
4. a sequential or temporally adaptive baseline when sufficient calibration
   coverage exists across the evaluated decision times;
5. random, prevalence-matched, fixed-boundary, and never-alarm controls.

All monitor functions must receive the same signal values at the same decision
boundaries, use the same calibration population, face the same missing-score and
finished-sequence rules, and trigger the same downstream action during matched
policy comparison.

If CRC, UCB, or a sequential guarantee is technically inapplicable, the report
must identify the failed assumption and downgrade the result to empirical
calibration. It may not retain guarantee language.

A learned temporal monitor must beat the simple risk-calibrated threshold at
matched false-alarm or missed-detection risk after including its training,
memory, latency, and serving cost. Model complexity alone is not evidence of a
better monitor.

## Partition and post-selection certification gate

Freeze separate populations for:

1. signal-model or probe training;
2. layer, feature, token-boundary, pooling, and aggregation selection;
3. monitor-function and threshold tuning;
4. risk calibration or post-selection certification;
5. final sealed evaluation.

A calibration or certification population may not be reused to train the signal,
select a layer, select a feature family, choose the monitored boundary, choose
between CRC/UCB/sequential methods, or repair a failed certificate.

All candidate signals and monitor functions considered during selection must be
included in multiplicity accounting. Reporting only the selected monitor after
searching many layers, thresholds, horizons, aggregations, or signal families is
prohibited.

## Dependence, exchangeability, and drift gate

Agent trajectories create dependence across steps, retries, branches, users,
task templates, environments, and repeated rollouts. Treating individual steps
as exchangeable calibration examples is prohibited unless that assumption is
established prospectively.

Calibration, confidence intervals, and certification must use the appropriate
independent unit, normally the complete task or episode, and must cluster by at
least task family, template, environment, user or tenant where applicable, and
repeated rollout source.

Report guarantee validity separately for:

- in-distribution exchangeable evaluation;
- family-disjoint and template-disjoint evaluation;
- horizon and trajectory-length shift;
- model, checkpoint, quantization, processor, harness, and decoding drift;
- verifier, tool, environment, and serving-topology drift;
- adversarially selected or adaptively retried trajectories.

When exchangeability or stationarity is not defensible, CRC or UCB results are
empirical baselines only. A bound calibrated on one generator, verifier, task
family, or horizon may not be transferred silently to another.

## Label and verifier binding

Every proxy and outcome label must be frozen by exact identity and information
boundary. Record the verifier model or executable checker, immutable revision,
processor, prompt, parsing rules, decision cadence, precision, runtime, and
failure handling.

External verifier scores must be treated as model outputs rather than ground
truth unless agreement with the canonical executable or benchmark outcome is
established. Report verifier-versus-canonical disagreement, verifier abstention,
timeout, malformed output, and unavailability.

The monitor may not consume the final outcome, later tool result, future token,
future hidden state, retry result, or verifier label that would not exist at the
claimed decision boundary. Offline prefix replay must be reported separately
from a single-pass online stream.

## Event-onset and detection-delay gate

Sequence-level eventual failure and first actionable failure are separate
labels. A monitor can flag a doomed trajectory before the final wrong answer
without locating the first error, and it can flag after the first error while
still appearing early relative to total sequence length.

Report at least:

- false-alarm risk on canonically safe episodes;
- missed-detection risk and power on canonically unsafe episodes;
- absolute tokens, steps, and wall-clock time to alarm;
- normalized delay as a fraction of the observed trajectory;
- delay from a preregistered independently labeled error-onset boundary when such
  a boundary is available;
- fraction of failures detected before any irreversible external action;
- fraction detected only after the harmful or incorrect action occurred;
- censoring, already-finished, zero-length, malformed, timeout, and
  verifier-unavailable cases.

Do not call a result causal localization or pre-error detection when only the
final sequence label is available.

## Full cost and privacy accounting

For every signal and monitor function, include:

- generator work before and after the alarm;
- external-verifier forward passes and scoring cadence;
- hidden-state, route, workspace, sparse-feature, or Jacobian capture;
- device transfer, synchronization, batching, cache retention, and replay;
- monitor training, calibration, certification, storage, and retraining;
- latency, accelerator-seconds, peak memory, interconnect traffic, and energy
  where measurable;
- failed alarms, missed detections, unnecessary escalation, discarded work, and
  fallback execution;
- privacy exposure, retention window, reconstruction risk, membership-inference
  risk, and access-control surface.

A simple threshold has low decision overhead but does not make an expensive
verifier or internal capture path cheap. A weaker internal signal is not the
preferred production option merely because its score is already available.
Compare complete risk-cost frontiers.

No full raw trajectory retention is implied or authorized. Use bounded online
summaries and aggregate-only reporting under the existing privacy and sealed-data
rules.

## Detection-before-intervention boundary

This addendum authorizes no stopping or control action.

An alarm is a detection output. Abort, truncation, retry, escalation, human
review, tool suppression, expert skipping, forced routing, activation steering,
or production deployment remains a separately preregistered intervention.

Before any intervention study:

1. freeze the signal, monitor function, calibration artifact, threshold, and
   decision cadence;
2. pass sealed family-disjoint detection and risk-control evaluation;
3. establish incremental value over cheaper signals under the same simple
   monitor-function baseline;
4. define allowed actions, fallback identities, verifier behavior, rollback, and
   production disposition;
5. report right-to-wrong and wrong-to-right transitions and irreversible harms.

## Agents-A1 scaling consequence

For Agents-A1 or a comparable large MoE, the first online-control study must not
begin with a learned router-telemetry or Jacobian stopping policy.

At matched decision boundaries, construct frozen streams for the cheapest
available signals first:

1. deterministic schema, permission, provenance, ordering, and relational
   checks;
2. action, tool, finish, latency, modality, and trajectory metadata;
3. calibrated logits, entropy, margins, and confidence;
4. external verifier or process-reward scores when technically and economically
   feasible;
5. selected decision-boundary hidden-state and bounded trajectory readouts;
6. matched testing on the separately admitted Agents-A1-4B dense sibling;
7. minimal route identity, weight, margin, entropy, occupancy, and path summaries
   on Agents-A1-35B;
8. sparse-feature or transcoder streams;
9. Jacobian-Lens streams only after exact derivative parity and bounded capture
   cost.

Apply the mandatory simple threshold, CRC/UCB where valid, and temporal baselines
to each candidate stream. Router or Jacobian features must demonstrate sealed
incremental signal value after conditioning on the cheaper streams and must also
show that any complex temporal monitor beats a risk-calibrated threshold on the
same signal.

Effects shared by Agents-A1-4B and Agents-A1-35B are general task, agent-family,
or representation evidence. Route-only incremental value remains MoE-specific
and must pass all existing occupancy, ancestry, semantic, topology, expert
identity, and serving-cost controls.

This ordering does not reduce the Q35Q provenance, strict-loading, forward,
derivative-parity, privacy, verifier, or production gates.

## Program status after this addendum

Established from the inspected public sources:

- a simple first-threshold-crossing monitor can be calibrated for expected or
  high-probability risk under the paper’s stated assumptions;
- on the authors’ tested proxy streams, simple CRC/UCB monitors are reported as
  competitive with more complex sequential e-valuator monitor functions and
  often detect successful alarms earlier;
- signal quality can dominate monitor-function complexity: the reported external
  process-reward signal is substantially stronger than token log-probability at
  matched false-alarm rates;
- signal construction, monitor function, and intervention policy are distinct
  scientific objects and are now bindingly separated in future jLens studies;
- risk-calibrated simple streaming thresholds are mandatory future comparator
  monitor functions when technically applicable.

Unproven:

- independent reproduction of the paper’s reported results;
- validity of exchangeability and stationarity assumptions on long-horizon agent
  episodes, repeated rollouts, adaptive retries, or production workloads;
- robust risk control under model, verifier, task, harness, horizon, or topology
  drift;
- reliable error-onset localization from sequence-level labels;
- usefulness of cheap internal signals on Agents-A1;
- incremental route or Jacobian signal value after matched monitor-function and
  cheaper-signal controls;
- safe abort, truncation, retry, escalation, tool suppression, expert
  intervention, activation steering, or production deployment.

## Active blocker remains unchanged

The next admissible engineering progress remains one clean-subprocess,
fail-closed production adapter that verifies the frozen upstream Transformers
artifact, binds the live import to its owning installed distribution and complete
source closure, invokes the actual dispatch and GPTQModel/Defuser loader entry,
rejects shadowing/editable-install/monkeypatch/identity-forgery failures, freezes
the immutable runtime tuple, passes the adversarial integration conjunction, and
emits only the permitted aggregate result.

Until that work lands and passes, Q35Q remains
`q35q_artifact_admission_blocked`; the research program is not finished and no
later Q35Q or Agents-A1 phase may advance.
