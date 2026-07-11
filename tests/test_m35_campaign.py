"""CPU-only tests for M35 campaign generation and split assignment."""
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m35_campaign as M35  # noqa: E402
import verifiers as VZ  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m35_campaign_manifest.json"
PRIOR_ARGS = [str(ROOT / "data/prompts" / name) for name in (
    "m29_power_manifest.json", "m30_decisive_manifest.json",
    "m31_intervention_manifest.json", "m32_repair_manifest.json",
    "m33_tool_routing_manifest.json", "m34_transfer_manifest.json")]


@pytest.fixture(scope="module")
def manifest():
    return M35.load_manifest(MANIFEST_PATH)


@pytest.fixture(scope="module")
def tasks(manifest):
    return M35.generate_tasks(manifest, *PRIOR_ARGS)


def test_load_manifest_validates(manifest, tmp_path):
    bad = json.loads(MANIFEST_PATH.read_text())
    bad["split_assignment"]["sequence"][0] = "R"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        M35.load_manifest(path)


def test_generation_counts_and_uniqueness(manifest, tasks):
    assert len(tasks) == manifest["n_tasks_total"] == 1536
    by_family = Counter(t["family"] for t in tasks)
    for family in manifest["families"]:
        assert by_family[family["family_id"]] == family["n_tasks"]
    pairs = [(t["a"], t["b"]) for t in tasks]
    assert len(set(pairs)) == len(pairs)


def test_split_fractions_exact_per_cell(manifest, tasks):
    by_split = Counter(t["split"] for t in tasks)
    assert by_split == {"D": 576, "R": 288, "B_test": 288, "A_test": 384}
    cells = Counter((t["family"], t["stratum"], t["split"]) for t in tasks)
    for family in manifest["families"]:
        per_stratum = family["n_tasks"] // 4
        for stratum in family["strata"]:
            key = (family["family_id"], stratum["stratum_id"])
            assert cells[(*key, "D")] == per_stratum * 6 // 16
            assert cells[(*key, "A_test")] == per_stratum * 4 // 16


def test_answers_and_constraints(tasks):
    for t in tasks:
        if t["family"] == "add_carry":
            assert int(t["known_answer"]) == t["a"] + t["b"]
        elif t["family"] == "sub_borrow":
            assert t["a"] > t["b"]
            assert int(t["known_answer"]) == t["a"] - t["b"]
        elif t["family"] == "mul_carry":
            assert int(t["known_answer"]) == t["a"] * t["b"]
        elif t["family"] == "div_exact":
            assert t["a"] == t["q"] * t["b"]
            assert int(t["known_answer"]) == t["q"]
        elif t["family"] == "mul_add":
            assert 2 <= t["c"] <= 99
            assert int(t["known_answer"]) == t["a"] * t["b"] + t["c"]
        elif t["family"] == "mod_mul":
            assert 3 <= t["m"] <= 19
            assert int(t["known_answer"]) == (t["a"] * t["b"]) % t["m"]


def test_verifier_passes_known_answers_all_families(tasks):
    seen = set()
    for t in tasks:
        if t["family"] in seen:
            continue
        seen.add(t["family"])
        result = VZ.math_checker(t["known_answer"],
                                 known_answer=t["known_answer"],
                                 expression=t["expression"])
        assert result["verdict"] == "pass", (t["family"], result)


def test_disjoint_from_m34(tasks):
    import m34_detector_transfer as M34
    m34_manifest = M34.load_manifest(PRIOR_ARGS[5])
    m34_tasks = M34.generate_tasks(m34_manifest, *PRIOR_ARGS[:5])
    m34_pairs = {(t["a"], t["b"]) for t in m34_tasks}
    m35_pairs = {(t["a"], t["b"]) for t in tasks}
    assert not m35_pairs & m34_pairs
