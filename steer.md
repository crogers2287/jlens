# steer.md — M3 handoff

M2 DecodeGuard is complete. Future work should not continue the old M2 loop.

## What M2 established

Keep these findings as the working truth:

- RouterGuard works: prefill routing signatures classify prompt domain strongly.
- The r3 domain head transferred cleanly to r4 prefill.
- Decode-token routing still carries domain signal, but single-token predictions are soft.
- Windowed decode-domain shift is useful for code/prose mode changes.
- Final-logit entropy and selected-token probability are the strongest decode-time uncertainty signals.
- `topk_mass_or_margin` is the only router-derived decode feature with useful uncertainty signal so far.
- Routing drift failed. Both unweighted and weighted drift are not useful confidence/risk features.

Feature decision:

```text
KEEP:
  entropy_final_logits
  selected_token_prob
  topk_mass_or_margin
  prefill domain prediction and margin
  windowed decode-domain shift
  low-confidence / high-entropy spike counts

EXCLUDE FROM RISK HEADS:
  drift_from_prefill_signature
  drift_from_previous_token
  drift_from_prefill_weighted
  drift_from_previous_token_weighted
```

Drift may remain in schemas for provenance, but should not be fed to the risk model.

## Current milestone

Active milestone:

```text
M3: human-labeled risk dataset and calibrated risk heads
```

M3 is label-gated. Do not create fake labels or treat generated labels as ground truth.

## Required loop behavior

Before starting the next implementation loop, use `/prompt-master` to update/create a dedicated M3 loop prompt.

The loop prompt should require the agent to:

```text
1. Read steer.md first.
2. Read M3_RISK_LABELING.md, STATE.md, reports/FINDINGS.md, SCHEMA.md, schema/v3_decode.json, and r4 reports.
3. Continue from M3, not M2.
4. Treat human-approved labels as the hard gate.
5. Commit after each completed item.
6. Update STATE.md and reports/FINDINGS.md after each completed item.
7. Stop when the M3 scaffolding and human handoff are complete.
8. Never commit raw captures, logs, caches, or local environment files.
```

Suggested loop command:

```text
/jlens-m3-risk-loop
```

## M3 execution plan

### Step 1 — risk label schema

Create:

```text
schema/risk_labels_v1.json
```

Labels:

```text
answerable_from_memory
needs_current_info
needs_exact_citation
needs_math_verification
needs_code_execution
needs_user_file_context
high_stakes_or_sensitive
context_attack_present
unsupported_or_hallucinated
format_or_tool_mode_shift
```

Rules:

```text
- multi-label records
- labels are true / false / null
- null means unknown, not false
- finalized records require a human labeler field
- schema must reject unknown labels
```

### Step 2 — human label scaffold

Create:

```text
data/labels/risk_labels_seed.jsonl
src/build_label_scaffold.py
```

The scaffold may contain unlabeled records only. All labels should start as null.

### Step 3 — feature extractor

Create:

```text
src/risk_features.py
reports/features/r4_risk_features.jsonl
```

Required feature groups:

```text
prefill domain prediction / margin
entropy_final_logits stats
selected_token_prob stats
topk_mass_or_margin stats
windowed domain-shift stats
low-confidence / high-entropy spike counts
```

Do not include drift fields in model features.

### Step 4 — train/eval skeleton

Create:

```text
src/train_risk_heads.py
src/eval_risk_heads.py
```

Baselines:

```text
logistic regression with calibration
linear SVM with calibration
tiny MLP with calibration
hand-score baseline for comparison only
```

Required behavior:

```text
If labels are missing, all-null, or below minimum count, refuse to train with a clear error.
```

Metrics:

```text
AUROC
AUPRC
ECE
false-low-risk rate
false-high-risk rate
latency
```

### Step 5 — operator labeling handoff

Create:

```text
LABELING_HANDOFF.md
```

It should explain each label, how to label uncertain cases, how many examples are needed, and why false-low-risk matters more than false-high-risk.

## Stop condition

Stop when all are true:

```text
risk label schema exists
label scaffold exists and validates
feature extractor exists and excludes drift
train/eval skeleton exists and refuses unlabeled data
operator labeling handoff exists
STATE.md and reports/FINDINGS.md updated
all commits made
```

Do not train final heads until human-approved labels exist.

## Repository hygiene

Ensure `.gitignore` includes:

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
*.pt
data/captures/
logs/
.venv/
```

## Final architecture

```text
RouterGuard:
  prefill routing signatures and domain priors

DecodeGuard:
  entropy, selected-token confidence, router concentration, windowed mode shift

PolicyEngine:
  calibrated risk heads and route decisions

HiddenLens:
  future phase only after M3 is validated
```
