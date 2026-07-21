#!/usr/bin/env python3
"""
Pre-flight completeness and structural check for
docs/architecture-designer/session.json.

Three layers, in order:

1. Completeness — schemaVersion, project, description, and stages 1-5 are
   present and non-empty. "Non-empty" is checked recursively: a stage object
   whose only field is an empty string (e.g. {"backend": ""}) is treated as
   empty, not as a passing non-empty dict.
2. Structural schema — every other key present in the file (agentTools,
   pending, progress, lld, documents, remediationPlans, implementationPlans)
   is checked against session-schema.json, a JSON Schema sitting alongside
   this script. That file is the single source of truth for the fixed-shape
   parts of session.json (array-of-objects-or-legacy-string entries, the
   split object, enums); this script applies it with a small purpose-built
   subset of JSON Schema keywords (type/properties/required/items/oneOf/
   enum/minimum) rather than a third-party validator, to stay stdlib-only.
3. Referential integrity (advisory, non-blocking) — link fields between
   documents/remediationPlans/implementationPlans (document, remediationPlan,
   supersedes, split.previousPlan/nextPlan) are checked for whether they
   resolve to a path present elsewhere in the file. A mismatch is printed as
   a warning, not a failure: some links (e.g. a fresh remediationPlans
   entry's `document` field) legitimately point at a document not yet
   appended to `documents[]`, since review/SKILL.md step 4e saves the
   remediation plan before step 4f saves the document it targets. Warnings
   surface possible drift for a human to investigate without risking a false
   hard-block on a legitimate in-flight state.

Only layers 1 and 2 affect the exit code — layer 3 is always advisory.

Usage: python3 scripts/validate-session.py

Exit 0 -> completeness check passed and no schema violations found.
Exit 1 -> a required field/stage is missing or empty, a schema violation
          was found, the file can't be read, or its contents aren't a JSON
          object (e.g. valid JSON but the wrong top-level shape, such as an
          array or a bare string).
"""

import json
import sys
from pathlib import Path

SESSION_PATH = Path.cwd() / "docs" / "architecture-designer" / "session.json"
SCHEMA_PATH = Path(__file__).resolve().parent / "session-schema.json"

REQUIRED_STAGES = ["stage1", "stage2", "stage3", "stage4", "stage5"]
REQUIRED_TOP_LEVEL = ["schemaVersion", "project", "description"]


def is_empty(val):
    """Recursively empty: None, blank/whitespace-only string, or a dict/list
    that is either literally empty or whose every value is itself empty
    under this same definition. A bool or number is never empty."""
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip() == ""
    if isinstance(val, dict):
        return len(val) == 0 or all(is_empty(v) for v in val.values())
    if isinstance(val, list):
        return len(val) == 0 or all(is_empty(v) for v in val)
    return False


# --- Layer 2: minimal JSON Schema subset applier -----------------------

def validate_type(value, type_spec):
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    for t in types:
        if t == "null" and value is None:
            return True
        if t == "string" and isinstance(value, str):
            return True
        if t == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if t == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if t == "boolean" and isinstance(value, bool):
            return True
        if t == "object" and isinstance(value, dict):
            return True
        if t == "array" and isinstance(value, list):
            return True
    return False


def schema_matches(value, schema):
    probe = []
    validate_node(value, schema, "$", probe)
    return len(probe) == 0


