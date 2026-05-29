#!/bin/bash
# vivid — VIVID Agent CLI wrapper
# Installs Python deps and runs the agent

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "   Install from https://python.org"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "$SCRIPT_DIR/venv" ] && [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "📦 Installing VIVID Agent dependencies..."
    python3 -m venv "$SCRIPT_DIR/venv"
    "$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" -q
    echo "✅ Dependencies installed"
fi

# Run VIVID Agent
if [ -d "$SCRIPT_DIR/venv" ]; then
    "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/vivid.py" "$@"
else
    python3 "$SCRIPT_DIR/vivid.py" "$@"
fi
