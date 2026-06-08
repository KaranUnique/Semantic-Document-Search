# run.ps1
# Automated Setup and Launcher for Enterprise Knowledge Assistant (EKA)

Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "💼 ENTERPRISE KNOWLEDGE ASSISTANT SETUP & LAUNCHER" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Ensure we are in the root directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ($scriptPath) {
    Set-Location $scriptPath
}

# 1. SETUP BACKEND
Write-Host "`n[1/4] Setting up Backend Virtual Environment..." -ForegroundColor Yellow
if (-not (Test-Path "backend\venv")) {
    Write-Host "Creating backend virtual environment (venv)..." -ForegroundColor Blue
    python -m venv backend\venv
} else {
    Write-Host "Backend virtual environment already exists." -ForegroundColor Blue
}

Write-Host "Installing backend dependencies (this may take a moment)..." -ForegroundColor Blue
& ".\backend\venv\Scripts\pip.exe" install -r backend\requirements.txt

# 2. SETUP FRONTEND (no venv needed — pure static HTML/CSS/JS served by Python stdlib)
Write-Host "`n[2/4] Frontend is HTML/CSS/JS — no dependencies to install." -ForegroundColor Yellow

# 3. LAUNCH BACKEND
Write-Host "`n[3/4] Launching FastAPI Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; Write-Host '🚀 FastAPI Server Starting...' -ForegroundColor Green; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

# 4. LAUNCH FRONTEND
Write-Host "[4/4] Launching HTML Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; Write-Host '🎨 Static Frontend Starting...' -ForegroundColor Green; python server.py"

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "🎉 setup complete! servers are starting in separate windows." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "• Backend Swagger UI docs: http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "• Frontend UI:             http://localhost:8501" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "`nNote: Please make sure you have added your GEMINI_API_KEY inside 'backend/.env' to use RAG features!" -ForegroundColor DarkYellow
