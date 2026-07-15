"""Q35Q private sequence and tokenization-admission fixture tests."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_phase0 import Q35QBlock, scan_aggregate_only
from q35q_fixtures import (
    PHASE1_BATCH,
    PHASE1_LENGTH,
    SYNTHETIC_FIXTURE_KIND,
    TOKENIZER_FIXTURE_KIND,
    VOCAB,
    build_tokenization_fixture,
    deterministic_token_ids,
    sequence_digest,
    validate_tokenization_admission_fixture,
    verify_fixture,
)

KEY = bytes(range(32))
OTHER_KEY = bytes(range(1, 33))
FIXTURE_ID = "phase1-gptq-v1"
TOKENIZER_ID = "tok:" + "a" * 64
H = "b" * 64


def good_admission_fixture(**over):
    record = {
        "fixture_kind": TOKENIZER_FIXTURE_KIND,
        "length": PHASE1_LENGTH,
        "batch_size": PHASE1_BATCH,
        "vocab_size": VOCAB,
        "use_cache": False,
        "tokenizer_roundtrip_established": True,
        "text_only_load_established": True,
        "determinism_repeats": 2,
        "tokenizer_identity_sha256": hashlib.sha256(TOKENIZER_ID.encode()).hexdigest(),
        "private_input_commitment_kind": "hmac-sha256",
        "private_input_commitment_sha256": H,
        "sequence_sha256": "c" * 64,
    }
    record.update(over)
    return record


def test_deterministic_same_private_key_and_fixture_id():
    a = deterministic_token_ids(KEY, FIXTURE_ID)
    b = deterministic_token_ids(KEY, FIXTURE_ID)
    assert a == b and len(a) == PHASE1_LENGTH
    assert all(0 <= token_id < VOCAB for token_id in a)


def test_private_key_and_fixture_id_both_domain_separate_sequences():
    assert deterministic_token_ids(KEY, FIXTURE_ID) != deterministic_token_ids(
        OTHER_KEY, FIXTURE_ID
    )
    assert deterministic_token_ids(KEY, FIXTURE_ID) != deterministic_token_ids(
        KEY, "phase1-nf4-v1"
    )


@pytest.mark.parametrize("key", [b"short", "not-bytes", None])
def test_bad_private_key_blocked(key):
    with pytest.raises(Q35QBlock):
        deterministic_token_ids(key, FIXTURE_ID)


@pytest.mark.parametrize("fixture_id", ["", "contains space", "../escape", 7])
def test_bad_fixture_id_blocked(fixture_id):
    with pytest.raises(Q35QBlock):
        deterministic_token_ids(KEY, fixture_id)


@pytest.mark.parametrize("length", [0, -3, True])
def test_bad_length_blocked(length):
    with pytest.raises(Q35QBlock):
        deterministic_token_ids(KEY, FIXTURE_ID, length=length)


def test_synthetic_fixture_is_aggregate_only_and_non_admissible_by_claim():
    record = build_tokenization_fixture(KEY, FIXTURE_ID)
    assert record["fixture_kind"] == SYNTHETIC_FIXTURE_KIND
    assert record["length"] == PHASE1_LENGTH
    assert record["batch_size"] == PHASE1_BATCH
    assert record["use_cache"] is False
    assert record["tokenizer_roundtrip_established"] is False
    assert record["text_only_load_established"] is False
    assert "seed" not in record and "token_ids" not in record and "tokens" not in record
    assert len(record["secret_commitment_sha256"]) == 64
    assert len(record["sequence_sha256"]) == 64
    scan_aggregate_only(record)


def test_fixture_digest_matches_private_sequence():
    record = build_tokenization_fixture(KEY, FIXTURE_ID)
    ids = deterministic_token_ids(KEY, FIXTURE_ID)
    assert record["sequence_sha256"] == sequence_digest(ids)


def test_fixture_batch_must_be_exact_integer_one():
    for value in (2, True, 1.0):
        with pytest.raises(Q35QBlock):
            build_tokenization_fixture(KEY, FIXTURE_ID, batch_size=value)


def test_verify_fixture_requires_private_key_and_detects_tampering():
    record = build_tokenization_fixture(KEY, FIXTURE_ID)
    assert verify_fixture(record, KEY) is True
    assert verify_fixture(record, OTHER_KEY) is False
    assert verify_fixture(dict(record, sequence_sha256="0" * 64), KEY) is False


def test_verify_fixture_rejects_legacy_reconstructible_seed_schema():
    record = build_tokenization_fixture(KEY, FIXTURE_ID)
    record["seed"] = 42
    with pytest.raises(Q35QBlock):
        verify_fixture(record, KEY)


def test_tokenizer_admission_fixture_passes_exact_schema():
    record = validate_tokenization_admission_fixture(
        good_admission_fixture(), TOKENIZER_ID
    )
    assert record["fixture_kind"] == TOKENIZER_FIXTURE_KIND
    scan_aggregate_only(record)


@pytest.mark.parametrize(
    "over",
    [
        {"tokenizer_roundtrip_established": False},
        {"text_only_load_established": False},
        {"determinism_repeats": 1},
        {"determinism_repeats": True},
        {"private_input_commitment_kind": "sha256"},
        {"length": 31},
        {"batch_size": 1.0},
        {"vocab_size": VOCAB - 1},
        {"use_cache": True},
        {"tokenizer_identity_sha256": "d" * 64},
        {"sequence_sha256": "BAD"},
    ],
)
def test_tokenizer_admission_fixture_fails_closed(over):
    with pytest.raises(Q35QBlock):
        validate_tokenization_admission_fixture(good_admission_fixture(**over), TOKENIZER_ID)


def test_tokenizer_admission_fixture_rejects_unknown_fields_and_synthetic_fixture():
    record = good_admission_fixture(extra=True)
    with pytest.raises(Q35QBlock):
        validate_tokenization_admission_fixture(record, TOKENIZER_ID)
    with pytest.raises(Q35QBlock):
        validate_tokenization_admission_fixture(
            build_tokenization_fixture(KEY, FIXTURE_ID), TOKENIZER_ID
        )
