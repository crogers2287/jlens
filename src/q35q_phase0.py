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

_IMMUTABLE_REV = re.compile(r"^[0-9a-f]{40}$")


class Q35QBlock(Exception):
    """Raised on any fail-closed Phase-0 validation failure."""


# ---------- revision + file manifest ----------

def validate_revision(revision: str) -> str:
    """A pinned revision must be an immutable 40-hex commit, not a branch."""
    if not isinstance(revision, str) or not _IMMUTABLE_REV.match(revision):
        raise Q35QBlock("revision is not an immutable 40-hex commit sha")
    return revision


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_file_manifest(root: str, manifest: dict) -> dict:
    """manifest: {relpath: sha256}. Every listed file must exist and match.
    Fails closed on empty manifest or any missing/mismatched file."""
    if not manifest:
        raise Q35QBlock("empty file manifest")
    bad = []
    for rel, want in sorted(manifest.items()):
        p = os.path.join(root, rel)
        if not os.path.isfile(p) or sha256_file(p) != want:
            bad.append(rel)
    if bad:
        raise Q35QBlock(f"manifest mismatch: {len(bad)} file(s)")
    return {"files": len(manifest), "result": "pass"}


# ---------- architecture ----------

def validate_architecture(config: dict, expected: dict = QWEN35_35B_A3B_ARCH) -> dict:
    """config: model-config fields. Must match the frozen structure exactly on
    every expected key; the vision encoder must not be present."""
    bad = [k for k, v in expected.items() if config.get(k) != v]
    if config.get("vision_config") or config.get("has_vision"):
        bad.append("vision_encoder_present")
    if bad:
        raise Q35QBlock(f"architecture mismatch: {','.join(sorted(bad))}")
    return {"arch_keys_checked": len(expected), "result": "pass"}


# ---------- source/target layers ----------

def validate_layers(source_layer: int, target_layer: int = FINAL_RESIDUAL_LAYER,
                    num_layers: int = QWEN35_35B_A3B_ARCH["num_hidden_layers"]) -> dict:
    for name, v in (("source", source_layer), ("target", target_layer)):
        if not isinstance(v, int) or isinstance(v, bool) or not (0 <= v < num_layers):
            raise Q35QBlock(f"{name} layer out of range")
    if target_layer != FINAL_RESIDUAL_LAYER:
        raise Q35QBlock("target must be the final residual layer")
    if source_layer >= target_layer:
        raise Q35QBlock("source layer must precede target for transport")
    return {"source": source_layer, "target": target_layer, "result": "pass"}


# ---------- device placement ----------

def validate_device_map(device_map, allowed_devices=(0, 1)) -> dict:
    """Reject "auto"; require an explicit non-empty module->device dict placing
    every module on an allowed GPU; reject cpu/disk/meta offload."""
    if device_map == "auto" or not isinstance(device_map, dict) or not device_map:
        raise Q35QBlock('device_map must be an explicit non-empty module->device dict')
    offloaded, misplaced = [], []
    for mod, dev in device_map.items():
        if isinstance(dev, str) and dev.strip().lower() in OFFLOAD_TARGETS:
            offloaded.append(mod)
        elif isinstance(dev, int) and not isinstance(dev, bool):
            if dev not in allowed_devices:
                misplaced.append(mod)
        else:
            misplaced.append(mod)
    if offloaded:
        raise Q35QBlock(f"cpu/disk/meta offload on {len(offloaded)} module(s)")
    if misplaced:
        raise Q35QBlock(f"disallowed device placement on {len(misplaced)} module(s)")
    return {"modules": len(device_map),
            "devices": sorted({v for v in device_map.values()}),
            "result": "pass"}


# ---------- quantization config ----------

def canonical_quant_config(cfg: dict) -> str:
    """Deterministic canonical serialization for equality/hashing."""
    return json.dumps(cfg, sort_keys=True, separators=(",", ":"))


def quant_configs_equal(a: dict, b: dict) -> bool:
    return canonical_quant_config(a) == canonical_quant_config(b)


def detect_inference_only(markers) -> list:
    """markers: iterable of strings from serving/kernel config. Returns the
    sorted set of inference-only markers found (non-empty => not autograd)."""
    return sorted({m for token in markers if isinstance(token, str)
                   for m in INFERENCE_ONLY_MARKERS if m in token.lower()})


# ---------- aggregate-only privacy scan ----------

def scan_aggregate_only(artifact) -> bool:
    """Fail closed if an artifact carries any forbidden private key or a large
    numeric array (a proxy for a raw tensor/VJP/lens leak)."""
    def walk(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(k, str) and k.lower() in FORBIDDEN_ARTIFACT_KEYS:
                    raise Q35QBlock(f"forbidden artifact key: {k}")
                walk(v, f"{path}.{k}")
        elif isinstance(obj, (list, tuple)):
            if len(obj) > 64 and all(isinstance(x, (int, float))
                                     and not isinstance(x, bool) for x in obj):
                raise Q35QBlock(f"raw numeric array at {path or '<root>'}")
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")
    walk(artifact)
    return True


# ---------- VJP / resource gate artifact (aggregate-only) ----------

@dataclass
class VJPGateArtifact:
    """Aggregate booleans/scalars for a one-sequence exact-VJP feasibility gate.
    Holds no tensors, tokens, or per-example data."""
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

    def gates(self) -> dict:
        return {
            "vjp_non_none": bool(self.vjp_non_none),
            "vjp_nonzero": bool(self.vjp_nonzero),
            "vjp_finite": bool(self.vjp_finite),
            "repeat_stable": bool(self.repeat_stable),
            "weight_grads_absent": bool(self.weight_grads_absent),
            "token_parity_exact": bool(self.token_parity_exact),
            "logit_parity_within_tol": bool(self.logit_parity_within_tol),
            "no_offload": bool(self.no_offload),
            "identities_match": bool(self.identities_match),
            "mem_per_gpu_ok": self.peak_gib_per_gpu <= MEM_GIB_PER_GPU,
            "mem_total_ok": self.peak_gib_total <= MEM_GIB_TOTAL,
        }

    def passed(self) -> bool:
        return all(self.gates().values())

    def outcome(self):
        """Scoped Q35Q outcome for a passing gate, else None (caller escalates
        to q35q_gptq_autograd_unsupported / q35q_local_exact_vjp_blocked)."""
        if self.path_name not in ("gptq", "nf4"):
            raise Q35QBlock("unknown path_name")
        return f"q35q_{self.path_name}_exact_vjp_passed" if self.passed() else None


# ---------- atomic, resumable private checkpoint ----------

def atomic_write_json(path: str, obj) -> str:
    """Write JSON atomically (temp + fsync + rename). Enforces aggregate-only
    content so a checkpoint can never leak a raw tensor into a public artifact."""
    scan_aggregate_only(obj)
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return path
