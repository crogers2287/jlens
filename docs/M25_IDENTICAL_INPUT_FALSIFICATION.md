# M25 identical-input router falsification

M25 tests the strongest claim suggested by M24: whether frozen router telemetry
can identify action requirements when the model receives exactly the same input.
It is a deliberately adversarial metadata counterfactual, not another classifier
optimization pass.

## Preregistered design

The public manifest was committed before capture with 16 pairs / 32 task IDs:

- 8 checker-versus-no-action pairs
- 8 retrieval-versus-review pairs

The deterministic private task generator gives both members of every pair a
byte-identical prompt. Only trusted task metadata differs:

- Arithmetic pairs use the same trivial prompt and known answer. One member is
  categorized as math with a safe expression; the other is exact-answer without
  an expression.
- Topic pairs use the same neutral explanation prompt. One member is categorized
  current-info; the other is explain with no rubric.

The expected actions are therefore different even though Qwen cannot observe the
metadata. The existing M23-trained router-only nearest-centroid classifier is used
without refit or update. Features remain mean router entropy and mean expert
concentration.

## Real run

- All 16 private prompt pairs validated byte-equal before model load.
- 32/32 Qwen captures completed with logits and 24-layer × 60-expert router
  telemetry available; hidden states remained disabled.
- Actual actions exactly matched the intended balanced distribution:
  checker8/no-action8/retrieval8/review8.
- All eight arithmetic checks passed and reached EOS.
- All 16 topic members reached the 64-token cap. Because both members of each
  topic pair share the same prompt/output and their labels are metadata-driven,
  this does not change the counterfactual result.
- `agents-a1` was restored and verified after capture.

## Pair equality result

| Pair check | Result |
|---|---:|
| Actual labels discordant | 16 / 16 |
| Captured outputs identical | 16 / 16 |
| Frozen predictions identical | 16 / 16 |
| Prediction divergence rate | 0.0 |
| Mean/max router-entropy absolute difference | 0.0 / 0.0 |
| Mean/max expert-concentration absolute difference | 0.0 / 0.0 |

The stored aggregate features are exactly equal within every pair. There is no
determinism or capture anomaly to explain away.

## Frozen classifier behavior

The router-only classifier achieved accuracy 0.500, balanced accuracy 0.500, and
macro-F1 0.413; its fixed bootstrap accuracy interval is [0.3125, 0.6875]. The
balanced majority baseline is 0.250.

- Every checker/no-action pair received the checker prediction: checker recall
  1.0, no-action recall 0.0.
- Each retrieval/review pair received one shared prediction; across topics, three
  pairs mapped retrieval and five mapped review. Both classes therefore receive
  precision 0.5, with recall 0.375 and 0.625 respectively.

Exactly one member per indistinguishable pair can be correct when the prediction
is one of the pair's two labels, producing the observed 50% ceiling. The classifier
cannot recover metadata that was never part of the model input.

## Interpretation

M25 confirms that M24's 70% frozen router score was substantially driven by prompt
template/category associations. Router telemetry alone cannot determine whether a
trusted external workflow requires a checker, retrieval, review, or no action when
that requirement changes only in unobserved metadata.

This does not prove router telemetry is useless for every objective. It leaves two
distinct future problems:

1. Explicitly combine trusted task metadata with telemetry for action routing.
   That is a conventional supervised routing problem and must not be presented as
   telemetry discovering hidden metadata.
2. Collect balanced objective pass/fail outcomes for identical task categories to
   test whether telemetry predicts model errors rather than workflow applicability.

No policy was refit, no task was changed after capture, and no production threshold
is justified. Candidate-only and production gates remain.

## Privacy

The public report contains aggregate counts, confusion/class metrics, and pairwise
difference summaries only. It contains no pair/task IDs, prompt/output text,
per-pair predictions, hashes, paths, token data, tensors, or model weights. The
public manifest contains synthetic IDs/pair types/intended classes only.

Private ignored artifacts contain the generated tasks, 32 captures, and 32 each of
detailed telemetry/runtime/action/result rows.

Public artifacts:

- `data/prompts/m25_pair_manifest.json`
- `reports/telemetry/hf_m25_pair_run_summary.json`
- `reports/telemetry/hf_m25_pair_falsification.json`
