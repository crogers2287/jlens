# steer.md — DecodeGuard / RouterGuard execution plan

This file is the steering document for the next agent loop. It should be read before continuing `jlens` work.

The repo has already proven that Qwen3.6-35B-A3B router signatures carry useful semantic signal. Stop re-proving that. The next work is generation-time reliability: whether decode-step routing drift, final-logit entropy, and selected-token confidence can predict hallucination risk, mode shifts, prompt-injection compliance, or need for retrieval.

## Current project state

Known-good results:

- Prefill router signatures classify prompt domain strongly.
- Token-level router features retain domain signal under prompt-held-out splits.
- Multi-layer routing beats single-layer routing.
- Router-only sidecar inference is sub-millisecond.
- `capture_router_logits.py --max-new-tokens > 0` now performs real greedy decode.
- Decode steps include per-token router logits, final-logit entropy, selected-token probability, generated token id, and generated token text.
- `schema/v2_decode.json` exists for one-record-per-generated-token export.
- `src/export_decode_schema.py` exists and computes drift from prefill and drift from previous token.
- r4 decode capture has been launched for 32 prompts x 32 generated tokens.

Core interpretation:

```text
RouterGuard is feasible.
DecodeGuard is the active research front.
The next discovery is whether generation-time routing drift predicts unreliable output.
```

## North star

Build a local inference governor for sparse MoE models.

Target runtime logic:

```text
prompt
  -> prefill router signature
  -> domain / task / risk prior
  -> decode-step router telemetry
  -> drift + entropy + confidence features
  -> calibrated risk head
  -> policy decision
```

Policy actions:

```text
low risk      -> normal local decode
medium risk   -> conservative decode + self-check
high risk     -> force retrieval/tool verification
critical risk -> block autonomous tool action or require grounded path
```

Do not describe this as mind-reading, consciousness, or hidden thoughts. This is model-internal telemetry for local inference reliability.

## Required loop behavior

Before starting the next implementation loop, update the loop prompt using `/prompt-master`.

The loop should generate or update its own command prompt, then execute from that prompt.

Required instruction to the agent:

```text
Use /prompt-master to create or update a dedicated jlens DecodeGuard loop prompt. The loop prompt must tell the agent to:

1. Read steer.md, STATE.md, ROADMAP.md, SCHEMA.md, schema/v2_decode.json, and recent reports before coding.
2. Continue from the latest completed M2 item, not from stale assumptions.
3. Treat r4 decode export/validation as the current hard gate.
4. Commit after each completed item with a precise message.
5. Update STATE.md and reports/FINDINGS.md after each item.
6. Stop at the specified stop condition instead of inventing new work.
7. Never commit raw .pt captures, logs, caches, or __pycache__ artifacts.
```

Suggested loop command name:

```text
/jlens-decodeguard-loop
```

Suggested loop prompt body:

```text
You are continuing jlens DecodeGuard. Read steer.md first. Then read STATE.md, ROADMAP.md, SCHEMA.md, schema/v2_decode.json, and reports/FINDINGS.md. Determine the latest completed M2 item from STATE.md and continue from the next incomplete item.

Primary objective: complete DecodeGuard M2 through r4 export, drift analysis, router-only decode optimization, and the first calibrated risk-head dataset plan.

Rules:
- Do not restart from older r2/r3 assumptions.
- Do not re-run expensive GPU captures unless required.
- Do not start HiddenLens/Jacobian work.
- Do not do expert pruning or ablation.
- Do not hand-write final policy thresholds except as baselines.
- Do not commit .pt captures, logs, __pycache__, or local environment files.
- Commit each completed item separately.
- Update STATE.md and reports/FINDINGS.md after each completed item.
- When blocked by GPU/runtime state, write the exact command to resume and stop cleanly.

Stop condition: stop after producing a validated r4 decode drift report and a concrete M3 risk-labeling plan, unless explicitly told to continue.
```

## Execution plan

### Step 0 — refresh repository state

Goal: avoid stale assumptions.

Actions:

```bash
git status
git log --oneline -12
find . -maxdepth 3 -type f | sort
```

Read:

```text
steer.md
STATE.md
ROADMAP.md
SCHEMA.md
schema/v1.json
schema/v2_decode.json
reports/FINDINGS.md
reports/qwen3_6_35b_a3b_r3_bakeoff.json
reports/qwen3_6_35b_a3b_r3_token_probe_sgkf.json
```

Exit criteria:

```text
The loop knows the latest completed item and the next incomplete item.
```

### Step 1 — finish or resume r4 decode capture

Goal: complete M2 item 4.

Expected capture directory:

```text
data/captures/qwen3_6_35b_a3b_r4_decode/
```

Expected target:

```text
32 prompt .pt files, each with decode_steps, up to 32 generated tokens each
```

Actions:

```bash
ls -lh data/captures/qwen3_6_35b_a3b_r4_decode || true
find data/captures/qwen3_6_35b_a3b_r4_decode -name '*.pt' | wc -l
```

