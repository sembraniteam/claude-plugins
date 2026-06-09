#!/usr/bin/env bash
# Prints the first available TCP port >= 3000.
for port in $(seq 3000 9000); do
  if ! lsof -i tcp:"$port" &>/dev/null 2>&1; then
    echo "$port"
    exit 0
  fi
done
echo "3000"
