# steer.md — current M3 status

Read this first before continuing jlens.

M2 is complete. M3 is active.

## Completed

- Step 1: label schema exists.
- Step 2: seed label scaffold exists and validates.
- Step 3: feature extractor exists and excludes drift.
- Step 4: train/eval skeleton exists and refuses unlabeled data.

## Next

Create `LABELING_HANDOFF.md`.

It should explain the label fields, how to mark true, false, or null, how to handle uncertain cases, how many reviewed examples are needed, and how to keep train and test prompt templates separate.

After `LABELING_HANDOFF.md` is committed, stop and hand off to the operator. Do not run final training until reviewed labels exist.

## Feature direction

Use these feature groups:

- entropy_final_logits
- selected_token_prob
- topk_mass_or_margin
- prefill domain prediction and margin
- windowed decode-domain shift
- low-confidence and high-entropy counts

Do not use drift fields as model features. M2 showed drift does not track confidence.

## Loop rule

Before starting another loop, use `/prompt-master` and tell the agent to continue from M3 step 5, not M2.

## Repository hygiene

Do not commit raw captures, logs, caches, local environments, or model weights.
