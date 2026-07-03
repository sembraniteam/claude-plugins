#!/usr/bin/env python3
"""
PostToolUse hook: check recently written/edited files for high-risk security patterns.
Conservative — skips test files, markdown, and config. Only fires on clear signals.
Receives Claude tool call data as JSON on stdin.
"""
import json
import os
import re
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""

    if not file_path or not os.path.isfile(file_path):
        sys.exit(0)

    # Skip non-source files
    skip_ext = re.compile(
        r"\.(md|txt|json|yaml|yml|toml|lock|env\.example|gitignore|dockerignore|css|svg|png|jpg|gif|ico)$",
        re.IGNORECASE,
    )
    skip_path = re.compile(r"[/\\](test|tests|spec|specs|__tests__|__pycache__|node_modules)[/\\]", re.IGNORECASE)

    if skip_ext.search(file_path) or skip_path.search(file_path):
        sys.exit(0)

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        sys.exit(0)

    warnings = []

    # CWE-89: SQL injection — string concatenation into query-like patterns
    if re.search(
        r'(?:query|sql|execute|cursor\.execute)\s*[=(]\s*[f"\'`].*(?:\+|{)\s*\w',
        content, re.IGNORECASE | re.MULTILINE
    ):
        warnings.append("SQL injection risk (CWE-89): query built with string concatenation")

    # CWE-94: eval() with a non-literal argument
    if re.search(r'\beval\s*\(\s*(?!["\'`])', content):
        warnings.append("eval() with dynamic input (CWE-94)")

    # CWE-78: OS command execution — flag os.system (always uses shell) and
    # subprocess with shell=True (the dangerous form); list-arg subprocess calls are safe
    if re.search(r'\bos\.system\s*\(|subprocess\.[a-z_]+\s*\([^)]*shell\s*=\s*True', content):
        warnings.append("OS command execution (CWE-78): ensure arguments are not user-controlled")

    # CWE-798: hardcoded credential-like strings (8+ chars, not a placeholder)
    if re.search(
        r'''(?:password|passwd|secret|api_key|apikey|token|auth_token|private_key)\s*=\s*['"][A-Za-z0-9+/=_\-!@#$%^&*]{8,}['"]''',
        content, re.IGNORECASE,
    ):
        warnings.append("possible hardcoded credential (CWE-798)")

    # CWE-502: insecure deserialization
    if re.search(r'\bpickle\.loads?\b|\byaml\.load\s*\((?!.*Loader)', content):
        warnings.append("unsafe deserialization (CWE-502): pickle.load or yaml.load without SafeLoader")

    if warnings:
        basename = os.path.basename(file_path)
        print(f"\n⚠️  security-auditor: {basename}")
        for w in warnings:
            print(f"   • {w}")
        print(f"   Run: /audit-file {file_path}\n")


if __name__ == "__main__":
    main()
