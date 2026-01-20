"""
Configuration management for Nuke Plugin Manager.

Handles loading and saving the plugin manager JSON configuration file
with schema versioning and defensive error handling.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any


# Schema version
SCHEMA_VERSION = 1

# Default configuration
DEFAULT_CONFIG = {
    "schema_version": SCHEMA_VERSION,
    "vanilla": False,
    "plugins_root": "",
    "plugins": {}
}


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Returns default configuration if:
    - File does not exist
    - JSON is invalid
    - Required keys are missing

    Never raises exceptions - always returns a valid config dict.

    Args:
        config_path: Path to the JSON configuration file

    Returns:
        Dictionary containing the loaded configuration merged with defaults
    """
    config_file = Path(config_path)

    # Return defaults if file doesn't exist
    if not config_file.exists():
        return DEFAULT_CONFIG.copy()

    # Return defaults if not a file
    if not config_file.is_file():
        return DEFAULT_CONFIG.copy()

    try:
        # Read and parse JSON
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)

        # Ensure it's a dictionary
        if not isinstance(loaded_config, dict):
            return DEFAULT_CONFIG.copy()

        # Merge with defaults to ensure all keys exist
        config = DEFAULT_CONFIG.copy()
        config.update(loaded_config)

        # Ensure schema_version is set correctly
        config["schema_version"] = SCHEMA_VERSION

        # Validate and coerce types
        if not isinstance(config.get("vanilla"), bool):
            config["vanilla"] = DEFAULT_CONFIG["vanilla"]

        if not isinstance(config.get("plugins_root"), str):
            config["plugins_root"] = DEFAULT_CONFIG["plugins_root"]

        if not isinstance(config.get("plugins"), dict):
            config["plugins"] = DEFAULT_CONFIG["plugins"]

        return config

    except (json.JSONDecodeError, IOError, OSError, PermissionError):
        # Return defaults on any error (invalid JSON, read error, permission error, etc.)
        return DEFAULT_CONFIG.copy()


def save_config(config_path: str, config: Dict[str, Any]) -> bool:
    """
    Save configuration to a JSON file atomically.

    Writes to a temporary file first, then renames it to the target path
    to ensure atomic writes. This prevents corruption if the process
    is interrupted during writing.

    Args:
        config_path: Path where the configuration file should be saved
        config: Configuration dictionary to save

    Returns:
        True if save was successful, False otherwise
    """
    if not isinstance(config, dict):
        return False

    config_file = Path(config_path)

    # Ensure schema_version is set
    config_to_save = config.copy()
    config_to_save["schema_version"] = SCHEMA_VERSION

    # Ensure all required keys exist with defaults
    if "vanilla" not in config_to_save:
        config_to_save["vanilla"] = DEFAULT_CONFIG["vanilla"]
    if "plugins_root" not in config_to_save:
        config_to_save["plugins_root"] = DEFAULT_CONFIG["plugins_root"]
    if "plugins" not in config_to_save:
        config_to_save["plugins"] = DEFAULT_CONFIG["plugins"]

    try:
        # Create parent directory if it doesn't exist
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically: write to temp file, then rename
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=config_file.parent,
            delete=False,
            suffix='.tmp'
        ) as tmp_file:
            json.dump(
                config_to_save,
                tmp_file,
                indent=2,
                ensure_ascii=False
            )
            tmp_path = tmp_file.name

        # Atomic rename
        os.replace(tmp_path, config_file)
        return True

    except (IOError, OSError, PermissionError, json.JSONEncodeError):
        # Clean up temp file if it exists
        try:
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
        except OSError:
            pass
        return False
