"""Q35Q Phase-0 config admission (CPU-only, pure).

Repair item 1 of
docs/STEER_ADDENDUM_2026-07-17_Q35Q_REDUCED_META_EXTRAPOLATION_AND_SOURCE_INDEPENDENCE_CORRECTION.md:
the reconciliation CLI instantiated the source class from `config.json` bytes that
were never independently admitted. This module admits the config BEFORE it is used
for source construction:

- verify the config bytes against their immutable Git blob identity (config.json is
  a small non-LFS file, so its identity is the git blob sha1 == the Hub blob_id);
- parse with duplicate-key rejection;
- require the complete frozen text architecture conjunction and the GPTQ conjunction
  to pass.

The admitted config's layer/expert counts are then the authoritative construction
parameters, so the source class is built from admitted configuration rather than
from raw artifact-supplied bytes. Returns the validated config + counts.
"""
from __future__ import annotations

import json

from q35q_index_admission import _no_dupes, git_blob_sha1
from q35q_stage import Q35QStageBlock, validate_gptq_quant, validate_text_architecture


def verify_config_identity(config_bytes: bytes, expected_git_blob_sha1: str) -> str:
    if not isinstance(expected_git_blob_sha1, str) or len(expected_git_blob_sha1) != 40 \
            or any(c not in "0123456789abcdef" for c in expected_git_blob_sha1):
        raise Q35QStageBlock("expected config identity is not a 40-hex git blob sha1")
    observed = git_blob_sha1(config_bytes)
    if observed != expected_git_blob_sha1:
        raise Q35QStageBlock("config local bytes do not match the frozen git blob identity")
    return observed


def admit_config(config_bytes: bytes, expected_git_blob_sha1: str) -> dict:
    """Identity-verify, strict-parse, and require the full architecture + GPTQ
    conjunctions before the config may be used for source construction."""
    identity = verify_config_identity(config_bytes, expected_git_blob_sha1)
    try:
        cfg = json.loads(config_bytes.decode("utf-8"), object_pairs_hook=_no_dupes)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Q35QStageBlock(f"config not valid UTF-8 JSON: {type(e).__name__}")
    if not isinstance(cfg, dict):
        raise Q35QStageBlock("config top level is not an object")
    arch = validate_text_architecture(cfg)
    gptq = validate_gptq_quant(cfg.get("quantization_config") or {})
    if not arch.get("all_required_pass"):
        raise Q35QStageBlock("config architecture conjunction failed")
    if not gptq.get("all_required_pass"):
        raise Q35QStageBlock("config gptq conjunction failed")
    txt = cfg.get("text_config", cfg)
    return {
        "config_identity_git_sha1": identity,
        "architecture_pass": True,
        "gptq_pass": True,
        "num_experts": txt.get("num_experts"),
        "num_hidden_layers": txt.get("num_hidden_layers"),
        "full_attention_interval": txt.get("full_attention_interval"),
    }
