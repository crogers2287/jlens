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


@dataclass
class LoaderSpec:
    """Frozen, deterministic loader settings for a Phase-1 exact-VJP attempt."""
    path_name: str                       # "gptq" | "nf4"
    use_cache: bool
    mtp_disabled: bool
    speculative_disabled: bool
    frozen_weights: bool
    eager: bool
    attn_impl: str
    serving_markers: tuple = field(default_factory=tuple)

    def validate(self) -> dict:
        if self.path_name not in VALID_PATHS:
            raise Q35QBlock("unknown loader path")
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
            raise Q35QBlock(f"inference-only kernels not authorized: {','.join(inference)}")
        return {"path_name": self.path_name, "result": "pass"}


def build_device_plan(split_after: int | None = None, gpus=(0, 1),
                      num_layers: int = QWEN35_35B_A3B_ARCH["num_hidden_layers"]) -> dict:
    """Explicit module->device map across exactly two GPUs. Layers
    [0, split_after) go to gpus[0] and [split_after, num_layers) to gpus[1];
    the embedding sits with the first block, the final norm and lm_head with the
    last. Validated (no "auto", no cpu/disk/meta offload)."""
    if len(gpus) != 2 or len(set(gpus)) != 2:
        raise Q35QBlock("plan supports exactly two distinct GPUs")
    if split_after is None:
        split_after = num_layers // 2
    if not isinstance(split_after, int) or isinstance(split_after, bool) \
            or not (0 < split_after < num_layers):
        raise Q35QBlock("split_after out of range")
    g0, g1 = gpus
    dm = {"model.embed_tokens": g0}
    for i in range(num_layers):
        dm[f"model.layers.{i}"] = g0 if i < split_after else g1
    dm["model.norm"] = g1
    dm["lm_head"] = g1
    # The plan is the complete, explicit placement: every generated module is a
    # required-inventory entry for the hardened validator.
    validate_device_map(dm, allowed_devices=tuple(gpus),
                        required_modules=tuple(dm.keys()))
    return dm


def transport_boundary(device_map: dict) -> int:
    """The single layer index where the residual stream crosses GPUs (device of
    layer i-1 != device of layer i). Fails closed unless there is exactly one
    crossing (a clean two-way split), which an explicit training-compatible plan
    requires for a recorded cross-device transport point."""
    layer_dev = {}
    for k, v in device_map.items():
        m = _LAYER_RE.match(k)
        if m:
            layer_dev[int(m.group(1))] = v
    if not layer_dev:
        raise Q35QBlock("no layers in device map")
    crossings, prev = [], None
    for i in sorted(layer_dev):
        if prev is not None and layer_dev[i] != prev:
            crossings.append(i)
        prev = layer_dev[i]
    if len(crossings) != 1:
        raise Q35QBlock(f"expected exactly one GPU boundary, found {len(crossings)}")
    return crossings[0]
