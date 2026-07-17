"""Q35Q Phase-0 load-manifest / loader-transformation admission (CPU-only, pure).

Remaining Q35Q order item 3: module-SET equality does not establish strict
loadability. This module checks the one gate that decides whether the admitted
GPTQ artifact can be strictly loaded into the admitted text-only source class:
the routed-expert REPRESENTATION and the existence of a pinned loader transformation
between the artifact and source representations.

Observed facts (transformers 5.13.1 source inspection + pinned weight index):

- the source class `Qwen3_5MoeExperts` represents routed experts as a single PACKED
  3D `nn.Parameter` per layer (`gate_up_proj[num_experts, 2*intermediate, hidden]`,
  `down_proj[num_experts, hidden, intermediate]`), indexed by `gate_up_proj[e]`;
  these are plain parameters, not `nn.Linear` modules;
- the GPTQ artifact stores NUMBERED, per-expert 2D linears
  (`mlp.experts.{e}.{gate_proj,up_proj,down_proj}` with GPTQ tensors
  qweight/qzeros/scales/g_idx), i.e. a per-expert-`nn.Linear` representation;
- GPTQ quantizes `nn.Linear` modules; it has no mechanism to quantize a packed 3D
  parameter, so the artifact was quantized against an older per-expert structure;
- the source carries no `_checkpoint_conversion_mapping`, load-state-dict pre-hook,
  or `_load_from_state_dict` that maps numbered per-expert GPTQ tensors into the
  packed parameters.

Therefore no deterministic pinned loader transformation exists, and per the steer a
conversion may NOT be improvised after inspecting weight values. The verdict is
`q35q_load_manifest_blocked`.

Pure over enumerated names + a source-inspection boolean so it is unit-testable.
"""
from __future__ import annotations

import re

from q35q_stage import Q35QStageBlock

_NUMBERED_RE = re.compile(r"\bmlp\.experts\.\d+\.")
_PACKED_RE = re.compile(r"\bmlp\.experts\.(gate_up_proj|down_proj)\b")


def classify_expert_representation(names) -> str:
    """'numbered' (per-expert linears), 'packed' (fused stacked params), or
    'unknown'. Fails closed if both appear (ambiguous)."""
    numbered = any(_NUMBERED_RE.search(n) for n in names)
    packed = any(_PACKED_RE.search(n) for n in names)
    if numbered and packed:
        raise Q35QStageBlock("ambiguous expert representation (both numbered and packed present)")
    if numbered:
        return "numbered"
    if packed:
        return "packed"
    return "unknown"


def load_manifest_verdict(*, source_repr: str, artifact_repr: str,
                          conversion_hook_present: bool) -> dict:
    """Decide strict loadability of the artifact into the source class. Differing
    representations without a pinned conversion transformation is a hard block."""
    if source_repr == "unknown" or artifact_repr == "unknown":
        raise Q35QStageBlock("could not classify source or artifact expert representation")
    same = source_repr == artifact_repr
    loadable = same or conversion_hook_present
    return {
        "source_expert_representation": source_repr,
        "artifact_expert_representation": artifact_repr,
        "representations_match": same,
        "pinned_conversion_hook_present": bool(conversion_hook_present),
        "strictly_loadable": loadable,
        "outcome": ("q35q_phase0_load_manifest_candidate_ok" if loadable
                    else "q35q_load_manifest_blocked"),
        "blocker": None if loadable else (
            "the GPTQ artifact stores numbered per-expert linears but the source class "
            "packs routed experts into stacked 3D parameters, and no pinned loader "
            "transformation (checkpoint conversion mapping / load-state-dict hook) maps "
            "between them; a conversion may not be improvised"),
    }
