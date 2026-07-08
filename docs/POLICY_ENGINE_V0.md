# PolicyEngine v0 — advisory / shadow-mode risk governor

The first jlens **runtime** layer. It turns a prompt's captured telemetry into a
risk **level** and a recommended **action**, and logs the recommendation. It is
**advisory and shadow-mode only**: it recommends and records — it **never
blocks, executes, or gates** a real action. Prototype thresholds only; final /
production thresholds stay **gold/audit gated**.

## Files
- `config/policy_engine_v0.json` — thresholds, level→action map, posture.
- `src/policy_engine.py` — `PolicyEngine` (fits M5 heads, `score(row)`).
- `src/risk_runtime.py` — CLI: score feature rows + append to the shadow log.
- `reports/shadow/shadow_log.jsonl` — the shadow log (tracked).

## What it scores
Only the two labels with M5 end-to-end coverage:
`answerable_from_memory`, `unsupported_or_hallucinated`. Every other risk label
is **unscored** in v0 (unknown ≠ safe). The heads are the M5 prototype logreg
heads, fit from `reports/features/benchmark_m5_features.jsonl` joined to the
benchmark labels. **Drift is never a feature** (asserted at fit time).

## Risk score → level → action
- Per-label probability `p` from the fitted head.
- Risk **contribution**: for `answerable_from_memory` the risk direction is
  *false* (not answerable → needs grounding) so contribution = `1 − p`; for
  `unsupported_or_hallucinated` it is *true* so contribution = `p`.
- Overall **risk** = max contribution (the riskiest driver).
- **Level** from the config bands: low `[0,0.35)`, medium `[0.35,0.55)`,
  high `[0.55,0.75)`, critical `[0.75,1]`.
- **Action** from `level_action_map`: low→`answer_locally`, medium→`verify`,
  high→`retrieve`, critical→`require_confirmation`.

## v0 action semantics
| action | meaning |
|---|---|
| `answer_locally` | respond directly from the model; low risk |
| `verify` | do a self-check / second pass before answering |
| `retrieve` | pull grounding/RAG evidence before answering |
| `run_checker` | run a math/code/tool verifier on the answer |
| `ask_user` | ask the user to clarify |
| `require_confirmation` | get human sign-off before any autonomous action |

`run_checker` and `ask_user` are in the action vocabulary for future bands; the
v0 default map uses the other four.

## Policy output schema (`score(feature_row)`)
```json
{
  "prompt_id": "<str>",
  "level": "low|medium|high|critical",
  "scores": {"answerable_from_memory": 0.0, "unsupported_or_hallucinated": 0.0},
  "risk": 0.0,
  "recommended_action": "<one of the v0 actions>",
  "explanation": "<one-line human rationale, tagged [SHADOW/advisory]>"
}
```

## Shadow-log schema (`reports/shadow/shadow_log.jsonl`, one JSON per line)
```json
{
  "ts_placeholder": "<caller-supplied; no wall-clock in this env>",
  "prompt_id": "<str>",
  "feature_source": "<features file path>",
  "scores": {"answerable_from_memory": 0.0, "unsupported_or_hallucinated": 0.0},
  "level": "<level>",
  "recommended_action": "<action>",
  "mode": "shadow",
  "outcome_note": null
}
```
`outcome_note` is null, reserved for later human annotation (was the advisory
right?). The shadow log only records; it never changes behavior.

## Worked example — score one feature row
```bash
python src/risk_runtime.py \
    --features reports/features/benchmark_m5_features.jsonl \
    --ts 2026-07-08T00:00:00Z --limit 1
```
Result (a FEVER claim-verification prompt):
```json
{
 "prompt_id": "fever_0000ceade3f14c17cb71a431b5c8a81b",
 "level": "critical",
 "scores": {"answerable_from_memory": 0.541, "unsupported_or_hallucinated": 0.7511},
 "risk": 0.7511,
 "recommended_action": "require_confirmation",
 "explanation": "risk=0.75 (driver: unsupported_or_hallucinated p=0.75) -> level=critical -> advise: require_confirmation [SHADOW/advisory]"
}
```
Reading it: the telemetry marks this claim-verification prompt as high
hallucination risk, so v0 **advises** `require_confirmation` — and logs that
advice. Nothing is blocked or executed.

## Posture & guarantees
- **Advisory / shadow only.** The engine recommends + logs. It never blocks,
  executes, or gates any real action. Ordinary chat stays advisory.
- **Prototype thresholds, not production.** The bands come from the tiny-n M5
  smoke heads (AUROC ~0.84–0.88, poor calibration). No production claims.
- **Final / production thresholds stay gold/audit gated** (see
  `LABELING_HANDOFF.md`). The M5 metrics and training path are preserved
  unmodified — this layer only consumes them.
