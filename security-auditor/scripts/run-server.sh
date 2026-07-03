#!/bin/bash -l
# Login shell (-l) sources the user's shell profile, which ensures Homebrew,
# pyenv, asdf, and other PATH customizations are available. This is needed
# because Claude Code spawns MCP processes with a minimal PATH that often
# excludes package managers like /opt/homebrew/bin.
exec uv run "$(dirname "$0")/vuln_server.py"
