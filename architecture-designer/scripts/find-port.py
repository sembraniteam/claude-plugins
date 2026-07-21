#!/usr/bin/env python3
"""
Finds the first available TCP port in the range 3000-9000.
Uses only the built-in `socket` module -- no shell commands, no external
deps.
Prints the port number to stdout, then exits 0.
Exits 1 with an error message if the entire range is occupied.

Usage: python3 scripts/find-port.py
"""

import socket
import sys

START_PORT = 3000
END_PORT = 9000


def is_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def main():
    for port in range(START_PORT, END_PORT + 1):
        if is_free(port):
            sys.stdout.write(f"{port}\n")
            sys.exit(0)

    sys.stderr.write(
        f"Error: No free port found in range {START_PORT}-{END_PORT}.\n"
        "Please close some applications and try again.\n"
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
