# Agents-A1 bounded shadow run (M11)

Run a bounded batch of tasks through a local Agents-A1 endpoint, record
`auto_outcome` candidates locally, and produce an aggregate-only report plus a
local review queue of the escalated subset — without leaking any prompt/output
text. Advisory/shadow only; nothing here is a gold label.

> **Invariants:** raw prompt/output text stays in the gitignored private dir;
> only aggregate-only or redacted artifacts are committable (gated by
> `check_commit_safe.py`). `auto_outcome` is a CANDIDATE, never gold. The run
> NEVER writes the human `outcome`/`review_meta` fields. A GGUF endpoint has no
> router logits, so records set `telemetry_missing=true` and `policy=null`.

## Pieces

| File | Role |
|---|---|
| `config/agents_a1_shadow_run.json` | endpoint, task sources, batch bounds, verifier toggles, escalation thresholds, resume/deterministic flags |
| `data/prompts/agents_a1_smoke_batch.jsonl` | public 25-task smoke batch (the workload format) |
| `src/run_agents_a1_shadow_batch.py` | bounded, resume-safe runner → private run log + run-meta |
| `src/make_escalation_review_queue.py` | escalated-only local review queue |
| `src/agents_a1_run_report.py` | aggregate-only run report (no text) |
| `src/check_commit_safe.py` | mandatory pre-commit gate |

## 1. Smoke run (deterministic, no network, no GPU)

```bash
python src/run_agents_a1_shadow_batch.py --config config/agents_a1_shadow_run.json
# -> reports/shadow/private/agents_a1_run_local.jsonl        (gitignored)
#    reports/shadow/private/agents_a1_run_meta_local.json    (gitignored)
```

This uses the deterministic dry-run output — good for validating the pipeline
before touching a real model.

## 2. Live run against Agents-A1 (deliberate step — serve the endpoint first)

A live run needs the Agents-A1 GGUF served on an OpenAI-compatible endpoint. The
runner does **not** start models — serve the endpoint yourself (or have the
operator do it), then point a local config at it:

```bash
# 1) Serve InternScience/Agents-A1-Q8_0-GGUF on a free port via llama.cpp
#    (llama-server ... --port <free-port>), leaving llama-swap's own models alone.
# 2) Copy the config and set endpoint.base_url / model to your server, then:
python src/run_agents_a1_shadow_batch.py --config my_local_agents_a1.json --mode live
```

Keep the batch bounded (`batch.size` 25, cap 100). Live output text lands only in
the gitignored private run log.

## 3. Resume / retry

The runner is resume-safe: on re-run it reads the `prompt_id`s already in the run
log, runs only the missing tasks, and **appends** — a completed batch adds
nothing on a second run. If the endpoint fails on a task, that task is counted in
`n_failed` and the run continues. So a long/interrupted run can simply be
re-invoked with the same config and output path.

## 4. Review the escalated subset

```bash
python src/make_escalation_review_queue.py \
    --in reports/shadow/private/agents_a1_run_local.jsonl \
    --out reports/shadow/private/agents_a1_review_local.jsonl        # gitignored
```

The queue contains only rows with `auto_outcome.escalate_for_review == true`,
keeping the auto verdict as context, with the human `outcome`/`review_meta`
fields null. A human then annotates outcomes — see
`docs/SHADOW_OUTCOME_REVIEW.md` for the review CLI and field meanings. `null`
means unreviewed, never false.

## 5. Aggregate report + commit gate

```bash
python src/agents_a1_run_report.py \
    --in reports/shadow/private/agents_a1_run_local.jsonl \
    --meta reports/shadow/private/agents_a1_run_meta_local.json \
    --out reports/outcomes/agents_a1_run_summary_sample.json

python src/check_commit_safe.py reports/outcomes/agents_a1_run_summary_sample.json
# exit 0 => safe to commit;  nonzero => DO NOT COMMIT
```

The report is counts/rates/distributions only (run_id, model, completed/failed/
telemetry-missing counts, level & action & verdict distributions, escalation
rate, verifier distribution, auto-need counts, and auto-vs-human agreement over
**human-reviewed rows only** — null until a human reviews). No prompt/output/notes
text. Never `git add` anything under `reports/shadow/private/`.

## Guardrails + gating

- **No private raw logs or prompt/output text are ever committed.** Private run,
  review, and meta artifacts are gitignored; only aggregate-only or redacted
  artifacts are committable, enforced by `check_commit_safe.py`.
- **`auto_outcome` is a candidate, not gold** — promoted only by a later human
  audit. The run never writes human `outcome`/`review_meta` fields.
- **Honest telemetry.** GGUF exposes no router logits ⇒ `telemetry_missing=true`,
  `policy=null`; features are never fabricated.
- **Failures are counted and the run continues** when safe (`n_failed`).
- **No arbitrary command execution** as a verifier — the code verifier runs
  trusted fixtures only.
- **Production/final thresholds stay gold/audit gated** until enough
  human-reviewed real-workload records exist. This run is how `auto_outcome`
  candidates + escalations accumulate for that review (see
  `docs/AUTONOMOUS_SHADOW_SUPERVISOR.md`, `docs/PRIVATE_SHADOW_WORKFLOW.md`).
