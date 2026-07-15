"""Q35Q loader-path spec + explicit training-compatible multi-GPU placement
planner (CPU-only; no model load, no GPU, no network).

The protocol forbids `device_map="auto"` as evidence of a training-compatible
shard plan and requires deterministic eager execution with `use_cache=False`,
MTP/speculative decoding disabled, and frozen weights. This module produces and
validates that explicit plan and loader spec ahead of time so a later GPU run
has a recorded placement instead of inference autoplacement.

No torch/transformers import, no weights, no capture. See
docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md (Phase 0 / Phase 1).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from q35q_phase0 import (
    Q35QBlock,
    QWEN35_35B_A3B_ARCH,
    detect_inference_only,
    validate_device_map,
)

VALID_PATHS = ("gptq", "nf4")
_LAYER_RE = re.compile(r"model\.layers\.(\d+)$")
_BOOL_FIELDS = (
    "use_cache",
    "mtp_disabled",
    "speculative_disabled",
    "frozen_weights",
    "eager",
)


def _required_modules(num_layers: int) -> tuple[str, ...]:
    return (
        "model.embed_tokens",
        *(f"model.layers.{i}" for i in range(num_layers)),
        "model.norm",
        "lm_head",
    )


def _validate_num_layers(num_layers: int) -> int:
    frozen = QWEN35_35B_A3B_ARCH["num_hidden_layers"]
    if type(num_layers) is not int or num_layers != frozen:
        raise Q35QBlock(f"num_layers must match frozen Q35Q architecture ({frozen})")
    return num_layers


@dataclass
class LoaderSpec:
    """Frozen, deterministic loader settings for a Phase-1 exact-VJP attempt."""

    path_name: str  # "gptq" | "nf4"
    use_cache: bool
    mtp_disabled: bool
    speculative_disabled: bool
    frozen_weights: bool
    eager: bool
    attn_impl: str
    serving_markers: tuple = field(default_factory=tuple)

    def validate(self) -> dict:
        if not isinstance(self.path_name, str) or self.path_name not in VALID_PATHS:
            raise Q35QBlock("unknown loader path")
        for field_name in _BOOL_FIELDS:
            if type(getattr(self, field_name)) is not bool:
                raise Q35QBlock(f"{field_name} must be a strict boolean")
        if not isinstance(self.attn_impl, str):
            raise Q35QBlock("attention implementation must be a string")
        if self.use_cache:
            raise Q35QBlock("use_cache must be False")
        if not (self.mtp_disabled and self.speculative_disabled):
            raise Q35QBlock("MTP/speculative decoding must be disabled")
        if not self.frozen_weights:
            raise Q35QBlock("weights must be frozen")
        if not self.eager or self.attn_impl != "eager":
            raise Q35QBlock("deterministic eager execution required")
        inference = detect_inference_only(self.serving_markers)
        if inference:
            raise Q35QBlock(
                f"inference-only kernels not authorized: {','.join(inference)}"
            )
        return {"path_name": self.path_name, "result": "pass"}


def build_device_plan(
    split_after: int | None = None,
    gpus=(0, 1),
    num_layers: int = QWEN35_35B_A3B_ARCH["num_hidden_layers"],
) -> dict:
    """Build the exact Q35Q module-to-device plan across two GPUs.

    Layers ``[0, split_after)`` go to ``gpus[0]`` and the remaining layers go
    to ``gpus[1]``. The embedding stays with the first block; final norm and
    output head stay with the last block. The returned mapping is complete and
    contains no implicit parent placement, autoplacement, or offload target.
    """
    num_layers = _validate_num_layers(num_layers)
    if not isinstance(gpus, (tuple, list)) or len(gpus) != 2:
        raise Q35QBlock("plan supports exactly two GPU ids")
    if any(type(gpu) is not int for gpu in gpus) or len(set(gpus)) != 2:
        raise Q35QBlock("plan supports exactly two distinct integer GPU ids")
    if split_after is None:
        split_after = num_layers // 2
    if type(split_after) is not int or not (0 < split_after < num_layers):
        raise Q35QBlock("split_after out of range")

    g0, g1 = gpus
    dm = {"model.embed_tokens": g0}
    for i in range(num_layers):
        dm[f"model.layers.{i}"] = g0 if i < split_after else g1
    dm["model.norm"] = g1
    dm["lm_head"] = g1

    required = _required_modules(num_layers)
    validate_device_map(
        dm,
        allowed_devices=tuple(gpus),
        required_modules=required,
    )
    if tuple(dm) != required:
        raise Q35QBlock("device plan is not the canonical complete module inventory")
    return dm


def transport_boundary(
    device_map: dict,
    num_layers: int = QWEN35_35B_A3B_ARCH["num_hidden_layers"],
) -> int:
    """Return the single residual-stream cross-GPU boundary.

    This function accepts only the canonical complete Q35Q plan: embedding,
    every layer from 0 through 39, final norm, and output head, with exactly one
    contiguous transition between two integer GPU ids. Missing layers, extra
    modules, endpoint mismatches, offload targets, and zig-zag placement fail
    closed rather than producing a misleading boundary.
    """
    num_layers = _validate_num_layers(num_layers)
    if not isinstance(device_map, dict) or not device_map:
        raise Q35QBlock("device map must be a non-empty dict")

    required = _required_modules(num_layers)
    if set(device_map) != set(required):
        raise Q35QBlock("device map is not the complete canonical Q35Q inventory")

    layer_dev: dict[int, int] = {}
    for key, device in device_map.items():
        match = _LAYER_RE.fullmatch(key)
        if match:
            layer_dev[int(match.group(1))] = device
    if set(layer_dev) != set(range(num_layers)):
        raise Q35QBlock("device map layer inventory is incomplete or out of range")

    devices = set(layer_dev.values())
    if len(devices) != 2 or any(type(device) is not int for device in devices):
        raise Q35QBlock("layer plan must use exactly two integer GPU ids")
    validate_device_map(
        device_map,
        allowed_devices=tuple(sorted(devices)),
        required_modules=required,
    )

    if device_map["model.embed_tokens"] != layer_dev[0]:
        raise Q35QBlock("embedding must share the first layer device")
    final_device = layer_dev[num_layers - 1]
    if device_map["model.norm"] != final_device or device_map["lm_head"] != final_device:
        raise Q35QBlock("final norm and lm_head must share the final layer device")

    crossings = [
        index
        for index in range(1, num_layers)
        if layer_dev[index] != layer_dev[index - 1]
    ]
    if len(crossings) != 1:
        raise Q35QBlock(f"expected exactly one GPU boundary, found {len(crossings)}")
    return crossings[0]
