# steer.md — post-M3 benchmark-gold steering

Read this first before continuing `jlens`.

M2 DecodeGuard is complete. M3 scaffolding is complete. The next phase should use existing human-verified public datasets wherever possible, not rely only on local hand labeling.

## Current state

Completed:

```text
M1: RouterGuard feasibility
M2: DecodeGuard telemetry and feature discovery
M3: risk-labeling scaffold and training gate
```

M3/M4 planning docs delivered:

```text
schema/risk_labels_v1.json
data/labels/risk_labels_seed.jsonl
src/build_label_scaffold.py
src/risk_features.py
reports/features/r4_risk_features.jsonl
src/train_risk_heads.py
src/eval_risk_heads.py
LABELING_HANDOFF.md
SILVER_LABEL_SOURCE_PLAN.md
GOLD_DATASET_SOURCE_PLAN.md
```

The current seed label file is intentionally all-null. Training correctly refuses all-null labels.

## Labeling tiers

Use four tiers:

```text
bronze = deterministic labels from rules or dataset metadata
silver = frontier-model judge labels
benchmark-gold = public human-verified benchmark labels for their original task
gold = local human-audited labels for jlens semantics
```

Policy:

```text
prototype training may use bronze + silver + benchmark-gold
serious risk-head training should prioritize benchmark-gold
final operating thresholds require gold or benchmark-gold with local audit
null is unknown, never false
label_source and confidence should be recorded on generated labels
```

## Working features

Keep these feature groups for future heads:

```text
entropy_final_logits
selected_token_prob
topk_mass_or_margin
prefill domain prediction and margin
windowed decode-domain shift
low-confidence and high-entropy counts
```

Exclude these from model features:

```text
drift_from_prefill_signature
drift_from_previous_token
drift_from_prefill_weighted
drift_from_previous_token_weighted
```

Reason: M2 showed drift does not track confidence. Keep drift only for provenance/debugging.

## Next milestone: M4 benchmark-gold ingestion

M4 should build source registry + converters for public benchmark-gold datasets first. Frontier-judge silver labels remain useful but should not be the primary source if human-verified benchmark labels exist.

Read:

```text
GOLD_DATASET_SOURCE_PLAN.md
SILVER_LABEL_SOURCE_PLAN.md
LABELING_HANDOFF.md
M3_RISK_LABELING.md
schema/risk_labels_v1.json
reports/features/r4_risk_features.jsonl
reports/FINDINGS.md
```

Suggested command:

```text
/jlens-benchmark-gold-loop
```

The loop should:

```text
1. Read steer.md first.
2. Read GOLD_DATASET_SOURCE_PLAN.md.
3. Build a dataset source registry with license/availability notes.
4. Add converters from benchmark datasets into risk_labels_v1 format.
5. Start with 3 high-value benchmark-gold sources.
6. Add coverage reports by label, class balance, source, and tier.
7. Add local-audit hooks so benchmark-gold can become project-gold.
8. Keep frontier-judge silver labeling as optional fallback/augmentation.
9. Allow prototype training on benchmark-gold only when coverage gate passes.
10. Keep final threshold calibration gated on gold or audited benchmark-gold.
11. Do not treat null as false.
12. Do not use drift as a model feature.
```

Recommended first converters:

```text
TruthfulQA or SimpleQA -> answerable_from_memory / unsupported_or_hallucinated
FEVER or SciFact -> needs_exact_citation / unsupported_or_hallucinated
GSM8K or HumanEval/MBPP -> needs_math_verification or needs_code_execution
```

Recommended second wave:

```text
BeaverTails or PKU-SafeRLHF -> high_stakes_or_sensitive
BFCL or tool-use datasets -> format_or_tool_mode_shift
prompt-injection benchmark -> context_attack_present
SWE-bench/GitHub issue tasks -> needs_user_file_context
BrowseComp/GAIA-style tasks -> needs_current_info
```

M4 deliverables:

```text
dataset source registry
at least 3 benchmark-gold converters
converted risk_labels JSONL outputs
coverage report by label/source/tier
prototype-training command that refuses weak coverage
audit-sampling script for benchmark-gold -> project-gold promotion
updated FINDINGS and STATE
```

M4 stop condition:

```text
benchmark-gold sources can populate a training set
coverage report shows class balance by label and source
prototype training is allowed only when coverage gate passes
final calibration remains gated on gold/audited benchmark-gold labels
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
