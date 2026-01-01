# PATHFORGE Backend Server Startup Script
# This script properly sets up the environment and starts the backend server

Write-Host "================================" -ForegroundColor Green
Write-Host "PATHFORGE Backend Server Startup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Step 1: Navigate to backend directory
Write-Host "[1/4] Navigating to backend directory..." -ForegroundColor Cyan
Set-Location D:\projects\PATHFORGE1\backend

# Step 2: Activate virtual environment
Write-Host "[2/4] Activating Python virtual environment..." -ForegroundColor Cyan
$venvPath = Join-Path (Get-Location) "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
} else {
    Write-Host "⚠️ Virtual environment not found, installing..." -ForegroundColor Yellow
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
}

# Step 3: Install/update dependencies
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Cyan
pip install -q -r requirements.txt 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some dependencies may not have installed, but continuing..." -ForegroundColor Yellow
}

# Step 4: Start the server
Write-Host "[4/4] Starting uvicorn server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Server starting on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "📚 API docs available at http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server with reload enabled
uvicorn main:app --reload --host 127.0.0.1 --port 8000
