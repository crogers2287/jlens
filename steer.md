# steer.md — post-M4 steering

Read this first before continuing `jlens`.

M1, M2, M3, and M4 are complete. Do not restart benchmark-gold ingestion from scratch.

## Current state

Completed:

```text
M1: RouterGuard feasibility
M2: DecodeGuard telemetry and feature discovery
M3: risk-labeling scaffold and training gate
M4: benchmark-gold ingestion foundation
```

M4 delivered:

```text
data/registry/benchmark_sources.json
schema/risk_labels_v2.json
src/convert_truthfulqa.py
src/convert_fever.py
src/convert_gsm8k.py
data/labels/benchmark/truthfulqa.jsonl
data/labels/benchmark/fever.jsonl
data/labels/benchmark/gsm8k.jsonl
src/coverage_report.py
reports/coverage/benchmark_coverage.json
src/audit_sample.py
data/labels/audit_queue.jsonl
train_risk_heads.py tier/coverage gate updates
```

Benchmark-gold records currently ingested:

```text
TruthfulQA: 5,918 records
FEVER:      15,935 records
GSM8K:       1,319 records
Total:      23,172 records
```

Coverage gate result:

```text
PASS:
  answerable_from_memory
  unsupported_or_hallucinated

FAIL / needs more data:
  needs_current_info
  needs_exact_citation
  needs_math_verification
  needs_code_execution
  needs_user_file_context
  high_stakes_or_sensitive
  context_attack_present
  format_or_tool_mode_shift
```

Important: benchmark labels alone are not enough to train the actual telemetry risk heads. The risk heads need matching feature rows from the target model. Labels and telemetry must join by `prompt_id`.

## Working features

Keep these feature groups:

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

## Next milestone: M5 benchmark telemetry + prototype head

M5 should turn the ingested benchmark labels into actual trainable examples by capturing target-model telemetry for a balanced benchmark subset.

Suggested command:

```text
/jlens-m5-benchmark-telemetry-loop
```

Read first:

```text
steer.md
reports/FINDINGS.md
reports/coverage/benchmark_coverage.json
schema/risk_labels_v2.json
data/registry/benchmark_sources.json
GOLD_DATASET_SOURCE_PLAN.md
M3_RISK_LABELING.md
LABELING_HANDOFF.md
```

M5 objectives:

```text
1. Build benchmark prompt exporter.
2. Export balanced prompt packs for the two currently covered labels.
3. Capture router-only decode telemetry for that subset.
4. Export decode schema / v3 weighted schema as needed.
5. Build risk_features for benchmark prompt_ids.
6. Join benchmark labels to matching feature rows.
7. Replace trainer stub with real prototype training/eval for covered labels.
8. Preserve final calibration gate: final mode still requires gold/audited labels.
```

Recommended first target:

```text
prototype labels:
  answerable_from_memory
  unsupported_or_hallucinated

sources:
  TruthfulQA
  FEVER
  GSM8K for answerable_from_memory negatives
```

Do not try to capture all 23k records first. Start with a balanced sample:

```text
200-500 examples per class if runtime is acceptable
or smaller smoke test first
```

The benchmark prompt exporter must either:

```text
- reconstruct prompts from source datasets by source_record_id, or
- create a derived prompt pack with only permitted text under source license rules
```

Do not commit restricted raw datasets. Keep raw caches under `data/raw/` and gitignored.

## M5 deliverables

```text
src/build_benchmark_prompts.py
data/prompts/benchmark_m5_sample.jsonl or equivalent
capture command docs for router-only decode
reports/features/benchmark_m5_features.jsonl
label-feature join report
real train/eval implementation for prototype mode
prototype metrics for covered labels
updated STATE.md and reports/FINDINGS.md
```

M5 stop condition:

```text
benchmark labels and telemetry features join by prompt_id
prototype training runs for at least one covered label
metrics are reported honestly
final mode remains gold-gated
raw captures and raw datasets remain uncommitted
```

## Next data expansion after M5 smoke/prototype

Add second-wave converters to cover the 8 failing labels:

```text
HumanEval or MBPP -> needs_code_execution
GAIA or BrowseComp -> needs_current_info
SWE-bench -> needs_user_file_context
BFCL -> format_or_tool_mode_shift
prompt-injection benchmark -> context_attack_present
BeaverTails or PKU-SafeRLHF -> high_stakes_or_sensitive
stable closed-book QA -> needs_exact_citation false examples
non-math stable QA -> needs_math_verification false examples
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
