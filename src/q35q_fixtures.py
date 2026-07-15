"""Q35Q deterministic private sequence fixtures and admission schema (CPU-only).

The Phase-1 exact-VJP smoke may use a deterministic synthetic token-id sequence,
but the public fixture must not make those private ids reconstructible. A public
seed is therefore forbidden. Synthetic ids are derived with HMAC-SHA256 from a
high-entropy private key retained only in the sealed local ledger. The committed
record contains only domain-separated commitments and aggregate shape/settings.

A synthetic sequence is not evidence that the admitted tokenizer is deterministic
or that the text-only model load succeeds. Artifact admission therefore accepts
only a separate tokenizer-roundtrip record produced by the pinned execution
harness after two identical tokenizer runs and a successful text-only load probe.
"""
from __future__ import annotations

import hashlib
import hmac
import re

from q35q_phase0 import QWEN35_35B_A3B_ARCH, Q35QBlock, scan_aggregate_only

VOCAB = QWEN35_35B_A3B_ARCH["vocab_size"]
PHASE1_LENGTH = 32
PHASE1_BATCH = 1
MIN_PRIVATE_KEY_BYTES = 32
SYNTHETIC_FIXTURE_KIND = "synthetic_token_id_vjp_smoke_v1"
TOKENIZER_FIXTURE_KIND = "tokenizer_roundtrip_text_load_v1"

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_FIXTURE_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_SYNTHETIC_FIELDS = {
    "fixture_kind",
    "fixture_id",
    "length",
    "batch_size",
    "vocab_size",
    "use_cache",
    "secret_commitment_sha256",
    "sequence_sha256",
    "tokenizer_roundtrip_established",
    "text_only_load_established",
}
_TOKENIZER_ADMISSION_FIELDS = {
    "fixture_kind",
    "length",
    "batch_size",
    "vocab_size",
    "use_cache",
    "tokenizer_roundtrip_established",
    "text_only_load_established",
    "determinism_repeats",
    "tokenizer_identity_sha256",
    "private_input_commitment_kind",
    "private_input_commitment_sha256",
    "sequence_sha256",
}


def _pos_int(value, name):
    if type(value) is not int or value <= 0:
        raise Q35QBlock(f"{name} must be a positive int")
    return value


def _private_key(value) -> bytes:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise Q35QBlock("fixture private key must be bytes-like")
    key = bytes(value)
    if len(key) < MIN_PRIVATE_KEY_BYTES:
        raise Q35QBlock("fixture private key must contain at least 32 bytes")
    return key


def _valid_hex64(value, name):
    if not isinstance(value, str) or not _HEX64.fullmatch(value):
        raise Q35QBlock(f"{name} must be a lowercase sha256 digest")
    return value


def _validate_token_ids(token_ids, *, length: int, vocab_size: int) -> tuple:
    if not isinstance(token_ids, (list, tuple)):
        raise Q35QBlock("token ids must be a list or tuple")
    ids = tuple(token_ids)
    if len(ids) != length:
        raise Q35QBlock("token-id sequence length mismatch")
    if any(type(token_id) is not int or not (0 <= token_id < vocab_size)
           for token_id in ids):
        raise Q35QBlock("token ids out of range or malformed")
    return ids


def secret_commitment(private_key) -> str:
    key = _private_key(private_key)
    return hashlib.sha256(b"q35q-fixture-secret-v1\0" + key).hexdigest()


def deterministic_token_ids(private_key, fixture_id: str,
                            length: int = PHASE1_LENGTH,
                            vocab_size: int = VOCAB) -> tuple:
    """Derive a deterministic private synthetic sequence.

    ``private_key`` remains in the sealed local ledger. ``fixture_id`` is a public
    domain label, not a seed. Rejection sampling avoids modulo bias.
    """
    key = _private_key(private_key)
    if not isinstance(fixture_id, str) or not _FIXTURE_ID.fullmatch(fixture_id):
        raise Q35QBlock("fixture_id must be a canonical public identifier")
    _pos_int(length, "length")
    _pos_int(vocab_size, "vocab_size")
    if vocab_size > 2 ** 32:
        raise Q35QBlock("vocab_size exceeds the 32-bit fixture sampler")

    domain = (
        b"q35q-synthetic-token-smoke-v1\0"
        + fixture_id.encode("ascii")
        + b"\0"
        + length.to_bytes(8, "big")
        + vocab_size.to_bytes(8, "big")
    )
    cutoff = 2 ** 32 - ((2 ** 32) % vocab_size)
    ids = []
    counter = 0
    while len(ids) < length:
        block = hmac.new(
            key, domain + counter.to_bytes(8, "big"), hashlib.sha256
        ).digest()
        for offset in range(0, len(block), 4):
            candidate = int.from_bytes(block[offset:offset + 4], "big")
            if candidate >= cutoff:
                continue
            ids.append(candidate % vocab_size)
            if len(ids) == length:
                break
        counter += 1
    return tuple(ids)


def sequence_digest(token_ids) -> str:
    if not isinstance(token_ids, (list, tuple)) or not token_ids:
        raise Q35QBlock("token ids must be a non-empty list or tuple")
    ids = tuple(token_ids)
    if any(type(token_id) is not int or not (0 <= token_id < 2 ** 32)
           for token_id in ids):
        raise Q35QBlock("token ids are malformed")
    digest = hashlib.sha256()
    digest.update(b"q35q-token-sequence-v1\0")
    digest.update(len(ids).to_bytes(8, "big"))
    for token_id in ids:
        digest.update(token_id.to_bytes(4, "big"))
    return digest.hexdigest()