If the process is still running, poll until complete. If dead and incomplete, inspect log and resume only missing prompts if the script supports it. If the script does not support resume, add resume-skip behavior before rerunning:

```text
If output file for prompt_id exists and loads successfully, skip it.
```

Required improvement if not already present:

```text
capture_router_logits.py should skip existing valid captures unless --overwrite is set.
```

Exit criteria:

```text
r4 decode capture has all expected prompt files or a documented reason for fewer.
STATE.md updated.
reports/FINDINGS.md updated.
Commit made.
```

Commit message:

```text
M2 item 4: complete r4 decode capture
```

### Step 2 — export and validate decode schema

Goal: produce compact, shareable decode telemetry.

Command:

```bash
python src/export_decode_schema.py \
  data/captures/qwen3_6_35b_a3b_r4_decode \
  --run-id r4 \
  --top-k 8 \
  --out reports/schema/r4_decode.jsonl
```

Add a validator script if absent:

```text
src/validate_jsonl_schema.py
```

Required behavior:

```bash
python src/validate_jsonl_schema.py \
  --schema schema/v2_decode.json \
  --jsonl reports/schema/r4_decode.jsonl
```

Validation script requirements:

```text
- load JSON Schema draft-07
- validate every JSONL line
- print count of valid records
- fail nonzero on first invalid line
```

Exit criteria:

```text
reports/schema/r4_decode.jsonl exists.
Every line validates against schema/v2_decode.json.
Record count is reported.
STATE.md updated.
reports/FINDINGS.md updated.
Commit made.
```

Commit message:

```text
M2 item 4: export and validate r4 decode schema
```

### Step 3 — implement decode drift analysis

Goal: convert r4 decode telemetry into the first useful DecodeGuard report.

Create:

```text
src/decode_drift.py
reports/qwen3_6_35b_a3b_r4_decode_drift.json
```

Command:

```bash
python src/decode_drift.py \
  reports/schema/r4_decode.jsonl \
  --json reports/qwen3_6_35b_a3b_r4_decode_drift.json
```

Required metrics:

```text
n_records
n_prompts
n_domains
mean/max drift_from_prefill_signature
mean/max drift_from_previous_token
mean/max entropy_final_logits
mean/min selected_token_prob
by_domain summary
by_token_index summary
correlation: drift_prefill vs entropy_final_logits
correlation: drift_prefill vs selected_token_prob
correlation: drift_previous vs entropy_final_logits
correlation: drift_previous vs selected_token_prob
top drift_from_prefill spikes
top drift_from_previous spikes
top entropy spikes
lowest selected-token probability records
```

Spike records must include:

```json
{
  "prompt_id": "math_01",
  "domain": "math",
  "generated_token_index": 12,
  "generated_token_text": "...",
  "drift_from_prefill_signature": 0.0,
  "drift_from_previous_token": 0.0,
  "entropy_final_logits": 0.0,
  "selected_token_prob": 0.0
}
```

Exit criteria:

```text
Drift report exists.
The report identifies top spike tokens.
STATE.md updated.
reports/FINDINGS.md updated.
Commit made.
```

Commit message:

```text
M2 item 5: add r4 decode drift analysis
```

### Step 4 — manual interpretation pass

Goal: decide whether drift is informative enough to justify risk labels.

Create:

```text
reports/qwen3_6_35b_a3b_r4_decode_drift_notes.md
```

Manual questions:

```text
Do high drift tokens correspond to visible mode shifts?
Do high drift tokens correspond to code block starts, JSON starts, language shifts, math transitions, or factual claims?
Do entropy spikes overlap with drift spikes?
Do low selected-token probability tokens overlap with drift spikes?
Are drift spikes domain-specific?
Are first-token drifts systematically high and therefore less useful?
Does drift stabilize after the first few generated tokens?
```

Exit criteria:

```text
A short interpretation note exists.
The note states whether drift is useful, weak, or inconclusive.
Commit made.
```

Commit message:

```text
M2 item 5: interpret r4 drift spikes
```

### Step 5 — add router-only decode mode

Goal: make future captures faster and cheaper.

Problem: r4 decode was CPU-offload/PCIe-bound and slow. For DecodeGuard, hidden states are not required.

Add flags to `capture_router_logits.py`:

```text
--router-only
--no-hidden-states
--overwrite
```

Required behavior:

```text
--router-only means output_hidden_states=False and do not store hidden_states.
--no-hidden-states is an alias or clearer explicit flag.
--overwrite controls whether existing .pt files are replaced.
Default behavior preserves backward compatibility.
```

Payload rules:

```text
If hidden states were not requested, payload should omit hidden_states or set hidden_states=None.
Exporters must tolerate missing hidden_states.
```

Add/extend tests:

```text
tests/test_decode_capture.py
```

Test cases:

```text
prefill-only old path still works
decode path still works
router-only does not request/store hidden states
existing output skip works unless overwrite is set
```

