"""M36T Phase 0: budget-frontier feasibility from frozen M36C rows only.

Per steer 79878ab, candidate cells for pre-truncation routing are
identified purely from existing M36C calibration evidence — no new
capture. Gates:

  1. at least two task families with useful budget variation;
  2. pooled `needs_more_than_512_tokens` prevalence in [.20, .80]
     over the candidate families;
  3. most long-cap completions verifiable by the deterministic verifier;
  4. no cell selected for favorability: the selection rule is fixed
     here as "exclude only families with no budget variation
     (prevalence 1.0 or 0.0 at 512)" — nothing else.

Output is aggregate family-level stats only.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

OUT = "reports/telemetry/m36t_phase0_feasibility.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    from m36c_adaptive import load_original_rows, load_new_rows

    rows = load_original_rows() + load_new_rows()
    by_task = collections.defaultdict(list)
    for r in rows:
        by_task[r["task_id"]].append(r)

    fam = collections.defaultdict(
        lambda: {"tasks_at_512": 0, "needs_more_than_512": 0,
                 "rescued_completed": 0, "rescue_attempted": 0,
                 "rescued_verified_pass": 0})
    for trs in by_task.values():
        at512 = [r for r in trs if r["budget"] == 512]
        if not at512:
            continue
        s = fam[trs[0]["family"]]
        s["tasks_at_512"] += 1
        needs = at512[0]["classification"] == "truncated_budget"
        longs = [r for r in trs if r["budget"] > 512]
        if needs:
            s["needs_more_than_512"] += 1
            if longs:
                s["rescue_attempted"] += 1
                done = [r for r in longs
                        if r["classification"] != "truncated_budget"]
                if done:
                    s["rescued_completed"] += 1
                    if any(r["verdict"] == "pass" for r in done):
                        s["rescued_verified_pass"] += 1

    families = {}
    for name, s in sorted(fam.items()):
        prevalence = s["needs_more_than_512"] / s["tasks_at_512"]
        families[name] = {**s, "prevalence": round(prevalence, 3),
                          "has_budget_variation": 0.0 < prevalence < 1.0}

    candidates = [n for n, f in families.items() if f["has_budget_variation"]]
    pool_needs = sum(families[n]["needs_more_than_512"] for n in candidates)
    pool_tasks = sum(families[n]["tasks_at_512"] for n in candidates)
    pool_prev = pool_needs / pool_tasks if pool_tasks else 0.0
    rescued = sum(families[n]["rescued_completed"] for n in candidates)
    rescued_pass = sum(families[n]["rescued_verified_pass"]
                       for n in candidates)

    gates = {
        "two_plus_families_with_budget_variation": len(candidates) >= 2,
        "pooled_prevalence_in_20_80": 0.20 <= pool_prev <= 0.80,
        "long_cap_completions_verifiable": (
            rescued > 0 and rescued_pass / rescued >= 0.5),
        "selection_rule_fixed_not_favorability": True,
    }
    payload = {
        "schema_version": 1,
        "run_kind": "m36t_phase0_feasibility",
        "steer": "79878ab",
        "source": "frozen M36C calibration rows (aggregates only; no new capture)",
        "label_definition": "needs_more_than_512_tokens := truncated_budget at the 512 probe",
        "families": families,
        "candidate_families": candidates,
        "pooled_prevalence": round(pool_prev, 3),
        "pooled_needs_over_tasks": f"{pool_needs}/{pool_tasks}",
        "rescued_completed_verified_pass": f"{rescued_pass}/{rescued}",
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate family stats only",
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36T phase0: candidates={candidates} "
          f"prevalence={pool_prev:.3f} gates={gates}", flush=True)
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
