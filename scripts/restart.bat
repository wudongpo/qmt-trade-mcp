@echo off
setlocal

rem ============================================================
rem  restart.bat - Restart QMT Trade MCP server
rem  Stops only the process currently LISTENING on MCP_PORT
rem  (default 8000, overridable via .env or environment var),
rem  then starts the server again via startup.bat.
rem  This script never deletes or modifies any files.
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

rem --- Resolve listening port: env var > .env > default 8000 ---
if not defined MCP_PORT set "MCP_PORT=8000"
if exist "%ROOT%\.env" (
    for /f "usebackq eol=# tokens=1,* delims==" %%a in ("%ROOT%\.env") do (
        if /i "%%a"=="MCP_PORT" set "MCP_PORT=%%b"
    )
)

echo [INFO] Looking for server listening on port %MCP_PORT% ...
set "KILLED="
for /f "tokens=5" %%p in ('netstat -ano -p tcp ^| findstr "LISTENING" ^| findstr ":%MCP_PORT% "') do (
    echo [INFO] Stopping process with PID %%p ...
    taskkill /PID %%p /F >nul 2>nul
    set "KILLED=1"
)
if not defined KILLED echo [INFO] No running server found on port %MCP_PORT%.

rem --- Wait for the port to be released ---
timeout /t 2 /nobreak >nul

echo [INFO] Starting server ...
call "%SCRIPT_DIR%startup.bat"

endlocal
