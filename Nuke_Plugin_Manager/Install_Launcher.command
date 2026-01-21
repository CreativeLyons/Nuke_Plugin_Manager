#!/bin/bash
# Double-click installer for Nuke Plugin Manager launcher
# This creates the .app bundle in ~/.nuke/Nuke_Plugin_Manager/

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the Nuke_Plugin_Manager directory
cd "$SCRIPT_DIR"

# Run the installer
python3 core/install_launcher.py

# Keep Terminal open so user can see the result
echo ""
echo "Press any key to close this window..."
read -n 1
