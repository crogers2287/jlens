# steer.md — post-M22 within-model telemetry expansion

M1 through M22 are complete. Do not redo the GGUF supervisor, verifier, action,
grounded-regeneration, fixture telemetry, or eight-task real HF validation work.

`CODEX_AUTOSTEER.md` remains part of the operating contract.

## Autosteer mode

Default mode:

- Complete one milestone.
- Commit implementation.
- Update `steer.md` separately.
- Stop.

Loop mode requires `CODEX_AUTOSTEER_LOOP=true` or an explicit operator request.
The current operator approval covers the existing public Qwen MoE checkpoint on
the Thor mount, GPU-first dual-3090 use, and temporary llama-swap unload/restore.
Stop for a different model, new download/license, new hardware plan, storage move,
or materially larger resource footprint.

## Current state

Completed milestones:

- M1–M20: practical local supervisor track through fixture-grounded regeneration
- M21: fixture-first HF/safetensors telemetry backend
- M22: bounded real HF MoE telemetry validation

M22 result:

- Real public Qwen1.5-MoE-A2.7B-Chat checkpoint resolved locally with
  `local_files_only=true` and `trust_remote_code=false`.
- BF16 fit across dual 24 GiB 3090s without CPU/disk offload; hidden capture was
  disabled. The approximately 27 GiB checkpoint remains on Thor outside the repo.
- Eight shared M19 tasks × four decode steps completed.
- Real telemetry available on all eight:
  - logits-derived features 8/8
  - router features 8/8
  - 24 layers × 60 experts
  - hidden status disabled 8/8
- Alignment coverage: auto 8 / action 8 / grounded 1 / reviewed 1.
- Checker-needed selected rows had lower decode entropy than not-needed rows, but
  router entropy was effectively unchanged.
- Critical scope: Qwen supplied telemetry while agents-a1 supplied existing
  outcome/action labels on shared IDs. This is cross-model task-demand alignment,
  not within-Qwen error prediction.
- Retrieval and review positive groups each had n=1. No predictive value,
  calibration, threshold, or production usefulness was claimed.
- Raw captures and detailed schema records remain ignored/private. Public reports
  contain only counts/distributions/group means.
- Full suite green at 89 tests. Production remains gated.
- `agents-a1` serving was restored and verified after the capture window.

## Next milestone: M23 within-model telemetry/outcome validation

M23 should remove the M22 cross-model confound. Use the already-approved local
Qwen MoE to produce both internal telemetry and its own bounded outputs on a
predeclared shared batch, then run the existing deterministic verifiers/action
router against those transient Qwen outputs.

### M23 objectives

1. Predeclare a balanced 32-task batch before inspecting telemetry:
   - 8 deterministic checker candidates
   - 8 current-info/retrieval candidates
   - 8 review/open-explain candidates
   - 8 no-action controls
2. Use only existing public task IDs and metadata. Keep prompt text in the existing
   public dataset or ignored private run files; do not add it to reports.
3. Load the same approved local Qwen checkpoint with the existing dual-GPU BF16
   plan, local-only resolution, remote code disabled, hidden capture disabled,
   and a bounded decode length sufficient to verify outputs.
4. Capture Qwen logits/router telemetry and its output in the same forward/decode
   run so the signals and outcomes refer to the same model execution.
5. Pass the full Qwen output transiently to the existing approved deterministic
   verifiers and action router before truncation. Never persist full output in a
   public artifact.
6. Do not introduce shell execution, dynamic commands, live web retrieval, or a
   new checker. Retrieval remains fixture/read-only and action execution remains
   explicitly gated.
7. Align telemetry with Qwen-specific auto/action outcomes by task ID. Grounded
   and reviewed coverage may remain missing unless produced through the existing
   safe workflows; report missing coverage honestly.
8. Predeclare comparisons and report aggregate separation for:
   - checker-needed vs not-needed
   - retrieval-needed vs not-needed
   - review-needed vs not-needed
   - deterministic checker pass vs fail, only if both groups occur
9. Report group counts, mean/median logits features, mean/median router features,
   and simple effect sizes with bootstrap intervals only when group sizes permit.
   Do not fit a policy or choose thresholds after seeing the batch.
10. Keep all raw tensors, token IDs/text, full outputs, paths, and detailed records
    private/ignored. Keep production gated.

### M23 deliverables

- deterministic predeclared 32-task selection manifest with IDs/categories only
- same-run Qwen telemetry + transient-output adapter additions
- private raw captures and Qwen-specific outcome/action records
- private schema-valid detailed telemetry records
- public aggregate run summary
- public within-model alignment/comparison report
- `docs/M23_WITHIN_MODEL_TELEMETRY_VALIDATION.md`
- tests for same-run association, transient-output handling, predeclared groups,
  degraded/missing states, no-text reporting, and resume behavior
- updated `STATE.md` and `reports/FINDINGS.md`

### M23 stop condition

- exactly 32 predeclared tasks are processed or an honest degraded blocker is
  reported without redefining the batch
- Qwen telemetry and Qwen-specific outcomes are linked to the same execution
- logits and router capability states are honest
- comparisons remain descriptive and predeclared; no tiny-n predictive claim
- no weights/cache/path/raw prompt/output/token/tensor data are committed
- public artifacts pass schema, privacy, and commit-safety checks
- full test suite passes
- production remains gated

## After M23

Choose based on evidence, not preference:

- If within-model groups have enough support and stable separation: M24 frozen
  holdout evaluation with predeclared features/metrics and no threshold tuning.
- If positive groups are too small: M24 balanced batch expansion using the same
  model/hardware/privacy contract.
- If telemetry shows no useful separation: stop the telemetry-policy branch and
  return to practical verifier/retrieval quality work.
- If output capture cannot stay transient or same-run association is unreliable:
  stop and repair the adapter before any larger run.

## Repository hygiene

Do not commit local detailed records, prompts, full outputs, raw retrieved context,
token text/IDs, raw tensors, model paths, model weights, tokenizer/model caches,
environments, or large generated artifacts. Outcome labels remain candidates and
production remains gated until a future steer defines audited unlock criteria.
