"""Q35Q Phase-0 unified runtime conversion admission (CPU-only, injected).

Composition step per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_AST_DISPATCH_AND_SOURCE_PIN_COMPOSITION_CORRECTION.md
(defect 4/8): the dispatch-conversion verifier and the source-digest pin existed as
separate helpers with no single committed production path binding package version,
module import origin, loader entry point, source digests, and the dispatch-selected
conversion together. This module is that one composition, used identically by tests
and a live CLI.

It fails closed unless ALL of:
- the imported Transformers package version equals the frozen expected version;
- the module import origin ends with the frozen expected canonical path (so a wrong
  import origin / shadow module is rejected);
- the installed source files bind by equality to their frozen expected sha256;
- the dispatch-selected `qwen3_5_moe_text` conversion object verifies exactly
  (patterns/dims/counts/multiplicity).

Residual (recorded, not claimed solved): the frozen expected source digests must be
derived from an INDEPENDENT upstream artifact (wheel/sdist/commit/blob), not the
installed bytes; and the GPTQ loader tuple (Optimum / GPTQModel+Defuser) is required
for the differentiable-runtime fixture. Both remain open.
"""
from __future__ import annotations

from q35q_dispatch_conversion import verify_dispatch_conversion
from q35q_runtime_source_pin import bind_source_digests
from q35q_stage import Q35QStageBlock


def run_runtime_conversion_admission(*, package_version, expected_package_version,
                                     import_origin, expected_import_origin_suffix,
                                     source_digests_observed, source_digests_expected,
                                     dispatch_mapping_extracted,
                                     expected_digests_independent: bool) -> dict:
    """One production conjunction over package/import-origin/source-digest/dispatch.
    `expected_digests_independent` must assert the expected digests were derived from
    an independent upstream artifact, not the installed bytes; False -> fail closed."""
    if not isinstance(package_version, str) or not package_version:
        raise Q35QStageBlock("package version missing")
    if package_version != expected_package_version:
        raise Q35QStageBlock(f"package version {package_version!r} != expected")
    if not isinstance(import_origin, str) or not import_origin.endswith(expected_import_origin_suffix):
        raise Q35QStageBlock("module import origin does not match the frozen canonical path")
    if expected_digests_independent is not True:
        raise Q35QStageBlock(
            "expected source digests must be independently derived (not from installed bytes)")

    src = bind_source_digests(source_digests_observed, source_digests_expected)  # raises on mismatch
    disp = verify_dispatch_conversion(dispatch_mapping_extracted)
    if not disp["dispatch_conversion_pass"]:
        raise Q35QStageBlock("dispatch-selected conversion did not verify exactly")

    return {
        "outcome": "q35q_runtime_conversion_admission_pass",
        "artifact_admission_status": "q35q_artifact_admission_blocked",
        "package_version_bound": True,
        "import_origin_bound": True,
        "source_digests_bound": src["source_pin_pass"],
        "expected_digests_independent": True,
        "dispatch_conversion_verified": True,
        "files_bound": src["files_bound"],
        "note": "installed-runtime conversion admission conjunction; GPTQ loader tuple + differentiable fixture remain",
    }
