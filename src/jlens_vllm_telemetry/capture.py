"""Bounded, observation-only capture of MoE routing decisions.

The collector sits between router score production and the fused expert
dispatch call, exactly the boundary M36V Phase 1 authorizes. It never
modifies tensors: wrappers call the original method, record clones or
derived scalars, and return the original outputs untouched.

Per captured token row and routed layer it records:
  - exact top-k expert ids returned by ``select_experts`` (what dispatch
    consumes),
  - exact top-k dispatch weights,
  - full-softmax entropy over all experts (scalar, computed device-side),
  - pre-renormalization top-k probability mass (scalar),
  - the full router logits row for the first ``raw_sample_tokens`` rows
    (private validation sample only).

A second wrapper on ``forward_modular`` compares the (ids, weights) the
dispatch call actually receives against clones taken at router return,
accumulating mismatch counters for the dispatch/weight identity gates.

Buffers are preallocated to ``capacity_tokens`` rows; rows past capacity
are counted in ``dropped_rows`` and not stored (bounded-memory policy).
"""

from __future__ import annotations

import torch


class RouterTelemetryCollector:
    """Device-side accumulation; one instance per worker process."""

    def __init__(
        self,
        num_experts: int,
        top_k: int,
        capacity_tokens: int = 2048,
        raw_sample_tokens: int = 64,
    ) -> None:
        self.num_experts = int(num_experts)
        self.top_k = int(top_k)
        self.capacity_tokens = int(capacity_tokens)
        self.raw_sample_tokens = int(raw_sample_tokens)
        self.enabled = False

        self.layer_ids: list[int] = []       # model layer id per dense index
        self._dense_by_layer: dict[int, int] = {}

        # Allocated lazily on first capture (device comes from the input).
        self._ids = None          # [capacity, L, K] int32
        self._weights = None      # [capacity, L, K] float32
        self._entropy = None      # [capacity, L] float32
        self._mass = None         # [capacity, L] float32
        self._raw = None          # [raw_sample_tokens, L, E] float32
        self._cursor = None       # [L] int64 rows written per dense layer
        self._dropped = None      # [L] int64 rows dropped per dense layer

        # Dispatch-identity accumulators.
        self._snapshots: dict[int, tuple[torch.Tensor, torch.Tensor]] = {}
        self._id_mismatch = None      # [L] int64
        self._w_maxdiff = None        # [L] float32
        self._dispatch_calls = None   # [L] int64
        self._dispatch_missed = None  # [L] int64 (dispatch seen w/o snapshot)

        # Weight sanity accumulators (over all captured rows).
        self._w_nonfinite = None   # [L] int64
        self._w_min = None         # [L] float32 (most negative weight seen)
        self._w_normdev = None     # [L] float32 (max |sum(w) - 1|)

    # -- layer registration -------------------------------------------------

    def register_layer(self, layer_id: int) -> int:
        if layer_id in self._dense_by_layer:
            return self._dense_by_layer[layer_id]
        dense = len(self.layer_ids)
        self.layer_ids.append(int(layer_id))
        self._dense_by_layer[layer_id] = dense
        return dense

    @property
    def num_layers(self) -> int:
        return len(self.layer_ids)

    def allocate(self, device) -> None:
        """Eagerly allocate buffers OUTSIDE torch.inference_mode.

        Capture hooks run inside vLLM's inference-mode forward pass; tensors
        created there become inference tensors, and later out-of-band
        ``reset()`` calls (``zero_()``/``fill_()``) would raise
        "Inplace update to inference tensor outside InferenceMode".
        Allocating at install time keeps every buffer a normal tensor,
        which may be freely written inside inference mode.
        """
        self._ensure_buffers(torch.device(device))

    def _ensure_buffers(self, device: torch.device) -> None:
        if self._ids is not None:
            return
        L, K, E = self.num_layers, self.top_k, self.num_experts
        cap, raw_n = self.capacity_tokens, self.raw_sample_tokens
        self._ids = torch.zeros((cap, L, K), dtype=torch.int32, device=device)
        self._weights = torch.zeros((cap, L, K), dtype=torch.float32, device=device)
        self._entropy = torch.zeros((cap, L), dtype=torch.float32, device=device)
        self._mass = torch.zeros((cap, L), dtype=torch.float32, device=device)
        self._raw = torch.zeros((raw_n, L, E), dtype=torch.float32, device=device)
        self._cursor = torch.zeros(L, dtype=torch.int64, device="cpu")
        self._dropped = torch.zeros(L, dtype=torch.int64, device="cpu")
        self._id_mismatch = torch.zeros(L, dtype=torch.int64, device=device)
        self._w_maxdiff = torch.zeros(L, dtype=torch.float32, device=device)
        self._dispatch_calls = torch.zeros(L, dtype=torch.int64, device="cpu")
        self._dispatch_missed = torch.zeros(L, dtype=torch.int64, device="cpu")
        self._w_nonfinite = torch.zeros(L, dtype=torch.int64, device=device)
        self._w_min = torch.full((L,), float("inf"), dtype=torch.float32, device=device)
        self._w_normdev = torch.zeros(L, dtype=torch.float32, device=device)

    # -- capture hooks (called from inside the forward pass) ----------------

    def on_router(
        self,
        dense: int,
        router_logits: torch.Tensor,
        topk_weights: torch.Tensor,
        topk_ids: torch.Tensor,
    ) -> None:
        if not self.enabled:
            return
        self._ensure_buffers(topk_ids.device)

        # Snapshot for the dispatch-identity comparison regardless of
        # capacity, so the identity gates cover every call.
        self._snapshots[dense] = (
            topk_ids.detach().to(torch.int64).clone(),
            topk_weights.detach().to(torch.float32).clone(),
        )

        n = int(topk_ids.shape[0])
        start = int(self._cursor[dense].item())
        room = max(0, self.capacity_tokens - start)
        take = min(n, room)
        if take < n:
            self._dropped[dense] += n - take
        self._cursor[dense] = start + take

        w32 = topk_weights.detach().to(torch.float32)
        # Weight sanity runs over the full call, not just stored rows.
        # All accumulation stays on device; no host sync in the hot path.
        finite = torch.isfinite(w32)
        self._w_nonfinite[dense] += (~finite).sum()
        wf = torch.where(finite, w32, torch.zeros_like(w32))
        self._w_min[dense] = torch.minimum(self._w_min[dense], wf.min())
        self._w_normdev[dense] = torch.maximum(
            self._w_normdev[dense], (wf.sum(dim=-1) - 1.0).abs().max()
        )

        if take == 0:
            return
        rows = slice(start, start + take)
        self._ids[rows, dense, :] = topk_ids.detach()[:take].to(torch.int32)
        self._weights[rows, dense, :] = w32[:take]

        logits32 = router_logits.detach().to(torch.float32)
        probs = torch.softmax(logits32, dim=-1)
        ent = -(probs * probs.clamp_min(1e-12).log()).sum(dim=-1)
        self._entropy[rows, dense] = ent[:take]
        topk_probs = torch.topk(probs, k=self.top_k, dim=-1).values
        self._mass[rows, dense] = topk_probs.sum(dim=-1)[:take]

        raw_take = min(take, max(0, self.raw_sample_tokens - start))
        if raw_take > 0:
            self._raw[start : start + raw_take, dense, :] = logits32[:raw_take]

    def on_dispatch(
        self,
        dense: int,
        topk_weights: torch.Tensor,
        topk_ids: torch.Tensor,
    ) -> None:
        if not self.enabled:
            return
        self._ensure_buffers(topk_ids.device)
        self._dispatch_calls[dense] += 1
        snap = self._snapshots.pop(dense, None)
        if snap is None:
            self._dispatch_missed[dense] += 1
            return
        snap_ids, snap_w = snap
        recv_ids = topk_ids.detach().to(torch.int64)
        recv_w = topk_weights.detach().to(torch.float32)
        if snap_ids.shape != recv_ids.shape:
            self._id_mismatch[dense] += recv_ids.numel()
            return
        self._id_mismatch[dense] += (snap_ids != recv_ids).sum()
        self._w_maxdiff[dense] = torch.maximum(
            self._w_maxdiff[dense], (snap_w - recv_w).abs().max()
        )

    # -- control ------------------------------------------------------------

    def reset(self) -> None:
        """Zero counters and cursors; buffers are reused in place."""
        self._snapshots.clear()
        if self._ids is None:
            return
        self._cursor.zero_()
        self._dropped.zero_()
        self._id_mismatch.zero_()
        self._w_maxdiff.zero_()
        self._dispatch_calls.zero_()
        self._dispatch_missed.zero_()
        self._w_nonfinite.zero_()
        self._w_min.fill_(float("inf"))
        self._w_normdev.zero_()

    def summarize(self, prompt_rows: int,
                  expected_rows: int | None = None) -> dict:
        """Device-side router feature summary (M36C summary telemetry path).

        Mirrors the numpy router-feature semantics of
        ``m36_calibration.router_features`` exactly, in float64, and
        returns four bounded scalars — no per-token arrays leave the
        worker. Gate: per-feature |summary - raw recompute| <= 1e-5.

        ``expected_rows`` (prompt tokens + output tokens - 1) bounds the
        read: vLLM's async scheduler can still have the final sampled
        token's forward pass in flight when this RPC runs, appending rows
        concurrently. Rows below ``expected_rows`` were written by
        completed forward passes and are stable; everything beyond is
        ignored so the summary and any later raw recompute see the same
        slice.
        """
        if self._ids is None:
            return {"rows": 0}
        if self._ids.is_cuda:
            torch.cuda.synchronize(self._ids.device)
        cursors = self._cursor.tolist()
        rows = min(cursors) if cursors else 0
        if expected_rows is not None:
            rows = min(rows, int(expected_rows))
        prompt_rows = min(prompt_rows, rows)
        device = self._ids.device
        L, E = self.num_layers, self.num_experts

        def usage_sig(ids, weights):
            offsets = (torch.arange(L, device=device, dtype=torch.int64)
                       .view(1, L, 1) * E)
            flat = (ids.to(torch.int64) + offsets).reshape(-1)
            out = torch.zeros(L * E, dtype=torch.float64, device=device)
            out.index_add_(0, flat, weights.reshape(-1).to(torch.float64))
            out = out.view(L, E)
            sums = out.sum(dim=1, keepdim=True)
            out = torch.where(sums > 0, out / sums, out)
            return out.reshape(-1)

        def cos_drift(sig, ref):
            na, nb = sig.norm(), ref.norm()
            if float(na) == 0.0 or float(nb) == 0.0:
                return 0.0
            return float(1.0 - (sig @ ref) / (na * nb))

        prefill_sig = usage_sig(self._ids[:prompt_rows],
                                self._weights[:prompt_rows])
        drift = []
        step = max(1, (rows - prompt_rows) // 8)
        for start in range(prompt_rows, rows, step):
            window_sig = usage_sig(self._ids[start:start + step],
                                   self._weights[start:start + step])
            drift.append(cos_drift(window_sig, prefill_sig))

        decode_entropy = self._entropy[prompt_rows:rows].to(torch.float64)
        decode_mass = self._mass[prompt_rows:rows].to(torch.float64)
        return {
            "rows": rows,
            "prompt_rows": prompt_rows,
            "router_entropy_mean": (float(decode_entropy.mean())
                                    if decode_entropy.numel() else 0.0),
            "expert_concentration_mean": (float(decode_mass.mean())
                                          if decode_mass.numel() else 0.0),
            "windowed_expert_shift": (sum(drift) / len(drift)
                                      if drift else 0.0),
            "drift_final_window": drift[-1] if drift else 0.0,
        }

    def fetch(self) -> dict:
        """Move captured data to CPU numpy. Private-side use only."""
        if self._ids is None:
            return {
                "rows": 0,
                "layer_ids": list(self.layer_ids),
                "num_experts": self.num_experts,
                "top_k": self.top_k,
            }
        cursors = self._cursor.tolist()
        rows = min(cursors) if cursors else 0
        raw_rows = min(rows, self.raw_sample_tokens)
        return {
            "rows": rows,
            "rows_per_layer": cursors,
            "dropped_rows": self._dropped.tolist(),
            "layer_ids": list(self.layer_ids),
            "num_experts": self.num_experts,
            "top_k": self.top_k,
            "ids": self._ids[:rows].cpu().numpy(),
            "weights": self._weights[:rows].cpu().numpy(),
            "entropy": self._entropy[:rows].cpu().numpy(),
            "mass": self._mass[:rows].cpu().numpy(),
            "raw_logits_sample": self._raw[:raw_rows].cpu().numpy(),
            "dispatch_calls": self._dispatch_calls.tolist(),
            "dispatch_missed": self._dispatch_missed.tolist(),
            "id_mismatch": self._id_mismatch.cpu().tolist(),
            "weight_maxdiff": self._w_maxdiff.cpu().tolist(),
            "weight_nonfinite": self._w_nonfinite.cpu().tolist(),
            "weight_min": self._w_min.cpu().tolist(),
            "weight_normdev": self._w_normdev.cpu().tolist(),
        }


def install_router_telemetry(runners, collector: RouterTelemetryCollector):
    """Wrap select_experts / forward_modular on each MoE runner.

    ``runners`` is any iterable of objects exposing ``layer_id``,
    ``router.select_experts`` and ``routed_experts.forward_modular``
    (real vLLM ``MoERunner`` modules or test fakes). Returns opaque
    handles for :func:`uninstall_router_telemetry`.
    """
    handles = []
    for runner in runners:
        dense = collector.register_layer(runner.layer_id)
        router = runner.router
        routed = runner.routed_experts
        orig_select = router.select_experts
        orig_forward = routed.forward_modular

        def make_select(orig, dense):
            def wrapped_select_experts(*args, **kwargs):
                topk_weights, topk_ids = orig(*args, **kwargs)
                router_logits = kwargs.get(
                    "router_logits", args[1] if len(args) > 1 else None
                )
                collector.on_router(dense, router_logits, topk_weights, topk_ids)
                return topk_weights, topk_ids

            return wrapped_select_experts

        def make_forward(orig, dense):
            def wrapped_forward_modular(*args, **kwargs):
                topk_weights = kwargs.get(
                    "topk_weights", args[1] if len(args) > 1 else None
                )
                topk_ids = kwargs.get("topk_ids", args[2] if len(args) > 2 else None)
                collector.on_dispatch(dense, topk_weights, topk_ids)
                return orig(*args, **kwargs)

            return wrapped_forward_modular

        router.select_experts = make_select(orig_select, dense)
        routed.forward_modular = make_forward(orig_forward, dense)
        handles.append((router, routed))
    return handles


def uninstall_router_telemetry(handles) -> None:
    """Delete the instance-level wrappers, restoring the class methods."""
    for router, routed in handles:
        if "select_experts" in router.__dict__:
            del router.__dict__["select_experts"]
        if "forward_modular" in routed.__dict__:
            del routed.__dict__["forward_modular"]
