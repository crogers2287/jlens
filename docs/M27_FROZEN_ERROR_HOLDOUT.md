# M27 frozen holdout error prediction

M27 is the first predictive test of the objective error track: do M26's
internal telemetry signals predict deterministic pass/fail outcomes on unseen
tasks, inside one fixed task category, under a protocol frozen before any
capture?

## Frozen protocol

Everything evaluated here was predeclared in `data/prompts/m26_error_manifest.json`
before task generation:

- The 32-task holdout (8 per band) was fixed per-ID before generation and
  sealed through M26: no public artifact reported holdout verdicts or holdout
  telemetry, and no model touched holdout rows before this evaluation.
- Classifier family: train-standardized nearest centroid, squared Euclidean,
  lexicographic tie break. Fit on the 64 train rows only, then evaluated
  exactly once on the holdout. No refit, feature change, or threshold tuning
  after reading holdout rows.
- All six predeclared baselines with 2000-iteration fixed-seed bootstrap
  accuracy intervals.
- Template-leakage control: train and holdout share the single declared prompt
  template by design (that is the point of within-category control), operand
  tuples never repeat, and the metadata-only baseline prices the remaining
  difficulty-band shortcut explicitly.

`data/prompts/m27_holdout_manifest.json` records the frozen holdout IDs, band
counts, and the hash of the source manifest.

## Result

Holdout: 32 tasks, 9 fail / 23 pass, 0 undecided (train had 0 undecided too).

| Baseline | Accuracy | Balanced acc. | Macro-F1 | Acc. 95% bootstrap |
|---|---:|---:|---:|---|
| majority_class | .719 | .500 | .418 | [.563, .875] |
| metadata_only (band one-hot) | .969 | .944 | .960 | [.906, 1.0] |
| logits_only | .969 | .978 | .963 | [.906, 1.0] |
| router_only | .812 | .870 | .800 | [.688, .938] |
| router_plus_logits | .906 | .935 | .894 | [.813, 1.0] |
| full_telemetry | 1.000 | 1.000 | 1.000 | [1.0, 1.0] |

Per-class behavior:

- metadata_only misses one fail (fail recall .889): band membership cannot see
  within-band errors by construction.
- logits_only recalls every fail (recall 1.0) with one false positive — it
  catches the within-band fail that the band shortcut misses, using no
  metadata at all.
- router_only recalls every fail but over-flags (fail precision .60): the
  router signal alone is a blunt error detector here, and adding logits
  (router_plus_logits .906) is worse than logits alone (.969).
- full_telemetry classifies all 32 tasks correctly.

## Honest interpretation

1. Within-category telemetry does predict objective errors on a frozen,
   untouched holdout. This is the association M23–M25 could not legitimately
   claim; here action applicability and prompt family are constant, so the
   M25 failure mode is excluded by construction.
2. The difficulty-band shortcut is very strong (.969 alone). Telemetry's
   *increment* over it is one task at n=32 with heavily overlapping bootstrap
   intervals — no statistically meaningful increment can be claimed yet. What
   can be said precisely: logits-only telemetry, without any metadata,
   recovers the band shortcut's performance and additionally catches a
   within-band fail the shortcut cannot see.
3. full_telemetry's perfect score should be read cautiously: it includes
   decode_step_count and cap/length behavior, which correlate with operand
   size and hence with band difficulty. The [1.0, 1.0] bootstrap interval is
   degenerate (resampling a perfect prediction vector) and is not evidence of
   robustness. M28's ablation decomposes which signals carry this.
4. No policy, threshold, or production claim follows. Candidate-only and
   production gates remain.

## Privacy

Public artifacts contain the frozen synthetic holdout IDs, aggregate counts,
metrics, confusion matrices, and protocol declarations only — no task text,
operands, outputs, per-task labels or predictions, private paths, tokens, or
tensors.

Public artifacts:

- `data/prompts/m27_holdout_manifest.json`
- `reports/telemetry/hf_m27_frozen_error_evaluation.json`
