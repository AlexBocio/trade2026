# setup.ps1 - Automated setup script for Fractional Differentiation Engine
# Port: 5006

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fractional Differentiation Engine Setup" -ForegroundColor Cyan
Write-Host "Port: 5006" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# =============================================================================
# STEP 1: Check Python Installation
# =============================================================================

Write-Host "[1/7] Checking Python installation..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green

    # Check version is 3.9+
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]

        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
            Write-Host "  ERROR: Python 3.9+ required, found $pythonVersion" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.9+" -ForegroundColor Red
    Write-Host "  Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# =============================================================================
# STEP 2: Create Virtual Environment
# =============================================================================

Write-Host "[2/7] Creating virtual environment..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists" -ForegroundColor Yellow
    $response = Read-Host "  Recreate? (y/n)"

    if ($response -eq "y") {
        Write-Host "  Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "  Virtual environment recreated" -ForegroundColor Green
    } else {
        Write-Host "  Using existing virtual environment" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "  Virtual environment created" -ForegroundColor Green
}

Write-Host ""

# =============================================================================
# STEP 3: Activate Virtual Environment
# =============================================================================

Write-Host "[3/7] Activating virtual environment..." -ForegroundColor Yellow

$activateScript = ".\venv\Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "  Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Activation script not found" -ForegroundColor Red
    exit 1
}

Write-Host ""

# =============================================================================
# STEP 4: Upgrade pip
# =============================================================================

Write-Host "[4/7] Upgrading pip..." -ForegroundColor Yellow

python -m pip install --upgrade pip --quiet
Write-Host "  pip upgraded" -ForegroundColor Green

Write-Host ""

# =============================================================================
# STEP 5: Install Dependencies
# =============================================================================

Write-Host "[5/7] Installing dependencies..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    Write-Host "  Installing from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ERROR: requirements.txt not found" -ForegroundColor Red
    exit 1
}

Write-Host ""

# =============================================================================
# STEP 6: Run Tests
# =============================================================================

Write-Host "[6/7] Running tests..." -ForegroundColor Yellow

if (Test-Path "tests") {
    Write-Host "  Running pytest..." -ForegroundColor Yellow
    pytest tests/ -v --tb=short

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  All tests passed" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Some tests failed" -ForegroundColor Yellow
        Write-Host "  You can still start the server, but review test failures" -ForegroundColor Yellow
    }
} else {
    Write-Host "  WARNING: tests/ directory not found" -ForegroundColor Yellow
}

Write-Host ""

# =============================================================================
# STEP 7: Check Port Availability
# =============================================================================

Write-Host "[7/7] Checking port availability..." -ForegroundColor Yellow

$port = 5006
$portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if ($portInUse) {
    Write-Host "  WARNING: Port $port is already in use" -ForegroundColor Yellow
    Write-Host "  Process: $($portInUse.OwningProcess)" -ForegroundColor Yellow

    $response = Read-Host "  Kill process and continue? (y/n)"

    if ($response -eq "y") {
        Stop-Process -Id $portInUse.OwningProcess -Force
        Write-Host "  Process killed" -ForegroundColor Green
    } else {
        Write-Host "  Please free port $port manually or change PORT in config.py" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Port $port is available" -ForegroundColor Green
}

Write-Host ""

# =============================================================================
# SETUP COMPLETE
# =============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Start the server:" -ForegroundColor White
Write-Host "     python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Test the server:" -ForegroundColor White
Write-Host "     curl http://localhost:5006/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. View documentation:" -ForegroundColor White
Write-Host "     README.md" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to start server now
$startNow = Read-Host "Start server now? (y/n)"

if ($startNow -eq "y") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Starting Fractional Differentiation Engine" -ForegroundColor Cyan
    Write-Host "Port: 5006" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""

    python app.py
} else {
    Write-Host ""
    Write-Host "To start the server later, run:" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "  python app.py" -ForegroundColor Cyan
    Write-Host ""
}

# =============================================================================
# CONFIGURATION INFO
# =============================================================================

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Service: Fractional Differentiation Engine" -ForegroundColor White
Write-Host "  Port: 5006" -ForegroundColor White
Write-Host "  Endpoints:" -ForegroundColor White
Write-Host "    - GET  /health" -ForegroundColor Cyan
Write-Host "    - POST /api/fracdiff/transform" -ForegroundColor Cyan
Write-Host "    - POST /api/fracdiff/find-optimal-d" -ForegroundColor Cyan
Write-Host "    - POST /api/fracdiff/compare" -ForegroundColor Cyan
Write-Host "    - POST /api/fracdiff/batch" -ForegroundColor Cyan
Write-Host "    - POST /api/fracdiff/stationarity-test" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# VERIFICATION INSTRUCTIONS
# =============================================================================

Write-Host "Verification:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Health check:" -ForegroundColor White
Write-Host "     curl http://localhost:5006/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Transform test:" -ForegroundColor White
Write-Host "     curl -X POST http://localhost:5006/api/fracdiff/transform \" -ForegroundColor Cyan
Write-Host "       -H 'Content-Type: application/json' \" -ForegroundColor Cyan
Write-Host "       -d '{\"values\": [100, 102, 101, 103, 105], \"d\": 0.5}'" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Find optimal d:" -ForegroundColor White
Write-Host "     curl -X POST http://localhost:5006/api/fracdiff/find-optimal-d \" -ForegroundColor Cyan
Write-Host "       -H 'Content-Type: application/json' \" -ForegroundColor Cyan
Write-Host "       -d '{\"ticker\": \"SPY\", \"d_range\": [0, 1], \"step\": 0.1}'" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# TROUBLESHOOTING
# =============================================================================

Write-Host "Troubleshooting:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Port in use:" -ForegroundColor White
Write-Host "    netstat -ano | findstr :5006" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Import errors:" -ForegroundColor White
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "    pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Run tests:" -ForegroundColor White
Write-Host "    pytest tests/ -v" -ForegroundColor Cyan
Write-Host ""

Write-Host "For more information, see README.md" -ForegroundColor Yellow
Write-Host ""
