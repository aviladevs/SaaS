# Ávila DevOps SaaS - Load Test Runner (PowerShell)
# Automates load testing with k6 and generates reports for Windows

param(
    [string]$BaseUrl = $env:BASE_URL ?? "https://aviladevops.com.br",
    [string]$ResultsDir = "",
    [string]$K6Script = ""
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrEmpty($ResultsDir)) {
    $ResultsDir = Join-Path $ScriptDir "..\..\test-results"
}
if ([string]::IsNullOrEmpty($K6Script)) {
    $K6Script = Join-Path $ScriptDir "load-test-k6.js"
}

# Create results directory
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

# Banner
Write-Host ""
Write-Host "==========================================" -ForegroundColor Blue
Write-Host "  Ávila DevOps SaaS - Load Test Runner" -ForegroundColor Blue
Write-Host "==========================================" -ForegroundColor Blue
Write-Host ""

# Check if k6 is installed
try {
    $k6Version = k6 version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "k6 not found"
    }
} catch {
    Write-Host "❌ k6 is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install k6 on Windows:"
    Write-Host "  - Using Chocolatey: choco install k6"
    Write-Host "  - Using winget: winget install k6"
    Write-Host "  - Manual download: https://dl.k6.io/msi/k6-latest-amd64.msi"
    Write-Host "  - Using Docker: docker run --rm -i grafana/k6 run - <$K6Script"
    Write-Host ""
    exit 1
}

# Verify base URL is accessible
Write-Host "🔍 Checking system availability..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/health" -Method Head -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ System is accessible at $BaseUrl" -ForegroundColor Green
    } else {
        throw "Non-200 status code"
    }
} catch {
    Write-Host "❌ System is not accessible at $BaseUrl" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  - Is the system running?"
    Write-Host "  - Is the BASE_URL correct?"
    Write-Host "  - Are there any network issues?"
    exit 1
}

# Get system info before test
Write-Host ""
Write-Host "📊 Pre-test system check..." -ForegroundColor Yellow
Write-Host "Base URL: $BaseUrl"
Write-Host "K6 Version: $k6Version"
Write-Host "Test Script: $K6Script"
Write-Host "Results Directory: $ResultsDir"

# Timestamp for this test run
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultsFile = Join-Path $ResultsDir "load-test-$Timestamp.json"
$SummaryFile = Join-Path $ResultsDir "summary-$Timestamp.json"

# Run the load test
Write-Host ""
Write-Host "🚀 Starting load test..." -ForegroundColor Blue
Write-Host "Target: 1000+ concurrent requests per second"
Write-Host "Duration: ~45 minutes (full test cycle)"
Write-Host ""

# Set environment variable
$env:BASE_URL = $BaseUrl

# Run k6 with detailed output
$k6Args = @(
    "run",
    "--out", "json=$ResultsFile",
    "--summary-export=$SummaryFile",
    "--verbose",
    $K6Script
)

try {
    & k6 @k6Args
    $ExitCode = $LASTEXITCODE
} catch {
    Write-Host "❌ Error running k6: $_" -ForegroundColor Red
    exit 1
}

# Check test results
Write-Host ""
if ($ExitCode -eq 0) {
    Write-Host "✅ Load test completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Load test failed or had warnings (Exit code: $ExitCode)" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Blue
Write-Host "  Test Results Summary" -ForegroundColor Blue
Write-Host "==========================================" -ForegroundColor Blue
Write-Host ""
Write-Host "Results saved to:"
Write-Host "  - JSON: $ResultsFile"
Write-Host "  - Summary: $SummaryFile"
Write-Host ""

# Parse key metrics from summary if available
if (Test-Path $SummaryFile) {
    Write-Host "📈 Key Metrics:" -ForegroundColor Yellow
    
    try {
        $summary = Get-Content $SummaryFile -Raw | ConvertFrom-Json
        
        $totalRequests = $summary.metrics.http_reqs.values.count
        $reqRate = $summary.metrics.http_reqs.values.rate
        $avgDuration = $summary.metrics.http_req_duration.values.avg
        $p95Duration = $summary.metrics.http_req_duration.values.'p(95)'
        $errorRate = $summary.metrics.http_req_failed.values.rate
        
        Write-Host "  Total Requests: $totalRequests"
        Write-Host "  Request Rate: $($reqRate.ToString('F2')) req/s"
        Write-Host "  Avg Response Time: $($avgDuration.ToString('F2')) ms"
        Write-Host "  p95 Response Time: $($p95Duration.ToString('F2')) ms"
        Write-Host "  Error Rate: $(($errorRate * 100).ToString('F2'))%"
        
        # Check success criteria
        Write-Host ""
        Write-Host "✅ Success Criteria:" -ForegroundColor Yellow
        
        # p95 < 300ms
        if ($p95Duration -lt 300) {
            Write-Host "  ✅ p95 < 300ms: PASS" -ForegroundColor Green
        } else {
            Write-Host "  ❌ p95 < 300ms: FAIL ($($p95Duration.ToString('F2'))ms)" -ForegroundColor Red
        }
        
        # Error rate < 1%
        if ($errorRate -lt 0.01) {
            Write-Host "  ✅ Error rate < 1%: PASS" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Error rate < 1%: FAIL ($(($errorRate * 100).ToString('F2'))%)" -ForegroundColor Red
        }
        
        # Rate > 1000 req/s
        if ($reqRate -gt 1000) {
            Write-Host "  ✅ Rate > 1000 req/s: PASS" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Rate > 1000 req/s: FAIL ($($reqRate.ToString('F2')) req/s)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  (Error parsing metrics: $_)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Blue

# Clean up old test results (keep last 10)
Write-Host ""
Write-Host "🧹 Cleaning up old test results..." -ForegroundColor Yellow
try {
    $oldResults = Get-ChildItem -Path $ResultsDir -Filter "load-test-*.json" | 
                  Sort-Object LastWriteTime -Descending | 
                  Select-Object -Skip 10
    
    if ($oldResults) {
        $oldResults | Remove-Item -Force
        Write-Host "✅ Cleanup complete - removed $($oldResults.Count) old files" -ForegroundColor Green
    } else {
        Write-Host "✅ No old files to clean up" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Warning: Could not clean up old files: $_" -ForegroundColor Yellow
}

Write-Host ""

# Exit with k6's exit code
exit $ExitCode
