#!/usr/bin/env bash
# Starts the archimind static viewer server.
# Serves /tmp/archimind-viewer/ (writable) — index.html is copied from the
# plugin's scripts/site/ on every start so it stays up to date.
# Prints the URL on success.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_DIR="/tmp/archimind-viewer"
PID_FILE="/tmp/.archimind.pid"

# Stop any existing instance
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  kill -0 "$OLD_PID" 2>/dev/null && kill "$OLD_PID" 2>/dev/null
  rm -f "$PID_FILE"
fi

# Prepare writable viewer directory and refresh index.html from plugin
mkdir -p "$SITE_DIR"
cp "$SCRIPT_DIR/site/index.html" "$SITE_DIR/index.html"

# Create placeholder if content.md does not exist yet
if [ ! -f "$SITE_DIR/content.md" ]; then
  cat > "$SITE_DIR/content.md" << 'EOF'
# Archimind Viewer

> No content loaded yet.
>
> Run a design or review skill to generate content:
> - "Design an architecture for my project"
> - "Review my current architecture"
> - "Design a database for my app"
EOF
fi

# Find an available port
PORT=$(bash "$SCRIPT_DIR/find-port.sh")

# Start the server
cd "$SITE_DIR"
python3 -m http.server "$PORT" >/dev/null 2>&1 &
echo $! > "$PID_FILE"

echo "http://localhost:$PORT"
