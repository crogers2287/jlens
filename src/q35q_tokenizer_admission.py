"""Q35Q Phase-0 complete tokenizer-admission conjunction (CPU-only, pure, testable).

Second-repair defect 5 per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_PHASE0_SECOND_CORRECTION_AND_M39_PREGEN_PROBE.md.

The prior repair's overall boolean required only `roundtrip_pass`. The binding
correction requires the tokenizer verdict to additionally bind: tokenizer class
and `trust_remote_code`, normalization and cleanup settings, explicit
no-special-token encoding, separately-tested admitted BOS/EOS/PAD/special-token
behavior, deterministic encoded length + private ID digest, exact decode/re-encode,
deterministic chat-template identity + rendering digest, the tokenizer-file
manifest identity, and the exact model/tokenizer repository+revision pairing.

Pure over already-extracted metadata so it is unit-testable without loading a
model. Raw fixture text, rendered chat text, and token IDs stay private — only
booleans and hex digests reach the caller.
"""
from __future__ import annotations

import re

from q35q_stage import Q35QStageBlock

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def complete_tokenizer_admission(
    *,
    tokenizer_class: str | None,
    expected_tokenizer_class: str,
    trust_remote_code: bool,
    normalization: str | None,
    cleanup_setting,
    expected_normalization: str,
    roundtrip_verdict: dict,
    special_token_behavior_ok: bool,
    bos_token_id,
    eos_token_id,
    pad_token_id,
    encoded_length: int,
    id_sequence_sha256: str | None,
    chat_template_present: bool,
    chat_template_render_sha256: str | None,
    tokenizer_manifest_sha256: str | None,
    model_repo: str,
    model_revision: str,
    tokenizer_repo: str,
    tokenizer_revision: str,
) -> dict:
    """Per-field tokenizer admission + overall conjunction. Fails closed (raises)
    on structurally-invalid inputs; otherwise returns {field: bool, ...,
    'all_required_pass': bool}."""
    if not isinstance(roundtrip_verdict, dict):
        raise Q35QStageBlock("roundtrip_verdict must be a dict")
    if not model_repo or not tokenizer_repo:
        raise Q35QStageBlock("model/tokenizer repo identity missing")

    checks = {
        "tokenizer_class_admitted":
            bool(tokenizer_class) and tokenizer_class == expected_tokenizer_class,
        "trust_remote_code_false": trust_remote_code is False,
        "normalization_admitted":
            normalization is not None and normalization == expected_normalization,
        "cleanup_setting_recorded": cleanup_setting is not None,
        "roundtrip_pass": roundtrip_verdict.get("roundtrip_pass") is True,
        "no_special_tokens_encoding":
            roundtrip_verdict.get("no_special_tokens_requested") is True,
        "deterministic_encode": roundtrip_verdict.get("deterministic_encode") is True,
        "exact_decode_reencode": roundtrip_verdict.get("exact_decode_reencode") is True,
        "special_token_behavior_ok": special_token_behavior_ok is True,
        "bos_present": bos_token_id is not None,
        "eos_present": eos_token_id is not None,
        "pad_present": pad_token_id is not None,
        "encoded_length_positive": isinstance(encoded_length, int) and encoded_length > 0,
        "id_sequence_digest_bound": bool(id_sequence_sha256) and bool(_HEX64.match(id_sequence_sha256 or "")),
        "chat_template_present": chat_template_present is True,
        "chat_template_render_digest_bound":
            bool(chat_template_render_sha256) and bool(_HEX64.match(chat_template_render_sha256 or "")),
        "tokenizer_manifest_identity_bound":
            bool(tokenizer_manifest_sha256) and bool(_HEX64.match(tokenizer_manifest_sha256 or "")),
        "model_tokenizer_repo_paired": model_repo == tokenizer_repo,
        "model_tokenizer_revision_paired":
            model_revision == tokenizer_revision
            and bool(_HEX40.match(model_revision or "")),
    }
    checks["all_required_pass"] = all(
        v for k, v in checks.items() if k != "all_required_pass")
    return checks
