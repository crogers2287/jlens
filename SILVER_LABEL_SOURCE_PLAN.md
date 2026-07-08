# SILVER_LABEL_SOURCE_PLAN.md

Purpose: move past the idea that every M3 label must be hand-created from scratch.

Use three label tiers:

```text
bronze = deterministic labels from dataset metadata/rules
silver = frontier-model judge labels or public benchmark-derived labels
gold = human-reviewed labels
```

Training policy:

```text
- Prototype heads may train on bronze + silver.
- Final calibration and operating thresholds require gold or at least gold-audited samples.
- Never mix unknown/null with false.
- Keep label_source and label_confidence on every generated label record.
```

## Mapping public sources to jlens labels

### unsupported_or_hallucinated

Good seed sources:

```text
HaluEval / HaluEval-Wild
TruthfulQA
FEVER
SciFact / SciFact-Open
```

Mapping:

```text
HaluEval hallucinated answer -> unsupported_or_hallucinated=true
HaluEval faithful answer -> unsupported_or_hallucinated=false
TruthfulQA false answer -> unsupported_or_hallucinated=true
TruthfulQA truthful answer -> unsupported_or_hallucinated=false
FEVER supported -> unsupported_or_hallucinated=false
FEVER refuted / not-enough-info -> unsupported_or_hallucinated=true or needs_exact_citation=true depending task format
SciFact refuted / unsupported -> unsupported_or_hallucinated=true
```

### needs_exact_citation

Good seed sources:

```text
FEVER
SciFact / SciFact-Open
document QA / grounded QA datasets
long-context grounding datasets
```

Mapping:

```text
claim verification or source-grounded QA -> needs_exact_citation=true
ordinary stable knowledge QA -> needs_exact_citation=false
```

### needs_current_info

Good seed sources:

```text
BrowseComp
GAIA-style web/tool tasks
Fresh/current-event QA sets if license permits
custom generated current-info prompts
```

Mapping:

```text
requires web/current lookup -> needs_current_info=true
stable timeless explanation -> needs_current_info=false
```

### needs_math_verification

Good seed sources:

```text
GSM8K
MATH
MathQA
AQuA
```

Mapping:

```text
math problem with checkable numeric/symbolic answer -> needs_math_verification=true
concept-only math explanation -> needs_math_verification=false
```

### needs_code_execution

Good seed sources:

```text
HumanEval
MBPP
BigCodeBench
SWE-bench style tasks
DS-1000
```

Mapping:

```text
write/fix/verify runnable code -> needs_code_execution=true
explain concept without code execution -> needs_code_execution=false
```

### high_stakes_or_sensitive

Good seed sources:

```text
BeaverTails
PKU-SafeRLHF
medical QA sets
legal/tax/finance prompt sets
construction/electrical/fire-safety custom prompts
```

Mapping:

```text
medical/legal/finance/safety-critical -> high_stakes_or_sensitive=true
ordinary creative/general task -> high_stakes_or_sensitive=false
```

### context_attack_present

Good seed sources:

```text
public prompt-injection/context-injection datasets
DataFilter-style simulated injection datasets
custom benign-vs-context-attack prompt packs
```

Mapping:

```text
context contains instruction trying to override the user/developer task -> context_attack_present=true
ordinary context with no override attempt -> context_attack_present=false
```

### needs_user_file_context

Good seed sources:

```text
custom prompts based on repo/file/screenshot references
GitHub issue tasks where the repository context is required
user-file QA synthetic scaffolds
```

Mapping:

```text
prompt refers to attached/missing/local/project file context -> needs_user_file_context=true
self-contained prompt -> needs_user_file_context=false
```

### format_or_tool_mode_shift

Good seed sources:

```text
BFCL / function-calling tasks
JSON-mode tasks
tool-use tasks
code-vs-prose format prompts
custom format-control prompts
```

Mapping:

```text
output violates requested format or unexpectedly changes mode -> format_or_tool_mode_shift=true
output format matches requested mode -> format_or_tool_mode_shift=false
```

### answerable_from_memory

Good seed sources:

```text
TruthfulQA stable questions
MMLU-style stable knowledge prompts
simple educational QA
custom stable vs current split
```

Mapping:

```text
stable timeless fact/explanation -> answerable_from_memory=true
current/local/source-dependent/user-file-dependent prompt -> answerable_from_memory=false
```

## Frontier judge use

Use a frontier model as a silver-label judge with strict rubric output:

```json
{
  "labels": {
    "answerable_from_memory": true,
    "needs_current_info": false,
    "needs_exact_citation": false,
    "needs_math_verification": false,
    "needs_code_execution": false,
    "needs_user_file_context": false,
    "high_stakes_or_sensitive": false,
    "context_attack_present": false,
    "unsupported_or_hallucinated": null,
    "format_or_tool_mode_shift": null
  },
  "confidence": 0.0,
  "rationale": "short reason",
  "label_source": "frontier_judge_v1"
}
```

Rules:

```text
- prompt-time labels can be judged from prompt alone.
- generation-time labels require model output.
- use null when the judge cannot know.
- run at least two different judges or judge prompts for silver+.
- disagreement goes to null or human review.
```

## M4 objective

Build a label-ingestion pipeline, not final policy.

Tasks:

```text
1. Add a source registry file for public/benchmark/synthetic sources.
2. Add converters that map source rows into risk_labels_v1 records.
3. Add a frontier-judge silver-labeler that writes label_source/confidence.
4. Add agreement checks: bronze vs silver vs gold.
5. Add coverage reports by label and source.
6. Train only prototype heads on silver labels.
7. Reserve calibration thresholds for gold or gold-audited labels.
```

M4 stop condition:

```text
public/silver label sources can populate a training set
coverage report shows class balance by label
prototype training is allowed on silver labels
final calibration remains gated on gold/gold-audited labels
```
