"""
Plugin state management for Nuke Plugin Manager.

Merges plugin discovery results with configuration to produce
a unified plugin state for the UI/loader.
"""

from typing import Dict, Any, List
from pathlib import Path

from plugin_discovery import discover_plugins


def build_plugin_state(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build plugin state by merging discovery results with configuration.

    Discovers plugins from the configured plugins_root directory and merges
    them with configuration settings to produce a unified state.

    Args:
        config: Configuration dictionary containing plugins_root, vanilla, and plugins

    Returns:
        Dictionary with keys:
        - vanilla (bool): Vanilla mode setting
        - plugins_root (str): Plugins root directory path
        - plugins (list): List of plugin dictionaries, each containing:
          - name (str): Plugin name
          - path (str): Full path to plugin folder
          - underscore_disabled (bool): True if folder is prefixed with '_'
          - enabled (bool): Whether plugin is enabled (False if underscore_disabled)
          - max_nuke_major (int|None): Maximum Nuke major version, or None
    """
    # Extract values from config with defaults
    vanilla = config.get("vanilla", False)
    plugins_root = config.get("plugins_root", "")

    # Get plugins config from active root (v2 schema)
    # Normalize plugins_root to absolute path for consistent lookup
    if plugins_root:
        plugins_root_abs = str(Path(plugins_root).resolve())
    else:
        plugins_root_abs = ""

    roots = config.get("roots", {})
    active_root_config = roots.get(plugins_root_abs, {})
    plugins_config = active_root_config.get("plugins", {})

    # If plugins_root is empty or invalid, return empty plugins list
    if not plugins_root or not isinstance(plugins_root, str):
        return {
            "vanilla": bool(vanilla),
            "plugins_root": str(plugins_root) if plugins_root else "",
            "plugins": []
        }

    # Discover plugins, handling errors gracefully
    try:
        discovered_plugins = discover_plugins(plugins_root)
    except (ValueError, OSError):
        # Return empty plugins list if discovery fails (invalid path, permission error, etc.)
        return {
            "vanilla": bool(vanilla),
            "plugins_root": plugins_root,
            "plugins": []
        }

    # Build plugin state list
    plugins_state = []
    for plugin_info in discovered_plugins:
        plugin_name = plugin_info.name
        underscore_disabled = not plugin_info.enabled

        # Get plugin config, defaulting to empty dict if not found
        plugin_config = plugins_config.get(plugin_name, {})

        # Get enabled state from config, defaulting to True
        # But force False if underscore_disabled
        config_enabled = plugin_config.get("enabled", True)
        enabled = config_enabled if not underscore_disabled else False

        # Get max_nuke_major from config
        max_nuke_major = plugin_config.get("max_nuke_major", None)
        if max_nuke_major is not None:
            # Ensure it's an int or None
            try:
                max_nuke_major = int(max_nuke_major)
            except (ValueError, TypeError):
                max_nuke_major = None

        plugin_entry = {
            "name": plugin_name,
            "path": str(plugin_info.path),
            "underscore_disabled": underscore_disabled,
            "enabled": enabled,
            "max_nuke_major": max_nuke_major
        }
        plugins_state.append(plugin_entry)

    return {
        "vanilla": bool(vanilla),
        "plugins_root": plugins_root,
        "plugins": plugins_state
    }


def set_plugin_enabled(config: Dict[str, Any], plugin_name: str, enabled: bool) -> Dict[str, Any]:
    """
    Set the enabled state for a plugin in the configuration.

    Returns a new config dictionary with the updated plugin state.
    Does not save the configuration to disk.

    Plugin state is scoped to the active plugins_root (v2 schema).

    Args:
        config: Configuration dictionary to update
        plugin_name: Name of the plugin to update
        enabled: Whether the plugin should be enabled

    Returns:
        New configuration dictionary with updated plugin state
    """
    # Create a copy to avoid mutating the original
    updated_config = config.copy()

    # Get active plugins_root
    plugins_root = updated_config.get("plugins_root", "")
    if not plugins_root:
        return updated_config

    # Normalize to absolute path for consistent lookup
    plugins_root_abs = str(Path(plugins_root).resolve())

    # Ensure roots dict exists
    if "roots" not in updated_config:
        updated_config["roots"] = {}

    # Ensure active root entry exists
    if plugins_root_abs not in updated_config["roots"]:
        updated_config["roots"][plugins_root_abs] = {}

    # Ensure plugins dict exists in active root
    if "plugins" not in updated_config["roots"][plugins_root_abs]:
        updated_config["roots"][plugins_root_abs]["plugins"] = {}

    # Ensure plugin entry exists
    if plugin_name not in updated_config["roots"][plugins_root_abs]["plugins"]:
        updated_config["roots"][plugins_root_abs]["plugins"][plugin_name] = {}

    # Create a copy of the plugin config
    plugin_config = updated_config["roots"][plugins_root_abs]["plugins"][plugin_name].copy()
    plugin_config["enabled"] = bool(enabled)

    # Update the plugins dict
    updated_config["roots"] = updated_config["roots"].copy()
    updated_config["roots"][plugins_root_abs] = updated_config["roots"][plugins_root_abs].copy()
    updated_config["roots"][plugins_root_abs]["plugins"] = updated_config["roots"][plugins_root_abs]["plugins"].copy()
    updated_config["roots"][plugins_root_abs]["plugins"][plugin_name] = plugin_config

    return updated_config


def set_vanilla(config: Dict[str, Any], vanilla: bool) -> Dict[str, Any]:
    """
    Set the vanilla mode setting in the configuration.

    Returns a new config dictionary with the updated vanilla setting.
    Does not save the configuration to disk.

    Args:
        config: Configuration dictionary to update
        vanilla: Whether vanilla mode should be enabled

    Returns:
        New configuration dictionary with updated vanilla setting
    """
    updated_config = config.copy()
    updated_config["vanilla"] = bool(vanilla)
    return updated_config


def set_plugins_root(config: Dict[str, Any], plugins_root: str) -> Dict[str, Any]:
    """
    Set the plugins root directory path in the configuration.

    Returns a new config dictionary with the updated plugins_root setting.
    Does not save the configuration to disk.

    Ensures roots dict exists (v2 schema).

    Args:
        config: Configuration dictionary to update
        plugins_root: Path to the plugins root directory

    Returns:
        New configuration dictionary with updated plugins_root setting
    """
    updated_config = config.copy()
    updated_config["plugins_root"] = str(plugins_root)

    # Ensure roots dict exists (v2 schema)
    if "roots" not in updated_config:
        updated_config["roots"] = {}

    return updated_config
