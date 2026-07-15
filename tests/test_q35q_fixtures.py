"""Q35Q deterministic tokenization-fixture tests (CPU-only, no tokenizer/model)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_phase0 import Q35QBlock, scan_aggregate_only
from q35q_fixtures import (
    PHASE1_BATCH,
    PHASE1_LENGTH,
    VOCAB,
    build_tokenization_fixture,
    deterministic_token_ids,
    sequence_digest,
    verify_fixture,
)


def test_deterministic_same_seed():
    a = deterministic_token_ids(7)
    b = deterministic_token_ids(7)
    assert a == b and len(a) == PHASE1_LENGTH
    assert all(0 <= t < VOCAB for t in a)


def test_different_seed_differs():
    assert deterministic_token_ids(1) != deterministic_token_ids(2)


def test_length_respected():
    assert len(deterministic_token_ids(0, length=64)) == 64


@pytest.mark.parametrize("seed", [-1, True, 1.0, "x"])
def test_bad_seed_blocked(seed):
    with pytest.raises(Q35QBlock):
        deterministic_token_ids(seed)


@pytest.mark.parametrize("length", [0, -3, True])
def test_bad_length_blocked(length):
    with pytest.raises(Q35QBlock):
        deterministic_token_ids(0, length=length)


def test_fixture_aggregate_only():
    rec = build_tokenization_fixture(42)
    assert rec["length"] == PHASE1_LENGTH and rec["batch_size"] == PHASE1_BATCH
    assert rec["use_cache"] is False and rec["vocab_size"] == VOCAB
    assert len(rec["sequence_sha256"]) == 64
    # no raw ids in the committed record
    assert "token_ids" not in rec and "tokens" not in rec
    scan_aggregate_only(rec)


def test_fixture_digest_matches_ids():
    rec = build_tokenization_fixture(42)
    ids = deterministic_token_ids(42)
    assert rec["sequence_sha256"] == sequence_digest(ids)


def test_fixture_batch_must_be_one():
    with pytest.raises(Q35QBlock):
        build_tokenization_fixture(42, batch_size=2)


def test_verify_fixture_roundtrip():
    rec = build_tokenization_fixture(99)
    assert verify_fixture(rec) is True
    tampered = dict(rec, sequence_sha256="0" * 64)
    assert verify_fixture(tampered) is False


def test_verify_fixture_missing_field_blocked():
    rec = build_tokenization_fixture(99)
    del rec["seed"]
    with pytest.raises(Q35QBlock):
        verify_fixture(rec)
