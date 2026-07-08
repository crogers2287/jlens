# steer.md — post-M3 silver-label steering

Read this first before continuing `jlens`.

M2 DecodeGuard is complete. M3 scaffolding is complete. The next phase should not assume every label must be created manually from scratch.

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
SILVER_LABEL_SOURCE_PLAN.md
```

The current seed label file is intentionally all-null. Training correctly refuses all-null labels.

## Labeling policy

Use three tiers:

```text
bronze = deterministic labels from dataset metadata or rules
silver = public benchmark labels or frontier-model judge labels
gold = human-reviewed labels
```

Policy:

```text
prototype training may use bronze + silver
final calibration and production thresholds require gold or gold-audited labels
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

## Next milestone: M4 silver-label ingestion

M4 should build label sources and converters, not final production policy.

Read:

```text
SILVER_LABEL_SOURCE_PLAN.md
LABELING_HANDOFF.md
M3_RISK_LABELING.md
schema/risk_labels_v1.json
reports/features/r4_risk_features.jsonl
reports/FINDINGS.md
```

Suggested command:

```text
/jlens-silver-label-loop
```

The loop should:

```text
1. Read steer.md first.
2. Read SILVER_LABEL_SOURCE_PLAN.md.
3. Build a source registry for public datasets and frontier-judge labelers.
4. Add converters from source datasets into risk_labels_v1 format.
5. Add frontier-judge silver-label pipeline with strict JSON output.
6. Add agreement checks: bronze vs silver vs gold.
7. Add coverage reports by label, class balance, and source.
8. Allow prototype training on bronze+silver labels only when coverage is adequate.
9. Keep final threshold calibration gated on gold or gold-audited labels.
10. Do not treat null as false.
11. Do not use drift as a model feature.
```

Potential source families:

```text
hallucination / unsupported claims: HaluEval, HaluEval-Wild, TruthfulQA
fact verification / citation: FEVER, SciFact, SciFact-Open
current-info / web-needed: BrowseComp, GAIA-style tasks, custom current prompt packs
math verification: GSM8K, MATH, MathQA, AQuA
code execution: HumanEval, MBPP, BigCodeBench, SWE-bench style tasks, DS-1000
high-stakes or sensitive: BeaverTails, PKU-SafeRLHF, domain-specific custom prompts
context attack detection: public prompt/context-injection datasets, custom benign/adversarial context packs
format or tool mode: BFCL, JSON/tool-use tasks, custom format-control prompts
user file context: GitHub issue tasks, repo/file/screenshot reference prompts
```

M4 deliverables:

```text
label source registry
public-source converters
frontier silver-label judge prompt/spec
silver-label JSONL output
coverage report
prototype-training command that refuses weak coverage
updated FINDINGS and STATE
```

M4 stop condition:

```text
public/silver sources can populate a training set
coverage report shows class balance by label and source
prototype training is allowed only when coverage gate passes
final calibration remains gated on gold/gold-audited labels
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
