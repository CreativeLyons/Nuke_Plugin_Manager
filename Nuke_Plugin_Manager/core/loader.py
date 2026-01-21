"""
Nuke plugin loader module.

Safely applies plugin paths to Nuke based on configuration,
handling vanilla mode, version gating, and enabled states.
"""

from typing import Optional
from pathlib import Path

from config import load_config
from plugin_state import build_plugin_state


def _get_nuke_major_version(nuke_module, provided_nuke_major: Optional[int] = None) -> Optional[int]:
    """
    Safely determine the current Nuke major version.

    Args:
        nuke_module: The nuke module object
        provided_nuke_major: Optional explicitly provided Nuke major version

    Returns:
        Nuke major version as int, or None if unable to determine
    """
    if provided_nuke_major is not None:
        return provided_nuke_major

    try:
        # Try to get version from nuke module
        if hasattr(nuke_module, 'NukeVersion'):
            version_string = str(nuke_module.NukeVersion())
            # NukeVersion() returns something like "14.0v1" or "14.0"
            # Extract major version (first number)
            major_version = int(version_string.split('.')[0])
            return major_version
    except (AttributeError, ValueError, TypeError, IndexError):
        pass

    try:
        # Alternative: try NUKE_VERSION_MAJOR if available
        if hasattr(nuke_module, 'NUKE_VERSION_MAJOR'):
            return int(nuke_module.NUKE_VERSION_MAJOR)
    except (AttributeError, ValueError, TypeError):
        pass

    # Unable to determine version
    return None


def apply_plugin_paths(
    nuke_module,
    config_path: Optional[str] = None,
    nuke_major: Optional[int] = None
) -> bool:
    """
    Apply plugin paths to Nuke based on configuration.

    Loads configuration, builds plugin state, and adds plugin paths to Nuke
    according to enabled state, underscore-disabled status, and version gating.

    Args:
        nuke_module: The nuke module object (must have pluginAddPath method)
        config_path: Optional path to the configuration JSON file.
                     If None, uses default user config path with baseline copy.
                     If provided, uses it directly (no baseline copy).
        nuke_major: Optional Nuke major version override (if None, attempts to detect)

    Returns:
        True if operation completed successfully, False on fatal errors
    """
    try:
        # Determine config path
        if config_path is None:
            # Use default user config path and ensure it exists (with baseline copy if needed)
            from config import get_default_user_config_path, ensure_user_config
            user_config_path = get_default_user_config_path()
            ensure_user_config(user_config_path, use_baseline=True)
            config_path = str(user_config_path)

        # Load configuration
        config = load_config(config_path)

        # Check vanilla mode - if enabled, don't add any paths
        if config.get("vanilla", False):
            return True

        # Build plugin state
        try:
            state = build_plugin_state(config)
        except Exception as e:
            print(f"Warning: Failed to build plugin state: {e}")
            return False

        # Get current Nuke major version
        current_nuke_major = _get_nuke_major_version(nuke_module, nuke_major)

        # Collect plugins that will be loaded
        plugins_to_load = []

        # Process each plugin
        plugins = state.get("plugins", [])
        for plugin in plugins:
            try:
                # Skip if underscore-disabled
                if plugin.get("underscore_disabled", False):
                    continue

                # Skip if not enabled
                if not plugin.get("enabled", False):
                    continue

                # Check max_nuke_major version gating
                max_nuke_major = plugin.get("max_nuke_major")
                if max_nuke_major is not None:
                    if current_nuke_major is None:
                        # Can't determine version, skip to be safe
                        print(f"Warning: Skipping plugin '{plugin.get('name', 'unknown')}' "
                              f"- unable to determine Nuke version")
                        continue
                    if current_nuke_major > max_nuke_major:
                        # Current version exceeds max, skip
                        continue

                # Add plugin path
                plugin_path = plugin.get("path")
                if plugin_path:
                    try:
                        # Get plugin name for logging
                        plugin_name = plugin.get("name", Path(plugin_path).name)
                        plugins_to_load.append((plugin_name, plugin_path))
                    except Exception as e:
                        print(f"Warning: Error preparing plugin '{plugin_path}': {e}")
                        continue

            except Exception as e:
                # Catch any errors processing individual plugins
                print(f"Warning: Error processing plugin: {e}")
                continue

        # Print loaded plugins list with separators at start and end
        if plugins_to_load:
            print("=" * 80)
            for plugin_name, plugin_path in plugins_to_load:
                try:
                    print(f"Loading {plugin_name}...")
                    nuke_module.pluginAddPath(plugin_path)
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Failed to add plugin path '{plugin_path}': {e}")
                    continue
                except Exception as e:
                    # Catch any other unexpected errors from pluginAddPath
                    print(f"Warning: Unexpected error adding plugin path '{plugin_path}': {e}")
                    continue
            print("=" * 80)

        return True

    except Exception as e:
        # Catch any fatal errors
        print(f"Error: Fatal error in apply_plugin_paths: {e}")
        return False
