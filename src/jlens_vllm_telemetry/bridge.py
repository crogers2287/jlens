# M37J-C Phase 0B: observation-only semantic bridge (steer 8eb2e9e).
"""Bounded residual-checkpoint capture for the Agents-A1 AWQ runtime.

INERT BY DEFAULT: importing this module, or even installing the
collector, changes nothing until ``enabled`` is set; hooks only read
(``register_forward_hook`` on decoder layers) and never modify
activations, weights, routes, or outputs. The bridge projects captured
residuals through the model's OWN final normalization and unembedding
(standard logit-lens readout — the required baseline method). It must
not fit or apply the pilot Jacobian lens to Agents-A1.

Frozen configuration (before any live prompt):
  - five evenly spaced decoder layers of the 40-layer text stack;
  - every-32-decode-token cadence plus the final captured position;
  - top-k 10 readout;
  - the same five predeclared semantic groups used by M37J-A.

Memory is bounded: ``n_slots`` checkpoint slots per layer, fp16,
allocated once at install (outside inference mode, mirroring the M36V
capture constraint). Rows past capacity are dropped and counted.
"""
from __future__ import annotations

import torch

BRIDGE_LAYERS = (4, 12, 20, 28, 36)     # of the 40-layer text stack
CADENCE = 32
TOP_K = 10

SEMANTIC_GROUPS = {
    "completion": ["final", "answer", "done", "complete", "conclude"],
    "continuation": ["continue", "next", "more", "step", "then"],
    "verification": ["check", "verify", "recheck", "confirm", "calculate"],
    "error_conflict": ["error", "wrong", "mistake", "conflict", "but"],
    "uncertainty": ["uncertain", "maybe", "perhaps", "unsure", "doubt"],
}


