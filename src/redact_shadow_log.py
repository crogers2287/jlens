#!/usr/bin/env python3
"""Redact a shadow / outcome JSONL for safe sharing (M9).

Replaces the three free-text fields — prompt_preview, output_preview,
outcome.notes — with '[redacted]' (or, with --hash, a stable non-reversible
hash tag). KEEPS all structural fields: prompt_id, policy (level /
recommended_action / scores / explanation), policy_note, mode, outcome
booleans, review_meta. The output carries NO original prompt/output/notes text.

CLI:
  python src/redact_shadow_log.py \
      --in reports/shadow/private/realuse_local.jsonl \
      --out reports/shadow/private/realuse_local.redacted.jsonl [--hash]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TEXT_FIELDS = ["prompt_preview", "output_preview"]  # top-level free text
REDACTED = "[redacted]"


def _hash_tag(s: str) -> str:
    """Stable non-reversible short tag (no secrets, no original text)."""
    h = 0
    for ch in str(s):
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return f"[redacted:{h:08x}]"


def redact_record(rec: dict, use_hash: bool = False) -> dict:
    out = dict(rec)
    for f in TEXT_FIELDS:
        if out.get(f) not in (None, ""):
            out[f] = _hash_tag(out[f]) if use_hash else REDACTED
    # outcome.notes is free text
    oc = out.get("outcome")
    if isinstance(oc, dict) and oc.get("notes") not in (None, ""):
        oc = dict(oc)
        oc["notes"] = _hash_tag(oc["notes"]) if use_hash else REDACTED
        out["outcome"] = oc
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hash", action="store_true",
                    help="tag with a stable non-reversible hash instead of a flat "
                         "[redacted]")
    args = ap.parse_args(argv)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for line in open(args.inp, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            fh.write(json.dumps(redact_record(json.loads(line), args.hash)) + "\n")
            n += 1
    print(f"[jlens] redacted {n} records (prompt/output/notes scrubbed) -> {out}")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
