# Risk Service - Comprehensive Testing Script
# Tests: Component → Integration → Performance → Validation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Risk Service - Comprehensive Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BaseUrl = "http://localhost:8103"
$TestsPassed = 0
$TestsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null
    )
    
    Write-Host "Testing: $Name..." -ForegroundColor Yellow
    
    try {
        if ($Body) {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body ($Body | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 5
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -TimeoutSec 5
        }
        
        Write-Host "  ✓ PASSED" -ForegroundColor Green
        $script:TestsPassed++
        return $response
    } catch {
        Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        $script:TestsFailed++
        return $null
    }
}

# Test 1: Health Check
Write-Host "[1/10] Component Test - Health Check" -ForegroundColor Cyan
$health = Test-Endpoint -Name "Health Check" -Url "$BaseUrl/health"
if ($health) {
    Write-Host "  Service Status: $($health.status)" -ForegroundColor Gray
}
Write-Host ""

# Test 2: Service Stats
Write-Host "[2/10] Component Test - Service Statistics" -ForegroundColor Cyan
$stats = Test-Endpoint -Name "Service Stats" -Url "$BaseUrl/stats"
if ($stats) {
    Write-Host "  Orders Checked: $($stats.orders_checked)" -ForegroundColor Gray
    Write-Host "  Active Positions: $($stats.active_positions)" -ForegroundColor Gray
    Write-Host "  Risk Level: $($stats.current_risk_level)" -ForegroundColor Gray
}
Write-Host ""

# Test 3: Risk Limits
Write-Host "[3/10] Component Test - Risk Limits Configuration" -ForegroundColor Cyan
$limits = Test-Endpoint -Name "Risk Limits" -Url "$BaseUrl/risk/limits"
if ($limits) {
    Write-Host "  Configured Limits: $($limits.Keys.Count)" -ForegroundColor Gray
}
Write-Host ""

# Test 4: Portfolio Risk
Write-Host "[4/10] Component Test - Portfolio Risk Assessment" -ForegroundColor Cyan
$portfolio = Test-Endpoint -Name "Portfolio Risk" -Url "$BaseUrl/risk/portfolio"
if ($portfolio) {
    Write-Host "  Total Exposure: $$($portfolio.total_exposure)" -ForegroundColor Gray
    Write-Host "  Risk Level: $($portfolio.risk_level)" -ForegroundColor Gray
}
Write-Host ""

# Test 5: Active Alerts
Write-Host "[5/10] Component Test - Risk Alerts" -ForegroundColor Cyan
$alerts = Test-Endpoint -Name "Risk Alerts" -Url "$BaseUrl/risk/alerts?unacknowledged_only=false"
if ($alerts) {
    Write-Host "  Total Alerts: $($alerts.Count)" -ForegroundColor Gray
}
Write-Host ""

# Test 6: Integration Test - NATS Connection
Write-Host "[6/10] Integration Test - NATS Connectivity" -ForegroundColor Cyan
$logs = docker logs risk --tail 100 2>&1
if ($logs -match "Connected to NATS" -or $logs -match "Subscribed") {
    Write-Host "  ✓ NATS connectivity verified" -ForegroundColor Green
    $TestsPassed++
} else {
    Write-Host "  ❌ NATS connectivity not verified" -ForegroundColor Red
    $TestsFailed++
}
Write-Host ""

# Test 7: Integration Test - Redis Connection
Write-Host "[7/10] Integration Test - Redis/Valkey Connectivity" -ForegroundColor Cyan
if ($logs -match "Connected to Redis") {
    Write-Host "  ✓ Redis connectivity verified" -ForegroundColor Green
    $TestsPassed++
} else {
    Write-Host "  ❌ Redis connectivity not verified" -ForegroundColor Red
    $TestsFailed++
}
Write-Host ""

