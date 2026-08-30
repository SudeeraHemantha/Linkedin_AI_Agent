import os
import sys
import zipfile
import shutil
import subprocess
import traceback
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from typing import List
from src.installer.updater import GitHubReleaseUpdater
from src.backend.database import init_db

def get_bundle_base_path() -> Path:
    """Returns runtime directory path, accounting for PyInstaller sys._MEIPASS bundling."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.resolve()

def get_user_desktop_paths() -> List[Path]:
    """Resolves all physical Windows Desktop folders, including OneDrive and User Shell Registry mappings."""
    desktop_paths = []
    
    # 1. Standard User Profile Desktop
    home_desktop = (Path(os.path.expanduser("~")) / "Desktop").resolve()
    if home_desktop.exists():
        desktop_paths.append(home_desktop)
        
    # 2. OneDrive Desktop Mapping
    onedrive_desktop = (Path(os.path.expanduser("~")) / "OneDrive" / "Desktop").resolve()
    if onedrive_desktop.exists() and onedrive_desktop not in desktop_paths:
        desktop_paths.append(onedrive_desktop)

    # 3. Query Windows Registry for User Shell Folders Desktop
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        desktop_reg, _ = winreg.QueryValueEx(key, "Desktop")
        winreg.CloseKey(key)
        expanded = os.path.expandvars(desktop_reg)
        reg_path = Path(expanded).resolve()
        if reg_path.exists() and reg_path not in desktop_paths:
            desktop_paths.append(reg_path)
    except Exception:
        pass

    return desktop_paths

def create_windows_lnk_shortcut(target_path: Path, shortcut_path: Path, working_dir: Path, description: str = "LinkedIn Autonomous Agent"):
    """Generates a true Windows .lnk shortcut file via PowerShell WScript.Shell COM object."""
    ps_script = (
        f'$WshShell = New-Object -ComObject WScript.Shell; '
        f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
        f'$Shortcut.TargetPath = "{target_path}"; '
        f'$Shortcut.WorkingDirectory = "{working_dir}"; '
        f'$Shortcut.Description = "{description}"; '
        f'$Shortcut.Save()'
    )
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script], capture_output=True, text=True)
        if res.returncode == 0 and shortcut_path.exists():
            return True
    except Exception as e:
        print(f" -> PowerShell .lnk creation warning: {e}")
    
    # Fallback to .bat shortcut if .lnk COM call fails
    bat_shortcut = shortcut_path.with_suffix(".bat")
    with open(bat_shortcut, "w", encoding="utf-8") as f:
        f.write(f'@echo off\ncd /d "{working_dir}"\ncall "{target_path}"\n')
    return bat_shortcut.exists()

class StandaloneInstallationWizard:
    def __init__(self, target_dir: str = None):
        if target_dir:
            self.target_dir = Path(target_dir).resolve()
        else:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self.target_dir = (Path(appdata) / "LinkedInAgent").resolve()
        
        self.updater = GitHubReleaseUpdater()

    def run_installation_workflow(self, mock_archive_path: str = None, show_gui: bool = False) -> bool:
        """Executes full hardened automated installation sequence."""
        try:
            print("================================================================")
            print("    LinkedIn Autonomous Agent - Hardened Installation Wizard    ")
            print("================================================================")
            print(f"[STEP 1/4] Target Installation Directory: {self.target_dir}")

            os.makedirs(self.target_dir, exist_ok=True)

            # Step 2: Resolve / Fetch Release Archive Package
            print("[STEP 2/4] Resolving release archive bundle...")
            download_target = self.target_dir / "release_bundle.zip"

            base_path = get_bundle_base_path()
            bundled_zip = base_path / "release_v1.0.0.zip"
            
            if mock_archive_path and os.path.exists(mock_archive_path):
                shutil.copy(mock_archive_path, download_target)
                print(f" -> Using specified bundle archive: {download_target}")
            elif bundled_zip.exists():
                shutil.copy(bundled_zip, download_target)
                print(f" -> Found bundled installer payload: {download_target}")
            else:
                release_info = self.updater.fetch_latest_release_info()
                print(f" -> GitHub Release Meta: {release_info.get('name', 'v1.0.0')}")
                download_url = release_info.get("download_url") or "https://github.com/SudeeraHemantha/Linkedin_AI_Agent/archive/refs/heads/main.zip"
                download_success = self.updater.download_release_archive(download_url, str(download_target))
                if not download_success:
                    print(" -> [NOTICE] Running local setup initialization.")

            # Step 3: Decompress Archive & Initialize SQLite DB
            print("[STEP 3/4] Decompressing files and initializing database...")
            if download_target.exists() and os.path.getsize(download_target) > 0:
                with zipfile.ZipFile(download_target, 'r') as zip_ref:
                    zip_ref.extractall(self.target_dir)
                print(f" -> Successfully decompressed bundle into: {self.target_dir}")

            db_path = self.target_dir / "linkedin_agent.db"
            os.environ["DATABASE_PATH"] = str(db_path)
            init_db()
            print(f" -> SQLite Database active at: {db_path}")

            # Step 4: Create Hardened Launcher Script & Windows .LNK Desktop Shortcuts
            print("[STEP 4/4] Creating hardened dual-server launcher script & desktop shortcuts...")
            boot_script_path = self.target_dir / "boot_agent.bat"
            with open(boot_script_path, "w", encoding="utf-8") as f:
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
                f.write("echo Waiting for servers to initialize...\n")
                f.write("timeout /t 3 /nobreak >nul\n")
                f.write('start "" "http://localhost:3000"\n')
                f.write("echo ==================================================================\n")
                f.write("echo   LinkedIn Agent Active (Backend: 8000 | Frontend: 3000)\n")
                f.write("echo ==================================================================\n")



            print(f" -> Hardened Launcher Batch generated: {boot_script_path}")

            # Resolve all Desktop folders (OneDrive + standard + User Shell Folders)
            desktop_dirs = get_user_desktop_paths()
            for desktop_dir in desktop_dirs:
                lnk_path = desktop_dir / "Launch LinkedIn Agent.lnk"
                shortcut_created = create_windows_lnk_shortcut(
                    target_path=boot_script_path,
                    shortcut_path=lnk_path,
                    working_dir=self.target_dir,
                    description="LinkedIn Autonomous Agent Platform"
                )
                print(f" -> Shortcut (.lnk) created at: {lnk_path} (Success: {shortcut_created})")

            print("================================================================")
            print(" SUCCESS: LinkedIn Autonomous Agent Installation Completed!   ")
            print("================================================================")
            print(" Direct Launcher URL:  http://127.0.0.1:8000                    ")
            print(" Interactive Swagger:  http://127.0.0.1:8000/docs               ")
            print(" Or run directly via:  py run_app.py                            ")
            print("================================================================")

            if show_gui:
                try:
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showinfo(
                        "Installation Complete",
                        f"LinkedIn Autonomous Agent has been installed successfully!\n\nLocation: {self.target_dir}\nShortcuts generated on Desktop.\n\nLocal Daemon: http://127.0.0.1:8000"
                    )
                    root.destroy()
                except Exception:
                    pass

            return True

        except Exception as err:
            error_trace = traceback.format_exc()
            print("\n[CRITICAL INSTALLATION ERROR]")
            print(error_trace)

            log_paths = [
                Path(os.path.expanduser("~/Desktop")) / "installation_error.log",
                Path.cwd() / "installation_error.log"
            ]
            for p in log_paths:
                try:
                    with open(p, "w", encoding="utf-8") as lf:
                        lf.write(f"LinkedIn Agent Installation Error Log\n")
                        lf.write(f"Target Dir: {self.target_dir}\n")
                        lf.write(f"Traceback:\n{error_trace}\n")
                except Exception:
                    pass

            if show_gui:
                try:
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showerror(
                        "Installation Failed",
                        f"An error occurred during installation:\n\n{err}\n\nDetailed traceback logged to Desktop/installation_error.log"
                    )
                    root.destroy()
                except Exception:
                    pass

            return False

if __name__ == "__main__":
    wizard = StandaloneInstallationWizard()
    wizard.run_installation_workflow(show_gui=True)
