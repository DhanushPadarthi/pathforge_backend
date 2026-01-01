@echo off
REM PATHFORGE Backend Server Startup Script for Windows CMD
REM This script properly sets up the environment and starts the backend server

cls
echo.
echo ================================
echo PATHFORGE Backend Server Startup
echo ================================
echo.

REM Step 1: Navigate to backend directory
echo [1/4] Navigating to backend directory...
cd /d D:\projects\PATHFORGE1\backend

REM Step 2: Activate virtual environment
echo [2/4] Activating Python virtual environment...
call venv\Scripts\activate.bat

REM Step 3: Install/update dependencies
echo [3/4] Installing dependencies...
pip install -q -r requirements.txt
if %errorlevel% equ 0 (
    echo.✅ Dependencies installed successfully
) else (
    echo.⚠️ Some dependencies may not have installed, but continuing...
)

REM Step 4: Start the server
echo [4/4] Starting uvicorn server...
echo.
echo 🚀 Server starting on http://127.0.0.1:8000
echo 📚 API docs available at http://127.0.0.1:8000/docs
echo Press CTRL+C to stop the server
echo.

REM Start the server with reload enabled
uvicorn main:app --reload --host 127.0.0.1 --port 8000
