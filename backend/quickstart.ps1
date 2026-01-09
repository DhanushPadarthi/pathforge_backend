# Quick Start Script for PathForge Backend
# Run this script to check prerequisites and setup

Write-Host "🚀 PathForge Backend Quick Start" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "✓ Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor Green

# Check if MongoDB is running
Write-Host ""
Write-Host "✓ Checking MongoDB connection..." -ForegroundColor Yellow
try {
    $mongoTest = Test-NetConnection -ComputerName localhost -Port 27017 -WarningAction SilentlyContinue
    if ($mongoTest.TcpTestSucceeded) {
        Write-Host "  MongoDB is running on localhost:27017" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ MongoDB is not running. Please start MongoDB Compass." -ForegroundColor Red
        Write-Host "  Download from: https://www.mongodb.com/products/compass" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ Could not check MongoDB status" -ForegroundColor Yellow
}

# Check if virtual environment exists
Write-Host ""
Write-Host "✓ Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "  Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "✓ Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "  Virtual environment activated" -ForegroundColor Green

# Check if requirements are installed
Write-Host ""
Write-Host "✓ Checking dependencies..." -ForegroundColor Yellow
$installedPackages = pip list
if ($installedPackages -match "fastapi") {
    Write-Host "  Dependencies already installed" -ForegroundColor Green
} else {
    Write-Host "  Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "  Dependencies installed" -ForegroundColor Green
}

# Check if .env exists
Write-Host ""
Write-Host "✓ Checking environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  .env file exists" -ForegroundColor Green
} else {
    Write-Host "  Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  ⚠ Please edit .env file with your API keys" -ForegroundColor Red
    Write-Host "  Required: OPENAI_API_KEY, FIREBASE_CREDENTIALS_PATH" -ForegroundColor Yellow
}

# Check Firebase credentials
Write-Host ""
Write-Host "✓ Checking Firebase credentials..." -ForegroundColor Yellow
if (Test-Path "firebase-credentials.json") {
    Write-Host "  Firebase credentials found" -ForegroundColor Green
} else {
    Write-Host "  ⚠ firebase-credentials.json not found" -ForegroundColor Red
    Write-Host "  Download from Firebase Console > Project Settings > Service Accounts" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ensure MongoDB is running" -ForegroundColor White
Write-Host "2. Edit .env file with your API keys" -ForegroundColor White
Write-Host "3. Add firebase-credentials.json file" -ForegroundColor White
Write-Host "4. Run: python scripts/seed_data.py" -ForegroundColor White
Write-Host "5. Run: uvicorn main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - Setup Guide: SETUP_GUIDE.md" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "✨ Ready to code!" -ForegroundColor Green
