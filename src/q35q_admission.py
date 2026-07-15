"""Q35Q artifact-admission amendment schema + builder (CPU-only, aggregate-only).

Binds the exact identities the Q35Q protocol requires before any GPU backward
call and fails closed (`q35q_artifact_admission_blocked`) on missing, mutable,
contradictory, or unverifiable evidence. Produces a public-safe aggregate
record only: repo id, immutable revision, architecture pass, param/omitted
counts, canonical quantization config, toolchain versions, device-placement
summary, a combined weight-manifest digest (binds the full manifest without
listing local paths), tokenization-fixture digest, driver-source manifest
digest, and commit-safety status. No raw weights, tokens, states, local paths,
caches, or env values enter the record.

See docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md ("Artifact admission before
GPU execution"). CPU-only; produces no model-generated scientific row.
"""
from __future__ import annotations

import hashlib
import json
import posixpath

from q35q_phase0 import (
    Q35QBlock,
    canonical_quant_config,
    scan_aggregate_only,
    validate_architecture,
    validate_device_map,
    validate_revision,
)
from q35q_fixtures import validate_tokenization_admission_fixture

ADMISSION_BLOCKED = "q35q_artifact_admission_blocked"
ADMISSION_READY = "q35q_admission_ready"

REQUIRED_FIELDS = (
    "repo_id", "revision", "license", "lineage", "config", "tokenizer_id",
    "generation_id", "custom_code_id", "weight_manifest",
    "param_count_text_only", "omitted_modules", "toolchain", "quant",
    "device_map", "required_modules", "transport", "tokenization_fixture",
    "driver_files", "commit_safe",
)
REQUIRED_STRING_FIELDS = (
    "repo_id", "license", "lineage", "tokenizer_id", "generation_id",
    "custom_code_id", "transport",
)
REQUIRED_TOOLCHAIN = (
    "transformers", "accelerate", "torch", "cuda", "driver", "backend", "kernel",
)
REQUIRED_QUANT = ("quant_type", "group_size", "compute_dtype", "storage_dtype")

_HEX64 = set("0123456789abcdef")


class Q35QAdmissionBlock(Q35QBlock):
    """Fail-closed admission failure -> q35q_artifact_admission_blocked."""


def _validate_manifest_relpath(rel: str) -> str:
    """Require a canonical public artifact-relative POSIX path."""
    if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel:
        raise Q35QAdmissionBlock("manifest entry is not a relative POSIX path")
    normalized = posixpath.normpath(rel)
    if normalized in ("", ".", "..") or normalized.startswith("../"):
        raise Q35QAdmissionBlock("manifest entry escapes artifact root")
    if normalized != rel:
        raise Q35QAdmissionBlock("manifest entry is not canonical")
    return normalized


