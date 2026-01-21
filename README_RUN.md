# Running the Nuke Plugin Manager GUI

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Setup Instructions

1. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment**:

   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   venv\Scripts\activate
   ```

3. **Install PySide6**:
   ```bash
   pip install PySide6
   ```

4. **Run the application**:

   From the installable folder (`Nuke_Plugin_Manager/`):
   ```bash
   cd Nuke_Plugin_Manager
   python core/run_app.py
   ```

   Or directly:
   ```bash
   cd Nuke_Plugin_Manager
   python -c "import sys; sys.path.insert(0, 'core'); from app import main; main()"
   ```

   Or with a custom config path:
   ```bash
   cd Nuke_Plugin_Manager
   python core/run_app.py --config /path/to/your/config.json
   ```

## Default Configuration

If no `--config` argument is provided, the application will use `~/.nuke/Nuke_Plugin_Manager/plugin_manager.json` (with baseline copy from `default_config.json` if available).

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```
