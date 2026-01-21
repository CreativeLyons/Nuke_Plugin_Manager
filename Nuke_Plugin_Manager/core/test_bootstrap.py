"""
Tests for bootstrap helper functions.

We focus on small, easily testable pieces such as the pip command
construction for wheelhouse vs. non-wheelhouse scenarios.
"""

import os
from pathlib import Path

import bootstrap


def test_build_pip_install_command_without_wheelhouse(monkeypatch):
    """When no wheelhouse is set, use normal PySide6-Essentials install."""
    monkeypatch.delenv(bootstrap.WHEELHOUSE_ENV_VAR, raising=False)
    venv_python = Path("/fake/venv/python")

    cmd = bootstrap._build_pip_install_command(venv_python)

    assert str(venv_python) in cmd[0]
    assert cmd[-1] == "PySide6-Essentials"
    assert "--no-index" not in cmd
    assert "--find-links" not in cmd


def test_build_pip_install_command_with_wheelhouse(monkeypatch, tmp_path):
    """When a wheelhouse is set, use --no-index and --find-links."""
    wheelhouse = tmp_path / "wheels"
    wheelhouse.mkdir()
    monkeypatch.setenv(bootstrap.WHEELHOUSE_ENV_VAR, str(wheelhouse))
    venv_python = Path("/fake/venv/python")

    cmd = bootstrap._build_pip_install_command(venv_python)

    # Basic structure
    assert str(venv_python) in cmd[0]
    assert "PySide6-Essentials" in cmd

    # Offline flags present
    assert "--no-index" in cmd
    assert "--find-links" in cmd
    # Wheelhouse path included
    assert str(wheelhouse) in cmd

