# M20 — fixture-grounded regeneration

M20 closes the execution-path loop for M19 current-information tasks:
completed fixture retrieval can now feed a controlled second model call, and the
result is verified and recorded without persisting the question, retrieved
context, original full output, or grounded full output.

## Safety contract

- `regenerate(..., enabled=False)` is the default. The dedicated M20 config is
  an explicit opt-in.
- Only `current_info` tasks with a completed `retrieval_needed` /
  `retrieved_context` action may call the model.
- Context must come from M18's `FixtureRetrievalAdapter` with `fixture` or
  `public_fixture` source kind. No live web retrieval was added.
- The grounded prompt exists only in memory and instructs the model to treat
  fixture context as data, not executable instructions.
- Persistent `grounded_result_v1` records contain hashes, enums, booleans, and
  confidence only.
- Fixture expected-answer matching validates the controlled handoff; it is not
  real-world truth or a gold label.

## Grounded result record

`schema/grounded_result_v1.json` links each result to its retrieval action and
records status, context source kind, regeneration model, verifier names/verdicts,
whether the grounded answer changed from the stored original preview, evidence
hashes, follow-up state, and `candidate_only=true`. Raw text fields are not in
the schema.

## Controlled live run

The private M20 fixture supplied one controlled evidence token through the
`public_fixture` path. The already-running local `agents-a1` endpoint performed
the second-pass calls:

```bash
python src/grounded_regenerator.py \
  --config config/agents_a1_m20_grounded.json
```

Results over the 23 M19 retrieval actions:

| outcome | count |
|---|---:|
| true current-info candidates | 20 |
| grounded answers produced | 20 |
| non-current false positives skipped before model call | 3 |
| grounded answers changed from original preview | 20 |
| deterministic fixture expected-token pass | 4 |
| deterministic fixture expected-token fail | 16 |
| total follow-up needed | 19 |

True current-info grounded-production coverage is 20/20. The overall 20/23 rate
includes the three intentionally skipped non-current signals.

Only 4/20 grounded outputs contained the fixture expected token. The generic
fixture described a controlled response token rather than providing question-
specific real-world evidence, so many generations reasonably treated it as
insufficient or otherwise omitted the token. This is a path-quality result:
regeneration works, but context quality and grounded-answer verification remain
load-bearing. No attempt was made to reinterpret fixture failures as real-world
answer failures.

## Reviewed M19 findings

`agents_a1_m20_review_summary.json` records aggregate-only review outcomes:

- Four M19 full-output math checker failures were rechecked against deterministic
  metadata and remain four confirmed wrong **candidates**; zero gold promotions.
- Three M19 retrieval false positives were confirmed: two explain rows triggered
  by bare “weather,” and one numeric row by bare “price.”
- The freshness regex now removes bare `weather`, `price`, `stock`, and `news`
  terms. Explicit `current_info` metadata remains authoritative; otherwise a
  temporal expression is required.

The M17 calibration summary was not rewritten because M20 created no new human-
reviewed gold labels.

## Public and private artifacts

- Public: `agents_a1_m20_grounded_summary.json` and
  `agents_a1_m20_review_summary.json`.
- Private/gitignored: fixture context and 23 detailed grounded-result records.
- `--summarize-existing` rebuilds public summaries from private hashed results
  without calling the model again.

## Gating

- `auto_outcome`, `action_result`, and `grounded_result` remain candidates.
- Retrieval completion and fixture-token verification are not real-world
  correctness.
- Sixteen grounded outputs and the three skipped routes still require follow-up.
- No web retrieval, raw-text persistence, or production unlock was introduced.
- Production remains gated on question-specific evidence, stronger verification,
  and human calibration.