# Test 8: Performance Test - Response Time
Write-Host "[8/10] Performance Test - Health Check Latency" -ForegroundColor Cyan
$latencies = @()
for ($i = 1; $i -le 10; $i++) {
    $start = Get-Date
    try {
        Invoke-WebRequest -Uri "$BaseUrl/health" -Method GET -TimeoutSec 2 | Out-Null
        $end = Get-Date
        $latency = ($end - $start).TotalMilliseconds
        $latencies += $latency
    } catch {
        Write-Host "  ⚠ Request $i failed" -ForegroundColor Yellow
    }
}

if ($latencies.Count -gt 0) {
    $avgLatency = ($latencies | Measure-Object -Average).Average
    $p50 = $latencies | Sort-Object | Select-Object -Index ([math]::Floor($latencies.Count * 0.5))
    $p95 = $latencies | Sort-Object | Select-Object -Index ([math]::Floor($latencies.Count * 0.95))
    
    Write-Host "  Average: $([math]::Round($avgLatency, 2))ms" -ForegroundColor Gray
    Write-Host "  P50: $([math]::Round($p50, 2))ms" -ForegroundColor Gray
    Write-Host "  P95: $([math]::Round($p95, 2))ms" -ForegroundColor Gray
    
    if ($p50 -lt 100) {
        Write-Host "  ✓ Latency acceptable (P50 < 100ms)" -ForegroundColor Green
        $TestsPassed++
    } else {
        Write-Host "  ❌ Latency too high (P50 >= 100ms)" -ForegroundColor Red
        $TestsFailed++
    }
} else {
    Write-Host "  ❌ No successful requests" -ForegroundColor Red
    $TestsFailed++
}
Write-Host ""

# Test 9: Functional Test - Block Symbol
Write-Host "[9/10] Functional Test - Block/Unblock Symbol" -ForegroundColor Cyan
$blockResult = Test-Endpoint -Name "Block TESTUSDT" -Url "$BaseUrl/risk/symbol/TESTUSDT/block" -Method "POST"
if ($blockResult -and $blockResult.status -eq "blocked") {
    Write-Host "  ✓ Symbol blocked successfully" -ForegroundColor Green
    
    # Verify it's in stats
    Start-Sleep -Seconds 1
    $stats = Invoke-RestMethod -Uri "$BaseUrl/stats" -Method GET
    if ($stats.blocked_symbols -contains "TESTUSDT") {
        Write-Host "  ✓ Verified in blocked list" -ForegroundColor Green
    }
    
    # Unblock
    $unblockResult = Test-Endpoint -Name "Unblock TESTUSDT" -Url "$BaseUrl/risk/symbol/TESTUSDT/block" -Method "DELETE"
    if ($unblockResult -and $unblockResult.status -eq "unblocked") {
        Write-Host "  ✓ Symbol unblocked successfully" -ForegroundColor Green
    }
}
Write-Host ""

# Test 10: Validation - Container Health
Write-Host "[10/10] Validation - Container Status" -ForegroundColor Cyan
$containerStatus = docker inspect risk --format '{{.State.Health.Status}}' 2>$null

if ($containerStatus -eq "healthy") {
    Write-Host "  ✓ Container health status: healthy" -ForegroundColor Green
    $TestsPassed++
} elseif ($containerStatus -eq "starting") {
    Write-Host "  ⚠ Container still starting" -ForegroundColor Yellow
    $TestsPassed++
} else {
    Write-Host "  ❌ Container health status: $containerStatus" -ForegroundColor Red
    $TestsFailed++
}
Write-Host ""

# Final Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Results Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $TestsFailed" -ForegroundColor Red
Write-Host "Total Tests: $($TestsPassed + $TestsFailed)" -ForegroundColor Cyan
Write-Host ""

if ($TestsFailed -eq 0) {
    Write-Host "✓ All tests passed! Risk service is operational." -ForegroundColor Green
    Write-Host ""
    Write-Host "Risk Service Validation: PASSED ✓" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠ Some tests failed. Review logs:" -ForegroundColor Yellow
    Write-Host "  docker logs risk --tail 100" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Risk Service Validation: NEEDS ATTENTION ⚠" -ForegroundColor Yellow
    exit 1
}
