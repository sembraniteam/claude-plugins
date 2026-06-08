#!/usr/bin/env bash
# Stops the archimind static site viewer.
# Reads the PID from .archimind.pid and kills the process.
#
# Usage: bash stop-server.sh
# Run from project root.

PID_FILE="$(pwd)/.archimind.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No running archimind server found (.archimind.pid not found)."
  exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  rm -f "$PID_FILE"
  echo "Archimind server stopped (PID $PID)."
else
  rm -f "$PID_FILE"
  echo "Server was not running (stale PID $PID removed)."
fi