class SemanticBridgeCollector:
    """Bounded, observation-only residual checkpoints at fixed cadence."""

    def __init__(self, hidden_size: int, n_slots: int = 80,
                 layers: tuple[int, ...] = BRIDGE_LAYERS,
                 cadence: int = CADENCE):
        self.hidden_size = int(hidden_size)
        self.n_slots = int(n_slots)
        self.layers = tuple(int(l) for l in layers)
        self.cadence = int(cadence)
        self.enabled = False
        self._buf: torch.Tensor | None = None      # [L, slots, H] fp16
        self._slot_step: torch.Tensor | None = None  # [L, slots] int64
        self._cursor: torch.Tensor | None = None   # [L] int64 (cpu)
        self._decode_step: torch.Tensor | None = None  # [L] int64 (cpu)
        self._dropped: torch.Tensor | None = None  # [L] int64 (cpu)
        self._last: torch.Tensor | None = None     # [L, H] latest residual

    def allocate(self, device) -> None:
        """Eager allocation OUTSIDE inference mode (see M36V constraint)."""
        if self._buf is not None:
            return
        L, S, H = len(self.layers), self.n_slots, self.hidden_size
        dev = torch.device(device)
        self._buf = torch.zeros((L, S, H), dtype=torch.float16, device=dev)
        self._slot_step = torch.full((L, S), -1, dtype=torch.int64,
                                     device="cpu")
        self._cursor = torch.zeros(L, dtype=torch.int64, device="cpu")
        self._decode_step = torch.zeros(L, dtype=torch.int64, device="cpu")
        self._dropped = torch.zeros(L, dtype=torch.int64, device="cpu")
        self._last = torch.zeros((L, H), dtype=torch.float16, device=dev)

    def reset(self) -> None:
        if self._buf is None:
            return
        self._cursor.zero_()
        self._decode_step.zero_()
        self._dropped.zero_()
        self._slot_step.fill_(-1)

    def on_layer(self, dense: int, hidden: torch.Tensor) -> None:
        """Observation hook: ``hidden`` is the layer output residual
        [n_tokens, H] (or [1, n, H]). Decode steps are single-token
        rows; prefill rows advance no cadence."""
        if not self.enabled or self._buf is None:
            return
        h = hidden.detach()
        if h.ndim == 3:
            h = h[0]
        if h.shape[0] != 1:
            return                       # prefill chunk — not a decode step
        self._last[dense] = h[0].to(torch.float16)
        step = int(self._decode_step[dense])
        self._decode_step[dense] = step + 1
        if step % self.cadence != self.cadence - 1:
            return                       # off-cadence decode step
        cur = int(self._cursor[dense])
        if cur >= self.n_slots:
            self._dropped[dense] += 1
            return
        self._buf[dense, cur] = h[0].to(torch.float16)
        self._slot_step[dense, cur] = step
        self._cursor[dense] = cur + 1

    # -- readout ------------------------------------------------------------
    #
    # Tensor-parallel contract (steer fe6fcf2): projection must go
    # through the live model's supported compute_logits/LogitsProcessor
    # path — NEVER direct ParallelLMHead.forward, which vLLM makes raise
    # and which would yield shard-local, non-global token ids. Every
    # rank executes identical projection calls in identical order (the
    # capture state is token-synchronous across TP ranks), so the gather
    # collective cannot deadlock; only the rank that receives the full
    # global-vocabulary logits emits token ids — other ranks return
    # bounded status/counters only.

    #: Frozen slot-chunk size for projection (resource control, not a
    #: task-derived tuning variable). Bounds the transient
    #: [chunk, vocab] logits tensor.
    PROJECTION_CHUNK_SLOTS = 8

    @torch.no_grad()
    def readout(self, project_fn, vocab_size: int) -> dict:
        """Bounded top-k readout via ``project_fn`` (the worker's
        norm + compute_logits path). ``project_fn(residuals)`` returns
        global-vocabulary logits on the authoritative rank and ``None``
        elsewhere; padding columns beyond ``vocab_size`` are trimmed
        before top-k. Small int lists and scalars only."""
        if self._buf is None:
            return {"slots": 0}
        out: dict = {"layers": list(self.layers), "cadence": self.cadence,
                     "top_k": TOP_K, "dropped": self._dropped.tolist(),
                     "projection_calls": 0, "authoritative": True,
                     "readout": {}}
        chunk = self.PROJECTION_CHUNK_SLOTS
        for li, layer in enumerate(self.layers):
            n = int(self._cursor[li])
            slots = [self._buf[li, :n]]
            steps = self._slot_step[li, :n].tolist()
            if int(self._decode_step[li]) > 0:
                slots.append(self._last[li:li + 1])
                steps = steps + [int(self._decode_step[li]) - 1]
            residuals = torch.cat(slots, dim=0)
            ids, finite = [], True
            # Fixed chunk walk: identical call count on every rank for
            # the same capture state, bounded [chunk, vocab] transient.
            for start in range(0, residuals.shape[0], chunk):
                piece = residuals[start:start + chunk]
                logits = project_fn(piece)
                out["projection_calls"] += 1
                if logits is None:
                    out["authoritative"] = False
                    continue
                if hasattr(logits, "logits"):
                    logits = logits.logits
                logits = logits.float()[..., :vocab_size]  # trim padding
                finite &= bool(torch.isfinite(logits).all().item())
                top = torch.topk(logits, TOP_K, dim=-1).indices
                if int(top.max()) >= vocab_size or int(top.min()) < 0:
                    raise RuntimeError(
                        "top-k id outside global vocabulary — shard-local "
                        "leak or offset error")
                ids.extend(top.tolist())
            if out["authoritative"]:
                out["readout"][str(layer)] = {
                    "steps": steps, "token_ids": ids, "finite": finite}
        if not out["authoritative"]:
            out["readout"] = {}
        return out


def semantic_group_scores(readout: dict, decode_fn) -> dict:
    """Fixed-group scores from a readout dict; ``decode_fn`` maps a token
    id to text. Aggregate counts only."""
    scores = {f"group_{g}": 0.0 for g in SEMANTIC_GROUPS}
    for layer_data in readout.get("readout", {}).values():
        for ids in layer_data["token_ids"]:
            tokens = [decode_fn(t).strip().lower() for t in ids]
            for group, words in SEMANTIC_GROUPS.items():
                if any(any(w in tok for tok in tokens) for w in words):
                    scores[f"group_{group}"] += 1.0
    return scores


def install_bridge(decoder_layers, collector: SemanticBridgeCollector):
    """Attach observation-only forward hooks to the selected decoder
    layers. Returns removable handles. Layers outside the selection are
    untouched; nothing is patched or replaced."""
    handles = []
    for dense, layer_idx in enumerate(collector.layers):
        module = decoder_layers[layer_idx]

        def make_hook(d):
            def hook(mod, inputs, output):
                h = output[0] if isinstance(output, tuple) else output
                if torch.is_tensor(h):
                    collector.on_layer(d, h)
            return hook

        handles.append(module.register_forward_hook(make_hook(dense)))
    return handles


def uninstall_bridge(handles) -> None:
    for h in handles:
        h.remove()
