#!/usr/bin/env python3
"""Cheap verifier adapters for the M10 autonomous shadow supervisor.

Each adapter inspects a task + model output and returns a VerdictResult:
  {name, confidence (0..1), evidence_hash, verdict}
where verdict is one of "pass" / "fail" / "undecided" (or a signal-specific
string for heuristics). Verdicts feed the auto_outcome CANDIDATE — they are
NEVER gold labels, and never touch the human outcome fields.

Privacy: evidence is stored as a STABLE NON-REVERSIBLE HASH of the inputs, never
raw prompt/output text. No network, no arbitrary command execution.
"""
from __future__ import annotations

import json
import re
from typing import Optional

VERDICT_PASS = "pass"
VERDICT_FAIL = "fail"
VERDICT_UNDECIDED = "undecided"


def evidence_hash(*parts) -> str:
    """Stable non-reversible tag over the given parts — no original text leaks."""
    h = 0
    for p in parts:
        for ch in str(p):
            h = (h * 131 + ord(ch)) & 0xFFFFFFFFFFFFFFFF
    return f"[h:{h:016x}]"


def _result(name, confidence, verdict, *evidence_parts):
    return {"name": name, "confidence": round(float(confidence), 4),
            "verdict": verdict, "evidence_hash": evidence_hash(name, *evidence_parts)}


_NUM_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def _final_number(text: str) -> Optional[str]:
    nums = _NUM_RE.findall(text or "")
    return nums[-1].replace(",", "") if nums else None


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower()).rstrip(".")


# --- adapters ---------------------------------------------------------------
def exact_answer_match(output: str, known_answer: Optional[str] = None, **_):
    """Compare the model's final answer to a known reference answer."""
    if known_answer is None:
        return _result("exact_answer_match", 0.0, VERDICT_UNDECIDED, "no-ref")
    hit = _norm(known_answer) in _norm(output) or _norm(output) == _norm(known_answer)
    return _result("exact_answer_match", 0.9 if hit else 0.85,
                   VERDICT_PASS if hit else VERDICT_FAIL, known_answer, output)


def regex_or_schema_check(output: str, pattern: Optional[str] = None, **_):
    """Check the output matches a required regex/format (e.g. JSON-ish, id form)."""
    if not pattern:
        return _result("regex_or_schema_check", 0.0, VERDICT_UNDECIDED, "no-pattern")
    try:
        ok = re.search(pattern, output or "") is not None
    except re.error:
        return _result("regex_or_schema_check", 0.0, VERDICT_UNDECIDED, "bad-pattern")
    return _result("regex_or_schema_check", 0.8 if ok else 0.75,
                   VERDICT_PASS if ok else VERDICT_FAIL, pattern)


def math_checker(output: str, known_answer: Optional[str] = None,
                 expression: Optional[str] = None, **_):
    """Deterministically verify a numeric answer when possible.

    Prefers evaluating a safe arithmetic `expression`; else compares the output's
    final number to `known_answer`. Never eval()s arbitrary text.
    """
    truth = None
    if expression is not None:
        if re.fullmatch(r"[\d\s+\-*/().]+", expression or ""):
            try:
                truth = str(eval(expression, {"__builtins__": {}}, {}))  # arithmetic only
            except (SyntaxError, ZeroDivisionError, TypeError, ValueError):
                truth = None
    if truth is None and known_answer is not None:
        truth = _final_number(known_answer)
    if truth is None:
        return _result("math_checker", 0.0, VERDICT_UNDECIDED, "no-truth")
    got = _final_number(output)
    if got is None:
        return _result("math_checker", 0.3, VERDICT_UNDECIDED, "no-number-in-output")
    try:
        hit = abs(float(got) - float(truth)) < 1e-6
    except ValueError:
        hit = _norm(got) == _norm(truth)
    return _result("math_checker", 0.95 if hit else 0.9,
                   VERDICT_PASS if hit else VERDICT_FAIL, truth, got)


