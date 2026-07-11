"""Observation-only MoE router telemetry for the M36V isolated vLLM runtime.

No vLLM source file is modified. Expert ids ride the native
``enable_return_routed_experts`` path; weights, entropy/mass scalars, and a
small raw-logit validation sample come from a registered worker-extension
override that wraps ``router.select_experts`` and
``routed_experts.forward_modular`` on each MoE layer at runtime.
"""

from jlens_vllm_telemetry.capture import (
    RouterTelemetryCollector,
    install_router_telemetry,
    uninstall_router_telemetry,
)

__all__ = [
    "RouterTelemetryCollector",
    "install_router_telemetry",
    "uninstall_router_telemetry",
]
