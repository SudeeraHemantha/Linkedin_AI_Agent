@echo off
echo Booting LinkedIn Autonomous Agent Backend & UI...
start "" "http://localhost:3000"
py -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000 --reload
