# Autonomous shadow supervisor (M10)

Runs a task queue against a local endpoint, applies cheap verifiers, and records
an **auto_outcome candidate** per task — separate from human review, never gold.
It removes the manual bottleneck of driving every task by hand, without
pretending the system is production-calibrated. Advisory/shadow only.

> **Two rules that never bend:** (1) `auto_outcome` is a CANDIDATE, not a label —
> it is promoted to gold only by a later human audit. (2) The autonomous loop
> NEVER writes the human `outcome` / `review_meta` fields; those stay null until
> a human reviews. Raw prompt/output text stays in the gitignored private dir;
> only aggregate-only or redacted artifacts are committable.

## Pieces

| File | Role |
|---|---|
| `config/autonomous_supervisor_v0.json` | endpoint (Agents-A1 GGUF-style), task sources, verifier toggles, escalation thresholds |
| `schema/auto_outcome_v1.json` | record schema (separate from the frozen `shadow_outcome_v1`) |
| `src/verifiers.py` | six cheap verifier adapters (evidence hashed, never raw text) |
| `src/autonomous_shadow_supervisor.py` | runs tasks → writes auto_outcome records |
| `src/autonomous_outcome_report.py` | aggregate-only run summary (no text) |
| `src/check_commit_safe.py` | pre-commit gate (mandatory before staging under `reports/`) |

## 1. Run the supervisor

Dry-run (deterministic, no network) against the **public** task fixture, writing
to the **gitignored** private log:

```bash
python src/autonomous_shadow_supervisor.py \
    --config config/autonomous_supervisor_v0.json \
    --tasks data/prompts/autonomous_tasks_sample.jsonl \
    --out reports/shadow/private/autonomous_local.jsonl        # gitignored
```

Live against a local Agents-A1 GGUF endpoint (edit a local copy of the config
with your `base_url`/`model`), for your own prompts:

```bash
python src/autonomous_shadow_supervisor.py --mode live \
    --config my_local_supervisor.json \
    --tasks reports/shadow/private/task_queue_local.jsonl \
    --out reports/shadow/private/autonomous_local.jsonl        # gitignored
```

A GGUF chat endpoint returns **output text only** — no router logits — so each
record sets `telemetry_missing=true` and `policy=null`. Features are never
fabricated.

## 2. What each verifier contributes

Verifiers run only when their inputs are present (a task may carry
`known_answer`, `pattern`, `expression`, `task_category`). Each returns
`{name, confidence, verdict, evidence_hash}` — evidence is a **hash of inputs**,
never raw text.

| verifier | signal | feeds |
|---|---|---|
| `exact_answer_match` | output vs known answer | `auto_was_wrong` |
| `regex_or_schema_check` | output matches required format | `auto_was_wrong` |
| `math_checker` | deterministic arithmetic / final-number match | `auto_was_wrong`, `auto_needed_checker` |
| `code_test_stub` | runs a **trusted fixture** callable only (no arbitrary commands) | `auto_was_wrong`, `auto_needed_checker` |
| `retrieval_required_heuristic` | freshness / current-info task | `auto_needed_retrieval` |
| `self_consistency` | small-N sample agreement — **disagreement escalates, it is not proof of wrong** | escalation only |

## 3. auto_outcome vs human outcome

The record keeps the two namespaces strictly separate:

```
outcome / review_meta   -> HUMAN only; supervisor writes NULL, always
auto_outcome            -> autonomous CANDIDATE from verifiers
  auto_judged, auto_was_wrong, auto_needed_retrieval, auto_needed_checker,
  verifier_names, verifier_confidence, verifier_evidence_hash,
  escalate_for_review, auto_notes_redacted
```

A row is flagged `escalate_for_review = true` when: verifier confidence is below
`low_confidence_below`, correctness verifiers **contradict**, the policy level is
in `high_impact_levels`, self-consistency agreement is below
`self_consistency_min_agreement`, or a correctness verifier judged it wrong.
Escalation is advisory — it flags the row for a later human, it never sets a
human outcome.

## 4. Aggregate-only run report

```bash
python src/autonomous_outcome_report.py \
    --in reports/shadow/private/autonomous_local.jsonl \
    --out reports/outcomes/autonomous_summary_sample.json
```

Emits only counts / distributions / rates: totals, `telemetry_missing`, level &
action distributions, verifier-name distribution, escalation count+rate,
confidence buckets, and **auto-vs-human agreement computed only over
human-reviewed rows** (null until a human has reviewed). No prompt/output/notes
text — a recursive guard hard-fails on any text value. The committed sample
`reports/outcomes/autonomous_summary_sample.json` is generated from the public
fixture and is safe to share.

## 5. Gate the commit

Before staging anything under `reports/`:

```bash
python src/check_commit_safe.py reports/outcomes/autonomous_summary_sample.json
# exit 0 => safe;  nonzero => DO NOT COMMIT
```

Never `git add` a file under `reports/shadow/private/`. Commit only aggregate-only
or redacted artifacts.

## Guardrails + gating

- **auto_outcome is a candidate, not gold.** It is promoted only by a later human
  audit. Autonomous review never counts as gold on its own.
- **Human fields stay null** until a human (or an explicit trusted process)
  reviews. The supervisor never writes them.
- **Honest telemetry.** When GGUF serving exposes no router logits,
  `telemetry_missing=true` and `policy=null` — no fabricated features.
- **No real tool execution** beyond approved fixture commands. The code verifier
  runs trusted in-process fixtures only.
- **Privacy.** Private logs are gitignored; verifier evidence is hashed; only
  aggregate-only or redacted artifacts are committable, enforced by
  `check_commit_safe.py`.
- **Production/final thresholds stay gold/audit gated** until enough
  human-reviewed real-use records exist. This loop is how auto_outcome
  candidates + escalations accumulate for that review — see
  `docs/PRIVATE_SHADOW_WORKFLOW.md` and `docs/SHADOW_OUTCOME_REVIEW.md`.
