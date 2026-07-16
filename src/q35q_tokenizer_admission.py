"""Q35Q Phase-0 complete tokenizer-admission conjunction (CPU-only, pure, testable).

Second-repair defect 5 per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_PHASE0_SECOND_CORRECTION_AND_M39_PREGEN_PROBE.md,
corrected per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_TOKENIZER_BINDING_CORRECTION_AND_DECISION_POINT_COMPARATORS.md.

The first attempt's conjunction was too weak: cleanup was checked non-null rather
than for exact equality; BOS/EOS/PAD were checked non-null rather than bound to
expected identities; `isinstance(encoded_length, int)` accepts booleans; and the
digest fields were checked for hex *shape* rather than *equality* to an
independently recomputed value. This version binds every observed value to an
independently derived expected value by equality.

Purity note: this function performs the *comparisons*. The live orchestration is
responsible for deriving the expected values independently — the immutable
tokenizer-file manifest digest, a fresh deterministic chat-template rendering
digest, a fresh deterministic private-fixture encoding digest, and the expected
special-token identities from the pinned tokenizer files — and feeding both the
observed and independently-derived expected values here. A caller-supplied digest
that merely has valid hex shape is not admission evidence; it must equal the
independent recomputation.

Raw fixture text, rendered chat text, and token IDs stay private — only booleans
and hex digests reach the caller.
"""
from __future__ import annotations

import re

from q35q_stage import Q35QStageBlock

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _digest_matches(observed, expected) -> bool:
    """True iff observed is a valid 64-hex digest equal to the independently
    derived expected digest (also 64-hex). Shape alone is insufficient."""
    return (bool(observed) and bool(expected)
            and bool(_HEX64.match(observed)) and bool(_HEX64.match(expected))
            and observed == expected)


def _strict_positive_int(x) -> bool:
    """Reject booleans (bool is a subclass of int) and non-ints."""
    return type(x) is int and x > 0


def complete_tokenizer_admission(
    *,
    tokenizer_class: str | None,
    expected_tokenizer_class: str,
    trust_remote_code: bool,
    normalization: str | None,
    expected_normalization: str,
    cleanup_setting,
    expected_cleanup_setting,
    roundtrip_verdict: dict,
    special_token_behavior_ok: bool,
    bos_token_id,
    eos_token_id,
    pad_token_id,
    expected_bos_token_id,
    expected_eos_token_id,
    expected_pad_token_id,
    encoded_length: int,
    id_sequence_sha256: str | None,
    expected_id_sequence_sha256: str | None,
    chat_template_present: bool,
    chat_template_render_sha256: str | None,
    expected_chat_template_render_sha256: str | None,
    tokenizer_manifest_sha256: str | None,
    expected_tokenizer_manifest_sha256: str | None,
    model_repo: str,
    model_revision: str,
    tokenizer_repo: str,
    tokenizer_revision: str,
) -> dict:
    """Per-field tokenizer admission + overall conjunction. Every observed value
    is bound to an independently derived expected value by equality. Fails closed
    (raises) on structurally-invalid inputs; otherwise returns {field: bool, ...,
    'all_required_pass': bool}."""
    if not isinstance(roundtrip_verdict, dict):
        raise Q35QStageBlock("roundtrip_verdict must be a dict")
    if not model_repo or not tokenizer_repo:
        raise Q35QStageBlock("model/tokenizer repo identity missing")
    if expected_cleanup_setting is None:
        raise Q35QStageBlock("expected_cleanup_setting must be an independently derived value")
    for name, exp in (("bos", expected_bos_token_id), ("eos", expected_eos_token_id),
                      ("pad", expected_pad_token_id)):
        if exp is None:
            raise Q35QStageBlock(f"expected {name} token id must be independently derived")

    checks = {
        "tokenizer_class_admitted":
            bool(tokenizer_class) and tokenizer_class == expected_tokenizer_class,
        "trust_remote_code_false": trust_remote_code is False,
        "normalization_admitted":
            normalization is not None and normalization == expected_normalization,
        "cleanup_setting_admitted": cleanup_setting == expected_cleanup_setting,
        "roundtrip_pass": roundtrip_verdict.get("roundtrip_pass") is True,
        "no_special_tokens_encoding":
            roundtrip_verdict.get("no_special_tokens_requested") is True,
        "deterministic_encode": roundtrip_verdict.get("deterministic_encode") is True,
        "exact_decode_reencode": roundtrip_verdict.get("exact_decode_reencode") is True,
        "special_token_behavior_ok": special_token_behavior_ok is True,
        "bos_identity_bound": bos_token_id is not None and bos_token_id == expected_bos_token_id,
        "eos_identity_bound": eos_token_id is not None and eos_token_id == expected_eos_token_id,
        "pad_identity_bound": pad_token_id is not None and pad_token_id == expected_pad_token_id,
        "encoded_length_strict_positive_int": _strict_positive_int(encoded_length),
        "id_sequence_digest_bound":
            _digest_matches(id_sequence_sha256, expected_id_sequence_sha256),
        "chat_template_present": chat_template_present is True,
        "chat_template_render_digest_bound":
            _digest_matches(chat_template_render_sha256, expected_chat_template_render_sha256),
        "tokenizer_manifest_identity_bound":
            _digest_matches(tokenizer_manifest_sha256, expected_tokenizer_manifest_sha256),
        "model_tokenizer_repo_paired": model_repo == tokenizer_repo,
        "model_tokenizer_revision_paired":
            model_revision == tokenizer_revision
            and bool(_HEX40.match(model_revision or "")),
    }
    checks["all_required_pass"] = all(
        v for k, v in checks.items() if k != "all_required_pass")
    return checks
