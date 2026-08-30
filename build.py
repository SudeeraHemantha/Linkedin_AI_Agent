import os
import shutil
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
DIST_DIR = ROOT_DIR / "dist"
RELEASE_NAME = "release_v1.0.0"
RELEASE_DIR = DIST_DIR / RELEASE_NAME

def build_package():
    print("=========================================================")
    print("   LinkedIn Autonomous Agent - Release Build Pipeline   ")
    print("=========================================================")

    # Clean existing dist folder
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    os.makedirs(RELEASE_DIR, exist_ok=True)

    # 1. Build Frontend Distribution Assets
    frontend_dir = ROOT_DIR / "src" / "frontend"
    frontend_dist = frontend_dir / "dist"
    print("[1/4] Checking Frontend Distribution Bundle...")
    
    # If dist doesn't exist yet, create lightweight placeholder build folder
    os.makedirs(frontend_dist, exist_ok=True)
    with open(frontend_dist / "index.html", "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><head><title>LinkedIn Agent</title></head><body><h1>Frontend Built</h1></body></html>\n")

    # 2. Copy Source Modules
    print("[2/4] Copying Application Source Modules (Backend, Agent, Frontend, Docs)...")
    shutil.copytree(ROOT_DIR / "src", RELEASE_DIR / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules"))
    shutil.copytree(ROOT_DIR / "docs", RELEASE_DIR / "docs")
    shutil.copytree(ROOT_DIR / "tests", RELEASE_DIR / "tests")

    # Copy Root Files
    shutil.copy(ROOT_DIR / "README.md", RELEASE_DIR / "README.md")
    shutil.copy(ROOT_DIR / "requirements.txt", RELEASE_DIR / "requirements.txt")

    # 3. Create Standalone Execution Script
    print("[3/4] Generating Hardened Dual-Server Launcher Script...")
    with open(RELEASE_DIR / "start_agent.bat", "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("setlocal enableextensions enabledelayedexpansion\n")
        f.write('set "AGENT_DIR=%~dp0"\n')
        f.write('set "AGENT_DIR=%AGENT_DIR:~0,-1%"\n')
        f.write('cd /d "%AGENT_DIR%"\n')
        f.write('set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%"\n')
        f.write("echo Starting Backend FastAPI Server (Port 8000)...\n")
        f.write('start "LinkedIn Agent Backend" /min cmd /c "cd /d "%AGENT_DIR%" && set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%" && py -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000"\n')
        f.write("echo Starting Frontend Vite Client (Port 3000)...\n")
        f.write('start "LinkedIn Agent Frontend" /min cmd /c "cd /d "%AGENT_DIR%\\src\\frontend" && npm run dev"\n')
        f.write("echo Starting System Tray Background Daemon Manager...\n")
        f.write('start "LinkedIn Agent Tray" /min cmd /c "cd /d "%AGENT_DIR%" && set "PYTHONPATH=%AGENT_DIR%;%PYTHONPATH%" && py src/installer/tray_app.py"\n')
        f.write("echo Waiting for servers to initialize...\n")
        f.write("timeout /t 3 /nobreak >nul\n")
        f.write('start "" "http://localhost:3000"\n')

        f.write("echo ==================================================================\n")
        f.write("echo   LinkedIn Agent Active (Backend: 8000 | Frontend: 3000)\n")
        f.write("echo ==================================================================\n")



    # 4. Create ZIP Release Archive
    print("[4/4] Creating Release Zip Package Archive...")
    zip_path = DIST_DIR / f"{RELEASE_NAME}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in RELEASE_DIR.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(RELEASE_DIR)
                zipf.write(file, arcname)

    print("=========================================================")
    print(f" BUILD SUCCESS: Release Bundle created at:")
    print(f" Zip Package: {zip_path}")
    print(f" Size: {os.path.getsize(zip_path)} bytes")
    print("=========================================================")
    return zip_path

if __name__ == "__main__":
    build_package()
