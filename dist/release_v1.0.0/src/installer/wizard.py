import os
import sys
import zipfile
import shutil
import subprocess
import traceback
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from src.installer.updater import GitHubReleaseUpdater
from src.backend.database import init_db

def get_bundle_base_path() -> Path:
    """Returns runtime directory path, accounting for PyInstaller sys._MEIPASS bundling."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.resolve()

class StandaloneInstallationWizard:
    def __init__(self, target_dir: str = None):
        if target_dir:
            self.target_dir = Path(target_dir)
        else:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self.target_dir = Path(appdata) / "LinkedInAgent"
        
        self.updater = GitHubReleaseUpdater()

    def run_installation_workflow(self, mock_archive_path: str = None, show_gui: bool = False) -> bool:
        """Executes full automated installation sequence with explicit error logging."""
        try:
            print("================================================================")
            print("    LinkedIn Autonomous Agent - Standalone Installation Wizard  ")
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

            # Step 4: Create Launcher Scripts & Desktop Shortcuts
            print("[STEP 4/4] Creating launcher startup scripts & shortcuts...")
            boot_script_path = self.target_dir / "boot_agent.bat"
            with open(boot_script_path, "w", encoding="utf-8") as f:
                f.write("@echo off\n")
                f.write("echo Booting LinkedIn Autonomous Agent Local Daemon...\n")
                f.write(f'cd /d "{self.target_dir}"\n')
                f.write("py -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000\n")
                f.write("pause\n")

            desktop = Path(os.path.expanduser("~/Desktop"))
            if desktop.exists():
                shortcut_bat = desktop / "Launch LinkedIn Agent.bat"
                with open(shortcut_bat, "w", encoding="utf-8") as f:
                    f.write(f'@echo off\ncall "{boot_script_path}"\n')
                print(f" -> Desktop Shortcut created: {shortcut_bat}")

            print("================================================================")
            print(" SUCCESS: LinkedIn Autonomous Agent Installation Completed!   ")
            print("================================================================")

            if show_gui:
                try:
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showinfo(
                        "Installation Complete",
                        f"LinkedIn Autonomous Agent has been installed successfully!\n\nLocation: {self.target_dir}\nShortcut: Desktop/Launch LinkedIn Agent.bat"
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

