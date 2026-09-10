@echo off
setlocal

rem ============================================================
rem  startup.bat - Start QMT Trade MCP server
rem  Location: <project-root>\scripts\startup.bat
rem  The project root is derived from this script's location,
rem  so do not move this file out of the "scripts" folder.
rem ============================================================

rem --- Locate project root (parent of the scripts folder) ---
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.." >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to locate project root from %SCRIPT_DIR%
    exit /b 1
)
set "ROOT=%CD%"
popd

if not exist "%ROOT%\main.py" (
    echo [ERROR] main.py not found in %ROOT%
    echo Please keep this script inside the project's "scripts" folder.
    exit /b 1
)

where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] "uv" was not found in PATH.
    echo Install it first: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)

cd /d "%ROOT%"
echo [INFO] Project root : %ROOT%
echo [INFO] Starting QMT Trade MCP server ...
uv run python main.py

endlocal
