#!/bin/bash
# Double-click installer for Nuke Plugin Manager launcher (macOS)
# This creates/updates the .app launcher and then opens it

# Get the directory where this script is located (install/ folder)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the Nuke_Plugin_Manager tool root (parent of install/)
TOOL_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
cd "$TOOL_ROOT"

# 1) Create/update the macOS .app launcher in ~/.nuke/Nuke_Plugin_Manager/
python3 core/install_launcher.py

# 2) Open the .app launcher (detached from this Terminal)
APP_PATH="$HOME/.nuke/Nuke_Plugin_Manager/Nuke_Plugin_Manager_Panel.app"
if [ -d "$APP_PATH" ]; then
  open "$APP_PATH"
fi

