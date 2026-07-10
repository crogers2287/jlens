# steer.md — M31 telemetry-triggered intervention study

M1 through M30 are complete. The M30 decisive test classified the
telemetry-vs-metadata increment as **ESTABLISHED** under the preregistered
rule (+.099 accuracy, 95% CI [+.042, +.156], n=192 once-read holdout).
Per the operator's result-driven branching (steer 2a4699e, Branch 1), the
next milestone is the telemetry-triggered intervention study.

`CODEX_AUTOSTEER.md` remains the operating contract. The operator authorized
a telemetry-focused autoloop of up to three milestones starting with M30;
M30 was the first, M31 is the second.

## Current evidence after M30

- Full telemetry .917 vs metadata .818 on the powered n=192 holdout;
  27 metadata errors corrected vs 8 introduced; both accuracy and
  balanced-accuracy paired CIs exclude zero.
- metadata_plus_telemetry .922 (+.104 [+.057,+.156]); window_entropy alone is
  insufficient (+.031, CI spans zero) — the increment needs all ten features.
- Candidate calibration transfers: full_telemetry ECE .032, threshold .50
  p(fail), holdout balanced accuracy .916. Candidate-only, production gated.
- Suite green at 136 tests. Scope remains one category/model/decode protocol.

## M31 — telemetry-triggered intervention study (current milestone)

Goal: measure whether the frozen M30 telemetry score, used as a retry
trigger, improves verified task success at reasonable compute cost — against
no-retry, matched-compute random retry, and always-retry controls.

Preregister in `data/prompts/m31_intervention_manifest.json` before any
generation or capture:

1. A fresh 192-task set: the same six bands × 32, operand tuples
   deterministically disjoint from both the M29 and M30 manifests. No
   train/validation split — the classifier and threshold are frozen from M30.
2. Frozen score: the M30 full_telemetry nearest-centroid model,
   deterministically re-instantiated from the private M30 train records with
   no refitting, plus the frozen validation threshold p(fail) ≥ .50.
   Verification hash of the M30 training protocol must match.
3. Original decode: the standard greedy protocol (chat template, 64-token
   cap, router-only capture).
4. Retry decode: one seeded sampled decode per task (temperature 0.7,
   deterministic per-task generator seed derived from the manifest seed and
   task id), same template and cap. The greedy capture path stays untouched;
   sampling is an opt-in flag addition to the capture script.
5. Policies compared on identical tasks and the identical single retry
   capture (replace-on-trigger semantics; no policy may consult the label):
   - no_retry — original outputs
   - always_retry — retry outputs for all tasks
   - random_retry — fixed-seed random subset, size matched to the telemetry
     trigger count
   - telemetry_triggered — retry iff frozen p(fail) ≥ .50 on the original
     decode's telemetry
6. Deterministic labels: math_checker on original and retry outputs;
   undecided excluded and reported.
7. Metrics per policy: verified success rate, retries used (compute), false
   alarms (retries on originally-correct tasks), errors rescued
   (wrong→right), errors introduced (right→wrong), paired bootstrap CIs for
   success-rate deltas (fixed seeds, 2000 iterations).
8. Preregistered classification of the telemetry policy:
   - useful: success delta over no_retry has a positive CI excluding zero
     AND success delta over matched-compute random_retry has a positive CI
     excluding zero
   - harmful: success delta over no_retry has a negative CI excluding zero
   - not_established: otherwise
9. Recovery traces: for verified wrong→right rescues only, write private
   gitignored trace records; public artifacts report aggregate counts and a
   trace schema description only.
10. Honest reporting: class balance, undecided, decode-cap counts, trigger
    rate, and every shortfall. No production policy or threshold unlock.

Deliverables:

- `data/prompts/m31_intervention_manifest.json` (predeclare commit first)
- sampling support in the capture script (greedy path unchanged) + tests
- `src/m31_intervention_study.py` + tests
- `reports/telemetry/hf_m31_intervention_run_summary.json`
- `reports/telemetry/hf_m31_intervention_evaluation.json`
- `docs/M31_TELEMETRY_INTERVENTION_STUDY.md`
- private recovery-trace JSONL (gitignored)
- updated `STATE.md` and `reports/FINDINGS.md`; full suite green

Stop condition: all four policies evaluated on identical fresh tasks with
deterministic labels; the telemetry policy classified useful, not
established, or harmful under the preregistered rule; recovery traces
private; public artifacts aggregate-only; commit-safe passes; tests green;
production gated.

## After M31

Report the intervention verdict and stop for operator review unless the
autoloop budget (three milestones from M30) and time limits still allow the
operator's Branch-1 continuation (scaling recovery-trace generation) — a
third milestone requires the M31 verdict first.

## Repository hygiene

Do not commit private prompts/outputs, operands, per-task predictions/labels,
token IDs/text, raw tensors, file-system paths, model weights, caches, or
detailed records. Public reports remain aggregate-only. No candidate becomes
gold and production remains gated until explicit audited unlock criteria are
defined.