def code_test_stub(output: str, fixture_test=None, **_):
    """Run FIXTURE tests only — never arbitrary/untrusted commands.

    `fixture_test` is an OPTIONAL in-process callable(output)->bool provided by a
    trusted fixture. With no fixture this is a low-confidence no-op (by design:
    real code execution is out of scope for the autonomous loop).
    """
    if fixture_test is None:
        return _result("code_test_stub", 0.1, VERDICT_UNDECIDED, "no-fixture")
    try:
        ok = bool(fixture_test(output))
    except Exception:  # a fixture that errors is a fail signal, not a crash
        return _result("code_test_stub", 0.6, VERDICT_FAIL, "fixture-raised")
    return _result("code_test_stub", 0.85 if ok else 0.8,
                   VERDICT_PASS if ok else VERDICT_FAIL, "fixture")


_FRESH_RE = re.compile(
    r"\b(today|current|currently|latest|now|this year|as of|2024|2025|2026|"
    r"who is the (president|ceo)|when did .* (release|launch))\b",
    re.I)


def retrieval_required_heuristic(output: str, prompt: str = "",
                                 task_category: Optional[str] = None, **_):
    """Flag tasks that likely need fresh/grounded info (auto_needed_retrieval)."""
    # Bare topic words such as weather/price/news are not freshness by
    # themselves (M19 found three false positives). Explicit current-info task
    # metadata remains authoritative; otherwise require a temporal expression.
    needs = (task_category in {"current_info", "retrieval", "news"} or
             bool(_FRESH_RE.search(prompt or "")))
    # confidence reflects how sure the heuristic is, not correctness of the answer
    return _result("retrieval_required_heuristic", 0.7 if needs else 0.5,
                   VERDICT_FAIL if needs else VERDICT_PASS,
                   task_category or "none")


def self_consistency(samples, **_):
    """Compare small-N samples. DISAGREEMENT is an ESCALATION signal, NOT proof
    the answer is wrong. Returns agreement fraction as confidence."""
    finals = [_final_number(s) or _norm(s) for s in (samples or [])]
    n = len(finals)
    if n < 2:
        return _result("self_consistency", 0.0, VERDICT_UNDECIDED, "n<2")
    top = max(set(finals), key=finals.count)
    agreement = finals.count(top) / n
    # high agreement = consistent (pass-ish); low = escalate (undecided, not fail)
    verdict = VERDICT_PASS if agreement == 1.0 else VERDICT_UNDECIDED
    return _result("self_consistency", round(agreement, 4), verdict, f"n={n}")


