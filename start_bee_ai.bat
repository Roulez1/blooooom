@echo off
title Bee AI Auto-Startup
echo.
echo ========================================
echo    🐝 Bee AI Auto-Startup System
echo ========================================
echo.

REM Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PowerShell not available. Using fallback method...
    goto :fallback
)

echo 🚀 Starting Bee AI System with PowerShell...
powershell -ExecutionPolicy Bypass -File "start_bee_ai.ps1" start

if %errorlevel% equ 0 (
    echo.
    echo ✅ Bee AI System started successfully!
    echo 🌐 Opening application in browser...
    timeout /t 2 /nobreak >nul
    start "" "start_bee_ai.html"
) else (
    echo.
    echo ❌ Failed to start with PowerShell. Using fallback method...
    goto :fallback
)

goto :end

:fallback
echo.
echo 🔄 Using fallback startup method...
echo 📋 Starting Python server manually...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python first.
    echo 📥 Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if config.py exists
if not exist "config.py" (
    echo ❌ config.py not found. Please create it with your API key.
    echo 📝 Example: GEMINI_API_KEY = "your_api_key_here"
    pause
    exit /b 1
)

REM Install requirements if needed
echo 📦 Checking dependencies...
pip install -r requirements_gemini.txt >nul 2>&1

REM Start the server
echo 🚀 Starting Gemini AI server...
start /min python bee_ai_gemini_server.py

REM Wait a moment for server to start
echo ⏳ Waiting for server to initialize...
timeout /t 5 /nobreak >nul

REM Open the startup page
echo 🌐 Opening application...
start "" "start_bee_ai.html"

:end
echo.
echo 🎉 Bee AI System is ready!
echo 💡 You can now use the application in your browser.
echo.
echo 📋 Available commands:
echo    - Double-click start_bee_ai.html to restart
echo    - Run start_gemini_ai.bat for manual control
echo    - Press Ctrl+C in the server window to stop
echo.
pause
