#!/usr/bin/env bash
# Stops the running archimind viewer server.
PID_FILE="/tmp/.archimind-${UID}.pid"

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID"
    rm -f "$PID_FILE"
    echo "Server stopped."
  else
    rm -f "$PID_FILE"
    echo "Server was not running."
  fi
else
  echo "No running server found."
fi