Exit criteria:

```text
Tests pass.
STATE.md updated.
reports/FINDINGS.md updated.
Commit made.
```

Commit message:

```text
M2 optimization: add router-only decode capture mode
```

### Step 6 — add weighted drift features

Goal: distinguish expert-ID drift from confidence-weighted routing drift.

Extend decode export append-only.

Add fields to records if staying v2 append-only is acceptable:

```json
{
  "drift_from_prefill_weighted": 0.0,
  "drift_from_previous_token_weighted": 0.0,
  "topk_mass_or_margin": 0.0
}
```

If strict schema `additionalProperties: false` blocks append-only fields, create `schema/v3_decode.json` instead of mutating v2. Do not silently break v2 validation.

Weighted signature idea:

```text
For each layer, build a 256-dim vector using top-k probabilities instead of 1/k expert counts.
Concatenate layers.
Cosine distance against weighted prefill/decode signatures.
```

Exit criteria:

```text
Weighted drift export works.
Schema validates.
Drift analysis includes weighted/unweighted comparison.
Commit made.
```

Commit message:

```text
M2 item 5: add weighted decode drift features
```

### Step 7 — domain shift probe over decode tokens

Goal: detect whether generated tokens shift away from the prompt's prefill domain.

Approach:

```text
Train or reuse the r3 router sidecar domain head.
Apply it to decode-step routing signatures.
Compare:
  prefill_domain_label
  prefill_predicted_domain
  decode_step_predicted_domain
```

Derived features:

```text
prefill_label_vs_decode_pred_disagree
prefill_pred_vs_decode_pred_disagree
decode_domain_confidence
decode_domain_margin
number_of_domain_switches
first_domain_switch_token_index
```

Exit criteria:

```text
decode_domain_shift report exists.
Findings updated with whether domain-shift signal is meaningful.
Commit made.
```

Commit message:

```text
M2 item 5: add decode domain-shift probe
```

### Step 8 — create M3 risk-labeling plan

Goal: move from telemetry to supervised risk modeling.

Create:

```text
M3_RISK_LABELING.md
```

Required label taxonomy:

```text
answerable_from_memory
needs_current_info
needs_exact_citation
needs_math_verification
needs_code_execution
needs_user_file_context
unsafe_or_high_stakes
prompt_injection_present
unsupported_or_hallucinated
format_or_tool_mode_shift
```

Dataset design:

```text
At least 50 prompts per label family.
Prompt-held-out splits only.
Separate train/test prompt templates.
Include clean, adversarial, high-stakes, and tool-needed examples.
Include deliberately unanswerable factual questions.
Include current-events questions that require retrieval.
Include code/math prompts with known verifiable answers.
```

Risk-head features:

```text
prefill routing signature
prefill domain prediction
prefill entropy statistics
decode drift statistics
decode entropy statistics
selected token probability statistics
domain shift features
spike counts
low-confidence counts
```

Baseline models:

```text
logistic regression + calibration
linear SVM + calibration
tiny MLP + calibration
simple hand-score baseline for comparison only
```

Metrics:

```text
AUROC
AUPRC
ECE
false-low-risk rate
false-high-risk rate
latency per prompt
latency per decode token
```

Policy priority:

```text
False-low-risk is worse than false-high-risk.
Do not optimize only for accuracy.
```

Exit criteria:

```text
M3_RISK_LABELING.md exists.
It includes label definitions, data sources, model baselines, metrics, and stop conditions.
Commit made.
```

Commit message:

```text
Plan M3 risk-labeling dataset and calibrated heads
```

## Stop condition for this loop

Stop after all are true:

```text
r4 decode capture exported and validated
r4 decode drift report produced
drift notes written
router-only decode mode implemented or explicitly deferred with reason
M3_RISK_LABELING.md written
STATE.md and reports/FINDINGS.md updated
all commits made
```

Do not continue into HiddenLens, Jacobian Lens, SAE pruning, expert ablation, or production integration without explicit operator approval.

## Strong warnings

Do not overfit to 32 prompts.

Do not interpret drift as hallucination by itself.

Do not claim safety detection until labels exist.

Do not prune or ablate experts based on current overlap results.

Do not use hand-picked thresholds as final policy.

Do not treat generated token text alone as ground truth.

Do not commit large raw captures.

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

If cache files are tracked:

```bash
git rm -r --cached src/__pycache__
git commit -m "Remove Python cache artifacts"
```

## Final intended architecture

```text
RouterGuard
  prefill router signatures
  domain/risk priors

DecodeGuard
  per-generated-token router drift
  final-logit uncertainty
  selected-token confidence
  mode-shift detection

PolicyEngine
  calibrated risk heads
  local/retrieval/tool/block decisions

HiddenLens
  future phase only after router/decode baselines are exhausted
```

The immediate product is not a visualization. It is a local model reliability governor that decides when local inference is trustworthy, when it needs grounding, and when autonomous action should be blocked.
