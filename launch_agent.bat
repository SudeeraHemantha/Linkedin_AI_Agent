@echo off
setlocal enableextensions enabledelayedexpansion
set "AGENT_DIR=%~dp0"
set "AGENT_DIR=%AGENT_DIR:~0,-1%"
cd /d "%AGENT_DIR%"
set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%"

echo ==================================================================
echo   LinkedIn Autonomous Agent - Hybrid Application Launcher        
echo ==================================================================
echo [1/3] Starting Backend FastAPI Server (Port 8000)...
start "LinkedIn Agent Backend" /min cmd /c "cd /d "%AGENT_DIR%" && set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%" && py -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Starting Frontend Vite SPA Client (Port 3000)...
start "LinkedIn Agent Frontend" /min cmd /c "cd /d "%AGENT_DIR%\src\frontend" && npm run dev"

echo [3/4] Launching System Tray Background Daemon Manager...
start "LinkedIn Agent Tray" /min cmd /c "cd /d "%AGENT_DIR%" && set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%" && py src/installer/tray_app.py"

echo [4/4] Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser interface at http://localhost:3000...
start "" "http://localhost:3000"


echo ==================================================================
echo   LinkedIn Agent active! (Backend: 8000 | Frontend: 3000)
echo ==================================================================
