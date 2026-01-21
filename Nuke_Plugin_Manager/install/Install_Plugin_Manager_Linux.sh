#!/bin/bash
# Double-click installer for Nuke Plugin Manager launcher (Linux)
# This creates/uses a venv and launches the panel

# Get the directory where this script is located (install/ folder)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the Nuke_Plugin_Manager tool root (parent of install/)
TOOL_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
cd "$TOOL_ROOT"

# Run the panel via bootstrap
python3 core/run_panel.py

# Keep terminal open so user can see the result
echo ""
echo "Press Enter to close this window..."
read
