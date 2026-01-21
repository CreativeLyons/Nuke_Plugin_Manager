try:
    import nuke
    import sys
    from pathlib import Path

    # Add core/ to path (works regardless of CWD)
    core_dir = Path(__file__).parent / "core"
    if core_dir.exists() and str(core_dir) not in sys.path:
        sys.path.insert(0, str(core_dir))

    from loader import apply_plugin_paths

    # Put your config somewhere stable:
    # Option A (recommended): inside ~/.nuke/Nuke_Plugin_Manager/
    # If None, uses default user config path with baseline copy
    config_path = None  # Uses ~/.nuke/Nuke_Plugin_Manager/plugin_manager.json

    apply_plugin_paths(nuke, config_path)

except Exception:
    pass
