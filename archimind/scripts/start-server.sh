#!/usr/bin/env bash
# Starts the archimind static site viewer.
# - Finds a free port
# - Copies index.html to docs/archimind/
# - Generates docs/archimind/manifest.json
# - Starts python3 -m http.server from docs/archimind/
# - Saves PID to .archimind.pid in the current directory
#
# Usage: bash start-server.sh
# Run from project root.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$(pwd)/docs/archimind"
PID_FILE="$(pwd)/.archimind.pid"
INDEX_SRC="$PLUGIN_ROOT/scripts/site/index.html"

# --- Check for existing server ---
if [[ -f "$PID_FILE" ]]; then
  OLD_PID=$(cat "$PID_FILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Server is already running (PID $OLD_PID). Stop it first with stop-server.sh"
    exit 1
  else
    rm -f "$PID_FILE"
  fi
fi

# --- Ensure docs/archimind exists ---
mkdir -p "$DOCS_DIR"

# --- Find available port ---
PORT=$(bash "$PLUGIN_ROOT/scripts/find-port.sh" 3000)
if [[ -z "$PORT" ]]; then
  echo "ERROR: Could not find an available port." >&2
  exit 1
fi

# --- Copy viewer index.html ---
cp "$INDEX_SRC" "$DOCS_DIR/index.html"

# --- Generate manifest.json ---
MANIFEST_FILE="$DOCS_DIR/manifest.json"
GENERATED=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Build manifest entries array then join with commas
ENTRIES=()
while IFS= read -r filepath; do
  filename=$(basename "$filepath")
  title=$(echo "$filename" \
    | sed 's/^[0-9]*_//' \
    | sed 's/-/ /g' \
    | sed 's/\.md$//')
  ENTRIES+=("    { \"name\": \"$filename\", \"title\": \"$title\" }")
done < <(find "$DOCS_DIR" -maxdepth 1 -name "*.md" | sort -r)

{
  echo '{'
  echo "  \"generated\": \"$GENERATED\","
  echo '  "files": ['
  for i in "${!ENTRIES[@]}"; do
    if [[ $i -lt $(( ${#ENTRIES[@]} - 1 )) ]]; then
      echo "${ENTRIES[$i]},"
    else
      echo "${ENTRIES[$i]}"
    fi
  done
  echo '  ]'
  echo '}'
} > "$MANIFEST_FILE"

# --- Start server in background ---
cd "$DOCS_DIR"
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

# --- Wait briefly to confirm server started ---
sleep 0.5
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
  echo "ERROR: Server failed to start." >&2
  rm -f "$PID_FILE"
  exit 1
fi

echo "Archimind viewer started."
echo "URL:  http://localhost:$PORT"
echo "PID:  $SERVER_PID (saved to .archimind.pid)"
echo "Stop: bash $PLUGIN_ROOT/scripts/stop-server.sh"

# --- Attempt to open in default browser ---
if command -v open &>/dev/null; then
  open "http://localhost:$PORT"
elif command -v xdg-open &>/dev/null; then
  xdg-open "http://localhost:$PORT" &>/dev/null &
fi
