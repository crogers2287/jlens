# M23 within-model telemetry/outcome validation

M23 removes M22's cross-model confound. The same local Qwen decode supplied both
the internal logits/router telemetry and the output evaluated by the existing
verifier/action pipeline. Results remain descriptive candidate evidence.

## Predeclared design

`data/prompts/m23_manifest.json` was committed as the run contract before any M23
telemetry was inspected. It selects 32 existing public task IDs:

| Predeclared group | n |
|---|---:|
| deterministic checker candidates | 8 |
| current-info/retrieval candidates | 8 |
| open-explain/review candidates | 8 |
| no-action controls | 8 |

The five telemetry features and four comparisons were fixed in code before the
run: decode entropy, selected-token probability, top-k margin, router entropy,
and expert concentration; checker/retrieval/review need plus checker fail/pass.
Effects require at least four rows in both groups.

## Approved runtime

- Model: the existing local Qwen1.5-MoE-A2.7B-Chat checkpoint from M22.
- Resolution: local files only, remote code disabled.
- Hardware: BF16 across the two 24 GiB RTX 3090 GPUs with a 20 GiB/GPU cap; no
  CPU or disk offload.
- Input: tokenizer chat template with an assistant-generation marker.
- Output: greedy decode, up to 64 tokens, router-only telemetry.
- Serving lifecycle: llama-swap was temporarily unloaded; `agents-a1` was
  restored afterward and verified by a live response and its prior GPU residency.

The local workflow is:

```bash
export JLENS_HF_MODEL=/absolute/local/path/to/Qwen1.5-MoE-A2.7B-Chat

.venv/bin/python src/m23_within_model.py --prepare-only

.venv/bin/python src/capture_router_logits.py \
  --model "$JLENS_HF_MODEL" \
  --prompts reports/shadow/private/m23_hf_prompts_local.jsonl \
  --out data/captures/m23_qwen15_moe \
  --dtype bf16 --max-gpu-mem-gib 20 --router-only --chat-template \
  --max-new-tokens 64 --limit 32

.venv/bin/python src/m23_within_model.py --model-ref "$JLENS_HF_MODEL"
```

Each `.pt` capture is resume-safe and ignored. Its decoded output is supplied to
the existing supervisor, deterministic verifiers, action router, and allowlisted
action executor. Only bounded previews enter the ignored runtime record; action
and telemetry records contain IDs/enums/hashes/numeric aggregates.

## Completion and capability

- 32/32 same-run captures completed.
- Logits telemetry was available 32/32.
- Real 24-layer, 60-expert router telemetry was available 32/32.
- Hidden telemetry was disabled 32/32.
- Actual routing exactly matched the predeclared split: 8 checker, 8 retrieval,
  8 review, and 8 no-action.
- Allowlisted execution completed 8 deterministic checks and 8 fixture retrievals;
  review/no-action remained intentionally unautomated.
- Arithmetic checker results were 7 pass / 1 fail.

Nine rows reached the 64-token cap: three retrieval and six review candidates.
All eight checker outputs reached EOS before the cap. Retrieval routing is driven
by current-info metadata and review routing by the existing no-rubric/low-confidence
path, so capped prose does not alter those action labels. It does mean M23 does not
claim complete generated answers for all 32 tasks.

## Descriptive alignment

The actual action groups each have n=8 positive and n=24 negative, so the frozen
descriptive effects were emitted:

| Positive group | Feature | Mean difference | Hedges g | Bootstrap 95% interval |
|---|---|---:|---:|---:|
| checker-needed | decode entropy | -0.1311 | -1.0637 | [-0.1975, -0.0556] |
| checker-needed | router entropy | +0.2004 | +1.8964 | [+0.1301, +0.2655] |
| checker-needed | expert concentration | -0.0455 | -1.9319 | [-0.0612, -0.0290] |
| retrieval-needed | router entropy | -0.1624 | -1.3696 | [-0.2230, -0.0989] |
| retrieval-needed | expert concentration | +0.0346 | +1.2755 | [+0.0201, +0.0482] |
| review-needed | router entropy | -0.1291 | -1.0170 | [-0.1946, -0.0571] |
| review-needed | expert concentration | +0.0260 | +0.8924 | [+0.0127, +0.0401] |

Retrieval/review logits effects had intervals spanning zero. The checker fail/pass
comparison was correctly withheld because its groups were n=1 fail and n=7 pass,
below the predeclared minimum of four per group.

These effects can reflect task category, prompt form, output length, or position
as well as action need. The action labels are largely determined by trusted task
metadata and verifier applicability. M23 therefore establishes same-run linkage
and repeatable descriptive separation, not independent predictive value, causal
features, thresholds, or production utility.

## Privacy and gating

Public reports contain only counts, distributions, group means/medians, effects,
and fixed-seed bootstrap intervals. They contain no task IDs, prompt/output/token
text, local paths, raw logits/router tensors, or model weights. The separate public
manifest contains only already-public task IDs and group names.

Private ignored artifacts include the selected prompt rows, 32 raw captures, 32
auto-outcome records, 32 action records/results, and 32 detailed telemetry records.
All outcome records remain candidates. No policy or threshold was fit. Production
remains gated.

Public artifacts:

- `data/prompts/m23_manifest.json`
- `reports/telemetry/hf_m23_same_run_summary.json`
- `reports/telemetry/hf_m23_within_model_alignment.json`
