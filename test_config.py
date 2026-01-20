"""Simple test script to verify config functionality."""

import os
import tempfile
from config import load_config, save_config, DEFAULT_CONFIG

if __name__ == "__main__":
    # Create a temporary config file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        test_config_path = tmp.name

    try:
        print("Testing load_config with non-existent file...")
        config = load_config(test_config_path)
        print(f"  Result: {config}")
        assert config == DEFAULT_CONFIG, "Should return defaults"
        print("  ✓ Passed\n")

        print("Testing save_config...")
        test_config = {
            "schema_version": 1,
            "vanilla": True,
            "plugins_root": "/path/to/plugins",
            "plugins": {"PluginA": {"enabled": True}}
        }
        success = save_config(test_config_path, test_config)
        assert success, "Save should succeed"
        print(f"  ✓ Saved successfully\n")

        print("Testing load_config with existing file...")
        loaded = load_config(test_config_path)
        print(f"  Result: {loaded}")
        assert loaded["vanilla"] == True
        assert loaded["plugins_root"] == "/path/to/plugins"
        assert loaded["plugins"] == {"PluginA": {"enabled": True}}
        print("  ✓ Passed\n")

        print("Testing load_config with invalid JSON...")
        with open(test_config_path, 'w') as f:
            f.write("invalid json {")
        invalid_loaded = load_config(test_config_path)
        assert invalid_loaded == DEFAULT_CONFIG, "Should return defaults on invalid JSON"
        print("  ✓ Passed\n")

        print("Testing load_config with missing keys...")
        with open(test_config_path, 'w') as f:
            f.write('{"vanilla": true}')
        partial_loaded = load_config(test_config_path)
        assert partial_loaded["vanilla"] == True
        assert partial_loaded["plugins_root"] == ""  # Should use default
        assert partial_loaded["plugins"] == {}  # Should use default
        print("  ✓ Passed\n")

        print("All tests passed!")

    finally:
        # Clean up
        try:
            os.unlink(test_config_path)
        except OSError:
            pass
