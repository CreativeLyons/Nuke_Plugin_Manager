"""Simple test script to verify plugin discovery functionality."""

from plugin_discovery import discover_plugins, get_plugin_names, get_plugins_by_status

if __name__ == "__main__":
    # Test with the sandbox
    sandbox_path = "sandbox/plugins"

    print(f"Discovering plugins in: {sandbox_path}\n")

    # Test discover_plugins
    plugins = discover_plugins(sandbox_path)
    print(f"Found {len(plugins)} plugins:")
    for plugin in plugins:
        status = "✓ enabled" if plugin.enabled else "✗ disabled"
        print(f"  {status}: {plugin.name} ({plugin.path.name})")

    print("\n" + "="*50 + "\n")

    # Test get_plugin_names
    names = get_plugin_names(sandbox_path)
    print(f"Plugin names: {names}")

    print("\n" + "="*50 + "\n")

    # Test get_plugins_by_status
    by_status = get_plugins_by_status(sandbox_path)
    print(f"Enabled plugins ({len(by_status[True])}):")
    for plugin in by_status[True]:
        print(f"  - {plugin.name}")

    print(f"\nDisabled plugins ({len(by_status[False])}):")
    for plugin in by_status[False]:
        print(f"  - {plugin.name}")