def build_tokenization_fixture(private_key, fixture_id: str,
                               length: int = PHASE1_LENGTH,
                               vocab_size: int = VOCAB,
                               batch_size: int = PHASE1_BATCH) -> dict:
    """Build the public synthetic sequence record used only for the VJP smoke.

    The historical function name is retained for callers, but the returned record
    explicitly states that tokenizer roundtrip and text-only load are unestablished.
    It cannot satisfy artifact admission by itself.
    """
    if type(batch_size) is not int or batch_size != PHASE1_BATCH:
        raise Q35QBlock("Phase-1 batch size must be 1")
    ids = deterministic_token_ids(private_key, fixture_id, length, vocab_size)
    if deterministic_token_ids(private_key, fixture_id, length, vocab_size) != ids:
        raise Q35QBlock("synthetic sequence is not deterministic")
    _validate_token_ids(ids, length=length, vocab_size=vocab_size)
    record = {
        "fixture_kind": SYNTHETIC_FIXTURE_KIND,
        "fixture_id": fixture_id,
        "length": length,
        "batch_size": batch_size,
        "vocab_size": vocab_size,
        "use_cache": False,
        "secret_commitment_sha256": secret_commitment(private_key),
        "sequence_sha256": sequence_digest(ids),
        "tokenizer_roundtrip_established": False,
        "text_only_load_established": False,
    }
    scan_aggregate_only(record)
    return record


def verify_fixture(record: dict, private_key) -> bool:
    """Verify a synthetic fixture with the private key from the sealed ledger."""
    if not isinstance(record, dict) or set(record) != _SYNTHETIC_FIELDS:
        raise Q35QBlock("synthetic fixture schema mismatch")
    if record["fixture_kind"] != SYNTHETIC_FIXTURE_KIND:
        raise Q35QBlock("synthetic fixture kind mismatch")
    if record["tokenizer_roundtrip_established"] is not False:
        raise Q35QBlock("synthetic fixture cannot establish tokenizer roundtrip")
    if record["text_only_load_established"] is not False:
        raise Q35QBlock("synthetic fixture cannot establish text-only load")
    if record["use_cache"] is not False:
        raise Q35QBlock("synthetic fixture must bind use_cache=False")
    if type(record["batch_size"]) is not int or record["batch_size"] != PHASE1_BATCH:
        raise Q35QBlock("fixture batch size must be 1")
    _pos_int(record["length"], "length")
    _pos_int(record["vocab_size"], "vocab_size")
    _valid_hex64(record["secret_commitment_sha256"], "secret commitment")
    _valid_hex64(record["sequence_sha256"], "sequence digest")

    key = _private_key(private_key)
    if not hmac.compare_digest(
        secret_commitment(key), record["secret_commitment_sha256"]
    ):
        return False
    ids = deterministic_token_ids(
        key, record["fixture_id"], record["length"], record["vocab_size"]
    )
    return hmac.compare_digest(sequence_digest(ids), record["sequence_sha256"])


def validate_tokenization_admission_fixture(record: dict,
                                            tokenizer_id: str) -> dict:
    """Validate the only tokenization fixture schema accepted by admission.

    The record must come from two identical runs of the pinned tokenizer and a
    successful text-only load probe. The private text remains sealed and is bound
    only by a keyed HMAC commitment.
    """
    if not isinstance(record, dict) or set(record) != _TOKENIZER_ADMISSION_FIELDS:
        raise Q35QBlock("tokenization admission fixture schema mismatch")
    if record["fixture_kind"] != TOKENIZER_FIXTURE_KIND:
        raise Q35QBlock("tokenization admission fixture kind mismatch")
    if not isinstance(tokenizer_id, str) or not tokenizer_id:
        raise Q35QBlock("tokenizer identity is missing")
    if record["tokenizer_roundtrip_established"] is not True:
        raise Q35QBlock("tokenizer roundtrip is not established")
    if record["text_only_load_established"] is not True:
        raise Q35QBlock("text-only load is not established")
    if record["use_cache"] is not False:
        raise Q35QBlock("tokenization fixture must bind use_cache=False")
    if type(record["batch_size"]) is not int or record["batch_size"] != PHASE1_BATCH:
        raise Q35QBlock("tokenization fixture batch size must be 1")
    if type(record["length"]) is not int or record["length"] != PHASE1_LENGTH:
        raise Q35QBlock("tokenization fixture length must be 32")
    if type(record["vocab_size"]) is not int or record["vocab_size"] != VOCAB:
        raise Q35QBlock("tokenization fixture vocabulary mismatch")
    if type(record["determinism_repeats"]) is not int or record["determinism_repeats"] < 2:
        raise Q35QBlock("tokenizer determinism requires at least two repeats")
    if record["private_input_commitment_kind"] != "hmac-sha256":
        raise Q35QBlock("private input must use a keyed HMAC commitment")

    for field in (
        "tokenizer_identity_sha256",
        "private_input_commitment_sha256",
        "sequence_sha256",
    ):
        _valid_hex64(record[field], field)
    expected_tokenizer_digest = hashlib.sha256(tokenizer_id.encode()).hexdigest()
    if not hmac.compare_digest(
        record["tokenizer_identity_sha256"], expected_tokenizer_digest
    ):
        raise Q35QBlock("tokenization fixture tokenizer identity mismatch")
    scan_aggregate_only(record)
    return dict(record)
