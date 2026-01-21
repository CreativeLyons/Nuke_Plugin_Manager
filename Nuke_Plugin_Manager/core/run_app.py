#!/usr/bin/env python3
"""
Simple launcher script for Nuke Plugin Manager GUI.

This script ensures the package can be run from the repo root.
"""

import sys
from pathlib import Path

# Add core to path if running from repo root
core_dir = Path(__file__).parent
if core_dir.exists() and str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

# Run the app
if __name__ == "__main__":
    from app import main
    sys.exit(main())
