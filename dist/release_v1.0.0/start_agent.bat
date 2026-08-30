@echo off
setlocal enableextensions enabledelayedexpansion
set "AGENT_DIR=%~dp0"
set "AGENT_DIR=%AGENT_DIR:~0,-1%"
cd /d "%AGENT_DIR%"
set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%"
echo Starting Backend FastAPI Server (Port 8000)...
start "LinkedIn Agent Backend" /min cmd /c "cd /d "%AGENT_DIR%" && set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%" && py -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000"
echo Starting Frontend Vite Client (Port 3000)...
start "LinkedIn Agent Frontend" /min cmd /c "cd /d "%AGENT_DIR%\src\frontend" && npm run dev"
echo Starting System Tray Background Daemon Manager...
start "LinkedIn Agent Tray" /min cmd /c "cd /d "%AGENT_DIR%" && set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%" && py src/installer/tray_app.py"
echo Waiting for servers to initialize...
timeout /t 3 /nobreak >nul
start "" "http://localhost:3000"
echo ==================================================================
echo   LinkedIn Agent Active (Backend: 8000 | Frontend: 3000)
echo ==================================================================
