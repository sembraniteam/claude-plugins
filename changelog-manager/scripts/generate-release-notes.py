#!/usr/bin/env python3

import re
import sys
from pathlib import Path

CHANGELOG = Path("CHANGELOG.md")

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

MIN_INTRO_CHARS = 100
MAX_ITEMS = 6


def latest_release_block(text: str) -> str:
    parts = re.split(r"\n## ", text)
    for part in parts[1:]:
        if re.match(r"\[v?\d+\.\d+\.\d+\]", part):
            return "## " + part
    raise RuntimeError("No release section found in CHANGELOG.md")


def extract_by_category(block: str) -> dict:
    categories = {}
    current = None
    for line in block.splitlines():
        m = re.match(r"^###\s+(.*)", line)
        if m:
            current = m.group(1).strip().lower()
            categories[current] = []
            continue
        m = re.match(r"^- (.+)", line)
        if m and current:
            text = re.sub(r"\s*\(#\d+\)", "", m.group(1))
            categories[current].append(text)
    return categories


def auto_extract(categories: dict) -> list:
    order = ["breaking", "added", "changed", "fixed", "reverted"]
    items = []
    for cat in order:
        items.extend(categories.get(cat, []))
    return items


def clean_items(raw: list) -> list:
    items = []
    for line in raw:
        line = re.sub(r"^\d+\.\s*|^[-*•]\s*", "", line.strip())
        line = re.sub(r"\.$", "", line).strip()
        if line:
            items.append(line[0].upper() + line[1:])
    return items


def build_section(intro: str, items: list, max_chars, outro: str = "") -> str:
    intro = intro.strip()
    if len(intro) < MIN_INTRO_CHARS:
        raise RuntimeError(
            f"Intro must be at least {MIN_INTRO_CHARS} chars (got {len(intro)}). "
            "Write a fuller opening sentence."
        )
    if not items:
        raise RuntimeError("At least one item is required.")

    text = intro + "\n\n" + "\n".join(f"- {i}" for i in items[:MAX_ITEMS])
    if outro:
        text += "\n\n" + outro.strip()

    if max_chars and len(text) > max_chars:
        raise RuntimeError(
            f"Exceeds {max_chars} char limit (got {len(text)}). "
            "Shorten intro, remove outro, or reduce items."
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
            current = {"code": argv[i + 1], "intro": "", "items": [], "outro": ""}
            langs.append(current)
            i += 2
        elif arg in ("--intro", "--outro"):
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
            i += 1
    if not langs:
        raise RuntimeError("At least one --lang block is required.")
    return platform, langs


def main():
    if not CHANGELOG.exists():
        raise FileNotFoundError("CHANGELOG.md not found")

    platform, langs_input = parse_args(sys.argv[1:])
    max_chars = PLATFORM_LIMITS[platform]
    output = PLATFORM_OUTPUT[platform]

    changelog_text = CHANGELOG.read_text()
    latest = latest_release_block(changelog_text)
    categories = extract_by_category(latest)

    content = f"# Release Notes — {PLATFORM_LABELS[platform]}\n\n"

    for lang in langs_input:
        if lang["items"]:
            items = clean_items(lang["items"])
        else:
            items = clean_items(auto_extract(categories))

        section = build_section(lang["intro"], items, max_chars, lang.get("outro", ""))
        content += f"## {lang['code'].upper()}\n{section}\n\n"

    output.write_text(content.strip())
    limit_info = f"{max_chars} chars/lang" if max_chars else "no char limit"
    print(f"Written: {output} [{PLATFORM_LABELS[platform]}, {limit_info}]")


if __name__ == "__main__":
    main()
