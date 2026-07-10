# steer.md — post-M21 real HF telemetry validation gate

M1 through M21 are complete. Do not redo the GGUF supervisor, verifier, action,
grounded-regeneration, or fixture HF telemetry work.

`CODEX_AUTOSTEER.md` remains part of the operating contract.

## Autosteer mode

Default mode:

- Complete one milestone.
- Commit implementation.
- Update `steer.md` separately.
- Stop.

Loop mode requires `CODEX_AUTOSTEER_LOOP=true` or an explicit operator request.
Even in loop mode, stop for model downloads, licenses, local-path selection,
disk-space, or hardware/VRAM decisions.

## Current state

Completed milestones:

- M1–M20: practical local supervisor track through fixture-grounded regeneration
- M21: fixture-first HF/safetensors telemetry backend

M21 result:

- Added `hf_telemetry_record_v1` with aggregate numeric fields only.
- Added explicit backend separation:
  - GGUF runtime -> `auto_outcome_v1`, internal telemetry honestly missing
  - HF/safetensors -> `hf_telemetry_record_v1`
- Added no-download loader contract:
  - existing local safetensors directory, or
  - explicitly approved cached model ID
  - always `local_files_only=true`
  - always `trust_remote_code=false`
- Added logits-derived features:
  - selected token id/probability
  - entropy
  - top-k mass and margin
  - decode-window entropy/confidence counts and margin trend
- Added optional hidden-state aggregate summaries.
- Added honest router states: `available`, `not_moe`, `missing`, `unsupported`.
- Added router entropy, expert concentration, top expert IDs, and windowed expert
  shift when fixture telemetry actually exposes them.
- Fixture batch: 3 schema-valid records, zero weights loaded:
  - logits available 2 / missing 1
  - hidden available 1 / disabled 1 / missing 1
  - router available 1 / not_moe 1 / missing 1
- Outcome alignment flags: auto 2 / action 2 / grounded 1 / reviewed 0.
- Repository tracks no model weights/caches.
- Full suite green at 84 tests.
- Production remains gated.

## Required operator decision before M22

Do not start a real HF model run until the operator provides all of:

1. **Model kind:** dense or MoE.
2. **Model reference:**
   - an existing local directory containing safetensors, or
   - an explicitly approved model ID already available in the HF cache.
3. **Hardware plan:** CPU, one GPU, multiple GPUs, or approved offload strategy.
4. **Resource approval:** expected disk/RAM/VRAM footprint and permission to use it.

Do not download weights, accept a license, move caches, unload serving models, or
guess a model choice. If the reference is not already local/cached, stop.

Current live GGUF context remains unchanged:

- model: agents-a1
- endpoint: llama-swap port 9069 on fred
- hardware: dual 3090s
- GGUF telemetry: missing; `policy=null` when no feature row exists

## Next milestone: M22 real local HF telemetry validation

M22 should run the M21 backend against one operator-approved local/cached
safetensors model on a small shared task batch and test whether real internal
telemetry aligns with verifier/action outcomes.

### M22 objectives

1. Resolve the approved reference through `HFSafetensorsLoader` without network
   access.
2. Record the exact local model kind and hardware plan without committing paths,
   weights, cache locations, or secrets.
3. Run a bounded 8–32 task batch shared with existing public task IDs.
4. Capture real logits-derived telemetry and decode-window aggregates.
5. Capture hidden summaries only if explicitly enabled and affordable.
6. For a dense model, record router status `not_moe`.
7. For an MoE model, attempt router capture only through actual exposed outputs or
   documented hooks; otherwise record `missing` or `unsupported`.
8. Align telemetry with available auto/action/grounded/review outcomes by task ID.
9. Produce aggregate-only public summaries; keep prompts, outputs, raw tensors,
   paths, and detailed records private/ignored.
10. Report whether telemetry adds any observable separation for
    retrieval/checker/review needs. Do not claim predictive value from tiny-n.
11. Keep production gated.

### M22 deliverables

- local/private run config or documented environment contract
- real-model adapter additions, if required
- private schema-valid telemetry records
- public aggregate telemetry summary
- public alignment/comparison summary
- `docs/M22_REAL_HF_TELEMETRY_VALIDATION.md`
- tests for the selected architecture path and failure/degraded states
- updated `STATE.md` and `reports/FINDINGS.md`

### M22 stop condition

- approved model resolves without download
- bounded real telemetry run completes or reports an honest degraded blocker
- logits telemetry validates
- router state is honest for the architecture
- no model weights/cache/path/raw text/raw tensors are committed
- public artifacts pass commit-safety checks
- production remains gated

## Alternatives if the operator does not approve a real HF model

- M22C: broader GGUF model comparison using the M19/M20 harness
- M22D: improve open-ended explain verification with reference/rubric strategy
- M22E: larger grounded-regeneration run with question-specific public fixtures
- M22F: missing-label dataset converters

## Repository hygiene

Do not commit local detailed records, prompts, full outputs, raw tensors, model
paths, model IDs that reveal private infrastructure, model weights, tokenizer or
model caches, environments, or large generated artifacts unless explicitly
intended and public-safe.
