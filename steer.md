# steer.md — M34 second-category detector transfer

M1 through M33 are complete. M33 established the first positive intervention
result of the repair track: on a fresh disjoint decision set the frozen M30
trigger reproduced (precision .902 / recall .889) and verifier-first tool
routing gated on it was USEFUL (.938 vs .435 no-repair CI [.453, .555]; vs
.714 random routing CI [.177, .271]) and EFFICIENT (uplift retention .889
CI [.846, .929] at invocation fraction .557). Zero errors introduced.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Operator decision

Per Branch 3 of `docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`, M34 is a
**second-category transfer test of the frozen detector**, not trace scaling.
This is the final milestone of the bounded autoloop budget authorized at M32
reactivation (M32, M33 complete). After M34 the loop STOPS and prints the
required final stop report regardless of outcome.

## M34 protocol

Predeclare `data/prompts/m34_transfer_manifest.json` BEFORE any task
generation or capture, in its own commit, then execute exactly as written.

- Category shift: mixed arithmetic expressions `a*b + c` (the M19-M24 prompt
  family), a genuine shift from the pure-multiplication M30 training
  distribution while remaining deterministically checkable by the existing
  math verifier.
- Decision set: 384 tasks over the six M32/M33 multiplication bands with a
  predeclared additive term range (c drawn per band from [2, 99]), seed
  `m34-transfer-v1`, (a, b) tuples disjoint from everything M29-M33 generate.
- One GPU capture phase: greedy 64-token originals, same validity rules.
- Detector: the frozen M30 classifier, refit deterministically, threshold 0.5,
  scored on the same feature recipe. No M34 labels may influence triggering;
  no refitting, recalibration, or threshold tuning on M34 data.
- Tool: deterministic integer evaluator on the task's own predeclared
  expression, verifier-first, zero decode tokens (as in M33).
- Policies: `no_repair`, `tool_on_every_task`, `random_trigger_tool`
  (count-matched, seed `m34:random-trigger`), `telemetry_trigger_tool`.
- T1 transfer classification (primary, descriptive thresholds preregistered):
  - `transfer_maintained`: precision >= .80 AND recall >= .75;
  - `transfer_degraded`: below either bound but routing H1 still useful;
  - `transfer_failed`: otherwise.
- H1 routing usefulness and H2 routing efficiency: identical claim rules to
  M33 (paired bootstrap 95% CIs strictly > 0 for both H1 comparisons;
  retention >= .80 at invocation fraction <= .60), bootstrap seeds
  predeclared (`m34:h1`, `m34:h2:retention`, 2000 iterations). H1/H2 verdicts
  are reported under whichever T1 class obtains — there is no reproduction
  gate blocking them in M34, because degradation itself is the measurement.
- Report per-band trigger and routing metrics descriptively (aggregate-only),
  secondary and non-confirmatory.

## Stop conditions

Stop immediately and report the exact blocker on: any policy arm replacing a
passing original, privacy/commit-safety failure, test failure, tuple
exhaustion during generation, or unresumable capture invalidity.

## Required final stop report (end of autoloop)

After the M34 result commit, print the `docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`
required final stop report: latest commit SHA and milestone count; M32 H1/H2
verdicts; trigger precision and rescue rates across M32/M33/M34; best
model-side operator and compute per rescue; whether M33/M34 ran and why;
public artifacts created; private traces intentionally not committed; tests
passed; and the M34 transfer classification with its routing verdicts. The
autoloop then STOPS; any further milestone requires a fresh operator decision.

## Repository hygiene

Unchanged: no operands, prompts, outputs, per-task predictions/labels/
triggers, token ids/text, raw tensors, or local model paths in public
artifacts; aggregate-only public reports; `src/check_commit_safe.py` must pass
on anything staged under `reports/`. Candidate-only; production remains gated;
no weight training; no training dataset from tool outputs.
