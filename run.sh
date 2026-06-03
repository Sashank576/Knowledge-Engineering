#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/visualization"
VENV_DIR="$SRC_DIR/venv"
REQUIREMENTS="$SRC_DIR/requirements.txt"

cd "$SRC_DIR"

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip --quiet
python -m pip install --quiet -r "$REQUIREMENTS"

# Run
echo "Starting app..."
python main.py