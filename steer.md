# steer.md — post-M3 steering

Read this first before continuing `jlens`.

M2 DecodeGuard is complete. M3 scaffolding is also complete. Do not continue from M2 or from M3 step 5.

## Current state

Completed:

```text
M1: RouterGuard feasibility
M2: DecodeGuard telemetry and feature discovery
M3: risk-labeling scaffold and training gate
```

M3 delivered:

```text
schema/risk_labels_v1.json
data/labels/risk_labels_seed.jsonl
src/build_label_scaffold.py
src/risk_features.py
reports/features/r4_risk_features.jsonl
src/train_risk_heads.py
src/eval_risk_heads.py
LABELING_HANDOFF.md
```

The current label file is intentionally all-null. Training correctly refuses to run until reviewed labels exist.

## Working findings

Keep these feature groups for future heads:

```text
entropy_final_logits
selected_token_prob
topk_mass_or_margin
prefill domain prediction and margin
windowed decode-domain shift
low-confidence and high-entropy counts
```

Do not use these as model features:

```text
drift_from_prefill_signature
drift_from_previous_token
drift_from_prefill_weighted
drift_from_previous_token_weighted
```

Reason: M2 showed drift does not track confidence. Keep drift only for provenance/debugging.

## What happens next

The project is now operator-gated.

Next useful work is not more modeling. It is labeling and dataset expansion.

Human/operator action:

```text
1. Review LABELING_HANDOFF.md.
2. Fill labels in data/labels/risk_labels_seed.jsonl, or approve a larger labeling file.
3. Add enough examples to reach useful coverage across label families.
4. Keep train/test prompt templates separate.
```

After reviewed labels exist, a future loop can train and calibrate the risk heads.

## If starting another agent loop

Use `/prompt-master` first and create/update a loop prompt that starts from post-M3 state.

Suggested command:

```text
/jlens-labeling-ops-loop
```

The loop should:

```text
1. Read steer.md first.
2. Read LABELING_HANDOFF.md, M3_RISK_LABELING.md, STATE.md, reports/FINDINGS.md, schema/risk_labels_v1.json, and reports/features/r4_risk_features.jsonl.
3. Confirm M3 scaffolding is complete.
4. Do not fabricate labels.
5. Do not treat null as false.
6. Do not train final heads on all-null or undercovered labels.
7. Help build/validate labeling batches and operator workflow.
8. Commit only documentation, schemas, validation helpers, or approved labeled files.
9. Stop when it reaches a human decision point.
```

## Suggested next milestone: M4 labeling operations

M4 should be about making the labeling process easy and reliable, not training yet.

Potential M4 tasks:

```text
create a label-review dashboard or simple HTML table
create scripts to validate completed label files
create scripts to summarize label coverage by family
create scripts to sample more prompts for weak label families
create prompt packs for current-info, citation, math-check, code-check, user-file-context, high-stakes, context-attack, unsupported-output, and format-shift cases
create capture commands using router-only decode mode for new prompt packs
create a merge script for multiple human label files
```

M4 stop condition:

```text
operator can label examples without touching raw JSON by hand
coverage report shows which labels still need examples
no final risk heads trained unless label coverage meets the gate
```

## Final architecture

```text
RouterGuard: prefill routing signatures and domain priors
DecodeGuard: entropy, selected-token confidence, router concentration, windowed mode shift
PolicyEngine: calibrated risk heads and route decisions
HiddenLens: future phase only after the risk governor baseline is validated
```

## Repository hygiene

Do not commit raw captures, logs, caches, local environments, model weights, or large generated artifacts unless explicitly intended.
