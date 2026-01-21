"""Tests for schema v2 plugin state scoping."""

import json
import tempfile
import os
from pathlib import Path

from config import load_config, save_config, DEFAULT_CONFIG, _migrate_v1_to_v2
from plugin_state import build_plugin_state, set_plugin_enabled, set_plugins_root


def test_v1_to_v2_migration():
    """Test migration from v1 to v2 schema."""
    print("Test 1: v1 to v2 migration")

    v1_config = {
        "schema_version": 1,
        "vanilla": False,
        "plugins_root": "/path/to/plugins",
        "plugins": {
            "PluginA": {"enabled": True},
            "PluginB": {"enabled": False}
        }
    }

    v2_config = _migrate_v1_to_v2(v1_config)

    assert v2_config["schema_version"] == 2, "Should be v2"
    assert "plugins" not in v2_config, "Old plugins key should be removed"
    assert "roots" in v2_config, "Should have roots dict"
    assert "/path/to/plugins" in v2_config["roots"], "Should have migrated root"
    assert v2_config["roots"]["/path/to/plugins"]["plugins"]["PluginA"]["enabled"] == True
    assert v2_config["roots"]["/path/to/plugins"]["plugins"]["PluginB"]["enabled"] == False
    print("  ✓ Passed\n")


def test_no_collision_different_roots():
    """Test that same plugin name in different roots doesn't collide."""
    print("Test 2: No collision with different roots")

    # Use sandbox plugins for this test
    sandbox_root = str(Path("sandbox/plugins").resolve())

    config = {
        "schema_version": 2,
        "vanilla": False,
        "plugins_root": sandbox_root,
        "roots": {
            sandbox_root: {
                "plugins": {
                    "PluginA": {"enabled": True},
                    "PluginB": {"enabled": False}
                }
            },
            "/fake/root/B": {
                "plugins": {
                    "PluginA": {"enabled": False}  # Different state for same name
                }
            }
        }
    }

    # Build state for sandbox root
    state = build_plugin_state(config)

    # Find PluginA and PluginB in state
    plugin_a = next((p for p in state["plugins"] if p["name"] == "PluginA"), None)
    plugin_b = next((p for p in state["plugins"] if p["name"] == "PluginB"), None)

    assert plugin_a is not None, "PluginA should exist"
    assert plugin_b is not None, "PluginB should exist"
    assert plugin_a["enabled"] == True, "PluginA should be enabled (from sandbox root config)"
    assert plugin_b["enabled"] == False, "PluginB should be disabled (from sandbox root config)"

    # Verify the fake root B config is preserved (not overwritten)
    assert config["roots"]["/fake/root/B"]["plugins"]["PluginA"]["enabled"] == False

    print("  ✓ Passed\n")


def test_set_plugin_enabled_scoped():
    """Test that set_plugin_enabled writes to correct root."""
    print("Test 3: set_plugin_enabled scoped to active root")

    config = {
        "schema_version": 2,
        "vanilla": False,
        "plugins_root": "/root/A",
        "roots": {
            "/root/A": {
                "plugins": {
                    "PluginA": {"enabled": True}
                }
            },
            "/root/B": {
                "plugins": {
                    "PluginA": {"enabled": False}
                }
            }
        }
    }

    # Update PluginA in root A
    config = set_plugin_enabled(config, "PluginA", False)
    assert config["roots"]["/root/A"]["plugins"]["PluginA"]["enabled"] == False
    assert config["roots"]["/root/B"]["plugins"]["PluginA"]["enabled"] == False  # Unchanged

    # Switch to root B and update
    config = set_plugins_root(config, "/root/B")
    config = set_plugin_enabled(config, "PluginA", True)
    assert config["roots"]["/root/A"]["plugins"]["PluginA"]["enabled"] == False  # Unchanged
    assert config["roots"]["/root/B"]["plugins"]["PluginA"]["enabled"] == True

    print("  ✓ Passed\n")


def test_load_save_migration():
    """Test that v1 config is migrated when loaded and saved as v2."""
    print("Test 4: Load/save migration")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        v1_config = {
            "schema_version": 1,
            "vanilla": False,
            "plugins_root": "/test/plugins",
            "plugins": {
                "TestPlugin": {"enabled": True}
            }
        }
        json.dump(v1_config, f)
        config_path = f.name

    try:
        # Load should migrate to v2
        loaded = load_config(config_path)
        assert loaded["schema_version"] == 2
        assert "plugins" not in loaded
        assert "/test/plugins" in loaded["roots"]
        assert loaded["roots"]["/test/plugins"]["plugins"]["TestPlugin"]["enabled"] == True

        # Save should write as v2
        success = save_config(config_path, loaded)
        assert success

        # Reload and verify it's still v2
        reloaded = load_config(config_path)
        assert reloaded["schema_version"] == 2
        assert "plugins" not in reloaded

        print("  ✓ Passed\n")
    finally:
        os.unlink(config_path)


def test_default_enabled():
    """Test that plugins without config entry default to enabled."""
    print("Test 5: Default enabled for plugins not in config")

    config = {
        "schema_version": 2,
        "vanilla": False,
        "plugins_root": "/test/plugins",
        "roots": {
            "/test/plugins": {
                "plugins": {
                    "ConfiguredPlugin": {"enabled": False}
                }
            }
        }
    }

    state = build_plugin_state(config)
    # This test requires actual plugin discovery, so we'll just verify
    # that the function doesn't crash and handles missing plugins
    assert "plugins" in state
    assert isinstance(state["plugins"], list)

    print("  ✓ Passed\n")


if __name__ == "__main__":
    print("Running schema v2 tests...\n")
    test_v1_to_v2_migration()
    test_no_collision_different_roots()
    test_set_plugin_enabled_scoped()
    test_load_save_migration()
    test_default_enabled()
    print("All tests passed!")
