#!/usr/bin/env python3
"""
Prints the sha256 hex digest of the file passed as the first CLI argument.
Uses only the built-in `hashlib`/`pathlib` modules -- no shell commands
(e.g. `shasum`, which isn't guaranteed on Windows), no external deps.
Prints the digest to stdout, then exits 0.
Exits 1 with an error message if no path was given or the file can't be
read.

Usage: python3 scripts/hash-file.py <path>
"""

import hashlib
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        sys.stderr.write(
            "Error: pass a file path, e.g. python3 hash-file.py docs/architecture-designer/diagrams.json\n"
        )
        sys.exit(1)

    path = Path(sys.argv[1])
    try:
        contents = path.read_bytes()
    except OSError as err:
        sys.stderr.write(f'Error: could not read "{path}": {err}\n')
        sys.exit(1)

    digest = hashlib.sha256(contents).hexdigest()
    sys.stdout.write(f"{digest}\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
