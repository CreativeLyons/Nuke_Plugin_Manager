"""Simple test script to verify plugin_state functionality."""

from config import DEFAULT_CONFIG
from plugin_state import (
    build_plugin_state,
    set_plugin_enabled,
    set_vanilla,
    set_plugins_root
)

if __name__ == "__main__":
    print("Testing build_plugin_state with empty plugins_root...")
    config_empty = DEFAULT_CONFIG.copy()
    state_empty = build_plugin_state(config_empty)
    assert state_empty["plugins"] == [], "Should return empty plugins list"
    assert state_empty["plugins_root"] == ""
    print("  ✓ Passed\n")

    print("Testing build_plugin_state with sandbox...")
    config_sandbox = DEFAULT_CONFIG.copy()
    config_sandbox["plugins_root"] = "sandbox/plugins"
    state_sandbox = build_plugin_state(config_sandbox)
    print(f"  Found {len(state_sandbox['plugins'])} plugins")
    for plugin in state_sandbox["plugins"]:
        print(f"    - {plugin['name']}: enabled={plugin['enabled']}, "
              f"underscore_disabled={plugin['underscore_disabled']}, "
              f"max_nuke_major={plugin['max_nuke_major']}")
    assert len(state_sandbox["plugins"]) == 4, "Should find 4 plugins"
    print("  ✓ Passed\n")

    print("Testing build_plugin_state with config overrides...")
    config_with_overrides = DEFAULT_CONFIG.copy()
    config_with_overrides["plugins_root"] = "sandbox/plugins"
    config_with_overrides["plugins"] = {
        "PluginA": {"enabled": False, "max_nuke_major": 14},
        "PluginC": {"enabled": True, "max_nuke_major": 15},
        "BrokenLegacy": {"enabled": True}
    }
    state_overrides = build_plugin_state(config_with_overrides)
    plugin_a = next(p for p in state_overrides["plugins"] if p["name"] == "PluginA")
    plugin_c = next(p for p in state_overrides["plugins"] if p["name"] == "PluginC")
    assert plugin_a["enabled"] == False, "PluginA should be disabled from config"
    assert plugin_a["max_nuke_major"] == 14, "PluginA should have max_nuke_major 14"
    assert plugin_c["enabled"] == False, "PluginC should be disabled (underscore forces it)"
    assert plugin_c["max_nuke_major"] == 15, "PluginC should have max_nuke_major 15"
    print("  ✓ Passed\n")

    print("Testing set_plugin_enabled...")
    config_test = DEFAULT_CONFIG.copy()
    config_test["plugins"] = {"PluginA": {"enabled": True}}
    updated = set_plugin_enabled(config_test, "PluginA", False)
    assert updated["plugins"]["PluginA"]["enabled"] == False
    assert config_test["plugins"]["PluginA"]["enabled"] == True, "Original should be unchanged"
    updated2 = set_plugin_enabled(config_test, "PluginB", True)
    assert updated2["plugins"]["PluginB"]["enabled"] == True
    print("  ✓ Passed\n")

    print("Testing set_vanilla...")
    config_test2 = DEFAULT_CONFIG.copy()
    updated_vanilla = set_vanilla(config_test2, True)
    assert updated_vanilla["vanilla"] == True
    assert config_test2["vanilla"] == False, "Original should be unchanged"
    print("  ✓ Passed\n")

    print("Testing set_plugins_root...")
    config_test3 = DEFAULT_CONFIG.copy()
    updated_root = set_plugins_root(config_test3, "/new/path")
    assert updated_root["plugins_root"] == "/new/path"
    assert config_test3["plugins_root"] == "", "Original should be unchanged"
    print("  ✓ Passed\n")

    print("All tests passed!")
