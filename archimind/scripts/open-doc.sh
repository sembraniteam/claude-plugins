#!/usr/bin/env bash
# Opens a previously saved docs/archimind document in the viewer.
# Copies the file to /tmp/archimind-viewer/content.md and starts the server.
#
# Usage:
#   bash open-doc.sh <path/to/docs/archimind/**/*.md>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOC="$1"

if [ -z "$DOC" ]; then
  echo "Error: no file specified." >&2
  echo "Usage: bash $(basename "$0") <path/to/docs/archimind/**/*.md>" >&2
  exit 1
fi

if [ ! -f "$DOC" ]; then
  echo "Error: file not found: $DOC" >&2
  exit 1
fi

mkdir -p /tmp/archimind-viewer
cp "$DOC" /tmp/archimind-viewer/content.md

URL=$(bash "$SCRIPT_DIR/start-server.sh")
open "$URL"
echo "$URL"
