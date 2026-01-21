"""
Configuration management for Nuke Plugin Manager.

Handles loading and saving the plugin manager JSON configuration file
with schema versioning and defensive error handling.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional


# Schema version
SCHEMA_VERSION = 2

# Default configuration (v2)
DEFAULT_CONFIG = {
    "schema_version": SCHEMA_VERSION,
    "vanilla": False,
    "plugins_root": "",
    "roots": {}
}


def get_default_user_config_path() -> Path:
    """
    Get the default user config file path.

    Returns:
        Path to ~/.nuke/Nuke_Plugin_Manager/plugin_manager.json
    """
    home = Path.home()
    config_dir = home / ".nuke" / "Nuke_Plugin_Manager"
    return config_dir / "plugin_manager.json"


def resolve_baseline_config_path() -> Optional[Path]:
    """
    Resolve the baseline config file path.

    Checks:
    1. NUKE_PLUGIN_MANAGER_BASELINE environment variable
    2. default_config.json next to this module (config.py)

    Returns:
        Path to baseline config if found, None otherwise
    """
    # Check environment variable
    env_baseline = os.environ.get("NUKE_PLUGIN_MANAGER_BASELINE")
    if env_baseline:
        baseline_path = Path(env_baseline).expanduser().resolve()
        if baseline_path.exists() and baseline_path.is_file():
            return baseline_path

    # Look for default_config.json next to this module (in core/)
    module_dir = Path(__file__).parent
    default_config = module_dir / "default_config.json"
    if default_config.exists() and default_config.is_file():
        return default_config

    return None


def ensure_user_config(user_config_path: Path, use_baseline: bool = True) -> bool:
    """
    Ensure user config file exists, copying from baseline if needed.

    If user config doesn't exist:
    - If use_baseline is True and baseline exists: copy baseline → user config
    - Else: create default config at user config path

    Args:
        user_config_path: Path where user config should exist
        use_baseline: If True, try to copy baseline config if user config is missing

    Returns:
        True if user config now exists (was created or already existed), False otherwise
    """
    # If user config already exists, nothing to do
    if user_config_path.exists():
        return True

    # Try to copy baseline if requested
    if use_baseline:
        baseline_path = resolve_baseline_config_path()
        if baseline_path:
            try:
                # Create parent directory
                user_config_path.parent.mkdir(parents=True, exist_ok=True)
                # Copy baseline to user location
                shutil.copy2(baseline_path, user_config_path)
                return True
            except (IOError, OSError, PermissionError):
                # If copy fails, fall through to create defaults
                pass

    # Create default config
    try:
        user_config_path.parent.mkdir(parents=True, exist_ok=True)
        save_config(str(user_config_path), DEFAULT_CONFIG.copy())
        return True
    except (IOError, OSError, PermissionError):
        return False


def _migrate_v1_to_v2(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate schema v1 config to v2 format.

    Moves plugins dict to roots[plugins_root]["plugins"].
    Preserves all data.

    Args:
        config: v1 config dictionary

    Returns:
        v2 config dictionary
    """
    if config.get("schema_version") != 1:
        return config

    migrated = config.copy()
    migrated["schema_version"] = 2

    plugins_root = migrated.get("plugins_root", "")
    plugins = migrated.get("plugins", {})

    # Remove old plugins key
    if "plugins" in migrated:
        del migrated["plugins"]

    # Initialize roots dict
    if "roots" not in migrated:
        migrated["roots"] = {}

    # Migrate plugins to roots[plugins_root]["plugins"]
    if plugins_root and plugins:
        if plugins_root not in migrated["roots"]:
            migrated["roots"][plugins_root] = {}
        migrated["roots"][plugins_root]["plugins"] = plugins

    return migrated


def load_config(config_path: str, return_status: bool = False):
    """
    Load configuration from a JSON file.

    Returns default configuration if:
    - File does not exist
    - JSON is invalid
    - Required keys are missing

    Never raises exceptions - always returns a valid config dict.

    Args:
        config_path: Path to the JSON configuration file
        return_status: If True, returns tuple (config, status) where status is
                      "ok", "missing", or "invalid"

    Returns:
        Dictionary containing the loaded configuration merged with defaults,
        or tuple (config, status) if return_status=True
    """
    config_file = Path(config_path)

    # Return defaults if file doesn't exist
    if not config_file.exists():
        if return_status:
            return (DEFAULT_CONFIG.copy(), "missing")
        return DEFAULT_CONFIG.copy()

    # Return defaults if not a file
    if not config_file.is_file():
        if return_status:
            return (DEFAULT_CONFIG.copy(), "missing")
        return DEFAULT_CONFIG.copy()

    try:
        # Read and parse JSON
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)

        # Ensure it's a dictionary
        if not isinstance(loaded_config, dict):
            if return_status:
                return (DEFAULT_CONFIG.copy(), "invalid")
            return DEFAULT_CONFIG.copy()

        # Get schema version
        schema_version = loaded_config.get("schema_version", SCHEMA_VERSION)

        # Migrate v1 to v2 if needed
        if schema_version == 1:
            config = _migrate_v1_to_v2(loaded_config)
        else:
            config = loaded_config.copy()

        # Merge with defaults to ensure all keys exist
        default_config = DEFAULT_CONFIG.copy()
        default_config.update(config)
        config = default_config

        # Ensure schema_version is set correctly
        config["schema_version"] = SCHEMA_VERSION

        # Validate and coerce types
        if not isinstance(config.get("vanilla"), bool):
            config["vanilla"] = DEFAULT_CONFIG["vanilla"]

        if not isinstance(config.get("plugins_root"), str):
            config["plugins_root"] = DEFAULT_CONFIG["plugins_root"]

        if not isinstance(config.get("roots"), dict):
            config["roots"] = DEFAULT_CONFIG["roots"]

        if return_status:
            return (config, "ok")
        return config

    except (json.JSONDecodeError, IOError, OSError, PermissionError):
        # Return defaults on any error (invalid JSON, read error, permission error, etc.)
        if return_status:
            return (DEFAULT_CONFIG.copy(), "invalid")
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

    # Migrate v1 to v2 if needed before saving
    schema_version = config.get("schema_version", SCHEMA_VERSION)
    if schema_version == 1:
        config = _migrate_v1_to_v2(config)

    # Ensure schema_version is set
    config_to_save = config.copy()
    config_to_save["schema_version"] = SCHEMA_VERSION

    # Ensure all required keys exist with defaults
    if "vanilla" not in config_to_save:
        config_to_save["vanilla"] = DEFAULT_CONFIG["vanilla"]
    if "plugins_root" not in config_to_save:
        config_to_save["plugins_root"] = DEFAULT_CONFIG["plugins_root"]
    if "roots" not in config_to_save:
        config_to_save["roots"] = DEFAULT_CONFIG["roots"]

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
