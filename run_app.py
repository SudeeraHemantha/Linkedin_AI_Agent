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

def main():
    print("==================================================================")
    print("      LinkedIn Autonomous Agent - Direct Daemon Launcher         ")
    print("==================================================================")
    print("  Local Frontend Client: http://localhost:3000                   ")
    print("  Local Backend API:     http://127.0.0.1:8000                   ")
    print("  API Documentation:     http://127.0.0.1:8000/docs              ")
    print("==================================================================")
    print("Booting local daemon server & launching frontend UI...\n")

    # Automatically open local frontend client in default browser
    try:
        webbrowser.open("http://localhost:3000")
    except Exception:
        pass

    uvicorn.run("src.backend.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
