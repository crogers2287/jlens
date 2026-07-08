# Private real-use shadow workflow (M9)

How to run jlens's PolicyEngine advisor against **real prompts** on your own
machine, review the outcomes, and share results **without ever leaking prompt or
output text**. Everything with raw text stays local and gitignored; only
aggregate-only summaries or explicitly-redacted logs are ever committable.

> **The one rule that matters:** raw `prompt_preview` / `output_preview` /
> `outcome.notes` text from real use is NEVER committed. The private dir is
> gitignored, and `src/check_commit_safe.py` refuses to let unredacted text (or
> a private-log path) reach a commit. All examples below use the **public
> fixture** `reports/shadow/realuse_sample.jsonl` so nothing sensitive is
> produced.

## Where private data lives

```
reports/shadow/private/          # gitignored — local only
  README.md                      # the ONLY committed file here
  *.jsonl                        # your real-use logs — NEVER committed
```

`reports/shadow/private/*.jsonl` is in `.gitignore`; the README is not. Confirm:

```bash
git check-ignore reports/shadow/private/realuse_local.jsonl   # prints the path = ignored
git check-ignore reports/shadow/private/README.md             # prints nothing = tracked
```

## 1. Generate a private log (local only)

Run real prompts through the shadow wrapper, writing to the **gitignored**
private path. The wrapper is advisory-only (it never blocks the model); in
`--mode live` it also calls your local endpoint. Raw text lands only in this
local file.

```bash
# LIVE against your local model, logging to the gitignored private dir:
python src/local_shadow_wrapper.py --mode live \
    --endpoint-config config/local_endpoint_example.json \
    --prompts my_real_prompts.jsonl \
    --log reports/shadow/private/realuse_local.jsonl
```

**Do not commit `realuse_local.jsonl`.** It carries your real prompt/output text.

*Safe demonstration (no real data) — the committed public fixture was produced in
dry-run mode from benchmark prompts:*

```bash
python src/local_shadow_wrapper.py \
    --prompts data/prompts/benchmark_m5_sample.jsonl \
    --log reports/shadow/realuse_sample.jsonl        # public benchmark text — safe
```

## 2. Review outcomes locally (M8 CLI)

Build a review queue from your private log, then annotate outcomes. **A human
sets outcomes — the tooling never fabricates one; `null` means unreviewed.**
Keep the queue in the private dir too, since it still contains prompt text.

```bash
python src/build_review_queue.py \
    --inputs reports/shadow/private/realuse_local.jsonl \
    --out reports/shadow/private/review_queue_local.jsonl

python src/review_shadow_log.py \
    --queue reports/shadow/private/review_queue_local.jsonl \
    --prompt-id <id> --was-wrong false --needed-retrieval false \
    --reviewer YOURNAME --review-source manual --review-confidence 0.9
```

(Full reviewer guide: `docs/SHADOW_OUTCOME_REVIEW.md`.)

## 3. Make a shareable artifact — choose ONE

### (a) Aggregate-only summary (preferred — no text at all)

```bash
python src/private_outcome_summary.py \
    --in reports/shadow/private/review_queue_local.jsonl \
    --out reports/outcomes/private_summary_sample.json
```

Emits only counts and distributions (total / reviewed / unreviewed, level and
recommended-action distributions, per-outcome-field non-null counts, and
reviewed-only false-low-risk / false-high-risk). It is built from a fixed set of
numeric/label keys, so free text never enters — safe to commit even though the
input was private.

*Committed sample (from the public fixture):*
`reports/outcomes/private_summary_sample.json`.

### (b) Redacted log (keeps structure, scrubs the text)

```bash
python src/redact_shadow_log.py \
    --in reports/shadow/private/review_queue_local.jsonl \
    --out reports/shadow/review_queue_local.redacted.jsonl        # [--hash] for stable tags
```

Replaces `prompt_preview` / `output_preview` / `outcome.notes` with `[redacted]`
(or `[redacted:<hash>]`), keeping `prompt_id`, `policy`, outcome booleans,
`policy_note`, `mode`, `review_meta`.

## 4. Gate the commit — always run the guard first

Before staging **anything** under `reports/`, run the safety guard. It exits
nonzero on a private-log path, a private-dir reference, or any unredacted
prompt/output/notes text; it passes aggregate-only, all-null-text, and redacted
files.

```bash
python src/check_commit_safe.py \
    reports/outcomes/private_summary_sample.json \
    reports/shadow/review_queue_local.redacted.jsonl
# exit 0 => safe to commit;  nonzero => DO NOT COMMIT (it prints why)
```

Only commit if the guard passes. Never `git add` a file under
`reports/shadow/private/` (other than the README).

## Privacy rules (recap)

- **Never commit private prompt/output/notes text.** The private dir is
  gitignored; only aggregate-only or redacted artifacts are committable.
- **`check_commit_safe.py` is mandatory** before staging anything under
  `reports/`. It is deliberately conservative — it flags *all* unredacted
  prompt/output text because it cannot tell public benchmark text from private.
- **Never fabricate outcomes.** `null = unreviewed`; only a human sets them.
- **Production/final thresholds stay gold/audit gated** until enough reviewed
  real-use records exist. This workflow is how those reviewed records
  accumulate — locally and privately — so calibration can eventually unlock
  production thresholds through a gold audit. Scores remain PROTOTYPE numbers
  from the tiny-n M5 heads until then.
