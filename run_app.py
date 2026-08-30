import os
import sys
import webbrowser
import time
import uvicorn
from pathlib import Path

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import subprocess

def main():
    print("==================================================================")
    print("      LinkedIn Autonomous Agent - Hybrid System Launcher         ")
    print("==================================================================")
    print("  Local Frontend Client: http://localhost:3000                   ")
    print("  Local Backend API:     http://127.0.0.1:8000                   ")
    print("  API Documentation:     http://127.0.0.1:8000/docs              ")
    print("==================================================================")
    print("Booting local daemon server & Vite client...\n")

    frontend_dir = ROOT_DIR / "src" / "frontend"
    
    # Spawn Vite dev server in background if package.json exists
    if (frontend_dir / "package.json").exists():
        try:
            subprocess.Popen(["npm", "run", "dev"], cwd=str(frontend_dir), shell=True)
            time.sleep(2)
        except Exception as e:
            print(f"Notice: Frontend dev server launch warning: {e}")

    try:
        webbrowser.open("http://localhost:3000")
    except Exception:
        pass

    uvicorn.run("src.backend.main:app", host="127.0.0.1", port=8000, reload=True)



if __name__ == "__main__":
    main()
