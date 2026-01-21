@echo off
REM Double-click installer for Nuke Plugin Manager launcher (Windows)
REM This creates/uses a venv and launches the panel

REM Get the directory where this script is located (install\ folder)
set "SCRIPT_DIR=%~dp0"

REM Change to the Nuke_Plugin_Manager tool root (parent of install\)
set "TOOL_ROOT=%SCRIPT_DIR%.."
cd /d "%TOOL_ROOT%"

REM Run the panel via bootstrap
python core\run_panel.py

REM Keep window open so user can see the result
echo.
echo Press any key to close this window...
pause >nul
