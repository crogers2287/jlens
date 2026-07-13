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
        # Allocate outside inference mode so reset()/fill_() stay legal.
        collector.allocate(self.model_runner.device)
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

    def jlens_fetch_telemetry(self, save_prefix: str | None = None) -> dict:
        """Return scalar counters over RPC; write arrays to a private npz.

        collective_rpc is a control plane: vLLM's msgpack layer ships large
        ndarrays as out-of-band buffer indices that untyped results cannot
        reconstruct. Arrays therefore go to disk (`{save_prefix}_rank{N}.npz`)
        and only plain scalars/lists travel back over the RPC.
        """
        import numpy as np

        collector, _ = self._jlens_state
        out = collector.fetch()
        out["rank"] = getattr(self, "rank", -1)
        arrays = {k: out.pop(k) for k in
                  ("ids", "weights", "entropy", "mass", "raw_logits_sample")
                  if k in out}
        if save_prefix is not None and arrays:
            path = f"{save_prefix}_rank{out['rank']}.npz"
            np.savez_compressed(path, **arrays)
            out["npz_path"] = path
        return out

    def jlens_fetch_summary(self, prompt_rows: int,
                            save_prefix: str | None = None,
                            expected_rows: int | None = None) -> dict:
        """Bounded router-feature summary (M36C summary telemetry path).

        Returns four float64 scalars computed device-side plus counters.
        When ``save_prefix`` is set (tiny validation samples only), also
        writes the full raw arrays npz exactly like jlens_fetch_telemetry
        so the equivalence gate can recompute features from raw capture.
        """
        collector, _ = self._jlens_state
        out = collector.summarize(prompt_rows, expected_rows=expected_rows)
        out["rank"] = getattr(self, "rank", -1)
        if collector._id_mismatch is not None:
            out["id_mismatch_total"] = int(collector._id_mismatch.sum())
            out["dispatch_missed_total"] = int(
                collector._dispatch_missed.sum())
        if save_prefix is not None:
            full = collector.fetch()
            if "ids" in full:
                import numpy as np

                arrays = {k: full[k] for k in
                          ("ids", "weights", "entropy", "mass",
                           "raw_logits_sample")}
                path = f"{save_prefix}_rank{out['rank']}.npz"
                np.savez_compressed(path, **arrays)
                out["npz_path"] = path
        return out

    def jlens_uninstall_telemetry(self) -> bool:
        state = getattr(self, "_jlens_state", None)
        if state is None:
            return False
        _, handles = state
        uninstall_router_telemetry(handles)
        self._jlens_state = None
        return True

    # -- M37J-C semantic bridge (observation-only; steer 8eb2e9e) --------

    def _jlens_find_decoder_stack(self):
        """The decoder layer ModuleList and the model's own final norm and
        LM head. Text stack only; never patched or replaced."""
        model = self.model_runner.model
        text = getattr(model, "language_model", model)
        inner = getattr(text, "model", text)
        layers = inner.layers
        norm = inner.norm
        lm_head = getattr(text, "lm_head", getattr(model, "lm_head", None))
        return layers, norm, lm_head

    def jlens_bridge_install(self, cfg: dict) -> dict:
        from jlens_vllm_telemetry.bridge import (
            SemanticBridgeCollector, install_bridge)

        if getattr(self, "_jlens_bridge", None) is not None:
            return {"error": "already installed"}
        layers, norm, lm_head = self._jlens_find_decoder_stack()
        collector = SemanticBridgeCollector(
            hidden_size=cfg["hidden_size"],
            n_slots=cfg.get("n_slots", 80))
        handles = install_bridge(layers, collector)
        collector.allocate(self.model_runner.device)
        self._jlens_bridge = (collector, handles, norm, lm_head)
        return {"rank": getattr(self, "rank", -1),
                "bridge_layers": list(collector.layers),
                "n_decoder_layers": len(layers)}

    def jlens_bridge_set_enabled(self, enabled: bool) -> bool:
        collector, _, _, _ = self._jlens_bridge
        collector.enabled = bool(enabled)
        return collector.enabled

    def jlens_bridge_reset(self) -> bool:
        collector, _, _, _ = self._jlens_bridge
        collector.reset()
        return True

    def jlens_bridge_fetch(self) -> dict:
        """Bounded top-k readout via the model's SUPPORTED projection
        path: final norm then ``compute_logits`` (LogitsProcessor, which
        applies the quantized head method and gathers TP vocabulary
        shards). Direct ParallelLMHead.forward is never called. Only the
        rank receiving full global-vocab logits returns token ids."""
        collector, _, norm, _ = self._jlens_bridge
        model = self.model_runner.model
        text_cfg = getattr(self.model_runner.model_config.hf_config,
                           "text_config",
                           self.model_runner.model_config.hf_config)
        vocab_size = int(text_cfg.vocab_size)

        def project(residuals):
            hidden = norm(residuals.to(norm.weight.dtype))
            return model.compute_logits(hidden)

        out = collector.readout(project, vocab_size)
        out["rank"] = getattr(self, "rank", -1)
        return out

    def jlens_bridge_uninstall(self) -> bool:
        from jlens_vllm_telemetry.bridge import uninstall_bridge

        state = getattr(self, "_jlens_bridge", None)
        if state is None:
            return False
        _, handles, _, _ = state
        uninstall_bridge(handles)
        self._jlens_bridge = None
        return True
