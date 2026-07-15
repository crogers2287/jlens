"""Q35Q Phase 0 — CPU-only admission, architecture, quantization, and
device-placement validators for the quantized Qwen3.5-35B-A3B Jacobian path.

Pure-Python, stdlib-only, fail-closed. No model loading, no GPU, no network,
and no private data. Operates only on public model-card facts and
caller-supplied metadata (config dicts, device maps, file manifests) and
produces aggregate-only artifact schemas.

See docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md and steer.md
(commit adopting Q35Q). Phase 0 produces no model-generated scientific row;
GPU execution is prohibited until M38E releases the dual-3090 window.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from dataclasses import dataclass

# --- Frozen architecture spec (public Qwen3.5-35B-A3B model-card facts) ---
QWEN35_35B_A3B_ARCH = {
    "hidden_size": 2048,
    "num_hidden_layers": 40,
    "num_routed_experts": 256,
    "num_experts_per_tok": 8,
    "num_shared_experts": 1,
    "moe_intermediate_size": 512,
    "vocab_size": 248320,
}

# 0-indexed final LM residual layer (last of 40 language-model layers).
FINAL_RESIDUAL_LAYER = 39

# Per-GPU / aggregate peak-memory ceilings (GiB) from the frozen protocol.
MEM_GIB_PER_GPU = 23.0
MEM_GIB_TOTAL = 46.0

# Serving/kernel markers that are inference-only and do NOT expose exact VJPs.
INFERENCE_ONLY_MARKERS = ("moe_wna16", "vllm", "sglang", "marlin")

# Placement targets that block the primary exact-VJP fit path.
OFFLOAD_TARGETS = ("cpu", "disk", "meta")

# Keys forbidden in any public aggregate artifact (privacy boundary).
FORBIDDEN_ARTIFACT_KEYS = (
    "prompt", "prompts", "text", "corpus", "token", "tokens", "token_ids",
    "hidden", "activation", "activations", "expert_output", "route", "routes",
    "jacobian", "jacobians", "vjp_values", "lens_matrix", "lens", "weights",
    "per_example", "readout", "readouts", "path", "paths", "cache",
    "env", "environ", "secret",
)

_BOOL_GATE_FIELDS = (
    "vjp_non_none", "vjp_nonzero", "vjp_finite", "repeat_stable",
    "weight_grads_absent", "token_parity_exact", "logit_parity_within_tol",
    "no_offload", "identities_match",
)

_IMMUTABLE_REV = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class Q35QBlock(Exception):
    """Raised on any fail-closed Phase-0 validation failure."""


# ---------- revision + file manifest ----------

def validate_revision(revision: str) -> str:
    """A pinned revision must be an immutable 40-hex commit, not a branch."""
    if not isinstance(revision, str) or not _IMMUTABLE_REV.fullmatch(revision):
        raise Q35QBlock("revision is not an immutable 40-hex commit sha")
    return revision


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_manifest_path(root_real: str, rel: str) -> str:
    """Resolve one manifest key while preventing absolute paths and root escape."""
    if not isinstance(rel, str) or not rel or os.path.isabs(rel):
        raise Q35QBlock("manifest path must be a non-empty relative path")
    normalized = os.path.normpath(rel)
    if normalized in ("", ".", "..") or normalized.startswith(".." + os.sep):
        raise Q35QBlock("manifest path escapes artifact root")
    candidate = os.path.realpath(os.path.join(root_real, normalized))
    try:
        inside = os.path.commonpath((root_real, candidate)) == root_real
    except ValueError as exc:
        raise Q35QBlock("manifest path is not comparable to artifact root") from exc
    if not inside:
        raise Q35QBlock("manifest path escapes artifact root")
    return candidate


def verify_file_manifest(root: str, manifest: dict) -> dict:
    """Verify every listed artifact file by a strict lowercase SHA-256 digest.

    Paths must be relative and remain inside ``root`` after symlink resolution.
    Fails closed on an invalid root, empty manifest, malformed digest, missing
    file, path escape, or digest mismatch.
    """
    if not isinstance(root, str) or not root:
        raise Q35QBlock("artifact root must be a non-empty path")
    root_real = os.path.realpath(root)
    if not os.path.isdir(root_real):
        raise Q35QBlock("artifact root is not a directory")
    if not isinstance(manifest, dict) or not manifest:
        raise Q35QBlock("empty or invalid file manifest")

    bad = []
    for rel, want in sorted(manifest.items()):
        if not isinstance(want, str) or not _SHA256.fullmatch(want):
            raise Q35QBlock(f"malformed sha256 for manifest entry: {rel!r}")
        path = _resolve_manifest_path(root_real, rel)
        if not os.path.isfile(path) or sha256_file(path) != want:
            bad.append(rel)
    if bad:
        raise Q35QBlock(f"manifest mismatch: {len(bad)} file(s)")
    return {"files": len(manifest), "result": "pass"}


# ---------- architecture ----------

def validate_architecture(config: dict, expected: dict = QWEN35_35B_A3B_ARCH) -> dict:
    """config: model-config fields. Must match the frozen structure exactly on
    every expected key; the vision encoder must not be present."""
    if not isinstance(config, dict):
        raise Q35QBlock("architecture config must be a dict")
    bad = [k for k, v in expected.items() if config.get(k) != v]
    if config.get("vision_config") or config.get("has_vision"):
        bad.append("vision_encoder_present")
    if bad:
        raise Q35QBlock(f"architecture mismatch: {','.join(sorted(bad))}")
    return {"arch_keys_checked": len(expected), "result": "pass"}


# ---------- source/target layers ----------

def validate_layers(source_layer: int, target_layer: int = FINAL_RESIDUAL_LAYER,
                    num_layers: int = QWEN35_35B_A3B_ARCH["num_hidden_layers"]) -> dict:
    for name, value in (("source", source_layer), ("target", target_layer)):
        if not isinstance(value, int) or isinstance(value, bool) or not (0 <= value < num_layers):
            raise Q35QBlock(f"{name} layer out of range")
    if target_layer != FINAL_RESIDUAL_LAYER:
        raise Q35QBlock("target must be the final residual layer")
    if source_layer >= target_layer:
        raise Q35QBlock("source layer must precede target for transport")
    return {"source": source_layer, "target": target_layer, "result": "pass"}


# ---------- device placement ----------

def validate_device_map(device_map, allowed_devices=(0, 1), required_modules=None) -> dict:
    """Validate explicit, complete module placement on the admitted GPUs.

    ``required_modules`` is mandatory and must enumerate every module whose
    placement the admission amendment binds. Every required module must have an
    explicit map entry. ``auto`` and cpu/disk/meta offload fail closed.
    """
    if device_map == "auto" or not isinstance(device_map, dict) or not device_map:
        raise Q35QBlock("device_map must be an explicit non-empty module->device dict")

    if (
        not isinstance(allowed_devices, (tuple, list, set))
        or not allowed_devices
        or any(type(device) is not int for device in allowed_devices)
    ):
        raise Q35QBlock("allowed_devices must be a non-empty collection of integer GPU ids")
    allowed = set(allowed_devices)

    if (
        not isinstance(required_modules, (tuple, list, set))
        or not required_modules
        or any(not isinstance(module, str) or not module for module in required_modules)
    ):
        raise Q35QBlock("required module inventory is missing or invalid")
    required = set(required_modules)
    if len(required) != len(required_modules):
        raise Q35QBlock("required module inventory contains duplicates")

    invalid_modules = [
        module for module in device_map
        if not isinstance(module, str) or not module
    ]
    if invalid_modules:
        raise Q35QBlock(f"invalid module key on {len(invalid_modules)} entry/entries")

    missing = sorted(required.difference(device_map))
    if missing:
        raise Q35QBlock(f"device_map missing {len(missing)} required module(s)")

    offloaded, misplaced = [], []
    for module, device in device_map.items():
        if isinstance(device, str) and device.strip().lower() in OFFLOAD_TARGETS:
            offloaded.append(module)
        elif type(device) is int:
            if device not in allowed:
                misplaced.append(module)
        else:
            misplaced.append(module)
    if offloaded:
        raise Q35QBlock(f"cpu/disk/meta offload on {len(offloaded)} module(s)")
    if misplaced:
        raise Q35QBlock(f"disallowed device placement on {len(misplaced)} module(s)")
    return {
        "modules": len(device_map),
        "required_modules_checked": len(required),
        "devices": sorted(set(device_map.values())),
        "result": "pass",
    }


# ---------- quantization config ----------

def canonical_quant_config(cfg: dict) -> str:
    """Deterministic canonical serialization for strict equality and hashing."""
    if not isinstance(cfg, dict):
        raise Q35QBlock("quantization config must be a dict")
    try:
        return json.dumps(
            cfg, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
    except (TypeError, ValueError) as exc:
        raise Q35QBlock("quantization config is not canonical JSON") from exc


def quant_configs_equal(a: dict, b: dict) -> bool:
    return canonical_quant_config(a) == canonical_quant_config(b)


def detect_inference_only(markers) -> list:
    """Return inference-only serving/kernel markers found in an iterable."""
    if isinstance(markers, (str, bytes)) or markers is None:
        raise Q35QBlock("kernel markers must be an iterable of strings")
    try:
        values = list(markers)
    except TypeError as exc:
        raise Q35QBlock("kernel markers must be an iterable of strings") from exc
    if any(not isinstance(token, str) for token in values):
        raise Q35QBlock("kernel markers must contain strings only")
    return sorted({
        marker
        for token in values
        for marker in INFERENCE_ONLY_MARKERS
        if marker in token.lower()
    })


# ---------- aggregate-only privacy scan ----------

def scan_aggregate_only(artifact) -> bool:
    """Fail closed on forbidden private keys, raw arrays, or nonfinite scalars."""
    def walk(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(key, str) and key.lower() in FORBIDDEN_ARTIFACT_KEYS:
                    raise Q35QBlock(f"forbidden artifact key: {key}")
                walk(value, f"{path}.{key}")
        elif isinstance(obj, (list, tuple)):
            if len(obj) > 64 and all(
                isinstance(value, (int, float)) and not isinstance(value, bool)
                for value in obj
            ):
                raise Q35QBlock(f"raw numeric array at {path or '<root>'}")
            for index, value in enumerate(obj):
                walk(value, f"{path}[{index}]")
        elif isinstance(obj, float) and not math.isfinite(obj):
            raise Q35QBlock(f"nonfinite scalar at {path or '<root>'}")
    walk(artifact)
    return True


# ---------- VJP / resource gate artifact (aggregate-only) ----------

@dataclass
class VJPGateArtifact:
    """Aggregate booleans/scalars for a one-sequence exact-VJP feasibility gate.

    Holds no tensors, tokens, or per-example data. Field types are checked
    strictly so truthy strings, negative memory, and NaN/Inf cannot pass.
    """
    path_name: str            # "gptq" | "nf4"
    vjp_non_none: bool
    vjp_nonzero: bool
    vjp_finite: bool
    repeat_stable: bool
    weight_grads_absent: bool
    token_parity_exact: bool
    logit_parity_within_tol: bool
    no_offload: bool
    identities_match: bool
    peak_gib_per_gpu: float
    peak_gib_total: float

    def __post_init__(self) -> None:
        if self.path_name not in ("gptq", "nf4"):
            raise Q35QBlock("unknown path_name")
        for field_name in _BOOL_GATE_FIELDS:
            if type(getattr(self, field_name)) is not bool:
                raise Q35QBlock(f"{field_name} must be a strict boolean")
        for field_name in ("peak_gib_per_gpu", "peak_gib_total"):
            value = getattr(self, field_name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise Q35QBlock(f"{field_name} must be finite and nonnegative")

    def gates(self) -> dict:
        return {
            "vjp_non_none": self.vjp_non_none,
            "vjp_nonzero": self.vjp_nonzero,
            "vjp_finite": self.vjp_finite,
            "repeat_stable": self.repeat_stable,
            "weight_grads_absent": self.weight_grads_absent,
            "token_parity_exact": self.token_parity_exact,
            "logit_parity_within_tol": self.logit_parity_within_tol,
            "no_offload": self.no_offload,
            "identities_match": self.identities_match,
            "mem_per_gpu_ok": self.peak_gib_per_gpu <= MEM_GIB_PER_GPU,
            "mem_total_ok": self.peak_gib_total <= MEM_GIB_TOTAL,
        }

    def passed(self) -> bool:
        return all(self.gates().values())

    def outcome(self):
        """Scoped Q35Q outcome for a passing gate, else None."""
        return f"q35q_{self.path_name}_exact_vjp_passed" if self.passed() else None


# ---------- atomic, resumable aggregate checkpoint ----------

def atomic_write_json(path: str, obj) -> str:
    """Write JSON atomically after aggregate-only validation."""
    scan_aggregate_only(obj)
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(obj, handle, sort_keys=True, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return path
