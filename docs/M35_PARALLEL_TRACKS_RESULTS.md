# M35 results — tracks A/B/C (aggregate-only study report)

Campaign: 1536 tasks, six families, fail rates .041-.953 (finding 214);
splits D 576 / R 288 / B-test 288 / A-test 384, each sealed set read exactly
once, in the preregistered order (B-test `89c80d6`, then A-test). Protocol
`docs/M35_PARALLEL_TRACKS_PROTOCOL.md`; manifest `47f4ed3` (+ pre-capture
amendment `2ad210b`); detector freeze `6b7e5fc` (hash `8cb5e95f3adfc0c4`);
router freeze `b7b86b3` (hash `d2b9333c3c8da41f`).

## Track B — transfer-robust detector (primary: LOFO)

Full-pipeline leave-one-family-out refits (withheld family indicator mapped
to unknown), evaluated on the withheld family's sealed B-test rows:

| Withheld family | Global (prec/rec) | Per-family | Hierarchical | B-test fails |
|---|---|---|---|---|
| add_carry | no triggers / .00 | no triggers / .00 | no triggers / .00 | 3/36 |
| sub_borrow | no triggers / .00 | no triggers / .00 | no triggers / .00 | 2/60 |
| mul_carry | 1.00 / .70 | .93 / .70 | .93 / .70 | 20/60 |
| div_exact | .50 / .36 | .50 / .45 | .50 / .45 | 11/60 |
| mul_add | .96 / .71 | .96 / .74 | .96 / .74 | 34/36 |
| mod_mul | .89 / 1.00 | .89 / 1.00 | .89 / 1.00 | 32/36 |

Claim (restricted per preregistration): robustness across these named
withheld families under this generator/prompt/model/decode/telemetry regime
— held for mul_carry, mul_add, and mod_mul; failed for div_exact (division
telemetry is structurally unlike the training families); high-competence
families produce no triggers (zero false alarms, sparse failures missed).
Nothing beyond these families is claimed. Pooled secondary (not transfer
evidence): global .92/.82 > hierarchical .81/.74 > per-family .73/.65.
Contrast with M34: the frozen proxy detector transferred at recall .612 with
no refit; family-refit detectors recover most failure-bearing regimes.

## Track A — hierarchical competence router (sealed A-test)

Router (t_low .05, t_high .70, frozen on R): 133/384 invocations (.346,
budget .50); actions: no_tool 128 rows, telemetry-gated 208, tool-everywhere
48. Family-weighted verified success:

- no_repair .573; count-matched random .727; **global threshold at same
  budget .940**; **hierarchical router .944**; tool-on-every-task 1.000.

**A-H1 = not_established.** Router beats random decisively (+.217,
CI [.177, .256]) but is statistically indistinguishable from the plain
global-detector threshold at matched budget (+.003, CI [0, .010]; lower
bound not strictly positive). The preregistered rule required beating both.

**A-H2 = not_established.** Success delta vs tool-on-every-task
[-.079, -.035] against a -.05 non-inferiority bound — the router saves 251
of 384 tool calls (65%) but gives up ~5.6pp, just missing the margin.

Interpretation: the global detector's family one-hot features already encode
category difficulty, so the explicit competence-prior routing layer is
redundant on this campaign. The strongest supported artifact is a single
well-fit global detector thresholded to budget: .94 verified success at ~35%
of tool calls. Verifier-first held in every arm (zero replacements of
passing originals; asserted in code).

## Track C — shadow mode (ongoing)

Advisory-only annotator shipped (`601fa3c`) with eligible-denominator
logging, config-hash versioning, and both-arm contingency rollups. Live
smokes: real-use log all-abstain (no telemetry, per M7); M24 math workload
13/40 eligible at advise rate .154 — quantifying the M34 recall collapse in
the product context.

## Gating

Aggregate-only public artifacts (check_commit_safe passed on every staged
report); operands/prompts/outputs/predictions/splits private and gitignored.
Candidate-only; production gated; no training data from tool outputs. Per
the operator steer, M36 (Agents-A1 AWQ INT4 raw-vs-jLens) begins after the
M35 result commits.
