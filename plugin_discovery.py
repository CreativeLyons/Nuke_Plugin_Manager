"""
Plugin folder discovery module for Nuke Plugin Manager.

Scans a configurable plugins root directory and returns a list of plugin folders,
excluding dotfolders and marking underscore-prefixed folders as disabled.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional


class PluginInfo:
    """Represents information about a discovered plugin folder."""

    def __init__(self, name: str, enabled: bool, path: Path):
        """
        Initialize PluginInfo.

        Args:
            name: Plugin folder name (without underscore prefix if disabled)
            enabled: Whether the plugin is enabled
            path: Full path to the plugin folder
        """
        self.name = name
        self.enabled = enabled
        self.path = path

    def __repr__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"PluginInfo(name='{self.name}', {status}, path={self.path})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, PluginInfo):
            return False
        return (self.name == other.name and
                self.enabled == other.enabled and
                self.path == other.path)


def discover_plugins(plugins_root: str) -> List[PluginInfo]:
    """
    Discover plugin folders in the specified root directory.

    Scans the plugins root directory and returns a list of PluginInfo objects
    representing each plugin folder found. Dotfolders (folders starting with '.')
    are excluded, and folders prefixed with '_' are marked as disabled.

    Args:
        plugins_root: Path to the root directory containing plugin folders

    Returns:
        List of PluginInfo objects, one for each discovered plugin folder

    Raises:
        ValueError: If plugins_root is not a valid directory
        OSError: If there are permission issues accessing the directory
    """
    plugins_root_path = Path(plugins_root)

    if not plugins_root_path.exists():
        raise ValueError(f"Plugins root directory does not exist: {plugins_root}")

    if not plugins_root_path.is_dir():
        raise ValueError(f"Plugins root path is not a directory: {plugins_root}")

    plugins = []

    try:
        for item in plugins_root_path.iterdir():
            # Skip if not a directory
            if not item.is_dir():
                continue

            folder_name = item.name

            # Exclude dotfolders (folders starting with '.')
            if folder_name.startswith('.'):
                continue

            # Check if folder is disabled (prefixed with '_')
            if folder_name.startswith('_'):
                # Remove the underscore prefix for the plugin name
                plugin_name = folder_name[1:]
                enabled = False
            else:
                plugin_name = folder_name
                enabled = True

            plugin_info = PluginInfo(
                name=plugin_name,
                enabled=enabled,
                path=item
            )
            plugins.append(plugin_info)

    except PermissionError as e:
        raise OSError(f"Permission denied accessing plugins directory: {plugins_root}") from e

    # Sort plugins by name for consistent ordering
    plugins.sort(key=lambda p: p.name.lower())

    return plugins


def get_plugin_names(plugins_root: str) -> List[str]:
    """
    Get a simple list of plugin folder names from the plugins root directory.

    This is a convenience function that returns just the plugin names without
    the full PluginInfo objects.

    Args:
        plugins_root: Path to the root directory containing plugin folders

    Returns:
        List of plugin folder names (strings)
    """
    plugins = discover_plugins(plugins_root)
    return [plugin.name for plugin in plugins]


def get_plugins_by_status(plugins_root: str) -> Dict[bool, List[PluginInfo]]:
    """
    Get plugins grouped by enabled/disabled status.

    Args:
        plugins_root: Path to the root directory containing plugin folders

    Returns:
        Dictionary with keys True (enabled) and False (disabled),
        each containing a list of PluginInfo objects
    """
    plugins = discover_plugins(plugins_root)
    result = {True: [], False: []}

    for plugin in plugins:
        result[plugin.enabled].append(plugin)

    return result
