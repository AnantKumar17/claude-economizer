#!/usr/bin/env bash
# prompt-economizer entry point
# Called by Claude Code UserPromptSubmit hook
# Reads JSON from stdin, writes JSON to stdout

set -euo pipefail

# Get the directory this script lives in
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Python must be available
PYTHON_BIN="$(which python3 2>/dev/null || which python 2>/dev/null)"

if [ -z "$PYTHON_BIN" ]; then
    # No Python — pass through silently
    cat  # echo stdin to stdout unchanged
    exit 0
fi

# Run the Python optimizer, passing stdin through
exec "$PYTHON_BIN" "$SCRIPT_DIR/economizer.py"
