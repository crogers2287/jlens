# GOLD_DATASET_SOURCE_PLAN.md

Purpose: identify public, human-verified or benchmark-verified datasets that can be treated as gold or benchmark-gold for jlens risk-head training.

Important distinction:

```text
benchmark-gold = trusted for the original dataset task/label
project-gold = audited and confirmed to match jlens risk_labels_v1 semantics
```

Use benchmark-gold immediately for prototype and serious training. Reserve final operating thresholds for project-gold or benchmark-gold with a small local audit.

## Label source tiers

```text
bronze = deterministic rules or dataset metadata
benchmark-gold = public dataset labels created/verified by humans for their original task
silver = frontier-model judge labels
gold = local human-audited labels for jlens semantics
```

Training policy:

```text
prototype training: bronze + benchmark-gold + silver
serious risk-head training: benchmark-gold + gold-audited silver
final calibration thresholds: gold or benchmark-gold with local audit sample
```

## Best public benchmark-gold sources by jlens label

### unsupported_or_hallucinated

Primary sources:

```text
HaluEval / HaluEval-Wild
TruthfulQA
SimpleQA
FEVER
SciFact
```

Mapping:

```text
HaluEval hallucinated -> unsupported_or_hallucinated=true
HaluEval non-hallucinated -> unsupported_or_hallucinated=false
TruthfulQA false/myth answer -> unsupported_or_hallucinated=true
TruthfulQA truthful answer -> unsupported_or_hallucinated=false
SimpleQA incorrect -> unsupported_or_hallucinated=true
SimpleQA correct -> unsupported_or_hallucinated=false
FEVER/SciFact refuted -> unsupported_or_hallucinated=true
FEVER/SciFact supported -> unsupported_or_hallucinated=false
```

Notes:

```text
- SimpleQA is ideal for short factuality and know-what-you-know behavior.
- FEVER/SciFact are claim-level, not freeform-answer-level, so converter should preserve source_task.
```

### needs_exact_citation

Primary sources:

```text
FEVER
SciFact
Climate-FEVER
Poly-FEVER
source-grounded QA datasets
```

Mapping:

```text
claim verification with evidence requirement -> needs_exact_citation=true
source-grounded QA requiring evidence -> needs_exact_citation=true
ordinary closed-book QA -> needs_exact_citation=false only if stable and non-high-stakes
```

### needs_current_info

Primary sources:

```text
BrowseComp
GAIA-style web/tool tasks
Fresh/current-event QA datasets where license permits
custom dated-current prompts
```

Mapping:

```text
requires browsing/current lookup -> needs_current_info=true
stable timeless prompt -> needs_current_info=false
```

Notes:

```text
This label is partly time-relative. Store dataset date and cutoff assumptions.
```

### needs_math_verification

Primary sources:

```text
GSM8K
MATH
MathQA
AQuA
SVAMP
```

Mapping:

```text
numeric/math word problem -> needs_math_verification=true
known correct solution/answer -> can evaluate unsupported_or_hallucinated for model output
non-math prompt -> needs_math_verification=false
```

### needs_code_execution

Primary sources:

```text
HumanEval
MBPP
BigCodeBench
DS-1000
SWE-bench style tasks
```

Mapping:

```text
requires writing/fixing executable code -> needs_code_execution=true
unit tests pass -> unsupported_or_hallucinated=false for code correctness
unit tests fail -> unsupported_or_hallucinated=true for code correctness
concept-only code explanation -> needs_code_execution=false
```

### high_stakes_or_sensitive

Primary sources:

```text
BeaverTails
PKU-SafeRLHF
medical exam / medical QA datasets
legal/tax/finance custom packs
construction/electrical/fire-safety custom packs
```

Mapping:

```text
safety meta-label or harm category present -> high_stakes_or_sensitive=true
ordinary benign prompt -> high_stakes_or_sensitive=false
```

Notes:

```text
Use public safety datasets as gold for generic safety classes. Add custom construction/battery/permitting packs for this user's practical domains.
```

### context_attack_present

Primary sources:

```text
prompt-injection benchmark datasets
indirect prompt-injection / RAG injection datasets
custom benign-vs-injected context packs
```

Mapping:

```text
context contains instruction trying to override trusted task -> context_attack_present=true
ordinary context -> context_attack_present=false
```

Notes:

```text
Prefer datasets that distinguish user instruction from untrusted external context.
```

### format_or_tool_mode_shift

Primary sources:

```text
BFCL / function-calling benchmarks
JSON-mode / structured-output datasets
tool-use benchmarks
custom format-control prompts
```

Mapping:

```text
output violates requested format -> format_or_tool_mode_shift=true
output matches requested format -> format_or_tool_mode_shift=false
```

Notes:

```text
This usually requires generating output from the target local model and then grading it. Public datasets provide expected format; the label applies to the target model's output.
```

### needs_user_file_context

Primary sources:

```text
repo issue datasets
SWE-bench style repository-context tasks
DocVQA / document QA style tasks
custom prompts referencing attached/missing files
```

Mapping:

```text
requires repo/file/document/context to answer -> needs_user_file_context=true
self-contained prompt -> needs_user_file_context=false
```

### answerable_from_memory

Primary sources:

```text
TruthfulQA
SimpleQA
MMLU-style stable knowledge sets
custom stable-vs-current prompt split
```

Mapping:

```text
stable fact/explanation answerable without tools -> answerable_from_memory=true
current/source/file/tool-dependent prompt -> answerable_from_memory=false
```

## Converter requirements

Every converter should emit records compatible with schema/risk_labels_v1.json plus metadata fields if schema evolves:

```text
prompt_id
source_dataset
source_split
source_record_id
source_label
source_license
label_source=benchmark_gold
label_confidence=1.0 unless source has uncertainty/inter-annotator metadata
labels.{...}=true/false/null
notes
```

If schema/risk_labels_v1.json cannot hold source metadata cleanly, create schema/risk_labels_v2.json rather than overloading notes.

## M4 updated objective

M4 should be renamed from silver-label ingestion to benchmark-label ingestion.

Deliverables:

```text
1. dataset source registry
2. source license/availability notes
3. converters for at least 3 benchmark-gold sources
4. frontier judge remains optional silver, not primary
5. coverage report by label/source/class balance
6. prototype risk-head training on benchmark-gold if coverage gate passes
7. final calibration remains gated on local audit/gold subset
```

Recommended first three converters:

```text
1. TruthfulQA or SimpleQA -> answerable_from_memory / unsupported_or_hallucinated
2. FEVER or SciFact -> needs_exact_citation / unsupported_or_hallucinated
3. GSM8K or HumanEval/MBPP -> needs_math_verification or needs_code_execution
```

Recommended second wave:

```text
BeaverTails or PKU-SafeRLHF -> high_stakes_or_sensitive
BFCL -> format_or_tool_mode_shift
prompt-injection benchmark -> context_attack_present
```
