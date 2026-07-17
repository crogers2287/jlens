"""Q35Q unified runtime conversion-admission tests (CPU-only, no network).

Proves the one production conjunction fails closed on a wrong package version, a
wrong import origin, a non-independent (self-bound) expected digest, a wrong source
digest, and a wrong dispatch-selected conversion.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_runtime_admission import run_runtime_conversion_admission

A = "a" * 64
B = "b" * 64
VER = "5.13.1"
ORIGIN = "site-packages/transformers/conversion_mapping.py"


def good_dispatch():
    return [
        {"kind": "PrefixChange", "prefix_to_remove": "language_model", "model_prefix": "model"},
        {"kind": "WeightConverter", "target": ["mlp.experts.gate_up_proj"],
         "source": ["mlp.experts.*.gate_proj.weight", "mlp.experts.*.up_proj.weight"],
         "ops": [("MergeModulelist", 0), ("Concatenate", 1)]},
        {"kind": "WeightConverter", "target": ["mlp.experts.down_proj"],
         "source": ["mlp.experts.*.down_proj.weight"], "ops": [("MergeModulelist", 0)]},
    ]


def run(**over):
    kw = dict(package_version=VER, expected_package_version=VER,
              import_origin=ORIGIN, expected_import_origin_suffix="transformers/conversion_mapping.py",
              source_digests_observed={"f1": A}, source_digests_expected={"f1": A},
              dispatch_mapping_extracted=good_dispatch(), expected_digests_independent=True)
    kw.update(over)
    return run_runtime_conversion_admission(**kw)


def test_pass():
    out = run()
    assert out["outcome"] == "q35q_runtime_conversion_admission_pass"
    assert out["artifact_admission_status"] == "q35q_artifact_admission_blocked"


def test_wrong_package_version_fails():
    with pytest.raises(Q35QStageBlock, match="package version"):
        run(package_version="4.99.0")


def test_wrong_import_origin_fails():
    with pytest.raises(Q35QStageBlock, match="import origin"):
        run(import_origin="site-packages/evil/conversion_mapping.py",
            expected_import_origin_suffix="transformers/conversion_mapping.py")


def test_non_independent_expected_digests_fails():
    with pytest.raises(Q35QStageBlock, match="independently derived"):
        run(expected_digests_independent=False)


def test_wrong_source_digest_fails():
    with pytest.raises(Q35QStageBlock, match="source-digest mismatch"):
        run(source_digests_observed={"f1": A}, source_digests_expected={"f1": B})


def test_wrong_dispatch_conversion_fails():
    m = good_dispatch(); m[1]["ops"] = [("MergeModulelist", 0), ("Concatenate", 0)]  # wrong dim
    with pytest.raises(Q35QStageBlock, match="did not verify exactly"):
        run(dispatch_mapping_extracted=m)


def test_extra_dispatch_converter_fails():
    m = good_dispatch()
    m.append({"kind": "WeightConverter", "target": ["mlp.experts.gate_up_proj"],
              "source": ["decoy"], "ops": [("Transpose", 1)]})
    with pytest.raises(Q35QStageBlock, match="did not verify exactly"):
        run(dispatch_mapping_extracted=m)
