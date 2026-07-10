#!/usr/bin/env python3
"""Opt-in qwen2_moe route override via router-logit editing (M32P Phase 0).

transformers 5.13.0 computes qwen2_moe expert selection inside
``Qwen2MoeTopKRouter``: ``forward -> (router_logits, router_scores,
router_indices)``. The controller registers a prepended forward hook on one
layer's router for the duration of exactly one intervention. The hook edits
only the LAST position's router logits, recomputes that single row's
scores/indices with the router's own arithmetic (softmax -> top-k -> native
``norm_topk_prob`` -> dtype cast), and splices it into otherwise-untouched
outputs. Expert dispatch and the shared expert run the model's own code
unchanged; a disabled controller is bit-for-bit the original path.

Swap semantics (equal compute): the incoming expert receives the outgoing
expert's original router logit and the outgoing expert's logit is masked far
below the minimum. Exactly ``top_k`` experts stay active, duplicates are
impossible, and routing weights follow the model's own normalization of the
edited logits.

Soft-penalty semantics: subtract positive deltas from the logits of penalized
experts at the hooked layer; selection and weights again follow the model's
own arithmetic.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SwapPlan:
    layer_index: int
    swap_out: int
    swap_in: int


@dataclass(frozen=True)
class PenaltyPlan:
    layer_index: int
    penalties: tuple  # ((expert_id, positive_delta), ...)


@dataclass
class RouteController:
    """Attach to a qwen2_moe-style model; apply at most one plan at a time."""

    model: object
    num_experts: int
    top_k: int
    applications: int = 0
    _handle: object = field(default=None, repr=False)

    def _router(self, layer_index):
        layers = self.model.model.layers
        if not 0 <= layer_index < len(layers):
            raise ValueError(f"layer index out of range: {layer_index}")
        mlp = layers[layer_index].mlp
        gate = getattr(mlp, "gate", None)
        if gate is None or not hasattr(gate, "top_k") \
                or not hasattr(mlp, "experts"):
            raise ValueError(f"layer {layer_index} has no sparse MoE router")
        if int(gate.top_k) != int(self.top_k) \
                or int(gate.num_experts) != int(self.num_experts):
            raise ValueError("router top_k/num_experts mismatch")
        return gate

    def _validate_swap(self, plan, row):
        import torch
        for expert in (plan.swap_out, plan.swap_in):
            if not 0 <= expert < self.num_experts:
                raise ValueError(f"expert id out of range: {expert}")
        if plan.swap_out == plan.swap_in:
            raise ValueError("swap_out and swap_in must differ")
        selected = set(torch.topk(row, self.top_k).indices.tolist())
        if plan.swap_out not in selected:
            raise ValueError("swap_out expert is not currently selected")
        if plan.swap_in in selected:
            raise ValueError("swap_in expert is already selected")

    def _edit_row(self, plan, row):
        import torch
        row = row.clone()
        if isinstance(plan, SwapPlan):
            self._validate_swap(plan, row)
            row[plan.swap_in] = row[plan.swap_out]
            row[plan.swap_out] = torch.finfo(row.dtype).min / 2
        elif isinstance(plan, PenaltyPlan):
            for expert, delta in plan.penalties:
                if not 0 <= int(expert) < self.num_experts:
                    raise ValueError(f"penalty expert out of range: {expert}")
                if not math.isfinite(delta) or delta <= 0:
                    raise ValueError(
                        f"penalty delta must be finite positive: {delta}")
                row[int(expert)] = row[int(expert)] - delta
        else:
            raise ValueError(f"unknown plan type: {type(plan).__name__}")
        if bool(row.isnan().any()):
            raise ValueError("edited router logits are not finite")
        return row

    def _rebuild_last_row(self, router, logits, scores, indices, plan):
        """Edit the last position and recompute its selection like the router."""
        import torch
        edited_logits = logits.clone()
        edited_logits[-1] = self._edit_row(plan, logits[-1])
        probs = torch.nn.functional.softmax(
            edited_logits[-1], dtype=torch.float, dim=-1)
        top_value, top_index = torch.topk(probs, router.top_k, dim=-1)
        if router.norm_topk_prob:
            top_value = top_value / top_value.sum(dim=-1, keepdim=True)
        top_value = top_value.to(edited_logits.dtype)
        new_scores = scores.clone()
        new_indices = indices.clone()
        new_scores[-1] = top_value
        new_indices[-1] = top_index
        return edited_logits, new_scores, new_indices

    def active(self, plan):
        """Context manager: hook exactly one layer for one intervention."""
        controller = self

        class _Active:
            def __enter__(self_inner):
                if controller._handle is not None:
                    raise RuntimeError("route override already active")
                router = controller._router(plan.layer_index)

                def hook(module, _inputs, output):
                    logits, scores, indices = output
                    rebuilt = controller._rebuild_last_row(
                        module, logits, scores, indices, plan)
                    controller.applications += 1
                    return rebuilt

                controller._handle = router.register_forward_hook(
                    hook, prepend=True)
                return controller

            def __exit__(self_inner, *exc):
                if controller._handle is not None:
                    controller._handle.remove()
                    controller._handle = None
                return False

        return _Active()

    @property
    def enabled(self):
        return self._handle is not None


def clone_cache(past):
    """Deep-copy a transformers KV cache so branches cannot share state."""
    import copy
    return copy.deepcopy(past)
