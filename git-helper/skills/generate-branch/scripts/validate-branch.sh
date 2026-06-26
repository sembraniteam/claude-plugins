#!/usr/bin/env bash
# Validates a git branch name against team naming conventions.
# Usage: ./validate-branch.sh <branch-name>
# Exit 0 = valid, exit 1 = invalid (errors printed to stdout).

set -euo pipefail

branch="${1:-}"

if [[ -z "$branch" ]]; then
  echo "Usage: $0 <branch-name>"
  exit 1
fi

errors=()

# Valid prefixes
valid_prefixes=("feature/" "bugfix/" "hotfix/" "release/" "chore/" "bump/")
has_prefix=false
for prefix in "${valid_prefixes[@]}"; do
  if [[ "$branch" == "$prefix"* ]]; then
    has_prefix=true
    break
  fi
done
$has_prefix || errors+=("Missing required prefix. Valid: feature/ bugfix/ hotfix/ release/ chore/ bump/")

# No uppercase
[[ "$branch" =~ [A-Z] ]] && errors+=("Uppercase letters not allowed")

# No underscores
[[ "$branch" =~ _ ]] && errors+=("Underscores not allowed — use hyphens")

# No special characters (allow letters, digits, hyphens, dots, slashes)
[[ "$branch" =~ [^a-z0-9/.\-] ]] && errors+=("Special characters not allowed")

# No consecutive hyphens
[[ "$branch" =~ -- ]] && errors+=("Consecutive hyphens not allowed")

# No leading or trailing hyphen in slug
slug="${branch#*/}"
[[ "$slug" =~ ^- ]] && errors+=("Slug must not start with a hyphen")
[[ "$slug" =~ -$ ]] && errors+=("Slug must not end with a hyphen")

# Dots only in release/ branches (version numbers)
if [[ "$branch" != release/* && "$branch" =~ \. ]]; then
  errors+=("Dots are only allowed in release/ branches for version numbers")
fi

# No consecutive dots
[[ "$branch" =~ \.\. ]] && errors+=("Consecutive dots not allowed")

# Slug must not be empty
slug_part="${branch##*/}"
[[ -z "$slug_part" ]] && errors+=("Slug after prefix must not be empty")

# Release branches must have v-prefixed semver slug
if [[ "$branch" == release/* ]]; then
  release_slug="${branch#release/}"
  if [[ ! "$release_slug" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    errors+=("Release branches must use vMAJOR.MINOR.PATCH format (e.g. release/v1.2.0)")
  fi
fi

if [[ ${#errors[@]} -eq 0 ]]; then
  echo "✓ Valid: $branch"
  exit 0
else
  echo "✗ Invalid: $branch"
  for err in "${errors[@]}"; do
    echo "  - $err"
  done
  exit 1
fi
