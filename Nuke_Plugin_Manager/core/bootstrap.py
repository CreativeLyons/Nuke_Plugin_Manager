"""
Bootstrap utilities for Nuke Plugin Manager.

Responsibilities:
- Ensure a repo-local virtual environment exists at <tool_root>/.venv/
- Ensure required dependencies (PySide6-Essentials) are installed
- Support optional offline installs via a wheelhouse directory.
"""

import os
import subprocess
import sys
from pathlib import Path


WHEELHOUSE_ENV_VAR = "NUKE_PLUGIN_MANAGER_WHEELHOUSE"


def _get_tool_root() -> Path:
    """
    Determine the tool root directory (parent of the core/ directory).

    This works whether the code is run from the repo root or from an installed
    Nuke_Plugin_Manager folder under ~/.nuke.
    """
    return Path(__file__).resolve().parent.parent


def _get_venv_python(tool_root: Path) -> Path:
    """
    Return the path to the venv's Python executable for the current platform.
    """
    if os.name == "nt":
        return tool_root / ".venv" / "Scripts" / "python.exe"
    return tool_root / ".venv" / "bin" / "python"


def _ensure_venv(tool_root: Path) -> Path:
    """
    Ensure a virtual environment exists at <tool_root>/.venv/.

    Returns the path to the venv Python executable.
    """
    venv_dir = tool_root / ".venv"
    venv_python = _get_venv_python(tool_root)

    if not venv_python.exists():
        # Create the venv with pip available
        import venv

        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(venv_dir))

    return venv_python


def _build_pip_install_command(venv_python: Path) -> list[str]:
    """
    Build the pip install command for PySide6-Essentials.

    If NUKE_PLUGIN_MANAGER_WHEELHOUSE is set, use it as a --find-links wheelhouse
    and disable index lookups for offline installs.
    """
    wheelhouse = os.environ.get(WHEELHOUSE_ENV_VAR)
    base_cmd = [str(venv_python), "-m", "pip", "install"]

    if wheelhouse:
        return base_cmd + [
            "--no-index",
            "--find-links",
            wheelhouse,
            "PySide6-Essentials",
        ]

    return base_cmd + ["PySide6-Essentials"]


def _venv_has_pyside6(venv_python: Path) -> bool:
    """
    Check whether PySide6 is importable inside the venv.
    """
    try:
        result = subprocess.run(
            [str(venv_python), "-c", "import PySide6"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except OSError:
        return False


def ensure_venv_and_deps() -> Path | None:
    """
    Ensure the venv and required dependencies exist.

    Returns:
        Path to the venv Python executable on success, or None on failure.
    """
    tool_root = _get_tool_root()
    venv_python = _ensure_venv(tool_root)

    # If PySide6 is already available in the venv, we're done.
    if _venv_has_pyside6(venv_python):
        return venv_python

    # Otherwise, try to install PySide6-Essentials into the venv.
    install_cmd = _build_pip_install_command(venv_python)

    try:
        print("Ensuring PySide6-Essentials is installed in the Nuke Plugin Manager venv...")
        print("Running:", " ".join(install_cmd))
        result = subprocess.run(install_cmd)
    except OSError as exc:
        print("ERROR: Failed to invoke pip to install PySide6-Essentials.")
        print(f"Details: {exc}")
        print()
        print("Please ensure you have a working Python environment and pip installed.")
        return None

    if result.returncode != 0:
        wheelhouse = os.environ.get(WHEELHOUSE_ENV_VAR)
        print("=" * 70)
        print("ERROR: Failed to install PySide6-Essentials into the Nuke Plugin Manager venv.")
        print("=" * 70)
        if wheelhouse:
            print("\nOffline install was requested via NUKE_PLUGIN_MANAGER_WHEELHOUSE.")
            print("Please ensure the wheelhouse path is correct and contains PySide6-Essentials wheels.")
            print(f"Wheelhouse: {wheelhouse}")
        else:
            print("\nPlease connect to the internet and try again, or provide an offline")
            print("wheelhouse path via:")
            print("  NUKE_PLUGIN_MANAGER_WHEELHOUSE=/path/to/wheels")
        print("=" * 70)
        return None

    # Final sanity check: verify PySide6 is importable now.
    if not _venv_has_pyside6(venv_python):
        print("=" * 70)
        print("ERROR: PySide6 still not importable after installation.")
        print("=" * 70)
        return None

    return venv_python


if __name__ == "__main__":
    python_path = ensure_venv_and_deps()
    if python_path is None:
        sys.exit(1)
    print(f"Bootstrap succeeded. Venv python: {python_path}")

