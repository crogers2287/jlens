"""M32 secondary descriptive report: per-band frozen-trigger performance.

Non-confirmatory. Reads the private M32 repair rows locally and emits an
aggregate-only per-band summary of the frozen M30 trigger (precision/recall,
original fail rate, rescue counts) required descriptively by steer.md after
the M32P distribution-shift finding. No task text, ids, expressions, or
per-task predictions are written. Does not alter the frozen M32 evaluation.
"""
import argparse
import json
from pathlib import Path

THRESHOLD = 0.5
ALLOWED_KEYS = {
    "band", "n_tasks", "original_fail_count", "trigger_count",
    "trigger_true_positives", "trigger_false_alarms", "trigger_precision",
    "trigger_recall", "resample_rescues", "bundle_rescues",
}


def band_summary(rows):
    bands = {}
    for row in rows:
        b = bands.setdefault(row["band"], {
            "n_tasks": 0, "original_fail_count": 0, "trigger_count": 0,
            "trigger_true_positives": 0, "trigger_false_alarms": 0,
            "resample_rescues": 0, "bundle_rescues": 0,
        })
        b["n_tasks"] += 1
        fail = not row["original_pass"]
        triggered = row["p_fail"] >= THRESHOLD
        b["original_fail_count"] += fail
        b["trigger_count"] += triggered
        b["trigger_true_positives"] += triggered and fail
        b["trigger_false_alarms"] += triggered and not fail
        if fail and triggered:
            candidates = row["candidates"]
            if candidates.get("resample_t07", {}).get("pass"):
                b["resample_rescues"] += 1
            if any(candidates.get(name, {}).get("pass")
                   for name in ("independent_deliberate",
                                "checker_guided_repair",
                                "diagnose_then_repair")):
                b["bundle_rescues"] += 1
    out = []
    for band in sorted(bands):
        b = bands[band]
        out.append({
            "band": band, **b,
            "trigger_precision": (b["trigger_true_positives"]
                                  / b["trigger_count"])
            if b["trigger_count"] else None,
            "trigger_recall": (b["trigger_true_positives"]
                               / b["original_fail_count"])
            if b["original_fail_count"] else None,
        })
    return out


def check_no_text(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key not in ALLOWED_KEYS and not isinstance(value, (list, dict)):
                raise ValueError(f"unexpected key in band descriptives: {key}")
            check_no_text(value)
    elif isinstance(node, list):
        for item in node:
            check_no_text(item)
    elif isinstance(node, str) and node not in (
            "band_1", "band_2", "band_3", "band_4", "band_5", "band_6"):
        raise ValueError(f"unexpected string value: {node!r}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rows",
                    default="reports/shadow/private/m32_repair_rows_local.jsonl")
    ap.add_argument("--out",
                    default="reports/telemetry/hf_m32_band_descriptives.json")
    args = ap.parse_args(argv)

    rows = [json.loads(line) for line in Path(args.rows).read_text()
            .splitlines() if line]
    per_band = band_summary(rows)
    check_no_text(per_band)
    payload = {
        "schema_version": 1,
        "run_kind": "m32_band_descriptives_secondary",
        "confirmatory": False,
        "note": ("descriptive per-band frozen-trigger metrics required by the "
                 "post-M32P steer; secondary and non-confirmatory"),
        "threshold_fail_probability": THRESHOLD,
        "bands": per_band,
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    for band in per_band:
        print(f"[jlens] {band['band']}: n={band['n_tasks']} "
              f"fail={band['original_fail_count']} "
              f"precision={band['trigger_precision']} "
              f"recall={band['trigger_recall']}")
    print(f"[jlens] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
