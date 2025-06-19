# CECI-AI Complete System Startup Script
# Runs Frontend, Backend, and PandasAI Service

Write-Host "🚀 Starting CECI-AI Complete System" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start PandasAI Service
Write-Host "`n📊 Starting PandasAI Service..." -ForegroundColor Yellow
$pandasJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location "$dir\server\src\services\python"
    
    # Check if venv exists
    if (-not (Test-Path "venv")) {
        python -m venv venv
    }
    
    # Activate and run
    & ".\venv\Scripts\Activate.ps1"
    python pandasai_service.py
} -ArgumentList $scriptDir

# Wait a bit for PandasAI to start
Start-Sleep -Seconds 5

# Check if PandasAI is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001" -UseBasicParsing -TimeoutSec 2
    Write-Host "✅ PandasAI Service is running!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: PandasAI service might not be running properly" -ForegroundColor Yellow
}

# Start Backend
Write-Host "`n🔧 Starting Backend..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location "$dir\server"
    npm start
} -ArgumentList $scriptDir

# Wait for backend to start
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "`n🌐 Starting Frontend..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm run dev
} -ArgumentList $scriptDir

# Wait a bit
Start-Sleep -Seconds 3

Write-Host "`n✅ All services started!" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 PandasAI API: " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:8001" -ForegroundColor White
Write-Host "🔧 Backend API: " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:5173" -ForegroundColor White
Write-Host "🌐 Frontend: " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Monitor jobs
while ($true) {
    # Check job status
    $pandasStatus = $pandasJob.State
    $backendStatus = $backendJob.State
    $frontendStatus = $frontendJob.State
    
    if ($pandasStatus -eq "Failed" -or $backendStatus -eq "Failed" -or $frontendStatus -eq "Failed") {
        Write-Host "`nError: One or more services failed!" -ForegroundColor Red
        
        if ($pandasStatus -eq "Failed") {
            Write-Host "PandasAI Error:" -ForegroundColor Red
            Receive-Job $pandasJob
        }
        if ($backendStatus -eq "Failed") {
            Write-Host "Backend Error:" -ForegroundColor Red
            Receive-Job $backendJob
        }
        if ($frontendStatus -eq "Failed") {
            Write-Host "Frontend Error:" -ForegroundColor Red
            Receive-Job $frontendJob
        }
        break
    }
    
    # Show any output
    Receive-Job $pandasJob -Keep | Out-Host
    Receive-Job $backendJob -Keep | Out-Host
    Receive-Job $frontendJob -Keep | Out-Host
    
    Start-Sleep -Seconds 1
}

# Cleanup
Write-Host "`nStopping all services..." -ForegroundColor Yellow
Stop-Job $pandasJob, $backendJob, $frontendJob
Remove-Job $pandasJob, $backendJob, $frontendJob

Write-Host "All services stopped." -ForegroundColor Green
