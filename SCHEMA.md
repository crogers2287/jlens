# jlens capture schema v1 (FROZEN)

Versioned contract the routerguard sidecar heads consume. Machine-readable
form: `schema/v1.json` (JSON Schema draft-07). Exporter: `src/export_schema.py`.

## Why a frozen schema
Raw `.pt` captures carry hidden states + full router logits (~4 MB/prompt) and
are gitignored. Schema v1 is the **small, shareable, router-only** projection
(~0.1 MB/prompt) that downstream heads train on, so experiments are
reproducible without re-running the model.

## Format
- One JSON object per prompt, one per line (JSONL).
- Router-derived signal only — no hidden states, no raw logits.

## Fields
| field | type | notes |
|---|---|---|
| `schema_version` | int | always `1` |
| `model` | str | HF id, e.g. `Qwen/Qwen3.6-35B-A3B` |
| `model_type` | str | arch, e.g. `qwen3_5_moe` |
| `run_id` | str | capture batch, e.g. `r3` |
| `prompt_id` | str | e.g. `math_03` |
| `domain` | str | derived from prompt_id prefix (`domain_of()`) |
| `tokens` | int | prompt token count (prefill-only) |
| `num_layers` | int | MoE router layers (40 for 3.6-35B-A3B) |
| `num_experts` | int | experts per layer (256) |
| `top_k` | int | experts selected per token (8) |
| `layers[]` | array | one entry per router layer |

### `layers[]` entry
| field | type | notes |
|---|---|---|
| `layer` | int | 0-indexed |
| `logits_shape` | [int,int] | `[tokens, num_experts]` |
| `topk_experts` | int[tokens][top_k] | selected expert ids per token |
| `topk_probs` | float[tokens][top_k] | softmax over the top-k logits, per token |
| `entropy` | float | token-mean entropy (nats) of the FULL softmax(router_logits) |

## Stability rules
- v1 is frozen: fields are append-only. Any breaking change → v2 + new
  `schema/v2.json`, and exporters bump `schema_version`.
- `entropy` is over the full 256-way distribution (not just top-k) so it is a
  true routing-confidence signal for the risk head.

## Regenerate
```
python src/export_schema.py data/captures/<run> --run-id <id> \
    --top-k 8 --out reports/schema/<id>.jsonl
```
Validate: load `schema/v1.json` and `jsonschema.validate` each line
(all r3 rows pass).
