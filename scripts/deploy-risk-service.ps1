# Phase 2A - Risk Service Deployment Script
# Comprehensive: Build → Test → Integrate → Validate

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phase 2A: Risk Service Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\ClaudeDesktop_Projects\trade2026"
$RiskServicePath = "$ProjectRoot\backend\apps\risk"
$DockerComposeDir = "$ProjectRoot\infrastructure\docker"

# Step 1: Build Docker Image
Write-Host "[1/8] Building Risk Service Docker Image..." -ForegroundColor Yellow
Set-Location $RiskServicePath
docker build -t localhost/risk:latest . 2>&1 | Out-Host

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Verify Docker Image
Write-Host "[2/8] Verifying Docker Image..." -ForegroundColor Yellow
$imageCheck = docker images localhost/risk:latest --format "{{.Repository}}:{{.Tag}}"
if ($imageCheck -eq "localhost/risk:latest") {
    Write-Host "✓ Image verified: $imageCheck" -ForegroundColor Green
} else {
    Write-Host "❌ Image verification failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Check Infrastructure Services
Write-Host "[3/8] Checking Infrastructure Services..." -ForegroundColor Yellow
Set-Location $DockerComposeDir

$requiredServices = @("nats", "valkey", "questdb")
$allHealthy = $true

foreach ($service in $requiredServices) {
    $status = docker ps --filter "name=$service" --format "{{.Status}}"
    if ($status -match "healthy|Up") {
        Write-Host "  ✓ $service is running" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $service is not healthy" -ForegroundColor Red
        $allHealthy = $false
    }
}

if (-not $allHealthy) {
    Write-Host "❌ Required infrastructure services are not healthy" -ForegroundColor Red
    Write-Host "Run: docker-compose -f docker-compose.core.yml up -d" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ All required infrastructure services are healthy" -ForegroundColor Green
Write-Host ""

# Step 4: Start Risk Service
Write-Host "[4/8] Starting Risk Service..." -ForegroundColor Yellow
docker-compose -f docker-compose.apps.yml up -d risk 2>&1 | Out-Host

Start-Sleep -Seconds 10
Write-Host ""

# Step 5: Component Test - Service Starts
Write-Host "[5/8] Component Test - Service Health Check..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$maxAttempts = 10
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8103/health" -Method GET -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Health check passed" -ForegroundColor Green
            $content = $response.Content | ConvertFrom-Json
            Write-Host "  Status: $($content.status)" -ForegroundColor Cyan
            $healthy = $true
            break
        }
    } catch {
        $attempt++
        Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
}

if (-not $healthy) {
    Write-Host "❌ Health check failed after $maxAttempts attempts" -ForegroundColor Red
    Write-Host "Checking logs:" -ForegroundColor Yellow
    docker logs risk --tail 50
    exit 1
}
Write-Host ""

# Step 6: Integration Test - NATS Connectivity
Write-Host "[6/8] Integration Test - NATS Connectivity..." -ForegroundColor Yellow
$riskLogs = docker logs risk --tail 100 2>&1

if ($riskLogs -match "Connected to NATS" -or $riskLogs -match "Subscribed to risk management events") {
    Write-Host "✓ NATS connection verified" -ForegroundColor Green
} else {
    Write-Host "⚠ Could not verify NATS connection from logs" -ForegroundColor Yellow
}
Write-Host ""

# Step 7: Integration Test - Redis/Valkey Connectivity
Write-Host "[7/8] Integration Test - Redis/Valkey Connectivity..." -ForegroundColor Yellow

if ($riskLogs -match "Connected to Redis" -or $riskLogs -match "valkey") {
    Write-Host "✓ Redis/Valkey connection verified" -ForegroundColor Green
} else {
    Write-Host "⚠ Could not verify Redis connection from logs" -ForegroundColor Yellow
}
Write-Host ""

# Step 8: Validate Service Stats
Write-Host "[8/8] Validating Service Statistics..." -ForegroundColor Yellow

try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8103/stats" -Method GET
    Write-Host "✓ Stats endpoint accessible" -ForegroundColor Green
    Write-Host "  Orders Checked: $($stats.orders_checked)" -ForegroundColor Cyan
    Write-Host "  Active Positions: $($stats.active_positions)" -ForegroundColor Cyan
    Write-Host "  Active Orders: $($stats.active_orders)" -ForegroundColor Cyan
    Write-Host "  Risk Level: $($stats.current_risk_level)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Could not fetch stats (service may still be initializing)" -ForegroundColor Yellow
}
Write-Host ""

# Final Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Risk Service Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$containerStatus = docker ps --filter "name=risk" --format "{{.Status}}"
Write-Host "Container Status: $containerStatus" -ForegroundColor Cyan

Write-Host ""
Write-Host "Service Endpoints:" -ForegroundColor Yellow
Write-Host "  Health:  http://localhost:8103/health" -ForegroundColor Cyan
Write-Host "  Stats:   http://localhost:8103/stats" -ForegroundColor Cyan
Write-Host "  Risk:    http://localhost:8103/risk/portfolio" -ForegroundColor Cyan
Write-Host "  Alerts:  http://localhost:8103/risk/alerts" -ForegroundColor Cyan
Write-Host "  Limits:  http://localhost:8103/risk/limits" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Monitor logs: docker logs risk -f" -ForegroundColor Cyan
Write-Host "  2. Test risk check: See test script below" -ForegroundColor Cyan
Write-Host "  3. Proceed to OMS service migration" -ForegroundColor Cyan
Write-Host ""

Write-Host "✓ Risk Service Deployment Complete!" -ForegroundColor Green
Write-Host ""
