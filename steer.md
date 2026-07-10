# steer.md — M32R Agents-A1 counterfactual expert routing

M1 through M31 are complete. Do not redo the M30 decisive detector test or the
M31 naive-resample intervention study. The M27/M29/M30 holdouts and M31 task
set are spent as decision targets.

`CODEX_AUTOSTEER.md` remains the operating contract. The detailed operator
protocol for the current loop is:

`docs/M32R_AGENTS_A1_COUNTERFACTUAL_ROUTING_AUTOLOOP.md`

Read it in full before implementation.

## Supersession notice

The previously committed M32 structured-repair preregistration
`data/prompts/m32_repair_manifest.json` was never executed. It is preserved as
a historical artifact but is superseded **before any generation or capture**.
Do not delete it, edit its claim rules, run it, or report it as completed.

The current milestone is **M32R**, not the abandoned structured-repair bakeoff.

## Operator decision

The operator directs jlens hard toward causal expert-routing research:

- keep Agents-A1 as the base model;
- use an official Hugging Face safetensors checkpoint that fits the 48 GiB dual
  RTX 3090 pool under the protocol resource gate;
- determine whether telemetry-triggered failures are caused partly by poor
  token/layer expert choices;
- test equal-compute counterfactual routes;
- prefer dynamic, local rerouting or soft penalties over permanent expert
  shutdown;
- continue in a bounded autoloop only when preregistered results justify it.

The operator authorizes up to three milestone completions beginning with M32R,
subject to the normal four-hour and blocker limits. Use separate implementation
and steer commits for every milestone.

## Approved Agents-A1 model sources

Approved official identities:

1. `InternScience/Agents-A1`
   - official BF16 safetensors;
   - preferred research plan: runtime NF4 through the existing
     `qwen3_5_moe`/bitsandbytes path, router-only capture, short text contexts.
2. `InternScience/Agents-A1-FP8`
   - official compressed-tensors FP8 safetensors;
   - feasibility candidate only on RTX 3090/Ampere;
   - use only if the installed stack loads it without dequantizing past the
     memory ceiling and preserves router intervention hooks.

Hard memory ceiling: combined allocated/reserved GPU memory <= 44 GiB, leaving
at least 4 GiB headroom. No weights, caches, or local model paths may be
committed. If neither path passes the memory/hook gate, stop and report rather
than changing model families.

The current Q8 GGUF remains the practical Agents-A1 runtime, but it cannot be
the research backend for this milestone because it does not expose
controllable per-layer expert routes.

## Current evidence

### M30 — detector increment established

- Powered n=192 once-read holdout: full telemetry .917 vs metadata .818.
- Paired delta accuracy +.099 with 95% CI [+.042,+.156].
- The signal is distributed; window entropy alone is insufficient.

### M31 — trigger works; naive repair does not

- Frozen trigger found genuine failures with about 89% precision on fresh data.
- A temperature-0.7 resample rescued only about 4.5% of correctly triggered
  failures.
- Telemetry gating was the only non-losing policy.

### New routing hypothesis

A systematic failure may not mean every expert lacks the capability. The router
may choose a poor top-8 combination at one or more fragile tokens/layers. M32R
must distinguish:

- model-capacity failure: tested equal-compute alternatives also fail;
- router-reachable failure: another expert route inside the frozen model
  succeeds;
- deployable rerouting: telemetry/router-only features can choose that better
  route without seeing the answer.

## Important interpretation boundary

Do not claim that an individual expert has its own entropy or globally
“wobbles.” Router entropy is uncertainty over a route. Agents-A1 has layer-local
experts, and the same expert can help one token while hurting another.

The causal unit is a layer-expert-token choice. No global expert blacklist or
hard shutdown is permitted from observational failure rates.

## M32R — current milestone

Execute the M32R section of the detailed protocol.

Core requirements:

1. **Feasibility first**
   - load an approved Agents-A1 safetensors path under the 44 GiB ceiling;
   - verify `qwen3_5_moe`, 40 text layers, 256 experts, top-8 routing;
   - verify real decode router logits;
   - implement an opt-in route override whose disabled path is unchanged;
   - preserve exactly eight active experts and renormalize weights.
2. **Preregister before decision capture**
   - 192 fresh tasks across the six existing bands;
   - deterministic disjointness from M29/M30/M31 and the abandoned M32 set;
   - 96 discovery / 48 validation / 48 sealed holdout;
   - frozen trigger, fragile-window rule, layer rule, route families, branch
     budgets, seeds, metrics, and claim rules.
3. **Run a hierarchical fast expert screen**
   - identify telemetry-fragile decode steps;
   - identify implicated layers;
   - mask each selected top-8 expert one at a time and insert the next-ranked
     unselected expert;
   - use cheap one-step counterfactual statistics to rank swaps;
   - fully continue only the preregistered top branch variants.
4. **Separate oracle and deployable evidence**
   - oracle: did any tested equal-compute route repair the failure?
   - non-oracle: can telemetry/router signals choose a better route without
     verifier or answer access?
5. **Compare matched controls**
   - normal route;
   - selected-expert/rank-9 swaps;
   - lowest-weight swap;
   - diversity-boost swap;
   - discovery-fit soft expert penalty;
   - matched-random swap;
   - oracle best tested route, ceiling only.
6. **Primary verdicts**
   - H1: route-recoverable failures beat matched-random search with paired CI
     strictly above zero;
   - H2: a frozen non-oracle policy beats normal and matched-random routing on
     sealed holdout with paired CIs strictly above zero;
   - H3: any layer-expert soft penalty must generalize through discovery,
     validation, and corrected holdout gates.
7. **Privacy and safety**
   - detailed routes, token data, prompts, outputs, labels, and expert tables
     private and gitignored;
   - public reports aggregate-only;
   - no hard expert shutdown, full-model training, or production unlock.

## Result-driven continuation

Follow only the branch rules in the M32R protocol:

- H1 + H2 established: M33R frozen lightweight router-bias/router-only adapter,
  then eligible M34R partial-trajectory routing and transfer.
- H1 established but H2 not established: M33R route-selection research; do not
  pretend oracle search is deployable.
- H1 not established: stop expert-routing work and return to structured
  repair/tool routing.
- resource, architecture, or hook failure: stop and report the exact blocker.

## Repository hygiene

Do not commit model weights, caches, local model paths, prompts, outputs,
operands, per-task routes, expert identities tied to private tasks, token
ids/text, raw router tensors, or detailed counterfactual records. Public
artifacts remain aggregate-only. No candidate becomes gold and production
remains gated until explicit audited unlock criteria are defined.
