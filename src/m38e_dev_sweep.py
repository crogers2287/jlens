"""M38E Phase 1: bounded development difficulty sweep (steer dfcade7).

Executes the frozen dev manifest with hardened conformance:

  Ledger separation — ``--smoke`` runs write only to a distinct private
  smoke file and an aggregate ``m38e_driver_smoke`` artifact; they can
  never create, extend, or satisfy any gate for the official ledger.
  The official run refuses to start if the official row file contains a
  smoke marker, a foreign run id, a foreign manifest digest, or any row
  not proven to belong to this exact run.

  Provenance — derived, never trusted: clean tracked tree, full git
  commit, sha256 of the committed bytes of the driver, generators,
  frozen manifest, capture implementation, worker override, and
  verifier sources; the pinned model revision; the runtime override
  hash and output caps; and an ordered digest of the complete expected
  288-task set (task id, family, band, index, prompt hash, answer
  hash — text stays private). Every private row records the run
  identity; resume requires exact equality on all of it and exact
  task-set completion (set equality, never row-count >=).

  Cap escalation (frozen rule, executed not skipped) — each band runs
  fully at 2,048; if exact truncation > 0.10, the truncated task ids
  are ordered by SHA256("m38e-4096-pilot-v1:" + task_id) and the first
  eight rerun at 4,096 as cap-choice evidence only; material reduction
  (>= half of pilot truncations resolved AND >= 2 resolved) triggers a
  full-band 4,096 rerun whose complete ledger alone feeds eligibility;
  otherwise the band is ineligible-by-escalation-failure. Caps are
  never mixed inside a primary band estimate.

  Eligibility arithmetic — exact Fractions, no rounding in gates;
  raw_verified_pass_rate = completed_correct / n gated inclusively on
  [0.20, 0.80] (the completed-only rate is reported, not gated);
  completion/truncation gates use the final single-cap ledger; the
  overall >= 48 completed-incorrect count comes from ELIGIBLE bands
  only; frontier-not-found is legal only after every 2,048 band and
  every triggered pilot/full-band 4,096 path is complete.

Aggregate-only public artifacts; rows, prompts, and answers private.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

REPO = ROOT.parent
PROVENANCE_FILES = (
    "src/m38e_dev_sweep.py",
    "src/m38e_families.py",
    "src/m36c_adaptive.py",
    "src/m36_calibration.py",
    "src/verifiers.py",
    "src/jlens_vllm_telemetry/capture.py",
    "src/jlens_vllm_telemetry/worker_ext.py",
    "reports/telemetry/m38e_dev_manifest.json",
)
PINNED_CHECKPOINT = "cyankiwi/Agents-A1-AWQ-INT4"
PINNED_REVISION = "3e522d4e46438c782789b73c8ff4503e0edd037c"
TASKS_PER_BAND = 24
CAP_2048, CAP_4096 = 2048, 4096
PILOT_SALT = "m38e-4096-pilot-v1:"
PILOT_N = 8

OFFICIAL_ROWS = "reports/shadow/private/m38e_dev_rows.jsonl"
SMOKE_ROWS = "reports/shadow/private/m38e_smoke_rows.jsonl"
OUT = "reports/telemetry/m38e_dev_sweep.json"
SMOKE_OUT = "reports/telemetry/m38e_driver_smoke.json"

GATES = {"completion_rate_min": Fraction(90, 100),
         "truncation_rate_max": Fraction(10, 100),
         "raw_pass_lo": Fraction(20, 100), "raw_pass_hi": Fraction(80, 100),
         "min_completed_correct": 6, "min_completed_incorrect": 6}
OVERALL = {"min_eligible_families": 2, "min_completed_incorrect": 48}


class SweepBlocked(Exception):
    pass


# -- identity and provenance ----------------------------------------------

def source_provenance() -> dict:
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=REPO, capture_output=True, text=True).stdout.strip()
    if dirty:
        raise SweepBlocked("repository has uncommitted tracked changes")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                            capture_output=True, text=True).stdout.strip()
    if len(commit) != 40:
        raise SweepBlocked("could not derive full source commit")
    hashes = {}
    for rel in PROVENANCE_FILES:
        blob = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO,
                              capture_output=True).stdout
        if blob != (REPO / rel).read_bytes():
            raise SweepBlocked(f"working copy differs from HEAD: {rel}")
        hashes[rel] = hashlib.sha256(blob).hexdigest()
    return {"source_commit": commit, "file_sha256": hashes}


def expected_tasks() -> list[dict]:
    from m38e_families import BANDS, generate

    return [generate(family, band, i)
            for family in BANDS
            for band in range(1, len(BANDS[family]) + 1)
            for i in range(TASKS_PER_BAND)]


def task_identity(task: dict) -> dict:
    return {"task_id": task["task_id"], "family": task["family"],
            "band": task["band"],
            "prompt_sha256": hashlib.sha256(
                task["prompt"].encode()).hexdigest(),
            "answer_sha256": hashlib.sha256(
                task["known_answer"].encode()).hexdigest()}


def task_set_digest(tasks: list[dict]) -> str:
    lines = [json.dumps(task_identity(t), sort_keys=True)
             for t in sorted(tasks, key=lambda t: t["task_id"])]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def run_identity(model_ref: str) -> dict:
    frozen_ref = (REPO / ".m36c_model_ref").read_text().strip()
    if model_ref != frozen_ref:
        raise SweepBlocked("--model-ref does not repeat the frozen model")
    prov = source_provenance()
    manifest_digest = prov["file_sha256"][
        "reports/telemetry/m38e_dev_manifest.json"]
    tasks = expected_tasks()
    digest = task_set_digest(tasks)
    run_id = hashlib.sha256(
        f"{prov['source_commit']}:{manifest_digest}:{digest}:"
        f"{PINNED_CHECKPOINT}:{PINNED_REVISION}:{CAP_2048}".encode()
    ).hexdigest()[:16]
    return {"provenance": prov, "manifest_digest": manifest_digest,
            "task_set_digest": digest, "run_id": run_id,
            "checkpoint": PINNED_CHECKPOINT,
            "revision_pinned": PINNED_REVISION, "tasks": tasks}


# -- row ledger -----------------------------------------------------------

def validate_rows(rows: list[dict], ident: dict, override: str) -> None:
    """Every resumed row must match the exact run identity; no unknown,
    duplicate, or malformed rows (steer dfcade7 item 2)."""
    known = {t["task_id"]: task_identity(t) for t in ident["tasks"]}
    seen: set[tuple] = set()
    for r in rows:
        for field, want in (("run_id", ident["run_id"]),
                            ("manifest_digest", ident["manifest_digest"]),
                            ("task_set_digest", ident["task_set_digest"]),
                            ("source_commit",
                             ident["provenance"]["source_commit"]),
                            ("revision_pinned", ident["revision_pinned"]),
                            ("override_hash", override)):
            if r.get(field) != want:
                raise SweepBlocked(f"row {r.get('task_id')}: {field} "
                                   "mismatch")
        tid = r.get("task_id")
        if tid not in known:
            raise SweepBlocked(f"unknown task id in ledger: {tid}")
        for h in ("prompt_sha256", "answer_sha256"):
            if r.get(h) != known[tid][h]:
                raise SweepBlocked(f"row {tid}: task hash changed")
        kind = r.get("attempt_kind")
        if kind not in ("official_2048", "pilot_4096", "band_4096"):
            raise SweepBlocked(f"row {tid}: bad attempt_kind {kind}")
        cap = {"official_2048": CAP_2048, "pilot_4096": CAP_4096,
               "band_4096": CAP_4096}[kind]
        if r.get("output_cap") != cap:
            raise SweepBlocked(f"row {tid}: cap mismatch for {kind}")
        key = (tid, kind)
        if key in seen:
            raise SweepBlocked(f"duplicate attempt in ledger: {key}")
        seen.add(key)
        if "verdict" not in r or "truncated" not in r:
            raise SweepBlocked(f"row {tid}: malformed row")


def rows_of(rows, band_tasks, kind):
    ids = {t["task_id"] for t in band_tasks}
    return [r for r in rows
            if r["task_id"] in ids and r["attempt_kind"] == kind]


def pilot_subset(truncated_ids: list[str]) -> list[str]:
    ordered = sorted(truncated_ids, key=lambda t: hashlib.sha256(
        (PILOT_SALT + t).encode()).hexdigest())
    return ordered[:PILOT_N]


def material_reduction(pilot_rows: list[dict]) -> bool:
    n = len(pilot_rows)
    resolved = sum(1 for r in pilot_rows if not r["truncated"])
    return n > 0 and resolved * 2 >= n and resolved >= 2


# -- eligibility (exact arithmetic) ----------------------------------------

def band_report(final_rows: list[dict], cap: int,
                escalation: str) -> dict:
    n = len(final_rows)
    completed = [r for r in final_rows if not r["truncated"]]
    cc = sum(1 for r in completed if r["verdict"] == "pass")
    ci = len(completed) - cc
    completion = Fraction(len(completed), n) if n else Fraction(0)
    truncation = 1 - completion if n else Fraction(1)
    raw_pass = Fraction(cc, n) if n else Fraction(0)
    eligible = (n == TASKS_PER_BAND
                and completion >= GATES["completion_rate_min"]
                and truncation <= GATES["truncation_rate_max"]
                and GATES["raw_pass_lo"] <= raw_pass <= GATES["raw_pass_hi"]
                and cc >= GATES["min_completed_correct"]
                and ci >= GATES["min_completed_incorrect"]
                and escalation != "escalation_failed")
    return {
        "n": n, "final_cap": cap, "escalation": escalation,
        "completion_rate": round(float(completion), 4),
        "truncation_rate": round(float(truncation), 4),
        "raw_verified_pass_rate": round(float(raw_pass), 4),
        "completed_pass_rate": (round(cc / len(completed), 4)
                                if completed else None),
        "completed_correct": cc, "completed_incorrect": ci,
        "eligible": bool(eligible),
    }


# -- capture --------------------------------------------------------------

def capture_missing(llm, tasks, existing_keys, kind, cap, ident,
                    override, sink):
    from m36c_adaptive import timed_generation
    from m38e_families import verdict

    captured = 0
    for task in tasks:
        if (task["task_id"], kind) in existing_keys:
            continue
        record, timings = timed_generation(llm, task["prompt"], cap)
        v = verdict(task, record["text"])
        row = {
            **task_identity(task),
            "run_id": ident["run_id"],
            "manifest_digest": ident["manifest_digest"],
            "task_set_digest": ident["task_set_digest"],
            "source_commit": ident["provenance"]["source_commit"],
            "revision_pinned": ident["revision_pinned"],
            "override_hash": override,
            "attempt_kind": kind, "output_cap": cap,
            "verdict": v, "truncated": record["truncated"],
            "output_tokens": record["output_tokens"],
            "generation_s": round(timings["generation_s"], 2),
            "features": record["features"],
            "output_text": record["text"],
        }
        sink.write(json.dumps(row) + "\n")
        sink.flush()
        existing_keys.add((task["task_id"], kind))
        captured += 1
    return captured


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--smoke", type=int, default=0,
                    help="driver smoke over N tasks; separate ledger, "
                         "never satisfies official gates")
    ap.add_argument("--out")
    args = ap.parse_args()

    import os
    src = str(ROOT)
    if src not in os.environ.get("PYTHONPATH", "").split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            src + os.pathsep + os.environ.get("PYTHONPATH", ""))

    from m36v_phase1 import override_hash
    from m36c_adaptive import make_llm, install

    ident = run_identity(args.model_ref)
    override = override_hash()
    smoke = args.smoke > 0
    rows_path = Path(SMOKE_ROWS if smoke else OFFICIAL_ROWS)
    out_path = args.out or (SMOKE_OUT if smoke else OUT)

    rows = ([json.loads(l) for l in rows_path.read_text().splitlines()]
            if rows_path.exists() else [])
    if smoke:
        plan = ident["tasks"][:args.smoke]
    else:
        for r in rows:
            if r.get("attempt_kind", "").startswith("smoke"):
                raise SweepBlocked("official ledger contains smoke rows")
        validate_rows(rows, ident, override)
        plan = ident["tasks"]

    existing = {(r["task_id"], r["attempt_kind"]) for r in rows}
    llm = None

    def ensure(tasks, kind, cap):
        nonlocal llm
        need = [t for t in tasks if (t["task_id"], kind) not in existing]
        if not need:
            return 0
        if llm is None:
            llm = make_llm(args.model_ref)
            install(llm)
        with rows_path.open("a") as sink:
            n = capture_missing(llm, need, existing, kind, cap, ident,
                                override, sink)
        rows.extend([json.loads(l) for l in
                     rows_path.read_text().splitlines()][len(rows):])
        return n

    if smoke:
        ensure(plan, "official_2048", CAP_2048)
        Path(out_path).write_text(json.dumps({
            "schema_version": 1, "run_kind": "m38e_driver_smoke",
            "rows": len(plan), "run_id": ident["run_id"],
            "ledger": "separate smoke file; zero official interaction",
            "privacy_check_status": "aggregate smoke note only",
        }, indent=1) + "\n")
        print(f"[m38e] driver smoke complete ({len(plan)} tasks, "
              "separate ledger)", flush=True)
        return 0

    # ---- official sweep with frozen escalation ------------------------
    from m38e_families import BANDS

    bands_report, all_paths_complete = {}, True
    for family in BANDS:
        for band in range(1, len(BANDS[family]) + 1):
            band_tasks = [t for t in ident["tasks"]
                          if t["family"] == family
                          and t["band"] == f"b{band}"]
            key = f"{family}:b{band}"
            ensure(band_tasks, "official_2048", CAP_2048)
            base = rows_of(rows, band_tasks, "official_2048")
            if len(base) != TASKS_PER_BAND:
                all_paths_complete = False
                continue
            truncated_ids = [r["task_id"] for r in base if r["truncated"]]
            truncation = Fraction(len(truncated_ids), TASKS_PER_BAND)
            if truncation <= GATES["truncation_rate_max"]:
                bands_report[key] = band_report(base, CAP_2048,
                                                "not_triggered")
                continue
            # Frozen pilot escalation.
            pilot_ids = pilot_subset(truncated_ids)
            pilot_tasks = [t for t in band_tasks
                           if t["task_id"] in pilot_ids]
            ensure(pilot_tasks, "pilot_4096", CAP_4096)
            pilot_rows = rows_of(rows, pilot_tasks, "pilot_4096")
            if len(pilot_rows) != len(pilot_ids):
                all_paths_complete = False
                continue
            if material_reduction(pilot_rows):
                ensure(band_tasks, "band_4096", CAP_4096)
                full = rows_of(rows, band_tasks, "band_4096")
                if len(full) != TASKS_PER_BAND:
                    all_paths_complete = False
                    continue
                bands_report[key] = band_report(full, CAP_4096,
                                                "escalated_full_band")
            else:
                bands_report[key] = band_report(base, CAP_2048,
                                                "escalation_failed")

    eligible = {k: v for k, v in bands_report.items() if v["eligible"]}
    eligible_families = {k.split(":")[0] for k in eligible}
    ci_eligible = sum(v["completed_incorrect"] for v in eligible.values())
    gates_ok = (len(eligible_families) >= OVERALL["min_eligible_families"]
                and ci_eligible >= OVERALL["min_completed_incorrect"])
    expected_bands = sum(len(BANDS[f]) for f in BANDS)
    complete = (all_paths_complete
                and len(bands_report) == expected_bands)

    payload = {
        "schema_version": 1,
        "run_kind": "m38e_dev_sweep",
        "steer": "dfcade7",
        "run_id": ident["run_id"],
        "manifest_digest": ident["manifest_digest"],
        "task_set_digest": ident["task_set_digest"],
        "source_commit": ident["provenance"]["source_commit"],
        "revision_pinned": ident["revision_pinned"],
        "override_hash": override,
        "sweep_complete": bool(complete),
        "bands": bands_report,
        "eligible_families": sorted(eligible_families),
        "completed_incorrect_from_eligible_bands": ci_eligible,
        "overall_gates_passed": bool(gates_ok),
        "outcome": ("eligible" if gates_ok and complete
                    else "m38e_completed_error_frontier_not_found"
                    if complete else "in_progress"),
        "privacy_check_status": "aggregate band stats only; rows private",
    }
    Path(out_path).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[m38e] sweep: complete={complete} "
          f"eligible={sorted(eligible_families)} ci={ci_eligible} "
          f"gates={gates_ok} outcome={payload['outcome']}", flush=True)
    return 0 if (not complete or gates_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
