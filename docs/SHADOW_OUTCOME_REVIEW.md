# Shadow-outcome review — human reviewer guide

The PolicyEngine v0 advisor logs a recommendation for each prompt (M6/M7). This
milestone (M8) lets a **human** mark whether each recommendation was actually
right, and turns those judgments into calibration numbers. **Only a human sets
outcomes — the tooling never fabricates a judgment.** `null` means *unreviewed*,
not false.

## The flow
1. **Build a review queue** from shadow records (all outcomes start null):
   ```bash
   python src/build_review_queue.py \
       --inputs reports/shadow/realuse_sample.jsonl \
       --out reports/shadow/review_queue_sample.jsonl
   ```
2. **Review a record** — set only the fields you actually judged:
   ```bash
   python src/review_shadow_log.py \
       --queue reports/shadow/review_queue_sample.jsonl \
       --prompt-id tqa_0_c5971ef7b \
       --was-wrong false --needed-retrieval false \
       --reviewer YOURNAME --review-source manual --review-confidence 0.9
   ```
   Use `--dry-run` to preview + validate without writing. The CLI refuses invalid
   booleans, out-of-range confidence, and unknown prompt-ids.
3. **Report coverage + calibration**:
   ```bash
   python src/outcome_report.py \
       --queue reports/shadow/review_queue_sample.jsonl \
       --json reports/outcomes/outcome_coverage.json \
       --calibration reports/outcomes/calibration_notes.md
   ```

## Field meanings (each is `true` / `false` / `null=unreviewed`)
| field | you set `true` when… |
|---|---|
| `user_agreed` | you agreed with the model's answer |
| `was_wrong` | the model's answer was actually wrong/unsupported |
| `needed_retrieval` | the answer really needed grounding/RAG to be right |
| `needed_checker` | the answer really needed a math/code/tool check |
| `notes` | free text (string) — any context worth keeping |

Review metadata: `reviewer` (your name), `reviewed_at` (a placeholder string —
no wall-clock here), `review_source` (e.g. `manual`), `review_confidence`
(0..1, how sure you are).

## How to handle uncertainty
If you're not sure about a field, **leave it null**. Never guess. The calibration
uses only rows you actually judged; a null field is simply excluded.

## What the calibration measures
For rows where you set `was_wrong`, it compares the advisor's risk level
(high/critical = "flagged risky") to reality:
- **false-low-risk** — the answer was wrong but the advisor said low/medium risk
  (a *miss* — the costly error).
- **false-high-risk** — the advisor flagged risk but the answer was fine
  (over-caution — cheaper).
With 0 reviewed rows the report says *"calibration pending — no reviewed outcomes
yet."*

## Honesty & gating rules
- **Never fabricate an outcome.** Only a human sets these fields; `null =
  unreviewed`. Committed queues stay all-null until a human reviews.
- **Prototype only.** Scores come from the tiny-n M5 heads — no production claims.
- **Production/final thresholds stay gold/audit gated** until enough reviewed
  outcomes exist. This review loop is how those reviewed outcomes accumulate.
- **Privacy.** Commit only public/benchmark prompts. Keep private real-use logs
  out of git unless scrubbed and explicitly approved.
