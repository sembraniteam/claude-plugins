#!/usr/bin/env bash
set -e

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || true)

if [ -z "$LAST_TAG" ]; then
    LAST_TAG="v0.0.0"
    RANGE=""
else
    RANGE="$LAST_TAG..HEAD"
fi

# %x1f separates subject/body within a commit, %x1e terminates each commit
# record — both are non-printable and won't collide with real commit text.
RAW=$(git log $RANGE --pretty=format:"%s%x1f%b%x1e")

if [ -z "$RAW" ]; then
    echo "No changes since last release."
    exit 0
fi

VERSION=${LAST_TAG#v}
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: last tag '$LAST_TAG' is not a valid semver tag (expected vX.Y.Z or X.Y.Z). Cannot compute next version." >&2
    exit 1
fi
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"

BUMP_MAJOR=0
BUMP_MINOR=0
BUMP_PATCH=0

COMMITS_JSON="[]"

while IFS=$'\x1f' read -r -d $'\x1e' SUBJECT BODY; do
    # git inserts a newline before every record after the first (its own
    # separator between --pretty=format: entries) — strip it so it doesn't
    # leak into the next commit's subject.
    SUBJECT="${SUBJECT#$'\n'}"

    [ -z "$SUBJECT" ] && continue

    # Autosquash markers (from `git commit --fixup`/`--squash`) are meant to
    # be rebased away before merging and never represent a real changelog
    # entry on their own — skip before any type/breaking parsing.
    if [[ "$SUBJECT" =~ ^(fixup|squash|amend)\! ]]; then
        continue
    fi

    TYPE_FIELD=$(echo "$SUBJECT" | cut -d':' -f1)
    TYPE=$(echo "$TYPE_FIELD" | sed -E 's/\(.*\)//; s/!$//')

    CATEGORY="other"

    case "$TYPE" in
        feat )     CATEGORY="added" ;;
        fix )      CATEGORY="fixed" ;;
        perf )     CATEGORY="changed" ;;
        refactor ) CATEGORY="changed" ;;
        revert )   CATEGORY="reverted" ;;
        bump|test|ci|chore|docs ) CATEGORY="ignore" ;;
    esac

    # Native `git revert` produces `Revert "feat: x"` — capitalized, no
    # conventional type prefix — which the case match above won't catch.
    if [ "$CATEGORY" = "other" ] && [[ "$SUBJECT" =~ ^[Rr]evert[[:space:]] ]]; then
        CATEGORY="reverted"
    fi

    # Per Conventional Commits, a `!` after the type/scope OR a
    # `BREAKING CHANGE:` footer marks a breaking change regardless of type —
    # this must be checked before the ignore/other skip below, since even an
    # ignored type (e.g. `chore!:`) is still a mandatory MAJOR bump.
    BREAKING=false
    if [[ "$TYPE_FIELD" == *"!" ]] || [[ "$BODY" == *"BREAKING CHANGE"* ]] || [[ "$SUBJECT" == *"BREAKING CHANGE"* ]]; then
        BREAKING=true
    fi

    if [ "$BREAKING" = true ]; then
        CATEGORY="breaking"
        BUMP_MAJOR=1
    elif [ "$CATEGORY" = "ignore" ] || [ "$CATEGORY" = "other" ]; then
        continue
    elif [ "$CATEGORY" = "added" ]; then
        BUMP_MINOR=1
    else
        BUMP_PATCH=1
    fi

    PR=$(echo "$SUBJECT" | grep -oE '#[0-9]+' | head -n1 | tr -d '#' || true)

    # xargs is avoided here for trimming: native `git revert` subjects
    # (Revert "feat: x") carry an unbalanced quote that makes xargs abort
    # with "unterminated quote" and kill the script under `set -e`.
    MESSAGE=$(echo "$SUBJECT" \
        | sed -E 's/^[^:]+: //' \
        | sed -E 's/\(#?[0-9]+\)//g' \
        | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')

    COMMITS_JSON=$(echo "$COMMITS_JSON" | jq \
        --arg category "$CATEGORY" \
        --arg message "$MESSAGE" \
        --arg pr "$PR" \
        --argjson breaking "$BREAKING" \
        '. + [{
            category: $category,
            message: $message,
            pr: $pr,
            breaking: $breaking
        }]')

done <<< "$RAW"

if [ "$BUMP_MAJOR" -eq 0 ] && [ "$BUMP_MINOR" -eq 0 ] && [ "$BUMP_PATCH" -eq 0 ]; then
    echo "No changes since last release."
    exit 0
fi

if [ "$BUMP_MAJOR" -eq 1 ]; then
    MAJOR=$((MAJOR+1))
    MINOR=0
    PATCH=0
elif [ "$BUMP_MINOR" -eq 1 ]; then
    MINOR=$((MINOR+1))
    PATCH=0
elif [ "$BUMP_PATCH" -eq 1 ]; then
    PATCH=$((PATCH+1))
fi

NEXT_VERSION="v$MAJOR.$MINOR.$PATCH"
DATE=$(date +%Y-%m-%d)

jq -n \
    --arg last_tag "$LAST_TAG" \
    --arg next_version "$NEXT_VERSION" \
    --arg date "$DATE" \
    --argjson commits "$COMMITS_JSON" \
    '{
        last_tag: $last_tag,
        next_version: $next_version,
        date: $date,
        commits: $commits
    }'
