"""M38E Phase 1: bounded development difficulty sweep (gated on M36T stop).

Runs the frozen development manifest (reports/telemetry/
m38e_dev_manifest.json): 24 tasks per band x 4 bands x 3 procedural
families, one greedy generation each at the 2,048-token cap, full-run
telemetry features via the M36C capture path (features never include
the verifier result or known answer — labels only). Rows are private
and resume by task id. At the end the band-eligibility gates and
overall gates are evaluated and an aggregate artifact is written; if
the overall gates fail the artifact records
m38e_completed_error_frontier_not_found per the manifest stop rule.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from m36c_adaptive import make_llm, install, timed_generation  # noqa: E402
from m36v_phase1 import PRIVATE_DIR, override_hash  # noqa: E402
from m38e_families import BANDS, generate, verdict  # noqa: E402

TASKS_PER_BAND = 24
OUTPUT_CAP = 2048
ROWS_OUT = PRIVATE_DIR / "m38e_dev_rows.jsonl"
OUT = "reports/telemetry/m38e_dev_sweep.json"

GATES = {"completion_rate_min": 0.90, "truncation_rate_max": 0.10,
         "pass_rate_range": (0.20, 0.80), "min_completed_correct": 6,
         "min_completed_incorrect": 6}
OVERALL = {"min_eligible_families": 2, "min_completed_incorrect": 48}


def classify(row: dict) -> str:
    if row["truncated"]:
        return "truncated_budget"
    return ("completed_correct" if row["verdict"] == "pass"
            else "completed_incorrect")


def band_stats(rows: list[dict]) -> dict:
    n = len(rows)
    completed = [r for r in rows if not r["truncated"]]
    cc = sum(1 for r in completed if r["verdict"] == "pass")
    ci = len(completed) - cc
    stats = {
        "n": n,
        "completion_rate": round(len(completed) / n, 3) if n else 0.0,
        "truncation_rate": round(1 - len(completed) / n, 3) if n else 1.0,
        "pass_rate_completed": (round(cc / len(completed), 3)
                                if completed else None),
        "completed_correct": cc,
        "completed_incorrect": ci,
    }
    lo, hi = GATES["pass_rate_range"]
    stats["eligible"] = bool(
        n and stats["completion_rate"] >= GATES["completion_rate_min"]
        and stats["truncation_rate"] <= GATES["truncation_rate_max"]
        and stats["pass_rate_completed"] is not None
        and lo <= stats["pass_rate_completed"] <= hi
        and cc >= GATES["min_completed_correct"]
        and ci >= GATES["min_completed_incorrect"])
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--limit", type=int, help="task cap for smoke runs")
    args = ap.parse_args()

    import os
    src = str(ROOT)
    existing = os.environ.get("PYTHONPATH", "")
    if src not in existing.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            src + (os.pathsep + existing if existing else ""))

    tasks = [generate(family, band, i)
             for family in BANDS
             for band in range(1, len(BANDS[family]) + 1)
             for i in range(TASKS_PER_BAND)]
    done = set()
    if ROWS_OUT.exists():
        done = {json.loads(l)["task_id"]
                for l in ROWS_OUT.read_text().splitlines()}
    todo = [t for t in tasks if t["task_id"] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"[jlens] M38E sweep: {len(done)} done, {len(todo)} to go "
          f"(override_hash={override_hash()})", flush=True)

    if todo:
        llm = make_llm(args.model_ref)
        install(llm)
        with ROWS_OUT.open("a") as sink:
            for i, task in enumerate(todo, start=1):
                record, timings = timed_generation(
                    llm, task["prompt"], OUTPUT_CAP)
                v = verdict(task, record["text"])
                row = {
                    "task_id": task["task_id"], "family": task["family"],
                    "band": task["band"],
                    "verdict": v,
                    "truncated": record["truncated"],
                    "output_tokens": record["output_tokens"],
                    "prompt_rows": record["prompt_rows"],
                    "generation_s": round(timings["generation_s"], 2),
                    "features": record["features"],
                    "output_text": record["text"],
                }
                row["classification"] = classify(row)
                sink.write(json.dumps(row) + "\n")
                sink.flush()
                if i % 8 == 0:
                    print(f"[jlens] M38E sweep {len(done) + i}/"
                          f"{len(done) + len(todo)} done", flush=True)

    rows = [json.loads(l) for l in ROWS_OUT.read_text().splitlines()]
    by_band: dict[str, list] = {}
    for r in rows:
        by_band.setdefault(f"{r['family']}:{r['band']}", []).append(r)
    bands_report = {key: band_stats(v) for key, v in sorted(by_band.items())}
    eligible_families = {key.split(":")[0]
                         for key, s in bands_report.items() if s["eligible"]}
    total_ci = sum(s["completed_incorrect"] for s in bands_report.values())
    gates_ok = (len(eligible_families) >= OVERALL["min_eligible_families"]
                and total_ci >= OVERALL["min_completed_incorrect"])
    complete = len(rows) >= len(tasks)

    payload = {
        "schema_version": 1,
        "run_kind": "m38e_dev_sweep",
        "manifest": "reports/telemetry/m38e_dev_manifest.json",
        "sweep_complete": complete,
        "rows_captured": len(rows),
        "rows_planned": len(tasks),
        "bands": bands_report,
        "eligible_families": sorted(eligible_families),
        "completed_incorrect_total": total_ci,
        "overall_gates_passed": bool(gates_ok),
        "outcome": ("eligible" if gates_ok and complete else
                    "m38e_completed_error_frontier_not_found"
                    if complete else "in_progress"),
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate band stats only; rows private",
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M38E sweep report: complete={complete} "
          f"eligible_families={sorted(eligible_families)} "
          f"ci_total={total_ci} gates={gates_ok}", flush=True)
    return 0 if (not complete or gates_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
