"""Q35Q deterministic tokenization / text-only load fixtures (CPU-only).

Phase 0 requires deterministic tokenization and text-only load fixtures so the
Phase-1 one-sequence exact-VJP gate runs on a reproducible input without a live
tokenizer or model. This module derives a deterministic synthetic token-id
sequence from an integer seed (no corpus, no prompt) and emits an aggregate-only
fixture record binding only the sequence DIGEST, length, batch, and settings.

Raw token ids are returned for in-process Phase-1 use ONLY and are never placed
in the committed fixture record (the privacy boundary forbids committing token
ids). See docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md (Phase 0 / Phase 1).
"""
from __future__ import annotations

import hashlib

from q35q_phase0 import QWEN35_35B_A3B_ARCH, Q35QBlock, scan_aggregate_only

VOCAB = QWEN35_35B_A3B_ARCH["vocab_size"]  # 248320
PHASE1_LENGTH = 32
PHASE1_BATCH = 1


def _pos_int(value, name):
    if type(value) is not int or isinstance(value, bool) or value <= 0:
        raise Q35QBlock(f"{name} must be a positive int")
    return value


def deterministic_token_ids(seed: int, length: int = PHASE1_LENGTH,
                            vocab_size: int = VOCAB) -> tuple:
    """Reproducible synthetic token-id sequence derived from `seed` via a
    SHA-256 keystream (no corpus, no tokenizer). PRIVATE — never commit these."""
    if type(seed) is not int or isinstance(seed, bool) or seed < 0:
        raise Q35QBlock("seed must be a non-negative int")
    _pos_int(length, "length")
    _pos_int(vocab_size, "vocab_size")
    ids, counter = [], 0
    while len(ids) < length:
        block = hashlib.sha256(f"q35q-fixture:{seed}:{counter}".encode()).digest()
        for i in range(0, len(block), 4):
            if len(ids) >= length:
                break
            ids.append(int.from_bytes(block[i:i + 4], "big") % vocab_size)
        counter += 1
    return tuple(ids)


def sequence_digest(token_ids) -> str:
    return hashlib.sha256(",".join(str(t) for t in token_ids).encode()).hexdigest()


def build_tokenization_fixture(seed: int, length: int = PHASE1_LENGTH,
                               vocab_size: int = VOCAB,
                               batch_size: int = PHASE1_BATCH) -> dict:
    """Validate determinism and range, and return an aggregate-only fixture
    record (digest + shape + settings only; no raw ids)."""
    if batch_size != PHASE1_BATCH:
        raise Q35QBlock("Phase-1 batch size must be 1")
    ids = deterministic_token_ids(seed, length, vocab_size)
    if deterministic_token_ids(seed, length, vocab_size) != ids:
        raise Q35QBlock("tokenization is not deterministic")
    if len(ids) != length or any(not (0 <= t < vocab_size) for t in ids):
        raise Q35QBlock("token ids out of range")
    record = {
        "length": length,
        "batch_size": batch_size,
        "vocab_size": vocab_size,
        "seed": seed,
        "use_cache": False,
        "sequence_sha256": sequence_digest(ids),
    }
    scan_aggregate_only(record)  # guarantee no raw ids leak into the record
    return record


def verify_fixture(record: dict) -> bool:
    """Recompute the fixture from its bound (seed, length, vocab) and confirm the
    digest matches — a reproducibility check for a committed fixture record."""
    for k in ("seed", "length", "vocab_size", "sequence_sha256", "batch_size"):
        if k not in record:
            raise Q35QBlock(f"fixture record missing {k}")
    if record["batch_size"] != PHASE1_BATCH:
        raise Q35QBlock("fixture batch size must be 1")
    ids = deterministic_token_ids(record["seed"], record["length"],
                                  record["vocab_size"])
    return sequence_digest(ids) == record["sequence_sha256"]