def _first_json_value(text: str):
    """Extract + parse the first balanced {...} or [...] substring, or None.

    Tolerates leading/trailing prose or markdown fences by scanning for the
    first opener and matching braces respecting strings/escapes.
    """
    s = text or ""
    start = None
    for i, ch in enumerate(s):
        if ch in "{[":
            start = i
            open_ch, close_ch = ch, ("}" if ch == "{" else "]")
            break
    if start is None:
        return None
    depth, in_str, esc = 0, False, False
    for j in range(start, len(s)):
        ch = s[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(s[start:j + 1])
                except (json.JSONDecodeError, ValueError):
                    return None
    return None


def json_object_check(output: str, required_keys=None, expected_type="object", **_):
    """Validate that the output is (or contains) a JSON value of expected_type.

    Parses the stripped output, or the first balanced {...}/[...] substring if
    there is surrounding prose/whitespace. PASS on valid JSON meeting the type +
    required_keys requirements; FAIL otherwise. Evidence is hashed, never raw.
    """
    text = (output or "").strip()
    val = None
    try:
        val = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        val = _first_json_value(text)          # tolerate trailing/leading prose
    if val is None:
        return _result("json_object_check", 0.8, VERDICT_FAIL, "unparseable")
    if expected_type == "object" and not isinstance(val, dict):
        return _result("json_object_check", 0.75, VERDICT_FAIL, "not-object")
    if expected_type == "array" and not isinstance(val, list):
        return _result("json_object_check", 0.75, VERDICT_FAIL, "not-array")
    if required_keys and isinstance(val, dict):
        missing = [k for k in required_keys if k not in val]
        if missing:
            return _result("json_object_check", 0.8, VERDICT_FAIL,
                           "missing:" + ",".join(sorted(missing)))
    return _result("json_object_check", 0.85, VERDICT_PASS,
                   expected_type, *(sorted(required_keys) if required_keys else []))


def _all_numbers(text: str):
    """Every numeric value in the text as floats (thousands separators stripped)."""
    out = []
    for tok in _NUM_RE.findall(text or ""):
        try:
            out.append(float(tok.replace(",", "")))
        except ValueError:
            continue
    return out


# simple unit scale factors -> base unit within a family (extend as needed)
_UNIT_SCALE = {
    "m": 1.0, "meter": 1.0, "meters": 1.0,
    "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
}


def numeric_tolerant_check(output: str, expected_value=None, tolerance=None,
                           rel_tolerance=None, expected_units=None,
                           accepted_values=None, **_):
    """Numeric-tolerant answer check for approximate / unit-converted numbers.

    Extracts numbers from the output and PASSES if any is within tolerance of an
    accepted target (expected_value or accepted_values), using absolute
    `tolerance` or `rel_tolerance` (relative). FAILS when numbers are present but
    all outside tolerance; UNDECIDED (escalate) when no number can be extracted
    or no target was given. Evidence is hashed — never raw text.
    """
    targets = []
    if expected_value is not None:
        targets.append(float(expected_value))
    if accepted_values:
        targets += [float(v) for v in accepted_values]
    if not targets:
        return _result("numeric_tolerant_check", 0.0, VERDICT_UNDECIDED, "no-target")

    nums = _all_numbers(output)
    if not nums:
        return _result("numeric_tolerant_check", 0.3, VERDICT_UNDECIDED, "no-number")

    # optional unit normalization: also consider each number scaled by a known unit
    candidates = list(nums)
    if expected_units and expected_units.lower() in _UNIT_SCALE:
        base = _UNIT_SCALE[expected_units.lower()]
        candidates += [n * s / base for n in nums for s in _UNIT_SCALE.values()]

    def within(v, t):
        if rel_tolerance is not None and t != 0:
            if abs(v - t) <= abs(t) * float(rel_tolerance):
                return True
        if tolerance is not None:
            if abs(v - t) <= float(tolerance):
                return True
        if rel_tolerance is None and tolerance is None:
            return v == t
        return False

    hit = any(within(v, t) for v in candidates for t in targets)
    return _result("numeric_tolerant_check", 0.9 if hit else 0.85,
                   VERDICT_PASS if hit else VERDICT_FAIL,
                   *[f"{t:g}" for t in targets])


def explain_rubric_check(output: str, required_facts=None, **_):
    """Score an open-ended explanation ONLY against a public fact checklist.

    Counts how many required facts appear in the output (case-insensitive). PASS
    only when ALL required facts are present. UNDECIDED (escalate) when there is
    no rubric, or coverage is weak (a fact is missing). This NEVER claims a
    subjective explanation is gold — with no rubric it escalates rather than
    guessing. Evidence is hashed — never raw text.
    """
    if not required_facts:
        # no objective checklist -> cannot judge; escalate for a human
        return _result("explain_rubric_check", 0.0, VERDICT_UNDECIDED, "no-rubric")
    text = _norm(output)
    present = [f for f in required_facts if _norm(f) in text]
    coverage = len(present) / len(required_facts)
    if coverage == 1.0:
        return _result("explain_rubric_check", 0.8, VERDICT_PASS,
                       f"cov=1.0/{len(required_facts)}")
    # weak/partial coverage: escalate (not a wrongness claim), never gold
    return _result("explain_rubric_check", round(0.4 + 0.3 * coverage, 4),
                   VERDICT_UNDECIDED, f"cov={coverage:.2f}")


# Registry keyed by config toggle name.
ADAPTERS = {
    "exact_answer_match": exact_answer_match,
    "regex_or_schema_check": regex_or_schema_check,
    "json_object_check": json_object_check,
    "numeric_tolerant_check": numeric_tolerant_check,
    "explain_rubric_check": explain_rubric_check,
    "math_checker": math_checker,
    "code_test_stub": code_test_stub,
    "retrieval_required_heuristic": retrieval_required_heuristic,
    "self_consistency": self_consistency,
}
