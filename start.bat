@echo off
REM Simple startup script for Multi-Agent Loan Processing System

echo 🚀 Multi-Agent Loan Processing System
echo ======================================
echo.

REM Check requirements
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: 'uv' is required
    echo    Install from: https://astral.sh/uv/install.sh
    pause
    exit /b 1
)

echo 📋 Starting MCP servers...
python start_mcp_servers.py

echo.
echo 📋 Starting console application...
echo 💡 Press Ctrl+C to stop everything
echo.

uv run python run_console_app.py

REM Cleanup
echo.
echo 🧹 Stopping servers...
taskkill /F /IM python.exe /FI "COMMANDLINE eq *loan_processing.tools.mcp_servers*" >nul 2>nul
echo ✅ Cleanup completed
pause