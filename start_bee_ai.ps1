# Bee AI Auto-Startup Script
# This script automatically starts the Bee AI system when the HTML file is opened

param(
    [string]$Action = "start"
)

function Start-BeeAISystem {
    Write-Host "🐝 Starting Bee AI System..." -ForegroundColor Yellow
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
        return $false
    }
    
    # Check if required packages are installed
    try {
        python -c "import google.generativeai, flask" 2>&1 | Out-Null
        Write-Host "✅ Required packages are installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Installing required packages..." -ForegroundColor Yellow
        pip install -r requirements_gemini.txt
    }
    
    # Check if config.py exists
    if (Test-Path "config.py") {
        Write-Host "✅ Configuration file found" -ForegroundColor Green
    } else {
        Write-Host "❌ config.py not found. Please create it with your API key." -ForegroundColor Red
        return $false
    }
    
    # Start the Python server
    Write-Host "🚀 Starting Gemini AI server..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "bee_ai_gemini_server.py" -WindowStyle Hidden
    
    # Wait for server to start
    $maxWait = 30
    $waited = 0
    
    while ($waited -lt $maxWait) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 2
            if ($response.status -eq "healthy") {
                Write-Host "✅ Bee AI System is running successfully!" -ForegroundColor Green
                Write-Host "🌐 Server running on: http://localhost:5000" -ForegroundColor Cyan
                return $true
            }
        } catch {
            # Server not ready yet
        }
        
        Start-Sleep -Seconds 1
        $waited++
        Write-Host "⏳ Waiting for server to start... ($waited/$maxWait)" -ForegroundColor Yellow
    }
    
    Write-Host "❌ Server failed to start within $maxWait seconds" -ForegroundColor Red
    return $false
}

function Stop-BeeAISystem {
    Write-Host "🛑 Stopping Bee AI System..." -ForegroundColor Yellow
    
    # Find and stop Python processes running bee_ai_gemini_server.py
    $processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*bee_ai_gemini_server.py*"
    }
    
    if ($processes) {
        $processes | Stop-Process -Force
        Write-Host "✅ Bee AI System stopped" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ No Bee AI processes found" -ForegroundColor Blue
    }
}

function Show-Status {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 2
        Write-Host "✅ Bee AI System is running" -ForegroundColor Green
        Write-Host "📊 Status: $($response.status)" -ForegroundColor Cyan
        Write-Host "🧠 Knowledge Base: $($response.knowledge_entries) entries" -ForegroundColor Cyan
        Write-Host "🔗 Gemini API: $($response.gemini_loaded)" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ Bee AI System is not running" -ForegroundColor Red
    }
}

# Main execution
switch ($Action.ToLower()) {
    "start" {
        Start-BeeAISystem
    }
    "stop" {
        Stop-BeeAISystem
    }
    "status" {
        Show-Status
    }
    "restart" {
        Stop-BeeAISystem
        Start-Sleep -Seconds 2
        Start-BeeAISystem
    }
    default {
        Write-Host "Usage: .\start_bee_ai.ps1 [start|stop|status|restart]" -ForegroundColor Yellow
    }
}
