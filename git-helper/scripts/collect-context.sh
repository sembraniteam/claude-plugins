#!/usr/bin/env bash
set -e

# All arguments are optional file paths to filter the diff
FILES=("$@")

echo "=== GIT LOG (last 10 commits) ==="
git --no-pager log --oneline -10

echo ""
echo "=== GIT STATUS ==="
git --no-pager status --short

echo ""
echo "=== GIT DIFF (unstaged) ==="
if [ ${#FILES[@]} -gt 0 ]; then
  git --no-pager diff -- "${FILES[@]}"
else
  git --no-pager diff
fi

echo ""
echo "=== GIT DIFF STAGED ==="
if [ ${#FILES[@]} -gt 0 ]; then
  git --no-pager diff --cached -- "${FILES[@]}"
else
  git --no-pager diff --cached
fi

if [ ${#FILES[@]} -gt 0 ]; then
  echo ""
  echo "=== FILE FILTER ==="
  printf '%s\n' "${FILES[@]}"
fi
