
## 33. Token-level probe (r2, prompt-held-out)
- 264 tokens, 10240 feats (all-layer top-8 multi-hot), GroupKFold by prompt.
- Grouped 4-fold token accuracy: 0.578 vs 0.208 chance (~2.8x).
- Confirms routing carries domain signal at token granularity, not just via sequence aggregation. Per-layer sweep queued after r3.
