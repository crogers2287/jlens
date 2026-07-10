# M24 frozen telemetry holdout evaluation

M24 evaluates M23-trained telemetry classifiers on unseen Qwen task IDs without
updating features, scaling, centroids, thresholds, or class priors from holdout.
It measures task-demand classification only and does not unlock production.

## Preregistration and correction

The first public manifest proposed 48 tasks, but the source-resolution check found
that several referenced current-info/explain IDs did not exist. This was caught
before any M24 capture. The invalid manifest remains in git history; a second
pre-run commit transparently reduced the design to 40 valid tasks, 10 per class,
without changing model, features, classifier, or metrics. The matching steer was
also corrected before the first model load.

The corrected manifest is disjoint from all 32 M23 training IDs and resolves only
existing public M19 batch rows.

## Frozen protocol

Training data consisted of the 32 private M23 telemetry records and their balanced
8/8/8/8 actual action labels. Three classifiers were instantiated before loading
any M24 capture:

| Classifier | Frozen features |
|---|---|
| full | decode entropy, selected probability, top-k margin, router entropy, expert concentration |
| logits-only | decode entropy, selected probability, top-k margin |
| router-only | router entropy, expert concentration |

Each feature was standardized using M23 mean and sample standard deviation. Each
class centroid is the mean standardized M23 vector. Prediction uses minimum
squared Euclidean distance with lexical exact-tie breaking. No holdout update or
parameter selection is possible in the evaluation path.

Metrics were frozen to accuracy, balanced accuracy, macro F1, aggregate confusion,
per-class metrics, and a fixed-seed 2,000-resample accuracy interval.

## Runtime result

- 40/40 same-run Qwen captures completed.
- Logits and real 24-layer × 60-expert router telemetry were available 40/40.
- Predeclared groups were checker10/retrieval10/review10/control10.
- Actual actions were checker10/retrieval10/review11/no-action9; one control failed
  its deterministic correctness check and therefore routed to review.
- Arithmetic checker outcomes shifted to 1 pass / 9 fail. Every checker reached
  EOS, so this is not a decode-cap artifact. M24 does not fit an error predictor.
- Eighteen tasks reached 64 tokens: retrieval7/review10/control1; none were checker.
- `agents-a1` was restored and verified after the run.

## Frozen holdout performance

The actual majority-class baseline is 0.275 because of the 10/9/10/11 action
distribution.

| Frozen classifier | Accuracy | Bootstrap 95% | Balanced accuracy | Macro F1 |
|---|---:|---:|---:|---:|
| full | 0.600 | [0.450, 0.750] | 0.602 | 0.599 |
| logits-only | 0.225 | [0.100, 0.350] | 0.236 | 0.199 |
| router-only | 0.700 | [0.550, 0.850] | 0.693 | 0.700 |

Router-only recall was checker 0.80, no-action 0.44, retrieval 0.80, and review
0.73. Its dominant errors were five no-action rows predicted review and three
review rows predicted retrieval. Full features reduced review recall to 0.36,
while logits-only never correctly predicted a review row.

The frozen result supports further investigation of router aggregates and rejects
the M23 logits features as a useful standalone classifier on this holdout. It does
not show causal risk prediction: action class still tracks task category and
verifier applicability, and the holdout shares prompt templates with M23. The
wide accuracy intervals and weak no-action precision/recall also rule out a policy
or production claim.

## Privacy and artifacts

The evaluator retains no public per-task prediction. Confusion matrices and class
metrics are aggregate. Public files contain no task IDs, prompt/output/token text,
local path, raw tensor, centroid, or model weight; the manifest is the sole public
ID list and contains only already-public IDs/groups.

Private ignored artifacts include 40 raw captures and 40 each of detailed
telemetry, runtime, action, and action-result rows. All remain candidate evidence.

Public artifacts:

- `data/prompts/m24_holdout_manifest.json`
- `reports/telemetry/hf_m24_holdout_summary.json`
- `reports/telemetry/hf_m24_frozen_evaluation.json`
