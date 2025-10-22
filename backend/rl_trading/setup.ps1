# RL Trading Setup Script for Windows PowerShell

Write-Host "🤖 Trade2025 RL Trading System - Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check Python
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install PyTorch (CPU version)
Write-Host "`nInstalling PyTorch..." -ForegroundColor Yellow
Write-Host "(Installing CPU version - for GPU, see PyTorch website)" -ForegroundColor Gray
pip install torch torchvision torchaudio

# Install other dependencies
Write-Host "`nInstalling other dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes)" -ForegroundColor Gray
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create models directory
Write-Host "`nCreating models directory..." -ForegroundColor Yellow
if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
    Write-Host "✓ Models directory created" -ForegroundColor Green
} else {
    Write-Host "Models directory already exists" -ForegroundColor Yellow
}

# Test imports
Write-Host "`nTesting imports..." -ForegroundColor Yellow
$testScript = @"
import torch
import numpy
import pandas
import flask
print('All imports successful!')
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
"@

$testResult = $testScript | python 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All packages imported successfully" -ForegroundColor Green
    Write-Host $testResult -ForegroundColor Gray
} else {
    Write-Host "⚠️  Some imports failed, but continuing..." -ForegroundColor Yellow
}

# Summary
Write-Host "`n✅ Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server:" -ForegroundColor Cyan
Write-Host "  1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  2. Run server: python app.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Server will be available at: http://localhost:5002" -ForegroundColor Cyan
Write-Host ""
Write-Host "Example usage:" -ForegroundColor Cyan
Write-Host "  Train DQN: curl -X POST http://localhost:5002/api/rl/train-dqn -H 'Content-Type: application/json' -d '{\"ticker\":\"AAPL\",\"episodes\":50}'" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run now, execute: python app.py" -ForegroundColor Green
