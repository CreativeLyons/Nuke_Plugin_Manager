# Nuke Plugin Manager

**Early release / experimental**

**Test with Vanilla first**

**No warranty; use at your own risk**

---

Panel that manages plugins you want loaded into Nuke at startup.

## Quick Start

1. **Drag the `Nuke_Plugin_Manager/` folder into `~/.nuke/`**
   - This installs the plugin manager locally

2. **Add to your Nuke `init.py`:**
   ```python
   nuke.pluginAddPath("Nuke_Plugin_Manager")
   ```

3. **Open the panel standalone:**
   - Double-click `Nuke_Plugin_Manager_Panel.app` in `~/.nuke/Nuke_Plugin_Manager/`
   - Or run: `python ~/.nuke/Nuke_Plugin_Manager/core/run_app.py`

## Features

- Visual plugin management GUI
- Per-plugin enable/disable controls
- Version gating (max Nuke version per plugin)
- Underscore-prefixed folders automatically disabled
- Studio baseline config support
- Schema v2: plugin state scoped per plugins root (no name collisions)

## Installation

See [README_RUN.md](README_RUN.md) for detailed setup instructions.
