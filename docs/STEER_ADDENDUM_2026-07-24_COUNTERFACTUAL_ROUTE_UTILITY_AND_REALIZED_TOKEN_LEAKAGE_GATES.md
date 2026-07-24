# STEER ADDENDUM — Counterfactual route utility and realized-token leakage gates

Date: 2026-07-24

Status: binding protocol addendum. This file does not reopen M38E, advance Q35Q,
authorize weight staging, model execution, GPU use, hidden-state or router capture,
Jacobian fitting, sealed evaluation, intervention, or production deployment. It
weakens no privacy, sealed-data, verifier, provenance, exact-gradient, parity,
resource, production, or stop rule.

## Program state remains unchanged

- M38E remains terminally closed as `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active milestone remains production-path upstream/runtime provenance
  composition.
- GitHub reports this repository as public. Commits remain aggregate-only and may
  contain no prompts, outputs, token IDs, per-example routes, hidden states,
  Jacobians, sealed labels, verifier traces, or reconstruction artifacts.
- No runtime pin is advanced by this addendum.

## Material public evidence

The public preprint **When Are Experts Misrouted? Counterfactual Routing Analysis
in Mixture-of-Experts Language Models**, arXiv `2605.07260v1` dated 2026-05-08,
compares each executed top-k route with sampled equal-compute alternative expert
sets for the same token while holding the model fixed.

The reported analysis uses verified-correct, self-generated reasoning trajectories.
For each analyzed token and layer, it samples 32 alternative top-k routes from the
32 highest-scoring experts and scores each route by the probability assigned to the
realized next token after a single route substitution. Reported findings include:

1. On high-confidence tokens, the executed route is often close to the best sampled
   route and route choice has little observed probability consequence.
2. On ambiguous and fragile tokens, the executed route ranks poorly among sampled
   equal-compute alternatives and the best sampled route assigns substantially
   higher probability to the realized token.
3. The qualitative pattern is reported across Qwen3-30B-A3B, GPT-OSS-20B,
   DeepSeek-V2-Lite, and OLMoE-1B-7B, across multiple layers and reasoning or
   knowledge benchmarks.
4. A final-layer router-only update, with experts and all other routers frozen,
   reportedly changes pass@K on AIME and HMMT for Qwen3-30B-A3B and GPT-OSS-20B.

No attributable immutable public implementation was located during this review.
These are external author-reported results, not admitted jLens findings.

The evidence materially changes the future route-telemetry comparator set. Route
identity, margin, entropy, ancestry, and semantic content do not directly measure
whether the executed route was useful relative to equal-compute alternatives.
Counterfactual route utility is a distinct object.

## Binding claim separation

Future MoE studies must distinguish at least the following claims:

1. **Route observability:** the executed expert identities, weights, margins, or
   paths can be captured reproducibly.
2. **Route predictability:** route choices can be predicted from token, hidden-state,
   ancestry, semantic, or serving-state variables.
3. **Route association:** executed-route features correlate with an objective
   outcome.
4. **Local counterfactual route utility:** another equal-compute route changes a
   frozen local scoring target at one token or layer.
5. **Full-continuation route utility:** a route substitution improves the resulting
   continuation or independently scored task outcome.
6. **Router regret prediction:** a prospective signal predicts that the executed
   route is worse than available alternatives before the target continuation is
   observed.
7. **Router adaptation:** router parameters are modified using a frozen training
   procedure.
8. **Online route intervention:** execution selects, substitutes, skips, or forces
   experts during generation.
9. **Objective monitor value:** route-derived features add sealed objective-outcome
   information over every cheaper admitted baseline.
10. **Policy utility:** a route-based controller improves outcomes under equal-cost,
    calibrated, privacy-preserving, fail-closed evaluation.

Passing one claim does not establish another. In particular:

- A route that improves realized-next-token probability is not thereby the unique,
  globally optimal, safe, or task-improving route.
- Poor rank under sampled alternatives is not proof that the router caused an
  eventual task failure.
- A router-only adapted model is a new artifact, not passive telemetry from the
  original checkpoint.
- An online forced-route controller is an intervention, not an interpretability
  measurement.

## Realized-token and successful-trajectory leakage boundary

Scoring route alternatives by probability assigned to the realized next token uses
information unavailable at the pre-token decision boundary. Restricting analysis to
verified-correct trajectories additionally conditions on future success.

Therefore, realized-token route utility is **retrospective oracle analysis** by
default. It may establish local compatibility with one observed successful path. It
may not be represented as:

- prospective route-regret prediction;
- online error detection;
- evidence that the route would improve an unknown continuation;
- natural-population routing quality;
- objective correctness awareness;
- safe route intervention.

Future studies must freeze and report:

1. Whether the target token is generated by the same model and router, a reference
   solution, a human annotation, or another model.
2. Whether analyzed trajectories are correct-only, incorrect-only, mixed, or
   prevalence-matched.
3. The verification rule and whether verification selected the trajectory before
   route analysis.
4. The exact token boundary at which the target becomes available.
5. Whether the candidate route pool, layer, token positions, confidence bins, or
   metrics were selected after viewing target outcomes.
6. Results on full-population trajectories, not only retained successful paths.
7. Separate correct and incorrect trajectory analyses with task-clustered
   uncertainty.
8. A prospective training/validation/sealed split in which no realized token or
   future outcome from validation or sealed tasks influences feature, route,
   candidate-pool, layer, or threshold selection.

Any signal constructed with the realized future token, verified final answer,
future trajectory, or sealed outcome is prohibited from online or prospective
claims unless that information is independently available at the stated decision
boundary.

## Candidate-route coverage and search-identifiability gate

The best sampled route is a property of the search procedure, not necessarily the
best equal-compute route in the model.

Every counterfactual route study must freeze:

- model and checkpoint identity;
- layer and token positions;
- total and active expert counts;
- shared-expert treatment;
- expert candidate-pool construction;
- pool size;
- number of sampled alternatives;
- random-number generator and seeds;
- sampling distribution and temperature;
- top-k cardinality and gate-weight recomputation;
- whether expert ordering is material;
- quantization, kernel, topology, batching, cache, and serving state;
- local versus full-continuation recomputation boundary;
- scorer, verifier, and objective-outcome rule.

Required sensitivity analysis includes, where computationally feasible:

1. Multiple candidate-pool sizes.
2. Multiple route-sample counts and seeds.
3. Uniform, router-proportional, Gumbel, single-swap, and structured alternatives.
4. Exact enumeration on small-expert fixtures.
5. Standard route, random route, score-matched route, and frequency-matched route
   controls.
6. Expert permutations preserving marginal frequency.
7. Route alternatives differing by one expert versus complete expert-set changes.
8. Confidence intervals over tasks and route-search randomness.
9. Search saturation curves showing whether the estimated regret continues to
   grow as more alternatives are evaluated.
10. Explicit classification of `best_sampled_route`, never `best_route`, unless
    exhaustive equivalence is proven.

A low executed-route rank under a narrow, target-conditioned candidate search does
not establish global router failure.

## Local proxy versus full-path outcome gate

Single-token probability under teacher-forced continuation is a local proxy. It can
miss or misrepresent:

- alternative valid tokens or equivalent reasoning paths;
- downstream self-correction;
- future route changes caused by the substituted activation;
- KV-state and hidden-state lineage changes;
- tool calls, structured outputs, or multimodal actions;
- task-level correctness, safety, calibration, and cost;
- beneficial diversity that lowers the probability of the observed token while
  improving another valid continuation.

Future work must report local and full-path endpoints separately. Where route
substitution is executed beyond a single teacher-forced token, required reporting
includes:

1. Exact next-token and top-k distribution changes.
2. Future hidden-state, KV-state, and route divergence.
3. Complete generated-continuation outcomes under matched decoding seeds.
4. Objective task success and failure severity.
5. Verifier acceptance and independent objective validity separately.
6. Retry, repair, truncation, and token-cost changes.
7. p50, p95, and p99 latency and memory effects.
8. Whether the substituted route changes later expert occupancy, capacity pressure,
   cross-request scheduling, or another request's behavior.

A local probability improvement may be described only as local target compatibility
unless full-continuation and objective-outcome gains are separately established.

## Mandatory counterfactual routing comparators

After runtime, route-capture, and privacy admission, compatible Agents-A1-35B route
studies must include the following comparator families before claiming privileged
router-monitor value:

1. Executed route identity, weights, margins, entropy, occupancy, and ancestry.
2. Hidden-state, token, semantic, trajectory-phase, confidence, and serving-state
   controls at the same boundary.
3. Parent-route and route-transition predictors.
4. Sampled equal-compute local route-regret statistics on training-only and
   validation populations where computationally feasible.
5. Prospective predictors of route regret that do not consume the future realized
   token or outcome.
6. Random, frequency-matched, score-matched, and single-expert-swap controls.
7. Direct hidden-state and dense-sibling predictors of the same target.
8. External deterministic and verifier signals.
9. Sparse-feature or transcoder predictors when separately admitted.
10. Jacobian-Lens features only after exact derivative parity and only for sealed
    incremental value over the complete cheaper stack.

Counterfactual route-regret computation is not required as an online production
feature. It is a training-time or audit-time diagnostic and comparator. Its compute,
storage, replay, privacy, and intervention costs must be charged in full.

## Router-only adaptation and intervention boundary

A router-only update changes model behavior and creates a new adapted artifact even
when it modifies less than 0.001% of model parameters.

Future router adaptation must separately freeze and admit:

- base checkpoint and complete runtime;
- adapted router layers and parameter bytes;
- candidate-route generation and preference labels;
- loss, optimizer, schedule, seed, and stopping rule;
- training, calibration, certification, and sealed populations;
- full-model output, route, safety, calibration, and cost regression tests;
- artifact digest and rollback path.

Required equal-cost comparisons include:

1. Unmodified router.
2. Router-only adaptation.
3. Confidence or entropy-based compute allocation.
4. Additional sampling or self-consistency.
5. External verifier-guided selection.
6. Direct hidden-state sidecar prediction.
7. Online forced-route selection where separately authorized.
8. No-intervention and random-intervention controls.

Router adaptation, forced routing, expert skipping, expert substitution, retries,
early exit, truncation, and activation steering remain separately gated. A better
pass@K curve does not by itself establish safer, calibrated, or production-worthy
routing.

## Agents-A1 scaling directive

The technically credible sequence is now:

1. Complete Q35Q production-path provenance composition.
2. Prove strict packed-tensor consumption, expert ordering, forward parity, VJP
   parity, JVP parity, and finite-difference parity.
3. Separately admit Agents-A1-4B and establish deterministic, metadata, confidence,
   self-judgement, hidden-state, trajectory, program-state, and external-verifier
   baselines.
4. Freeze matched task families, objective outcomes, token and action boundaries,
   and irreversible-action definitions.
5. Separately admit Agents-A1-35B route capture under exact topology, cache,
   precision, batching, and privacy controls.
6. Establish executed-route, ancestry, semantic, occupancy, and serving-state
   baselines.
7. Run bounded retrospective counterfactual route audits on training-only and
   validation tasks, explicitly labeled as target-conditioned oracle analysis.
8. Train prospective route-regret predictors without future-token or future-outcome
   leakage and test them on family-disjoint validation.
9. Require route-regret features to add sealed objective-outcome value beyond the
   complete Agents-A1-4B, hidden-state, trajectory, confidence, and external-checker
   stack.
10. Add sparse-feature or transcoder comparators.
11. Add Agents-A1-35B Jacobian-Lens features only after exact derivative parity and
    sealed incremental value over all cheaper comparators, including prospective
    route-regret prediction.
12. Keep router adaptation and online route intervention under separate artifact,
    control-policy, safety, and production gates.

Counterfactual route analysis is a plausible bridge from passive telemetry to a
mechanistic test of whether route choice matters. It is not authorization to alter
Agents-A1 routing.

## Privacy, sealed-data, and repository boundary

Counterfactual route audits multiply sensitive observations by evaluating many
expert combinations for one token. The resulting route utilities can increase
prompt, token, task, outcome, or model-behavior reconstructability.

The following remain prohibited from this public repository:

- prompts, outputs, token IDs, per-token confidence bins, or target tokens;
- per-example executed or alternative route sets;
- per-route probabilities, losses, hidden states, KV states, or Jacobians;
- per-example verifier labels or objective outcomes;
- candidate-pool contents and reconstruction artifacts tied to private tasks.

Only preregistered aggregate results may be committed after the existing privacy,
sealed-data, membership, reconstruction, covert-channel, retention, and external
telemetry-store gates pass.

## Current blocker and execution order

This addendum does not change the immediate blocker. The next admissible repository
progress remains one clean-subprocess, CPU-only, fail-closed production adapter
that:

1. verifies the frozen upstream Transformers artifact;
2. derives expected source identities from that artifact;
3. binds the live import to its owning installed distribution and `RECORD`;
4. derives complete live-object source closure from the actual dispatch,
   converters, nested operations, model/configuration classes, and loader objects;
5. invokes and binds the real GPTQModel/Defuser loader entry point;
6. rejects shadow packages, editable installs, monkeypatches, forged identities,
   incomplete closure, wrong ownership, and unadmitted loaders;
7. freezes the exact immutable runtime tuple;
8. passes the complete adversarial integration conjunction; and
9. emits only the permitted aggregate fail-closed result.

After that remain packer-independent fixture validation, strict tensor consumption
and expert ordering, forward/VJP/JVP/finite-difference parity, Q35Q Phase-0
admission, weight staging, and a separately authorized GPU transition.

## Established versus unproven

Established only as external public evidence:

- Equal-compute alternative routes can assign materially different probability to
  the same realized token.
- The executed top-k route can rank poorly among sampled alternatives on reported
  low-confidence tokens.
- This reported pattern appears across several open MoE model families.
- A router-only adaptation can change downstream pass@K in the reported settings.
- Counterfactual route utility is distinct from route identity, ancestry, semantic
  predictability, and ordinary confidence.

Unproven for this program:

- Independent reproduction of arXiv `2605.07260v1`.
- Exhaustive or globally optimal alternative-route identification.
- Natural-population routing regret on incorrect and mixed trajectories.
- Prospective route-regret prediction without realized-token leakage.
- Full-continuation or objective-outcome benefit from locally better routes.
- Transfer to Qwen3.5/Qwen3.6 MoE or either Agents-A1 checkpoint.
- Incremental route-regret, router, or Jacobian-Lens value over every cheaper
  comparator.
- Complete Q35Q provenance, strict loading, forward parity, or derivative admission.
- Safe router adaptation, forced routing, expert substitution, early exit, retry,
  repair, truncation, activation steering, or production deployment.

The research program remains unfinished.
