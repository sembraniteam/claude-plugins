#!/usr/bin/env python3
"""
Pre-flight completeness check for docs/architecture-designer/session.json.
Verifies that schemaVersion, project, description, and stages 1-5 have been
confirmed and written before Stage 6 begins.
Usage: python3 scripts/validate-session.py

Exit 0 -> all required fields and stages present and non-empty.
Exit 1 -> one or more required fields or stages missing or empty.
"""

import json
import sys
from pathlib import Path

SESSION_PATH = Path.cwd() / "docs" / "architecture-designer" / "session.json"

REQUIRED_STAGES = ["stage1", "stage2", "stage3", "stage4", "stage5"]
REQUIRED_TOP_LEVEL = ["schemaVersion", "project", "description"]


def is_empty(val):
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip() == ""
    if isinstance(val, (dict, list)):
        return len(val) == 0
    return False


def main():
    try:
        raw = SESSION_PATH.read_text(encoding="utf-8")
    except OSError as err:
        sys.stderr.write(f"\nERROR: Cannot read {SESSION_PATH}\n  {err}\n")
        sys.stderr.write("Complete stages 1-5 of the design workflow first.\n\n")
        sys.exit(1)

    try:
        session = json.loads(raw)
    except json.JSONDecodeError as err:
        sys.stderr.write(f"\nERROR: session.json is not valid JSON\n  {err}\n\n")
        sys.exit(1)

    line = "─" * 60
    sys.stdout.write(f"\nSession Completeness Check\n{line}\n")
    sys.stdout.write(f"Source: {SESSION_PATH}\n{line}\n")

    any_failed = False

    for field in REQUIRED_TOP_LEVEL:
        if field not in session:
            sys.stdout.write(f"  ✗  {field} — missing\n")
            any_failed = True
        elif is_empty(session[field]):
            sys.stdout.write(f"  ✗  {field} — empty\n")
            any_failed = True
        else:
            sys.stdout.write(f"  ✓  {field}\n")

    for stage in REQUIRED_STAGES:
        if stage not in session:
            sys.stdout.write(f"  ✗  {stage} — missing\n")
            any_failed = True
        elif is_empty(session[stage]):
            sys.stdout.write(f"  ✗  {stage} — empty\n")
            any_failed = True
        else:
            sys.stdout.write(f"  ✓  {stage}\n")

    sys.stdout.write(f"{line}\n")
    if any_failed:
        sys.stdout.write(
            "SESSION CHECK FAILED — complete the missing fields/stages before starting Stage 6.\n\n"
        )
        sys.exit(1)
    else:
        sys.stdout.write(
            "SESSION CHECK PASSED — all required fields and stages are present.\n\n"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
