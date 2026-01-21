"""
Entry point to run the Nuke Plugin Manager panel via the bootstrap logic.

This script:
- Ensures a repo-local virtual environment exists
- Ensures PySide6-Essentials is installed in that venv
- Launches the GUI app using the venv's Python
"""

import subprocess
import sys
from pathlib import Path

from bootstrap import ensure_venv_and_deps


def main() -> int:
    # Ensure venv and dependencies
    venv_python = ensure_venv_and_deps()
    if venv_python is None:
        # Error messages already printed by bootstrap
        return 1

    tool_root = Path(__file__).resolve().parent.parent

    # Launch the GUI app using the venv's Python by running core/run_app.py.
    # That script already handles adding core/ to sys.path and calling app.main().
    cmd = [
        str(venv_python),
        str(tool_root / "core" / "run_app.py"),
    ]

    try:
        return subprocess.call(cmd, cwd=str(tool_root))
    except OSError as exc:
        print("ERROR: Failed to launch Nuke Plugin Manager panel.")
        print(f"Details: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

