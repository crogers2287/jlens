#!/usr/bin/env python3
"""M35 campaign extraction: telemetry, verdicts, features per task (CPU)."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import action_executor as EXEC  # noqa: E402
from hf_telemetry_backend import HFTelemetryBackend  # noqa: E402
import m23_within_model as M23  # noqa: E402
import m26_objective_error as M26  # noqa: E402
import m32_structured_repair as M32  # noqa: E402
import m35_campaign as M35  # noqa: E402


def bandless_features(telemetry):
    """M26 scalar feature vector; family indicators are added at fit time."""
    row = {}
    for name, getter in M26.FEATURES.items():
        value = getter(telemetry)
        if value is None:
            raise ValueError(f"missing feature {name}")
        row[name] = float(value)
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest",
                    default="data/prompts/m35_campaign_manifest.json")
    ap.add_argument("--tasks",
                    default="reports/shadow/private/m35_hf_prompts_local.jsonl")
    ap.add_argument("--captures-root", default="data/captures")
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--telemetry-out",
                    default="reports/shadow/private/"
                            "m35_hf_telemetry_records_local.jsonl")
    ap.add_argument("--rows-out",
                    default="reports/shadow/private/m35_campaign_rows_local.jsonl")
    ap.add_argument("--summary-out",
                    default="reports/telemetry/hf_m35_campaign_run_summary.json")
    args = ap.parse_args(argv)

    manifest = M35.load_manifest(args.manifest)
    tasks = [json.loads(line) for line in
             Path(args.tasks).read_text().splitlines() if line]
    if len(tasks) != manifest["n_tasks_total"]:
        raise ValueError("M35 tasks file does not match the manifest")

    import torch
    from jsonschema import Draft7Validator
    telemetry_schema = Draft7Validator(json.loads(Path(
        "schema/hf_telemetry_record_v1.json").read_text()))
    backend = HFTelemetryBackend(
        model_ref=args.model_ref, source_kind="local_path", top_k=5)
    adapter = EXEC.FixtureRetrievalAdapter({
        "*": {"source_kind": "public_fixture",
              "context": "M35 controlled local fixture context",
              "confidence": 0.8}})
    cfg = M23._qwen_config()
    root = Path(args.captures_root)

    telemetry_rows, rows = [], []
    undecided = Counter()
    capped = 0
    for index, task in enumerate(tasks):
        path = root / M35.CAPTURE_DIR / f"{task['prompt_id']}.pt"
        if not path.exists():
            raise FileNotFoundError(f"missing M35 capture: {task['prompt_id']}")
        original = torch.load(path, map_location="cpu", weights_only=False)
        telemetry, _runtime, action, result = M23.process_same_capture(
            task, original, backend, cfg=cfg, retrieval_adapter=adapter)
        errors = list(telemetry_schema.iter_errors(telemetry))
        if errors:
            raise ValueError(
                f"invalid telemetry for {task['prompt_id']}: "
                f"{errors[0].message}")
        telemetry_rows.append(telemetry)
        capped += telemetry["decode_step_count"] == 64
        original_verdict = M32.verdict_for(
            original.get("generated_output"), task)
        if original_verdict == "undecided":
            undecided[task["family"]] += 1
            continue
        tool_verdict = M32.verdict_for(task["known_answer"], task)
        rows.append({
            "task_id": task["prompt_id"],
            "family": task["family"],
            "stratum": task["stratum"],
            "split": task["split"],
            "original_pass": original_verdict == "pass",
            "tool_pass": tool_verdict == "pass",
            "features": bandless_features(telemetry),
        })
        if (index + 1) % 256 == 0:
            print(f"[jlens] M35 extract progress {index + 1}/{len(tasks)}",
                  flush=True)

    Path(args.telemetry_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.telemetry_out).write_text(
        "".join(json.dumps(row) + "\n" for row in telemetry_rows))
    Path(args.rows_out).write_text(
        "".join(json.dumps(row) + "\n" for row in rows))

    by_family_fail = {}
    for family in manifest["families"]:
        fid = family["family_id"]
        family_rows = [r for r in rows if r["family"] == fid]
        by_family_fail[fid] = {
            "n_rows": len(family_rows),
            "fail_rate": (sum(1 for r in family_rows
                              if not r["original_pass"]) / len(family_rows))
            if family_rows else None,
            "predicted_regime": family["predicted_regime"],
        }
    summary = {
        "schema_version": 1,
        "run_kind": "m35_campaign_dataset",
        "n_tasks": len(tasks),
        "n_rows_extracted": len(rows),
        "undecided_excluded_counts": dict(undecided),
        "original_decode_cap_reached_count": capped,
        "family_fail_rates_descriptive": by_family_fail,
        "split_row_counts": dict(Counter(r["split"] for r in rows)),
        "per_task_labels_or_predictions_persisted_publicly": False,
        "raw_text_token_tensor_or_path_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only campaign extraction summary",
    }
    Path(args.summary_out).write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[jlens] M35 extract: {len(rows)} rows; "
          f"undecided={sum(undecided.values())}; "
          f"family fail rates="
          f"{ {k: round(v['fail_rate'], 3) if v['fail_rate'] is not None else None for k, v in by_family_fail.items()} }",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
