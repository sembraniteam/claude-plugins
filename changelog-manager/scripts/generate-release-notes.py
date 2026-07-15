#!/usr/bin/env python3

import re
import sys
from pathlib import Path

PLATFORM_LIMITS = {
    "appstore": 4000,
    "playstore": 500,
    "web": None,
}

PLATFORM_OUTPUT = {
    "appstore": Path("RELEASE_NOTES_APPSTORE"),
    "playstore": Path("RELEASE_NOTES_PLAYSTORE"),
    "web": Path("RELEASE_NOTES"),
}

PLATFORM_LABELS = {
    "appstore": "App Store",
    "playstore": "Play Store",
    "web": "Web",
}

MIN_SUMMARY_CHARS = 100
MAX_ITEMS = 6


def clean_items(raw: list) -> list:
    items = []
    for line in raw:
        line = re.sub(r"^\d+\.\s*|^[-*•]\s*", "", line.strip())
        line = re.sub(r"\.$", "", line).strip()
        if line:
            items.append(line[0].upper() + line[1:])
    return items


def build_section(summary: str, items: list, max_chars, outro: str = "") -> str:
    summary = summary.strip()
    if len(summary) < MIN_SUMMARY_CHARS:
        raise RuntimeError(
            f"Summary must be at least {MIN_SUMMARY_CHARS} chars (got {len(summary)}). "
            "Write a fuller opening sentence."
        )
    if len(items) > MAX_ITEMS:
        dropped = items[MAX_ITEMS:]
        print(f"Warning: dropped {len(dropped)} item(s) beyond the {MAX_ITEMS}-item cap: "
              f"{'; '.join(dropped)}", file=sys.stderr)

    text = summary
    if items:
        text += "\n\n" + "\n".join(f"- {i}" for i in items[:MAX_ITEMS])
    if outro:
        text += "\n\n" + outro.strip()

    if max_chars and len(text) > max_chars:
        raise RuntimeError(
            f"Exceeds {max_chars} char limit (got {len(text)}). "
            "Shorten the summary, remove outro, or reduce items."
        )
    return text


def parse_args(argv: list):
    platform = "web"
    langs = []
    current = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--platform":
            platform = argv[i + 1].lower()
            if platform not in PLATFORM_LIMITS:
                raise RuntimeError(f"Unknown platform '{platform}'. Valid: {', '.join(PLATFORM_LIMITS)}")
            i += 2
        elif arg == "--lang":
            current = {"code": argv[i + 1], "summary": "", "items": [], "outro": ""}
            langs.append(current)
            i += 2
        elif arg in ("--summary", "--outro"):
            if not current:
                raise RuntimeError(f"{arg} must come after --lang")
            current[arg[2:]] = argv[i + 1]
            i += 2
        elif arg == "--item":
            if not current:
                raise RuntimeError("--item must come after --lang")
            current["items"].append(argv[i + 1])
            i += 2
        else:
            raise RuntimeError(f"Unknown argument '{arg}'.")
    if not langs:
        raise RuntimeError("At least one --lang block is required.")
    return platform, langs


def main():
    platform, langs_input = parse_args(sys.argv[1:])
    max_chars = PLATFORM_LIMITS[platform]
    output = PLATFORM_OUTPUT[platform]

    content = f"# Release Notes — {PLATFORM_LABELS[platform]}\n\n"

    for lang in langs_input:
        items = clean_items(lang["items"]) if lang["items"] else []
        section = build_section(lang["summary"], items, max_chars, lang.get("outro", ""))
        content += f"## {lang['code'].upper()}\n{section}\n\n"

    output.write_text(content.strip(), encoding="utf-8")
    limit_info = f"{max_chars} chars/lang" if max_chars else "no char limit"
    print(f"Written: {output} [{PLATFORM_LABELS[platform]}, {limit_info}]")


if __name__ == "__main__":
    main()
