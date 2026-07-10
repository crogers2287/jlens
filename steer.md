# steer.md — post-M20 autosteer + HF telemetry steering

M1 through M20 are complete. Do not redo the previous harness, review, verifier, metadata-cleanup, action-routing, reviewed-calibration, safe-action-executor, full-output action-run, or grounded-regeneration work.

Codex autosteer is now configured. `CODEX_AUTOSTEER.md` is part of the operating contract. Read it before acting.

## Autosteer mode

Default mode:

- Complete one milestone.
- Commit implementation.
- Update `steer.md` for the next milestone.
- Commit steer update separately.
- Stop.

Loop mode:

- Only continue automatically when `CODEX_AUTOSTEER_LOOP=true` is explicitly set or the operator explicitly requests loop mode.
- Maximum 3 milestones or 4 wall-clock hours.
- Stop immediately on tests failing, commit-safety failure, private-data risk, model-download/hardware decision, real web retrieval decision, or any major architecture decision.

Required at each stop:

- latest commit SHA
- milestone completed
- tests passed
- public artifacts created
- private artifacts intentionally not committed
- next steer target
- blockers or decisions needed

## Current state

Completed milestones:

- M1 RouterGuard feasibility
- M2 DecodeGuard telemetry and feature discovery
- M3 risk-labeling scaffold and training gate
- M4 benchmark-gold ingestion foundation
- M5 end-to-end benchmark telemetry smoke prototype
- M6 PolicyEngine v0 advisory runtime
- M7 local wrapper and runtime records
- M8 review and calibration loop
- M9 local workflow and aggregate reporting
- M10 autonomous supervisor
- M11 first live Agents-A1 run
- M12 JSON verifier hardening and reviewed escalation calibration
- M13 110-task live Agents-A1 run
- M14 numeric-tolerant verifier and explain-rubric coverage
- M15 261-task live Agents-A1 run after verifier fixes
- M16 metadata cleanup and read-only action routing
- M17 reviewed calibration pass
- M18 safe action execution
- M19 500-task live run with transient full-output action execution
- M20 grounded regeneration after retrieval

M20 result:

- Added `grounded_result_v1` schema.
- Added explicit-opt-in `grounded_regenerator.py`.
- Processed 23 M19 retrieval candidates.
- 20/20 true current-info rows entered grounded regeneration and produced changed grounded answers.
- 3 non-current retrieval false positives were skipped before model invocation.
- Deterministic fixture expected-token check: 4 pass / 16 fail.
- Follow-up still needed on 19 rows: 16 fixture-token fails + 3 skipped non-current routes.
- Four M19 arithmetic miss candidates reviewed as confirmed wrong candidates, not gold.
- Freshness heuristic refined: bare weather/price/stock/news no longer trigger non-current tasks; explicit `current_info` still routes.
- Full suite green at 76 tests.
- Production remains gated.

Important M20 limitation:

- Fixture-grounded regeneration proves the path, not real-world correctness.
- The generic fixture context was not question-specific evidence.
- The 4/20 fixture-token match rate is a grounding/context-quality signal, not a model-quality score.
- No web retrieval, raw-text persistence, or production unlock was introduced.

Current live model context:

- model: agents-a1
- source: InternScience/Agents-A1-Q8_0-GGUF
- host: fred
- endpoint: llama-swap on port 9069
- hardware: dual 3090s

GGUF serving still has telemetry_missing=true and policy=null when no feature rows are available. Do not invent telemetry.

## Next milestone: M21 HF/safetensors telemetry backend

M21 should bring the original internal-telemetry research track back online without disrupting the working GGUF runtime supervisor. The goal is to add a Hugging Face / safetensors backend that can collect logits/entropy/top-k telemetry and, when available, router/expert telemetry. It must be honest about missing or unsupported telemetry.

Suggested command:

/jlens-m21-hf-safetensors-telemetry-backend

## M21 objectives

1. Add a backend abstraction that separates GGUF runtime records from HF/safetensors telemetry records.
2. Add a HF/safetensors telemetry loader contract that can load from a local path or approved model id, but do not download weights automatically.
3. Add fixture/fake-model tests so the backend can be developed without committing model weights.
4. Capture final-token logits-derived features when available:
   - entropy
   - selected-token probability
   - top-k margin or top-k mass
   - sampled/selected token id
5. Capture decode-window aggregates when available:
   - mean entropy
   - high-entropy count
   - low-confidence count
   - top-k margin trend
6. Capture hidden states only when explicitly enabled and available.
7. Capture router/expert telemetry only for models that actually expose it:
   - router logits/probabilities
   - top-k expert ids
   - router entropy
   - expert concentration
   - windowed expert/domain shift
8. Mark router fields as `not_moe`, `missing`, or `unsupported` when appropriate. Never fabricate router/expert data.
9. Add telemetry schema/versioning for HF records.
10. Run a tiny fixture batch through the telemetry backend and produce public-safe aggregate telemetry summaries.
11. Align telemetry records with existing verifier/action/review outcome ids where possible.
12. Keep model weights, caches, full outputs, prompts, and private records out of git.
13. Keep production mode gated.

## M21 deliverables

- `schema/hf_telemetry_record_v1.json` or equivalent
- `src/hf_telemetry_backend.py` or equivalent
- backend interface documentation
- fixture/fake model for telemetry tests
- public-safe telemetry summary artifact
- `docs/M21_HF_SAFETENSORS_TELEMETRY.md`
- tests for logits telemetry, missing telemetry, not-MoE handling, no model-weight commits, no raw text persistence, and schema validation
- updated `STATE.md` and `reports/FINDINGS.md`

## M21 stop condition

- HF telemetry backend can run against fixture/fake model without external downloads
- logits-derived telemetry fields are captured from fixture outputs
- router/expert fields are honestly marked when unavailable
- telemetry records validate against schema
- public summaries contain no raw prompt/output/private text
- model weights/caches are not committed
- GGUF runtime path remains intact
- production mode remains gated

## After M21

If autosteer loop mode is enabled, choose one based on results:

- M22A: run HF telemetry backend against a locally available safetensors dense model and compare telemetry to verifier outcomes
- M22B: run HF telemetry backend against a locally available MoE safetensors model and collect real router/expert telemetry
- M22C: broader model comparison using the M19/M20 supervisor harness
- M22D: improve open-ended explain verifier coverage with rubric/reference strategy
- M22E: larger live run with grounded regeneration enabled and better question-specific fixture evidence

Stop instead of choosing automatically if a model download, model license, disk-space, or hardware/VRAM decision is required.

## Repository hygiene

Do not commit local detailed records, full model outputs, retrieved raw text, grounded raw outputs, model weights, tokenizer/model caches, local environments, raw datasets, or large generated artifacts unless explicitly intended.
