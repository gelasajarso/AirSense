# Simple API Restart Script for AirSense
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AirSense API Server Restart" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop existing API servers
Write-Host "Step 1: Stopping existing API servers..." -ForegroundColor Yellow
$processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -like "*uvicorn*"}
if ($processes) {
    $processes | Stop-Process -Force
    Write-Host "  Stopped existing API servers" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "  No running API servers found" -ForegroundColor Gray
}

# Step 2: Check if port 8000 is free
Write-Host ""
Write-Host "Step 2: Checking port 8000..." -ForegroundColor Yellow
$port = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port) {
    Write-Host "  Port 8000 is in use. Attempting to free it..." -ForegroundColor Red
    $processId = $port.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  Port 8000 should now be free" -ForegroundColor Green
} else {
    Write-Host "  Port 8000 is available" -ForegroundColor Green
}

# Step 3: Start the API server
Write-Host ""
Write-Host "Step 3: Starting API server..." -ForegroundColor Yellow
Write-Host "  Command: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  API Server Starting..." -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
