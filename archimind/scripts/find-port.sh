#!/usr/bin/env bash
# Prints the first available TCP port in 3000-3099, or exits non-zero if all are taken.
for port in $(seq 3000 3099); do
  if ! lsof -i tcp:"$port" &>/dev/null; then
    echo "$port"
    exit 0
  fi
done
echo "Error: no free TCP port in range 3000-3099" >&2
exit 1
