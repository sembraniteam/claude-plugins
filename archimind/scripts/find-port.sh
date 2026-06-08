#!/usr/bin/env bash
# Finds the first available TCP port starting from START_PORT (default: 3000).
# Prints the available port number to stdout.
# Usage: bash find-port.sh [start_port]

START_PORT="${1:-3000}"
MAX_PORT=9999

for port in $(seq "$START_PORT" "$MAX_PORT"); do
  if ! (echo "" 2>/dev/null >"/dev/tcp/127.0.0.1/$port") 2>/dev/null; then
    echo "$port"
    exit 0
  fi
done

echo "ERROR: No available port found between $START_PORT and $MAX_PORT" >&2
exit 1
