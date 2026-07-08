#!/usr/bin/env python3
"""Tests for the M9 private real-use workflow. CPU-only, no network.

Covers the four privacy invariants:
  (a) reports/shadow/private/*.jsonl is gitignored;
  (b) redaction strips the three text fields, keeps structure + booleans;
  (c) the aggregate summary has NO prompt/output/notes text and computes
      correct counts + FLR/FHR from a SYNTHETIC reviewed fixture;
  (d) check_commit_safe passes aggregate/all-null files, fails text-carrying
      records and private-log paths.

All reviewed records here are SYNTHETIC in-memory fixtures — never written as
real reviewed data.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import redact_shadow_log as RD       # noqa: E402
import private_outcome_summary as PS  # noqa: E402
import check_commit_safe as CS        # noqa: E402

NULL_OUT = {"user_agreed": None, "was_wrong": None, "needed_retrieval": None,
            "needed_checker": None, "notes": None}
NULL_META = {"reviewer": None, "reviewed_at": None, "review_source": None,
             "review_confidence": None}


def _rec(**over):
    r = {"prompt_id": "x", "prompt_preview": "raw prompt text",
         "output_preview": "raw output text",
         "policy": {"level": "low", "recommended_action": "answer_locally"},
         "policy_note": None, "mode": "shadow",
         "outcome": dict(NULL_OUT), "review_meta": dict(NULL_META)}
    r.update(over)
    return r


def _reviewed(level, was_wrong):
    return _rec(policy={"level": level, "recommended_action": "verify"},
               outcome={**NULL_OUT, "was_wrong": was_wrong, "notes": "reviewer note"},
               review_meta={**NULL_META, "reviewer": "t"})


# ---- (a) private dir is gitignored ------------------------------------------
def test_private_dir_gitignored():
    gi = (ROOT / ".gitignore").read_text()
    assert "reports/shadow/private/" in gi, "private dir not in .gitignore"
    # the pattern must not accidentally ignore the README
    assert "reports/shadow/private/README.md" not in gi
    # belt-and-suspenders: git itself agrees (skip silently if git absent)
    import shutil, subprocess
    if shutil.which("git"):
        r = subprocess.run(
            ["git", "check-ignore", "reports/shadow/private/realuse_local.jsonl"],
            cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0 and "private" in r.stdout


# ---- (b) redaction strips text, keeps structure + booleans ------------------
def test_redaction_strips_text_keeps_structure():
    src = _rec(outcome={**NULL_OUT, "was_wrong": True, "notes": "sensitive"})
    red = RD.redact_record(src)
    assert red["prompt_preview"] == "[redacted]"
    assert red["output_preview"] == "[redacted]"
    assert red["outcome"]["notes"] == "[redacted]"
    # structure + booleans intact
    assert red["prompt_id"] == "x"
    assert red["policy"]["level"] == "low"
    assert red["mode"] == "shadow"
    assert red["outcome"]["was_wrong"] is True
    assert red["review_meta"] == src["review_meta"]
    # original object not mutated
    assert src["prompt_preview"] == "raw prompt text"
    # --hash gives a stable non-reversible tag (no original text)
    h1 = RD.redact_record(src, use_hash=True)["prompt_preview"]
    h2 = RD.redact_record(src, use_hash=True)["prompt_preview"]
    assert h1 == h2 and h1.startswith("[redacted:") and "raw prompt" not in h1


# ---- (c) aggregate summary: no text keys + correct counts/FLR/FHR -----------
def _no_text_values(obj, where="root"):
    """No prompt_preview/output_preview keys anywhere; every 'notes' is an int."""
    if isinstance(obj, dict):
        assert "prompt_preview" not in obj, f"prompt_preview at {where}"
        assert "output_preview" not in obj, f"output_preview at {where}"
        for k, v in obj.items():
            if k == "notes":
                assert isinstance(v, int), f"notes holds non-int at {where}"
            _no_text_values(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _no_text_values(v, f"{where}[{i}]")


def test_aggregate_summary_no_text_and_counts():
    fx = [
        _reviewed("critical", True),   # wrong & risky -> TP
        _reviewed("low", True),        # wrong & not risky -> FN (false-low-risk)
        _reviewed("low", False),       # fine & not risky -> TN
        _rec(policy={"level": "medium", "recommended_action": "verify"}),  # unreviewed
    ]
    summ = PS.summarize(fx)
    _no_text_values(summ)  # HARD: no leaked text anywhere
    assert summ["n_total"] == 4
    assert summ["n_reviewed"] == 3 and summ["n_unreviewed"] == 1
    assert summ["level_distribution"] == {"critical": 1, "low": 2, "medium": 1}
    assert summ["recommended_action_distribution"] == {"verify": 4}
    # reviewed-only calibration: 1 FN of 2 positives; 0 FP of 1 negative
    assert summ["calibration"]["false_low_risk_rate"] == 0.5
    assert summ["calibration"]["false_high_risk_rate"] == 0.0
    assert summ["calibration"]["confusion"] == {"tp": 1, "fn": 1, "fp": 0, "tn": 1}
    # notes count reflects the 3 reviewed rows that carried a note (aggregate int)
    assert summ["outcome_field_nonnull_counts"]["notes"] == 3


def test_aggregate_summary_pending_when_none_reviewed():
    summ = PS.summarize([_rec(), _rec()])
    assert summ["n_reviewed"] == 0
    assert summ["calibration"] is None  # never fabricated


# ---- (d) check_commit_safe: pass safe, fail leaky ---------------------------
def _write(tmp, records):
    p = Path(tmp)
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return str(p)


def test_check_commit_safe_pass_and_fail():
    with tempfile.TemporaryDirectory() as d:
        # aggregate summary (no text) -> PASS
        summ = PS.summarize([_reviewed("low", False)])
        agg = Path(d) / "summary.json"
        agg.write_text(json.dumps(summ))
        assert CS.check_file(str(agg)) == []

        # all-null-text queue -> PASS
        nulls = _write(Path(d) / "nulltext.jsonl",
                       [_rec(prompt_preview=None, output_preview=None)])
        assert CS.check_file(nulls) == []

        # redacted -> PASS
        red = _write(Path(d) / "red.jsonl", [RD.redact_record(_rec())])
        assert CS.check_file(red) == []

        # real prompt text -> FAIL
        leak = _write(Path(d) / "leak.jsonl", [_rec()])
        assert CS.check_file(leak), "text-carrying record must FAIL"

        # unredacted outcome.notes -> FAIL
        note = _write(Path(d) / "note.jsonl",
                      [_rec(prompt_preview=None, output_preview=None,
                            outcome={**NULL_OUT, "notes": "sensitive"})])
        assert CS.check_file(note), "unredacted notes must FAIL"


TESTS = [test_private_dir_gitignored,
         test_redaction_strips_text_keeps_structure,
         test_aggregate_summary_no_text_and_counts,
         test_aggregate_summary_pending_when_none_reviewed,
         test_check_commit_safe_pass_and_fail]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] private-workflow tests PASSED ({len(TESTS)} tests)")
