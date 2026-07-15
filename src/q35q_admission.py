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

from q35q_phase0 import (
    Q35QBlock,
    canonical_quant_config,
    scan_aggregate_only,
    validate_architecture,
    validate_device_map,
    validate_revision,
)

ADMISSION_BLOCKED = "q35q_artifact_admission_blocked"
ADMISSION_READY = "q35q_admission_ready"

# Required top-level identity fields the amendment must bind.
REQUIRED_FIELDS = (
    "repo_id", "revision", "license", "lineage", "config", "tokenizer_id",
    "generation_id", "custom_code_id", "weight_manifest",
    "param_count_text_only", "omitted_modules", "toolchain", "quant",
    "device_map", "transport", "tokenization_fixture", "driver_files",
    "commit_safe",
)
REQUIRED_TOOLCHAIN = ("transformers", "accelerate", "torch", "cuda",
                      "driver", "backend", "kernel")
REQUIRED_QUANT = ("quant_type", "group_size", "compute_dtype", "storage_dtype")

_HEX64 = set("0123456789abcdef")


class Q35QAdmissionBlock(Q35QBlock):
    """Fail-closed admission failure -> q35q_artifact_admission_blocked."""


def _digest_manifest(manifest: dict) -> str:
    """Deterministic sha256 over a sorted {relpath: sha256} manifest. Binds the
    full manifest cryptographically without embedding it (relpaths are public
    artifact filenames, not local paths)."""
    if not isinstance(manifest, dict) or not manifest:
        raise Q35QAdmissionBlock("empty or malformed manifest")
    lines = []
    for rel in sorted(manifest):
        h = manifest[rel]
        if not (isinstance(h, str) and len(h) == 64 and set(h) <= _HEX64):
            raise Q35QAdmissionBlock(f"bad sha256 for a manifest entry")
        lines.append(f"{rel}:{h}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def build_admission_record(meta: dict) -> dict:
    """Validate admission metadata and return a public-safe aggregate record.
    Raises Q35QAdmissionBlock (caller records `q35q_artifact_admission_blocked`)
    on any missing/mutable/contradictory/unverifiable field."""
    missing = [f for f in REQUIRED_FIELDS
               if f not in meta or meta[f] in (None, "", [], {})]
    if missing:
        raise Q35QAdmissionBlock(f"missing fields: {','.join(sorted(missing))}")

    # Reuse Phase-0 validators, but surface every admission failure as the
    # single fail-closed admission type (-> q35q_artifact_admission_blocked).
    try:
        validate_revision(meta["revision"])
        validate_architecture(meta["config"])
        validate_device_map(meta["device_map"])
    except Q35QBlock as exc:
        raise Q35QAdmissionBlock(str(exc)) from exc

    if meta.get("commit_safe") is not True:
        raise Q35QAdmissionBlock("commit-safety not established")

    tc = meta["toolchain"]
    if not isinstance(tc, dict) or any(not tc.get(k) for k in REQUIRED_TOOLCHAIN):
        raise Q35QAdmissionBlock("incomplete toolchain identities")

    q = meta["quant"]
    if not isinstance(q, dict) or any(k not in q for k in REQUIRED_QUANT):
        raise Q35QAdmissionBlock("incomplete quantization config")

    if not isinstance(meta["param_count_text_only"], int) or \
            isinstance(meta["param_count_text_only"], bool) or \
            meta["param_count_text_only"] <= 0:
        raise Q35QAdmissionBlock("bad text-only parameter count")

    omitted = [str(m).lower() for m in meta["omitted_modules"]]
    if not any("vision" in m or "visual" in m for m in omitted):
        raise Q35QAdmissionBlock("vision module not recorded as omitted")

    record = {
        "outcome": ADMISSION_READY,
        "repo_id": meta["repo_id"],
        "revision": meta["revision"],
        "license": meta["license"],
        "lineage": meta["lineage"],
        "architecture_ok": True,
        "param_count_text_only": int(meta["param_count_text_only"]),
        "omitted_modules": sorted(set(omitted)),
        "tokenizer_id": meta["tokenizer_id"],
        "generation_id": meta["generation_id"],
        "custom_code_id": meta["custom_code_id"],
        "toolchain": {k: str(tc[k]) for k in REQUIRED_TOOLCHAIN},
        "quant_canonical": canonical_quant_config(q),
        "weight_file_count": len(meta["weight_manifest"]),
        "weight_manifest_digest": _digest_manifest(meta["weight_manifest"]),
        "device_module_count": len(meta["device_map"]),
        "device_set": sorted({v for v in meta["device_map"].values()}),
        "transport": meta["transport"],
        "tokenization_fixture_digest": hashlib.sha256(
            json.dumps(meta["tokenization_fixture"], sort_keys=True).encode()
        ).hexdigest(),
        "driver_file_count": len(meta["driver_files"]),
        "driver_manifest_digest": _digest_manifest(meta["driver_files"]),
        "commit_safe": True,
    }
    scan_aggregate_only(record)  # guarantee nothing private leaked
    return record


def admission_outcome(meta: dict):
    """Convenience: (record, ADMISSION_READY) on success; (None,
    ADMISSION_BLOCKED) on any fail-closed admission failure."""
    try:
        return build_admission_record(meta), ADMISSION_READY
    except Q35QAdmissionBlock:
        return None, ADMISSION_BLOCKED


def verify_manifest_digest(manifest: dict, digest: str) -> bool:
    """True iff `manifest` reproduces the bound `digest` (re-admission check)."""
    return _digest_manifest(manifest) == digest
