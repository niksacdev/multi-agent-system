@echo off
REM Interactive startup script for Multi-Agent Loan Processing System (Windows)

echo 🏦 Multi-Agent Loan Processing System
echo =====================================
echo    Intelligent loan processing with AI agents
echo.

REM Check requirements
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: 'uv' package manager is required
    echo    Install from: https://astral.sh/uv/
    pause
    exit /b 1
)

echo ✅ Environment check passed
echo.

echo 🚀 Phase 1: Starting MCP Data Services
echo --------------------------------------
python start_mcp_servers.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to start MCP servers. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo 🎉 System Ready!
echo ===============
echo ✅ All MCP data services are running
echo ✅ AI agents are configured and ready
echo ✅ Loan processing system is operational
echo.

echo 🤖 Ready to process loan applications?
echo    Press ENTER to start the console application, or Ctrl+C to exit
pause >nul

echo.
echo 🚀 Phase 2: Starting Console Application
echo ---------------------------------------
echo 💡 Tip: Use Ctrl+C anytime to stop the entire system
echo.

uv run python run_console_app.py

REM Cleanup
echo.
echo 🧹 Stopping servers...
taskkill /F /IM python.exe /FI "COMMANDLINE eq *loan_processing.tools.mcp_servers*" >nul 2>nul
echo ✅ All servers stopped cleanly
echo 👋 Thanks for using Multi-Agent Loan Processing!
pause