def _digest_manifest(manifest: dict) -> str:
    """Hash a canonical {artifact-relative path: lowercase sha256} manifest."""
    if not isinstance(manifest, dict) or not manifest:
        raise Q35QAdmissionBlock("empty or malformed manifest")
    lines = []
    for rel in sorted(manifest):
        normalized = _validate_manifest_relpath(rel)
        digest = manifest[rel]
        if not (
            isinstance(digest, str)
            and len(digest) == 64
            and set(digest) <= _HEX64
        ):
            raise Q35QAdmissionBlock("bad sha256 for a manifest entry")
        lines.append(f"{normalized}:{digest}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _canonical_digest(value, name: str) -> str:
    try:
        serialized = json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
    except (TypeError, ValueError) as exc:
        raise Q35QAdmissionBlock(f"{name} is not canonical JSON") from exc
    return hashlib.sha256(serialized.encode()).hexdigest()


def build_admission_record(meta: dict) -> dict:
    """Validate admission metadata and return a public-safe aggregate record."""
    if not isinstance(meta, dict):
        raise Q35QAdmissionBlock("admission metadata must be a dict")

    missing = [
        field for field in REQUIRED_FIELDS
        if field not in meta or meta[field] in (None, "", [], {})
    ]
    if missing:
        raise Q35QAdmissionBlock(f"missing fields: {','.join(sorted(missing))}")

    for field in REQUIRED_STRING_FIELDS:
        if not isinstance(meta[field], str) or not meta[field].strip():
            raise Q35QAdmissionBlock(f"{field} must be a non-empty string")

    try:
        validate_revision(meta["revision"])
        validate_architecture(meta["config"])
        placement = validate_device_map(
            meta["device_map"], required_modules=meta["required_modules"]
        )
        tokenization_fixture = validate_tokenization_admission_fixture(
            meta["tokenization_fixture"], meta["tokenizer_id"]
        )
    except Q35QBlock as exc:
        raise Q35QAdmissionBlock(str(exc)) from exc

    if meta.get("commit_safe") is not True:
        raise Q35QAdmissionBlock("commit-safety not established")

    toolchain = meta["toolchain"]
    if (
        not isinstance(toolchain, dict)
        or any(
            not isinstance(toolchain.get(key), str) or not toolchain[key].strip()
            for key in REQUIRED_TOOLCHAIN
        )
    ):
        raise Q35QAdmissionBlock("incomplete toolchain identities")

    quant = meta["quant"]
    if not isinstance(quant, dict) or any(key not in quant for key in REQUIRED_QUANT):
        raise Q35QAdmissionBlock("incomplete quantization config")
    try:
        quant_canonical = canonical_quant_config(quant)
    except Q35QBlock as exc:
        raise Q35QAdmissionBlock(str(exc)) from exc

    param_count = meta["param_count_text_only"]
    if (
        not isinstance(param_count, int)
        or isinstance(param_count, bool)
        or param_count <= 0
    ):
        raise Q35QAdmissionBlock("bad text-only parameter count")

    omitted_raw = meta["omitted_modules"]
    if (
        not isinstance(omitted_raw, (list, tuple, set))
        or not omitted_raw
        or any(not isinstance(module, str) or not module for module in omitted_raw)
    ):
        raise Q35QAdmissionBlock("omitted module inventory is malformed")
    omitted = [module.lower() for module in omitted_raw]
    if not any("vision" in module or "visual" in module for module in omitted):
        raise Q35QAdmissionBlock("vision module not recorded as omitted")

    record = {
        "outcome": ADMISSION_READY,
        "repo_id": meta["repo_id"],
        "revision": meta["revision"],
        "license": meta["license"],
        "lineage": meta["lineage"],
        "architecture_ok": True,
        "param_count_text_only": param_count,
        "omitted_modules": sorted(set(omitted)),
        "tokenizer_id": meta["tokenizer_id"],
        "generation_id": meta["generation_id"],
        "custom_code_id": meta["custom_code_id"],
        "toolchain": {key: toolchain[key] for key in REQUIRED_TOOLCHAIN},
        "quant_canonical": quant_canonical,
        "weight_file_count": len(meta["weight_manifest"]),
        "weight_manifest_digest": _digest_manifest(meta["weight_manifest"]),
        "device_module_count": placement["modules"],
        "required_module_count": placement["required_modules_checked"],
        "device_set": placement["devices"],
        "transport": meta["transport"],
        "tokenization_fixture_kind": tokenization_fixture["fixture_kind"],
        "tokenization_fixture_digest": _canonical_digest(
            tokenization_fixture, "tokenization fixture"
        ),
        "driver_file_count": len(meta["driver_files"]),
        "driver_manifest_digest": _digest_manifest(meta["driver_files"]),
        "commit_safe": True,
    }
    scan_aggregate_only(record)
    return record


def admission_outcome(meta: dict):
    """Return a record/ready pair or the single scoped blocked outcome."""
    try:
        return build_admission_record(meta), ADMISSION_READY
    except Q35QAdmissionBlock:
        return None, ADMISSION_BLOCKED


def verify_manifest_digest(manifest: dict, digest: str) -> bool:
    """True iff ``manifest`` reproduces the already bound digest."""
    if not isinstance(digest, str) or len(digest) != 64 or set(digest) > _HEX64:
        return False
    try:
        return _digest_manifest(manifest) == digest
    except Q35QAdmissionBlock:
        return False
