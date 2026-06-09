#!/usr/bin/env bash
# Starts the archimind static viewer server.
# The server serves scripts/site/ which contains index.html and content.md.
# Prints the URL on success.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_DIR="$SCRIPT_DIR/site"
PID_FILE="$(dirname "$SCRIPT_DIR")/.archimind.pid"

# Stop any existing instance
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  kill -0 "$OLD_PID" 2>/dev/null && kill "$OLD_PID" 2>/dev/null
  rm -f "$PID_FILE"
fi

# Find an available port
PORT=$(bash "$SCRIPT_DIR/find-port.sh")

# Start the server
cd "$SITE_DIR"
python3 -m http.server "$PORT" >/dev/null 2>&1 &
echo $! > "$PID_FILE"

echo "http://localhost:$PORT"
