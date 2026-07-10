# M21 — HF/safetensors telemetry backend

M21 restores jlens's internal-telemetry research track without changing the
working GGUF supervisor. The new backend is fixture-first and download-free: it
defines how Hugging Face/safetensors telemetry is loaded, summarized, validated,
and aligned before any real model or hardware decision is made.

## Backend separation

The runtime and telemetry paths remain different record families:

| backend | record kind | internal telemetry |
|---|---|---|
| GGUF chat runtime | `auto_outcome_v1` | honestly `missing` |
| HF/safetensors | `hf_telemetry_record_v1` | available only when the source exposes it |

No GGUF feature is inferred or fabricated. Existing M1–M20 runtime behavior is
unchanged.

## No-download loader contract

`HFSafetensorsLoader` accepts:

1. an existing local directory containing `*.safetensors` or
   `model.safetensors.index.json`; or
2. a model ID explicitly included in `JLENS_HF_APPROVED_MODEL_IDS` (or passed
   directly by an approved caller).

The model reference can come from `JLENS_HF_MODEL`. Any unapproved/nonexistent
ID raises `ModelApprovalRequired` before Transformers is invoked. Every real
load uses:

```text
local_files_only=True
trust_remote_code=False
```

This allows an approved model already present in the HF cache but never starts a
download. M21 does not select a model, accept a license, reserve VRAM, or load
weights.

## Telemetry record v1

`schema/hf_telemetry_record_v1.json` contains aggregate numeric telemetry only:

- final selected token id, entropy, selected-token probability, top-k mass, and
  top-k margin;
- decode-window mean entropy, high-entropy count, low-confidence count, and
  margin trend;
- optional hidden-state layer count and mean vector norm (no vectors);
- honest router state: `available`, `not_moe`, `missing`, or `unsupported`;
- when available, router entropy, expert concentration, last-step top expert
  IDs, and first-to-last expert shift;
- boolean alignment with auto/action/grounded/review record families;
- hashed model reference/evidence, candidate-only and production-gated flags.

The schema has no fields for prompts, token text, full outputs, model paths, raw
logits, hidden vectors, router vectors, weights, or caches.

## Fixture batch

```bash
python src/hf_telemetry_backend.py \
  --fixture-summary-out reports/telemetry/hf_fixture_summary.json
```

Three deterministic in-memory fixture records were validated:

| fixture | logits | hidden | router |
|---|---|---|---|
| dense | available | disabled | `not_moe` |
| MoE | available | available | available |
| unknown/missing | missing | missing | missing |

Summary:

- records: 3;
- weights loaded: 0;
- logits: 2 available / 1 missing;
- hidden: 1 available / 1 disabled / 1 missing;
- router: 1 available / 1 `not_moe` / 1 missing;
- outcome alignment: auto 2 / action 2 / grounded 1 / reviewed 0;
- raw prompt/output/tensor persistence: false.

The fake MoE exercises router entropy, expert concentration, expert IDs, and
windowed shift. Dense records explicitly return `not_moe`; missing data remains
missing rather than being inferred.

## Tests and gates

Tests cover:

- logits and decode-window math;
- missing/disabled hidden telemetry;
- dense `not_moe`, MoE features, and unsupported router hooks;
- loader refusal for unapproved IDs/non-safetensors directories;
- no-download Transformers flags;
- schema validation and raw-text/tensor key exclusion;
- GGUF/HF backend separation;
- repository-level proof that no weight file extensions are tracked.

The public fixture summary passes commit-safety checks. Production remains
gated.

## Next gate

A real M22 run requires an operator-selected local safetensors path or explicitly
approved cached model ID plus a hardware/VRAM decision. The autosteer contract
requires stopping for that choice; M21 does not guess or download a model.
