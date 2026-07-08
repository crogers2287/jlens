#!/usr/bin/env python3
"""Validate a JSONL file line-by-line against a JSON Schema (draft-07).

Prints the count of valid records; exits nonzero on the first invalid line
(with the line number and the validation error). Used to gate decode exports
against schema/v2_decode.json.

CLI:
  python src/validate_jsonl_schema.py \
      --schema schema/v2_decode.json --jsonl reports/schema/r4_decode.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schema", required=True)
    ap.add_argument("--jsonl", required=True)
    args = ap.parse_args(argv)

    from jsonschema import Draft7Validator

    schema = json.loads(Path(args.schema).read_text())
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    n = 0
    with open(args.jsonl, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            errs = sorted(validator.iter_errors(obj), key=lambda e: e.path)
            if errs:
                e = errs[0]
                print(f"[jlens] INVALID line {lineno}: {e.message} "
                      f"(path: {list(e.path)})", file=sys.stderr)
                return 1
            n += 1
    print(f"[jlens] {n} records valid against {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
