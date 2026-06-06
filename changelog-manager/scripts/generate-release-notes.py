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


def latest_release_block(text: str):
    parts = re.split(r"\n## ", text)
    for part in parts[1:]:
        if re.match(r"\[v?\d+\.\d+\.\d+\]", part):
            return "## " + part
    raise RuntimeError("No release section found in CHANGELOG.md")


def extract_changelog_by_category(block: str):
    categories = {}
    current = None

    for line in block.splitlines():
        header = re.match(r"^###\s+(.*)", line)
        if header:
            current = header.group(1).strip().lower()
            categories[current] = []
            continue

        item = re.match(r"^- (.+)", line)
        if item and current:
            text = re.sub(r"\s*\(#\d+\)", "", item.group(1))
            categories[current].append(text)

    return categories


def normalize_bullets(text: str):
    items = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"^\d+\.\s*", "", line)
        line = re.sub(r"^[-*]\s*", "", line)

        if line:
            items.append(line)

    return items


def lint_items(items):
    clean = []

    for item in items:
        item = item.strip()
        item = re.sub(r"\.$", "", item)
        item = item[0].upper() + item[1:] if item else item
        clean.append(item)

    return clean


def detect_item_category(item, categories):
    item_lower = item.lower()

    for cat, commits in categories.items():
        for commit in commits:
            if any(w in item_lower for w in commit.lower().split()):
                return cat

    return "other"


def rank_items(items, categories):
    priority = {
        "breaking": 1,
        "added": 2,
        "changed": 3,
        "fixed": 4,
        "reverted": 5,
        "other": 6,
    }

    ranked = []

    for item in items:
        cat = detect_item_category(item, categories)
        ranked.append((priority.get(cat, 6), item))

    ranked.sort(key=lambda x: x[0])

    return [i[1] for i in ranked]


def validate_against_changelog(items, categories):
    """
    Validates items against CHANGELOG entries by checking for shared words.
    Only applied to English items — non-English translations are skipped
    because CHANGELOG.md is written in English and word matching would fail
    for other languages.
    """
    changelog_items = []

    for commits in categories.values():
        changelog_items.extend(commits)

    changelog_lower = [c.lower() for c in changelog_items]

    valid = []

    for item in items:
        item_lower = item.lower()

        if any(word in item_lower for c in changelog_lower for word in c.split()):
            valid.append(item)

    return valid


def auto_extract_items(categories):
    priority_order = ["breaking", "added", "changed", "fixed", "reverted"]
    items = []
    for cat in priority_order:
        items.extend(categories.get(cat, []))
    return items


MIN_INTRO_CHARS = 100
MAX_ITEMS = 6


def build_section(intro, items, max_chars, outro=""):
    if not items:
        raise RuntimeError("Each language must contain at least one valid change.")

    intro = intro.strip()

    if len(intro) < MIN_INTRO_CHARS:
        raise RuntimeError(
            f"Intro must be at least {MIN_INTRO_CHARS} characters "
            f"(got {len(intro)}). Write a fuller opening sentence for general users."
        )

    text = intro + "\n\n"

    for item in items:
        text += f"- {item}\n"

    if outro:
        text += f"\n{outro.strip()}"

    text = text.strip()

    if max_chars is not None and len(text) > max_chars:
        raise RuntimeError(
            f"Section exceeds platform limit of {max_chars} characters "
            f"(got {len(text)}). Shorten your intro, remove the outro, or reduce items."
        )

    return text


def parse_args(argv):
    platform = "web"
    langs = []
    current = None

    i = 0
    while i < len(argv):
        arg = argv[i]

        if arg == "--platform":
            platform = argv[i + 1].lower()
            if platform not in PLATFORM_LIMITS:
                raise RuntimeError(
                    f"Unknown platform '{platform}'. "
                    f"Valid options: {', '.join(PLATFORM_LIMITS)}"
                )
            i += 2
            continue

        if arg == "--lang":
            current = {"code": argv[i + 1], "intro": "", "items": "", "outro": ""}
            langs.append(current)
            i += 2
            continue

        if arg == "--intro":
            if not current:
                raise RuntimeError("--intro must come after --lang")
            current["intro"] = argv[i + 1]
            i += 2
            continue

        if arg == "--items":
            if not current:
                raise RuntimeError("--items must come after --lang")
            current["items"] = argv[i + 1]
            i += 2
            continue

        if arg == "--outro":
            if not current:
                raise RuntimeError("--outro must come after --lang")
            current["outro"] = argv[i + 1]
            i += 2
            continue

        i += 1

    if not langs:
        raise RuntimeError("At least one --lang block is required")

    return platform, langs


def main():
    if not CHANGELOG.exists():
        raise FileNotFoundError("CHANGELOG.md not found")

    platform, langs_input = parse_args(sys.argv[1:])

    max_chars = PLATFORM_LIMITS[platform]
    output = PLATFORM_OUTPUT[platform]

    changelog_text = CHANGELOG.read_text()
    latest = latest_release_block(changelog_text)
    categories = extract_changelog_by_category(latest)

    platform_label = {
        "appstore": "App Store",
        "playstore": "Play Store",
        "web": "Web",
    }[platform]

    content = f"# Release Notes — {platform_label}\n\n"

    for lang_data in langs_input:
        code = lang_data["code"]
        intro = lang_data["intro"]
        items_raw = lang_data["items"]

        if items_raw.strip():
            items = normalize_bullets(items_raw)
            items = lint_items(items)
        else:
            items = lint_items(auto_extract_items(categories))

        if code.lower().split("_")[0] == "en":
            items = validate_against_changelog(items, categories)

        if not items:
            raise RuntimeError(f"{code} must contain at least one valid change")

        items = rank_items(items, categories)
        items = items[:MAX_ITEMS]
        outro = lang_data.get("outro", "")

        section = build_section(intro, items, max_chars, outro)

        content += f"## {code.upper()}\n{section}\n\n"

    output.write_text(content.strip())

    limit_info = f"{max_chars} chars/lang" if max_chars else "no char limit"
    print(f"RELEASE_NOTES generated: {output} [{platform_label}, {limit_info}]")


if __name__ == "__main__":
    main()
