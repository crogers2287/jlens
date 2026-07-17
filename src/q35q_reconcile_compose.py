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

from q35q_index_admission import admit_weight_index
from q35q_module_reconcile import reconcile_source_vs_artifact
from q35q_source_admission import canonical_module_path
from q35q_source_allowlist import derive_source_allowlist_from_modules
from q35q_stage import Q35QStageBlock


def run_reconciliation(*, source_param_names, index_bytes, index_expected_sha256,
                       num_experts, num_layers=40, interval=4) -> dict:
    """Compose strict index admission + source allow-list derivation + the frozen
    representation-map equality. `source_param_names` come from the admitted text-only
    class (meta-device enumeration); `index_bytes` are the downloaded weight index."""
    admitted = admit_weight_index(index_bytes, index_expected_sha256)
    artifact_modules = {canonical_module_path(name) for name in admitted["weight_map"]}
    source = derive_source_allowlist_from_modules(
        source_param_names, num_layers=num_layers, interval=interval)
    recon = reconcile_source_vs_artifact(source["allowlist"], artifact_modules, num_experts)
    return {
        "outcome": ("q35q_phase0_source_artifact_module_equality_established"
                    if recon["equal"] else "q35q_artifact_admission_blocked"),
        "artifact_admission_status": "q35q_artifact_admission_blocked",
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
