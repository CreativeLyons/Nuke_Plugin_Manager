"""Tests for baseline config functionality."""

import json
import os
import tempfile
import shutil
from pathlib import Path

from config import (
    get_default_user_config_path,
    resolve_baseline_config_path,
    ensure_user_config,
    load_config,
    DEFAULT_CONFIG
)


def test_get_default_user_config_path():
    """Test default user config path resolution."""
    print("Test 1: Default user config path")
    path = get_default_user_config_path()
    assert path.name == "plugin_manager.json"
    assert ".nuke" in str(path)
    assert "Nuke_Plugin_Manager" in str(path)
    print(f"  Path: {path}")
    print("  ✓ Passed\n")


def test_resolve_baseline_env_var():
    """Test baseline resolution from environment variable."""
    print("Test 2: Baseline resolution from env var")

    # Create a temporary baseline file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        baseline_content = {
            "schema_version": 2,
            "vanilla": False,
            "plugins_root": "/studio/plugins",
            "roots": {}
        }
        json.dump(baseline_content, f)
        baseline_path = f.name

    try:
        # Set environment variable
        os.environ["NUKE_PLUGIN_MANAGER_BASELINE"] = baseline_path
        resolved = resolve_baseline_config_path()
        assert resolved is not None
        assert resolved.resolve() == Path(baseline_path).resolve()
        print("  ✓ Passed\n")
    finally:
        # Cleanup
        os.unlink(baseline_path)
        if "NUKE_PLUGIN_MANAGER_BASELINE" in os.environ:
            del os.environ["NUKE_PLUGIN_MANAGER_BASELINE"]


def test_resolve_baseline_default_config():
    """Test baseline resolution from default_config.json."""
    print("Test 3: Baseline resolution from default_config.json")

    # Create default_config.json next to config.py
    config_dir = Path(__file__).parent
    default_config = config_dir / "default_config.json"

    baseline_content = {
        "schema_version": 2,
        "vanilla": False,
        "plugins_root": "/studio/plugins",
        "roots": {}
    }

    # Save baseline
    with open(default_config, 'w') as f:
        json.dump(baseline_content, f)

    try:
        # Clear env var if set
        env_baseline = os.environ.pop("NUKE_PLUGIN_MANAGER_BASELINE", None)

        resolved = resolve_baseline_config_path()
        assert resolved is not None
        assert resolved.name == "default_config.json"
        print("  ✓ Passed\n")
    finally:
        # Cleanup
        if default_config.exists():
            default_config.unlink()
        if env_baseline:
            os.environ["NUKE_PLUGIN_MANAGER_BASELINE"] = env_baseline


def test_ensure_user_config_with_baseline():
    """Test copying baseline to user config when user config is missing."""
    print("Test 4: Copy baseline to user config")

    # Create temporary baseline
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        baseline_content = {
            "schema_version": 2,
            "vanilla": True,
            "plugins_root": "/studio/plugins",
            "roots": {}
        }
        json.dump(baseline_content, f)
        baseline_path = f.name

    # Create temporary user config path
    with tempfile.TemporaryDirectory() as tmpdir:
        user_config = Path(tmpdir) / "user_config.json"

        try:
            # Set env var
            os.environ["NUKE_PLUGIN_MANAGER_BASELINE"] = baseline_path

            # Ensure user config (should copy baseline)
            result = ensure_user_config(user_config, use_baseline=True)
            assert result == True
            assert user_config.exists()

            # Verify content matches baseline
            loaded = load_config(str(user_config))
            assert loaded["vanilla"] == True
            assert loaded["plugins_root"] == "/studio/plugins"

            print("  ✓ Passed\n")
        finally:
            if "NUKE_PLUGIN_MANAGER_BASELINE" in os.environ:
                del os.environ["NUKE_PLUGIN_MANAGER_BASELINE"]
            os.unlink(baseline_path)


def test_ensure_user_config_without_baseline():
    """Test creating default config when baseline is missing."""
    print("Test 5: Create default config when baseline missing")

    # Create temporary user config path
    with tempfile.TemporaryDirectory() as tmpdir:
        user_config = Path(tmpdir) / "user_config.json"

        # Clear env var
        env_baseline = os.environ.pop("NUKE_PLUGIN_MANAGER_BASELINE", None)

        try:
            # Ensure user config (no baseline available)
            result = ensure_user_config(user_config, use_baseline=True)
            assert result == True
            assert user_config.exists()

            # Verify content is defaults
            loaded = load_config(str(user_config))
            assert loaded["schema_version"] == 2
            assert loaded["vanilla"] == False
            assert loaded["plugins_root"] == ""

            print("  ✓ Passed\n")
        finally:
            if env_baseline:
                os.environ["NUKE_PLUGIN_MANAGER_BASELINE"] = env_baseline


def test_ensure_user_config_skip_baseline():
    """Test that use_baseline=False creates defaults even if baseline exists."""
    print("Test 6: Skip baseline when use_baseline=False")

    # Create temporary baseline
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        baseline_content = {
            "schema_version": 2,
            "vanilla": True,
            "plugins_root": "/studio/plugins",
            "roots": {}
        }
        json.dump(baseline_content, f)
        baseline_path = f.name

    # Create temporary user config path
    with tempfile.TemporaryDirectory() as tmpdir:
        user_config = Path(tmpdir) / "user_config.json"

        try:
            # Set env var
            os.environ["NUKE_PLUGIN_MANAGER_BASELINE"] = baseline_path

            # Ensure user config with use_baseline=False
            result = ensure_user_config(user_config, use_baseline=False)
            assert result == True
            assert user_config.exists()

            # Verify content is defaults (not baseline)
            loaded = load_config(str(user_config))
            assert loaded["vanilla"] == False  # Default, not baseline value
            assert loaded["plugins_root"] == ""  # Default, not baseline value

            print("  ✓ Passed\n")
        finally:
            if "NUKE_PLUGIN_MANAGER_BASELINE" in os.environ:
                del os.environ["NUKE_PLUGIN_MANAGER_BASELINE"]
            os.unlink(baseline_path)


if __name__ == "__main__":
    print("Running baseline config tests...\n")
    test_get_default_user_config_path()
    test_resolve_baseline_env_var()
    test_resolve_baseline_default_config()
    test_ensure_user_config_with_baseline()
    test_ensure_user_config_without_baseline()
    test_ensure_user_config_skip_baseline()
    print("All tests passed!")
