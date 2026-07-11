"""vLLM worker extension exposing jLens router telemetry over collective_rpc.

Registered via ``LLM(worker_extension_cls=
"jlens_vllm_telemetry.worker_ext.JlensWorkerExtension")``. vLLM mixes this
class into the worker, so ``self`` is the live worker process object and
``self.model_runner`` is the GPU model runner. All methods are prefixed
``jlens_`` to avoid attribute conflicts (vLLM asserts on collisions).

No vLLM code path changes until ``jlens_install_telemetry`` is called, and
capture stays inert until ``jlens_set_telemetry_enabled(True)``.
"""

from __future__ import annotations

from jlens_vllm_telemetry.capture import (
    RouterTelemetryCollector,
    install_router_telemetry,
    uninstall_router_telemetry,
)


class JlensWorkerExtension:
    def _jlens_find_runners(self):
        from vllm.model_executor.layers.fused_moe.runner.moe_runner import MoERunner

        fc = self.model_runner.compilation_config.static_forward_context
        runners = [m for m in fc.values() if isinstance(m, MoERunner)]
        runners.sort(key=lambda m: m.layer_id)
        return runners

    def jlens_install_telemetry(self, cfg: dict) -> dict:
        if getattr(self, "_jlens_state", None) is not None:
            return {"error": "already installed"}
        runners = self._jlens_find_runners()
        collector = RouterTelemetryCollector(
            num_experts=cfg["num_experts"],
            top_k=cfg["top_k"],
            capacity_tokens=cfg.get("capacity_tokens", 2048),
            raw_sample_tokens=cfg.get("raw_sample_tokens", 64),
        )
        handles = install_router_telemetry(runners, collector)
        self._jlens_state = (collector, handles)
        return {
            "rank": getattr(self, "rank", -1),
            "num_moe_layers": len(runners),
            "layer_ids": [r.layer_id for r in runners],
        }

    def jlens_set_telemetry_enabled(self, enabled: bool) -> bool:
        collector, _ = self._jlens_state
        collector.enabled = bool(enabled)
        return collector.enabled

    def jlens_reset_telemetry(self) -> bool:
        collector, _ = self._jlens_state
        collector.reset()
        return True

    def jlens_fetch_telemetry(self) -> dict:
        collector, _ = self._jlens_state
        out = collector.fetch()
        out["rank"] = getattr(self, "rank", -1)
        return out

    def jlens_uninstall_telemetry(self) -> bool:
        state = getattr(self, "_jlens_state", None)
        if state is None:
            return False
        _, handles = state
        uninstall_router_telemetry(handles)
        self._jlens_state = None
        return True
