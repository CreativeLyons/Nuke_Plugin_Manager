@echo off
REM Double-click installer for Nuke Plugin Manager launcher (Windows)
REM This creates the .bat launcher in %USERPROFILE%\.nuke\Nuke_Plugin_Manager\

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Change to the Nuke_Plugin_Manager directory
cd /d "%SCRIPT_DIR%"

REM Run the installer
python core\install_launcher.py

REM Keep window open so user can see the result
echo.
echo Press any key to close this window...
pause >nul
