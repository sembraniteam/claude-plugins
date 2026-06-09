#!/usr/bin/env bash
# Starts the archimind static viewer server.
# Serves /tmp/archimind-viewer/ (writable) — index.html is copied from the
# plugin's scripts/site/ on every start so it stays up to date.
# Prints the URL on success.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_DIR="/tmp/archimind-viewer"
PID_FILE="/tmp/.archimind-${UID}.pid"

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

# Find an available port (exits non-zero if 3000-3099 are all taken)
PORT=$(bash "$SCRIPT_DIR/find-port.sh") || exit 1

# Start the server using --directory to avoid changing the working directory
python3 -m http.server "$PORT" --directory "$SITE_DIR" >/dev/null 2>&1 &
echo $! > "$PID_FILE"

# Wait until the server socket is ready before printing the URL
while ! lsof -i tcp:"$PORT" &>/dev/null; do sleep 0.05; done

echo "http://localhost:$PORT"
