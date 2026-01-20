try:
    import nuke
    from loader import apply_plugin_paths

    # Put your config somewhere stable:
    # Option A (recommended): inside ~/.nuke/
    config_path = nuke.toNode("root").knob("name").value()  # not reliable at startup; avoid

except Exception:
    pass
