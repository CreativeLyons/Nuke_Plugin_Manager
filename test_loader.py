"""Test script for loader.py using a FakeNuke class."""

from loader import apply_plugin_paths
from config import DEFAULT_CONFIG
import tempfile
import os
import json


class FakeNuke:
    """Fake Nuke module that captures added plugin paths."""

    def __init__(self, nuke_version_string=None, nuke_version_major=None):
        """
        Initialize FakeNuke.

        Args:
            nuke_version_string: Optional version string (e.g., "14.0v1")
            nuke_version_major: Optional major version number
        """
        self.added_paths = []
        self._nuke_version_string = nuke_version_string
        self._nuke_version_major = nuke_version_major

    def addPluginPath(self, path):
        """Add a plugin path (captures it for testing)."""
        self.added_paths.append(path)

    def NukeVersion(self):
        """Return fake Nuke version string."""
        if self._nuke_version_string:
            return self._nuke_version_string
        return "14.0v1"

    @property
    def NUKE_VERSION_MAJOR(self):
        """Return fake Nuke major version."""
        return self._nuke_version_major


def create_test_config(config_data):
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        return f.name


if __name__ == "__main__":
    print("Testing apply_plugin_paths...\n")

    # Test 1: vanilla=True adds nothing
    print("Test 1: vanilla=True should add nothing")
    config_vanilla = DEFAULT_CONFIG.copy()
    config_vanilla["vanilla"] = True
    config_vanilla["plugins_root"] = "sandbox/plugins"
    config_vanilla["plugins"] = {
        "PluginA": {"enabled": True}
    }
    config_path = create_test_config(config_vanilla)
    try:
        fake_nuke = FakeNuke()
        result = apply_plugin_paths(fake_nuke, config_path)
        assert result == True, "Should return True"
        assert len(fake_nuke.added_paths) == 0, "Should add no paths in vanilla mode"
        print("  ✓ Passed\n")
    finally:
        os.unlink(config_path)

    # Test 2: underscore-disabled adds nothing
    print("Test 2: underscore-disabled plugin should add nothing")
    config_underscore = DEFAULT_CONFIG.copy()
    config_underscore["plugins_root"] = "sandbox/plugins"
    config_underscore["plugins"] = {
        "PluginC": {"enabled": True}  # PluginC is _PluginC (underscore-disabled)
    }
    config_path = create_test_config(config_underscore)
    try:
        fake_nuke = FakeNuke()
        result = apply_plugin_paths(fake_nuke, config_path)
        assert result == True, "Should return True"
        # PluginC should be skipped because it's underscore-disabled
        plugin_c_paths = [p for p in fake_nuke.added_paths if "PluginC" in p or "_PluginC" in p]
        assert len(plugin_c_paths) == 0, "Should not add underscore-disabled plugin"
        print("  ✓ Passed\n")
    finally:
        os.unlink(config_path)

    # Test 3: enabled plugin adds its path
    print("Test 3: enabled plugin should add its path")
    config_enabled = DEFAULT_CONFIG.copy()
    config_enabled["plugins_root"] = "sandbox/plugins"
    config_enabled["plugins"] = {
        "PluginA": {"enabled": True},
        "PluginB": {"enabled": False}  # Should be skipped
    }
    config_path = create_test_config(config_enabled)
    try:
        fake_nuke = FakeNuke()
        result = apply_plugin_paths(fake_nuke, config_path)
        assert result == True, "Should return True"
        assert len(fake_nuke.added_paths) > 0, "Should add at least one path"
        plugin_a_paths = [p for p in fake_nuke.added_paths if "PluginA" in p]
        assert len(plugin_a_paths) == 1, "Should add PluginA path"
        plugin_b_paths = [p for p in fake_nuke.added_paths if "PluginB" in p]
        assert len(plugin_b_paths) == 0, "Should not add disabled PluginB path"
        print(f"  Added paths: {fake_nuke.added_paths}")
        print("  ✓ Passed\n")
    finally:
        os.unlink(config_path)

    # Test 4: max_nuke_major gating works when nuke_major is passed
    print("Test 4: max_nuke_major version gating")
    config_version = DEFAULT_CONFIG.copy()
    config_version["plugins_root"] = "sandbox/plugins"
    config_version["plugins"] = {
        "PluginA": {"enabled": True, "max_nuke_major": 13},
        "PluginB": {"enabled": True, "max_nuke_major": 15},
        "BrokenLegacy": {"enabled": True}  # No max_nuke_major, should always add
    }
    config_path = create_test_config(config_version)
    try:
        # Test with Nuke 14 - PluginA (max 13) should be skipped, PluginB (max 15) should be added
        fake_nuke_14 = FakeNuke()
        result = apply_plugin_paths(fake_nuke_14, config_path, nuke_major=14)
        assert result == True, "Should return True"
        plugin_a_paths = [p for p in fake_nuke_14.added_paths if "PluginA" in p]
        plugin_b_paths = [p for p in fake_nuke_14.added_paths if "PluginB" in p]
        broken_paths = [p for p in fake_nuke_14.added_paths if "BrokenLegacy" in p]
        assert len(plugin_a_paths) == 0, "PluginA (max 13) should be skipped for Nuke 14"
        assert len(plugin_b_paths) == 1, "PluginB (max 15) should be added for Nuke 14"
        assert len(broken_paths) == 1, "BrokenLegacy (no max) should be added"
        print(f"  Nuke 14 added paths: {fake_nuke_14.added_paths}")
        print("  ✓ Passed (Nuke 14)\n")

        # Test with Nuke 13 - PluginA (max 13) should be added
        fake_nuke_13 = FakeNuke()
        result = apply_plugin_paths(fake_nuke_13, config_path, nuke_major=13)
        assert result == True, "Should return True"
        plugin_a_paths = [p for p in fake_nuke_13.added_paths if "PluginA" in p]
        assert len(plugin_a_paths) == 1, "PluginA (max 13) should be added for Nuke 13"
        print(f"  Nuke 13 added paths: {fake_nuke_13.added_paths}")
        print("  ✓ Passed (Nuke 13)\n")

        # Test with Nuke 16 - PluginA (max 13) and PluginB (max 15) should be skipped
        fake_nuke_16 = FakeNuke()
        result = apply_plugin_paths(fake_nuke_16, config_path, nuke_major=16)
        assert result == True, "Should return True"
        plugin_a_paths = [p for p in fake_nuke_16.added_paths if "PluginA" in p]
        plugin_b_paths = [p for p in fake_nuke_16.added_paths if "PluginB" in p]
        broken_paths = [p for p in fake_nuke_16.added_paths if "BrokenLegacy" in p]
        assert len(plugin_a_paths) == 0, "PluginA (max 13) should be skipped for Nuke 16"
        assert len(plugin_b_paths) == 0, "PluginB (max 15) should be skipped for Nuke 16"
        assert len(broken_paths) == 1, "BrokenLegacy (no max) should be added"
        print(f"  Nuke 16 added paths: {fake_nuke_16.added_paths}")
        print("  ✓ Passed (Nuke 16)\n")
    finally:
        os.unlink(config_path)

    # Test 5: Invalid config path should not crash
    print("Test 5: Invalid config path should not crash")
    fake_nuke = FakeNuke()
    result = apply_plugin_paths(fake_nuke, "/nonexistent/path/config.json")
    assert result == True, "Should return True (uses defaults)"
    print("  ✓ Passed\n")

    print("All tests passed!")
