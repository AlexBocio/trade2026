# setup.ps1 - Advanced Backtesting Engine Setup Script

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Advanced Backtesting Engine - Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check Python version (must be 3.11+)
$pythonVersionNumber = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$majorVersion = [int]($pythonVersionNumber.Split('.')[0])
$minorVersion = [int]($pythonVersionNumber.Split('.')[1])

if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 11)) {
    Write-Host "ERROR: Python 3.11+ is required (found $pythonVersionNumber)" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Failed to upgrade pip (continuing anyway)" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ pip upgraded" -ForegroundColor Green
}
Write-Host ""

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "Try running manually: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}
Write-Host "  ✓ All dependencies installed" -ForegroundColor Green
Write-Host ""

# Verify key packages
Write-Host "Verifying installation..." -ForegroundColor Yellow
$packages = @("flask", "pandas", "numpy", "scipy", "sklearn", "yfinance")
$allInstalled = $true

foreach ($package in $packages) {
    $checkResult = python -c "import $package" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $package" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $package (failed to import)" -ForegroundColor Red
        $allInstalled = $false
    }
}
Write-Host ""

if (-not $allInstalled) {
    Write-Host "WARNING: Some packages failed to import" -ForegroundColor Yellow
    Write-Host "You may need to install them manually" -ForegroundColor Yellow
    Write-Host ""
}

# Create models directory (if needed for future use)
if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
    Write-Host "  ✓ Created models directory" -ForegroundColor Green
}

# Display next steps
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start the server:" -ForegroundColor White
Write-Host "     python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Server will run on:" -ForegroundColor White
Write-Host "     http://localhost:5003" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Available endpoints:" -ForegroundColor White
Write-Host "     POST /api/backtest/walk-forward" -ForegroundColor Cyan
Write-Host "     POST /api/backtest/cross-validation" -ForegroundColor Cyan
Write-Host "     POST /api/backtest/robustness" -ForegroundColor Cyan
Write-Host "     POST /api/backtest/comprehensive" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. See README.md for API examples and documentation" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to start the server now
$startNow = Read-Host "Start the server now? (y/n)"
if ($startNow -eq "y" -or $startNow -eq "Y") {
    Write-Host ""
    Write-Host "Starting Advanced Backtesting Engine..." -ForegroundColor Green
    Write-Host ""
    python app.py
}
