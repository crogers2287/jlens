"""Q35Q Phase-0 source<->artifact module reconciliation (CPU-only, pure).

Remaining Q35Q order items 1-2 per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_RANGE_PROVENANCE_AND_REPRODUCIBLE_LIVE_ADAPTER_CORRECTION.md:
freeze and verify the packed-source <-> numbered-GPTQ expert representation map,
then prove exact source-derived vs artifact-derived module-set equality.

The two representations differ in three frozen, independently-observed ways:

1. Prefix: the multimodal artifact nests the text model under
   `model.language_model.*`; the admitted text-only class exposes it as `model.*`.
2. Omission: the artifact carries `model.visual.*` (vision) and `mtp.*` (MTP)
   modules that are omitted from the admitted text-only load manifest.
3. Experts: the source fuses+packs routed experts as one `mlp.experts.gate_up_proj`
   and one `mlp.experts.down_proj` per layer; the GPTQ artifact stores NUMBERED,
   SPLIT experts `mlp.experts.{e}.{gate_proj,up_proj,down_proj}` for e in
   [0, num_experts). The frozen map fuses per-expert `gate_proj`+`up_proj` ->
   `gate_up_proj` and `down_proj` -> `down_proj`, collapsing all experts to the
   packed source form; every layer must carry exactly `num_experts` experts, each
   with the full {gate_proj, up_proj, down_proj} set.

Pure over already-enumerated canonical module names. Fails closed on any module
outside the frozen text-only / vision / MTP partition, a wrong expert id range, or
missing per-expert sub-modules. Returns counts + booleans (no module names) so the
committed record stays aggregate-only.
"""
from __future__ import annotations

import re

from q35q_stage import Q35QStageBlock

_LM_PREFIX = "model.language_model."
_VISION_PREFIXES = ("model.visual.",)
_MTP_PREFIXES = ("mtp.",)
_EXPERT_RE = re.compile(r"^(model\.layers\.\d+\.mlp\.experts)\.(\d+)\.(gate_proj|up_proj|down_proj)$")
_FUSE = {"gate_proj": "gate_up_proj", "up_proj": "gate_up_proj", "down_proj": "down_proj"}


def _canonical_expert_id(eid_str: str) -> int:
    """Require a canonical decimal expert id: digits only, no leading zeros (so
    `0` and `00` cannot collapse to the same integer via int())."""
    if not eid_str.isdigit() or (len(eid_str) > 1 and eid_str[0] == "0"):
        raise Q35QStageBlock(f"non-canonical expert id: {eid_str!r}")
    return int(eid_str)


def rewrite_artifact_to_textonly(artifact_modules, num_experts: int) -> dict:
    """Apply the frozen map to the artifact's canonical module set, returning the
    derived text-only module set plus omission counts. Fails closed on anything
    outside the frozen partition or a malformed expert layout."""
    if type(num_experts) is not int or num_experts <= 0:  # bool is an int subclass
        raise Q35QStageBlock("num_experts must be a positive non-boolean integer")
    textonly, vision, mtp = set(), 0, 0
    experts_seen = {}
    for m in artifact_modules:
        if any(m.startswith(p) for p in _VISION_PREFIXES):
            vision += 1
            continue
        if any(m.startswith(p) for p in _MTP_PREFIXES):
            mtp += 1
            continue
        if m == "lm_head":
            textonly.add("lm_head")
            continue
        if not m.startswith(_LM_PREFIX):
            raise Q35QStageBlock(f"module outside frozen text-only/vision/MTP partition: {m!r}")
        rest = "model." + m[len(_LM_PREFIX):]
        em = _EXPERT_RE.match(rest)
        if em:
            base, eid, sub = em.group(1), _canonical_expert_id(em.group(2)), em.group(3)
            if eid >= num_experts:
                raise Q35QStageBlock(f"expert id {eid} >= num_experts {num_experts}")
            slot = experts_seen.setdefault(base, {}).setdefault(eid, set())
            if sub in slot:
                raise Q35QStageBlock(f"duplicate expert sub-module {sub} at {base}.{eid}")
            slot.add(sub)
            textonly.add(f"{base}.{_FUSE[sub]}")
        else:
            textonly.add(rest)
    for base, experts in experts_seen.items():
        if set(experts) != set(range(num_experts)):
            raise Q35QStageBlock(f"expert ids are not exactly 0..{num_experts - 1} for a layer")
        for subs in experts.values():
            if subs != {"gate_proj", "up_proj", "down_proj"}:
                raise Q35QStageBlock("an expert is missing one of gate_proj/up_proj/down_proj")
    return {"textonly": textonly, "vision_omitted": vision, "mtp_omitted": mtp,
            "expert_layers": len(experts_seen)}


def reconcile_source_vs_artifact(source_modules, artifact_modules, num_experts: int) -> dict:
    """Require exact equality between the source-derived text-only module set and
    the artifact's module set rewritten under the frozen representation map."""
    rw = rewrite_artifact_to_textonly(artifact_modules, num_experts)
    src, art = set(source_modules), rw["textonly"]
    if not src:
        raise Q35QStageBlock("empty source module set")
    missing = src - art   # source module with no artifact evidence
    extra = art - src     # artifact text-only module not in the source class
    return {
        "equal": not missing and not extra,
        "source_count": len(src),
        "artifact_textonly_count": len(art),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "vision_omitted": rw["vision_omitted"],
        "mtp_omitted": rw["mtp_omitted"],
        "expert_layers": rw["expert_layers"],
    }