def validate_node(value, schema, path, errors):
    if "oneOf" in schema:
        matches = [s for s in schema["oneOf"] if schema_matches(value, s)]
        if len(matches) != 1:
            errors.append(f"{path}: value does not match exactly one allowed shape ({len(matches)} matched)")
            return
        validate_node(value, matches[0], path, errors)
        return

    if "enum" in schema:
        if value not in schema["enum"]:
            errors.append(f"{path}: {value!r} is not one of the allowed values {schema['enum']}")
            return

    if "type" in schema and not validate_type(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(value).__name__}")
        return

    if isinstance(value, dict):
        for required_key in schema.get("required", []):
            if required_key not in value:
                errors.append(f"{path}: missing required key '{required_key}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in value:
                validate_node(value[key], subschema, f"{path}.{key}", errors)

    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            validate_node(item, schema["items"], f"{path}[{i}]", errors)

    if "minimum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema["minimum"]:
            errors.append(f"{path}: {value} is below minimum {schema['minimum']}")


def run_schema_check(session):
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except OSError as err:
        return [f"could not read session-schema.json: {err}"]
    except json.JSONDecodeError as err:
        return [f"session-schema.json is not valid JSON: {err}"]

    errors = []
    validate_node(session, schema, "$", errors)
    return errors


# --- Layer 3: referential integrity between arrays (advisory) ----------

def normalize_entries(raw):
    """Tolerant-read: a legacy bare-string entry becomes {"path": <string>}.
    A value that isn't a list at all (wrong type, e.g. `"documents": true`)
    normalizes to no entries -- the schema check above already reports the
    type violation and fails the gate; this just keeps layer 3 from crashing
    on a shape layer 2 already rejected."""
    out = []
    for entry in raw if isinstance(raw, list) else []:
        if isinstance(entry, str):
            out.append({"path": entry})
        elif isinstance(entry, dict):
            out.append(entry)
    return out


def entry_label(entry):
    return entry.get("path") or '(entry missing "path")'


def check_links(session):
    warnings = []

    documents = normalize_entries(session.get("documents"))
    remediation = normalize_entries(session.get("remediationPlans"))
    implementation = normalize_entries(session.get("implementationPlans"))

    doc_paths = {d["path"] for d in documents if "path" in d}
    remediation_paths = {r["path"] for r in remediation if "path" in r}
    implementation_paths = {p["path"] for p in implementation if "path" in p}

    for r in remediation:
        doc = r.get("document")
        if doc and doc not in doc_paths:
            warnings.append(
                f"remediationPlans[{entry_label(r)}]: document '{doc}' not found in documents[] "
                "(may simply not be saved yet — a remediation plan's document field is written "
                "before the document itself in the review flow)"
            )
        sup = r.get("supersedes")
        if sup and sup not in remediation_paths:
            warnings.append(f"remediationPlans[{entry_label(r)}]: supersedes '{sup}', which is not present in remediationPlans[]")

    for p in implementation:
        doc = p.get("document")
        if doc and doc not in doc_paths:
            warnings.append(f"implementationPlans[{entry_label(p)}]: document '{doc}' not found in documents[]")
        rem = p.get("remediationPlan")
        if rem and rem not in remediation_paths:
            warnings.append(f"implementationPlans[{entry_label(p)}]: remediationPlan '{rem}' not found in remediationPlans[]")
        sup = p.get("supersedes")
        if sup and sup not in implementation_paths:
            warnings.append(f"implementationPlans[{entry_label(p)}]: supersedes '{sup}', which is not present in implementationPlans[]")

        split = p.get("split")
        if isinstance(split, dict):
            part, total = split.get("part"), split.get("total")
            if isinstance(part, int) and isinstance(total, int) and not (1 <= part <= total):
                warnings.append(f"implementationPlans[{entry_label(p)}]: split.part={part} out of range for split.total={total}")
            for neighbor_key in ("previousPlan", "nextPlan"):
                neighbor = split.get(neighbor_key)
                if neighbor and neighbor not in implementation_paths:
                    warnings.append(f"implementationPlans[{entry_label(p)}]: split.{neighbor_key} '{neighbor}' not found in implementationPlans[]")

    return warnings


def main():
    # Force UTF-8 output regardless of the console's active code page --
    # without this, the box-drawing/status glyphs below can raise
    # UnicodeEncodeError and crash on a legacy-code-page Windows console.
    # reconfigure() exists on real text streams; guard it for the rare case
    # stdout/stderr have been replaced with something that lacks it.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, ValueError, OSError):
                pass

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

    if not isinstance(session, dict):
        sys.stderr.write(
            f"\nERROR: session.json must contain a JSON object at the top level, "
            f"got {type(session).__name__}\n\n"
        )
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
    sys.stdout.write("Structural Schema Check\n")
    schema_errors = run_schema_check(session)
    if schema_errors:
        any_failed = True
        for err in schema_errors:
            sys.stdout.write(f"  ✗  {err}\n")
    else:
        sys.stdout.write("  ✓  all present keys match session-schema.json\n")

    link_warnings = check_links(session)
    if link_warnings:
        sys.stdout.write(f"{line}\n")
        sys.stdout.write("Referential Integrity (advisory — does not fail the gate)\n")
        for warning in link_warnings:
            sys.stdout.write(f"  ⚠  {warning}\n")

    sys.stdout.write(f"{line}\n")
    if any_failed:
        sys.stdout.write(
            "SESSION CHECK FAILED — complete the missing fields/stages, or fix the schema "
            "violation(s) above, before continuing.\n\n"
        )
        sys.exit(1)
    else:
        sys.stdout.write(
            "SESSION CHECK PASSED — all required fields and stages are present, and "
            "session.json's structure matches session-schema.json.\n\n"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
