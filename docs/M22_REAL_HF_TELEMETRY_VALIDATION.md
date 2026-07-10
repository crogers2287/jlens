# M22 real HF MoE telemetry validation

M22 validates the M21 HF/safetensors telemetry contract against real model
weights. It is a bounded research run, not a production-unlock result.

## Approved run

- Model: public `Qwen/Qwen1.5-MoE-A2.7B-Chat` checkpoint, resolved from an
  existing local safetensors directory after the operator approved a MoE model,
  GPU-first execution, model choice, download, and use of the Thor storage mount.
- Architecture: `qwen2_moe`, 24 layers, 60 experts, top-4 routing.
- Precision/hardware: BF16 across two 24 GiB RTX 3090 GPUs, with a 20 GiB
  per-GPU placement cap and no CPU or disk offload.
- Capture: eight existing M19 task IDs, four greedy decode steps per task,
  router-only mode. Hidden states were deliberately disabled.
- Storage: the approximately 27 GiB model directory remains outside the
  repository on the operator-approved Thor mount.

The local llama-swap model was unloaded for the capture window and successfully
restored afterward with an `agents-a1` response and its prior dual-GPU residency.

## Private environment contract

The absolute model path and detailed artifacts are local-only:

```bash
export JLENS_HF_MODEL=/absolute/local/path/to/Qwen1.5-MoE-A2.7B-Chat

.venv/bin/python src/m22_real_telemetry.py --prepare-only

.venv/bin/python src/capture_router_logits.py \
  --model "$JLENS_HF_MODEL" \
  --prompts reports/shadow/private/m22_hf_prompts_local.jsonl \
  --out data/captures/m22_qwen15_moe \
  --dtype bf16 --max-gpu-mem-gib 20 \
  --router-only --max-new-tokens 4 --limit 8

.venv/bin/python src/m22_real_telemetry.py --model-ref "$JLENS_HF_MODEL"
```

All Transformers config/tokenizer/model resolutions use
`local_files_only=true`; remote code remains disabled. The command does not
persist full vocabulary logits. The private capture files contain input token
IDs, generated token text, and raw router tensors and therefore stay under the
gitignored `data/captures/` path. Converted detailed schema records stay under
`reports/shadow/private/`.

## Real capture result

All eight records completed:

| Signal | Result |
|---|---:|
| Logits telemetry available | 8 / 8 |
| Router telemetry available | 8 / 8 |
| Hidden telemetry disabled | 8 / 8 |
| Decode steps | 4 per task |
| Router output | 24 layers × 60 experts |
| Auto-outcome alignment | 8 / 8 |
| Action-result alignment | 8 / 8 |
| Grounded-result alignment | 1 / 8 |
| Reviewed-outcome alignment | 1 / 8 |

The public aggregate mean decode-window entropy was 1.1563 nats, mean final
selected-token probability was 0.7778, mean router entropy was 3.4283, and mean
expert concentration was 0.1667. These values describe this selected four-token
window only.

## Outcome alignment

The batch intentionally contains two checker-needed tasks, one retrieval-needed
task, one review-needed task, and four no-action tasks.

The internal telemetry is from Qwen, but the aligned auto/action/grounded/review
records were produced by `agents-a1` on the shared task IDs. This is therefore a
cross-model comparison of telemetry with task-demand labels. It does not test
whether Qwen telemetry predicts errors made by Qwen itself.

- Checker-needed versus not-needed showed mean decode entropy 0.6767 versus
  1.3162 and final selected-token probability 0.6943 versus 0.8056.
- Router entropy for checker-needed versus not-needed was almost unchanged:
  3.4300 versus 3.4277.
- Retrieval and review each have only one positive row. Their apparent gaps are
  individual examples, not group evidence.
- The selected checker pair contains one pass and one known fail candidate, but
  two rows cannot measure failure prediction.

This is observable separation only. It does not establish predictive value,
thresholds, calibration, causality, or production usefulness. A larger,
predeclared within-model run with Qwen outputs, Qwen-specific verifier/action
outcomes, and enough positive retrieval/checker/review rows is required before
fitting or evaluating a telemetry policy.

## Privacy and safety

Public files contain distributions, counts, and group means only. They contain no
task IDs, prompt/output/generated-token text, model path, raw logits, hidden
vectors, router vectors, or weights. Model references in detailed schema records
are hashed. `auto_outcome`, `action_result`, `grounded_result`, and reviewed rows
remain candidate evidence; production remains gated.

Public artifacts:

- `reports/telemetry/hf_m22_real_summary.json`
- `reports/telemetry/hf_m22_alignment.json`

Private ignored artifacts:

- selected prompt batch
- eight raw `.pt` captures
- eight detailed `hf_telemetry_record_v1` JSONL records
- absolute model/cache/storage paths
