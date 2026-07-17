"""Q35Q Phase-0 source<->artifact reconciliation composition (CPU-only, injected).

Remaining Q35Q order item 2 / defect 6 of
docs/STEER_ADDENDUM_2026-07-17_HEADER_REDIRECT_AND_MODULE_RECONCILIATION_CORRECTION.md:
the source<->artifact module reconciliation existed only as a pure function + tests,
with no committed composition reproducing the live construction. This module is that
committed composition, used identically by tests and the live CLI:

  strict weight-index admission  -> validated weight_map -> canonical artifact modules
  source class module manifest   -> source-derived text-only allow-list
  frozen representation map       -> exact source == artifact equality

The two manifests come from independent providers (the admitted text-only class vs
the pinned weight index); neither side is copied into the other. This proves module-
SET correspondence only — NOT load-manifest tensor equality (that is order item 3:
exact tensors, quantization auxiliaries, dtype/shape, multiplicity, ordering,
fusion, and the numbered->packed loader transformation), and it does not admit the
source set until source/package identity is independently pinned (order item 4).
"""
from __future__ import annotations

from q35q_config_admission import admit_config
from q35q_index_admission import admit_weight_index
from q35q_module_reconcile import reconcile_source_vs_artifact
from q35q_source_admission import canonical_module_path
from q35q_source_allowlist import canonical_source_modules, extract_templates
from q35q_stage import Q35QStageBlock


def run_reconciliation(*, config_bytes, config_expected_git_sha1, source_param_names,
                       index_bytes, index_expected_sha256) -> dict:
    """Compose config admission + strict index admission + full-source module set +
    the frozen representation-map equality. `source_param_names` are the DIRECT full
    enumeration of the admitted text-only class (no reduced extrapolation); the
    admitted config supplies the authoritative expert/layer counts."""
    admitted_cfg = admit_config(config_bytes, config_expected_git_sha1)
    num_experts = admitted_cfg["num_experts"]
    num_layers = admitted_cfg["num_hidden_layers"]

    admitted = admit_weight_index(index_bytes, index_expected_sha256)
    artifact_modules = {canonical_module_path(name) for name in admitted["weight_map"]}

    # DIRECT full-source module set (not reduced+extrapolated): every layer present
    source_modules = canonical_source_modules(source_param_names)
    templates = extract_templates(source_modules, num_layers)
    if set(templates["per_layer"]) != set(range(num_layers)):
        raise Q35QStageBlock(
            f"source enumeration is not the complete {num_layers}-layer manifest")
    recon = reconcile_source_vs_artifact(source_modules, artifact_modules, num_experts)
    return {
        "outcome": ("q35q_phase0_source_artifact_module_equality_established"
                    if recon["equal"] else "q35q_artifact_admission_blocked"),
        "artifact_admission_status": "q35q_artifact_admission_blocked",
        "config_admitted": True,
        "config_architecture_pass": admitted_cfg["architecture_pass"],
        "config_gptq_pass": admitted_cfg["gptq_pass"],
        "admitted_num_layers": num_layers,
        "admitted_num_experts": num_experts,
        "full_source_enumeration": True,
        "equal": recon["equal"],
        "source_count": recon["source_count"],
        "artifact_textonly_count": recon["artifact_textonly_count"],
        "missing_count": recon["missing_count"],
        "extra_count": recon["extra_count"],
        "vision_omitted": recon["vision_omitted"],
        "mtp_omitted": recon["mtp_omitted"],
        "expert_layers": recon["expert_layers"],
        "index_tensor_count": admitted["tensor_count"],
        "index_shard_count": len(admitted["shard_set"]),
        "note": "module-set correspondence only; load-manifest tensor equality (item 3) and source/package identity (item 4) remain open",
    }
