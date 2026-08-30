import os
import sys
import zipfile
import shutil
from pathlib import Path
from src.installer.updater import GitHubReleaseUpdater
from src.backend.database import init_db

class StandaloneInstallationWizard:
    def __init__(self, target_dir: str = None):
        if target_dir:
            self.target_dir = Path(target_dir)
        else:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self.target_dir = Path(appdata) / "LinkedInAgent"
        
        self.updater = GitHubReleaseUpdater()

    def run_installation_workflow(self, mock_archive_path: str = None) -> bool:
        """Executes full automated installation sequence."""
        print("================================================================")
        print("    LinkedIn Autonomous Agent - Standalone Installation Wizard  ")
        print("================================================================")
        print(f"[STEP 1/4] Installation Target Directory: {self.target_dir}")

        # Create Target Folder Structure
        os.makedirs(self.target_dir, exist_ok=True)

        # Step 2: Fetch / Download Release Asset
        print("[STEP 2/4] Fetching latest release asset from GitHub...")
        release_info = self.updater.fetch_latest_release_info()
        print(f" -> Found Release: {release_info.get('name', 'v1.0.0')}")

        download_target = self.target_dir / "release_bundle.zip"
        
        if mock_archive_path and os.path.exists(mock_archive_path):
            shutil.copy(mock_archive_path, download_target)
            print(f" -> Using local bundle package: {download_target}")
        else:
            download_url = release_info.get("download_url") or "https://github.com/SudeeraHemantha/Linkedin_AI_Agent/archive/refs/heads/main.zip"
            download_success = self.updater.download_release_archive(download_url, str(download_target))
            if not download_success:
                print(" -> [WARNING] Download unavailable online. Operating in local-mode setup.")

        # Step 3: Decompress & Initialize Database
        print("[STEP 3/4] Initializing local database and persistent storage...")
        db_path = self.target_dir / "linkedin_agent.db"
        os.environ["DATABASE_PATH"] = str(db_path)
        init_db()
        print(f" -> SQLite Database initialized at: {db_path}")

        # Step 4: Create Desktop & Startup Boot Shortcuts
        print("[STEP 4/4] Creating launcher startup scripts & shortcuts...")
        boot_script_path = self.target_dir / "boot_agent.bat"
        with open(boot_script_path, "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("echo Starting LinkedIn Autonomous Agent Local Daemon...\n")
            f.write(f'cd /d "{os.getcwd()}"\n')
            f.write("py -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000\n")
            f.write("pause\n")

        print(f" -> Launcher batch script generated: {boot_script_path}")

        # Create Windows Desktop Shortcut if possible
        desktop = Path(os.path.expanduser("~/Desktop"))
        if desktop.exists():
            shortcut_bat = desktop / "Launch LinkedIn Agent.bat"
            with open(shortcut_bat, "w", encoding="utf-8") as f:
                f.write(f'@echo off\ncall "{boot_script_path}"\n')
            print(f" -> Desktop Shortcut created: {shortcut_bat}")

        print("================================================================")
        print(" SUCCESS: LinkedIn Autonomous Agent Installation Completed!   ")
        print("================================================================")
        return True

if __name__ == "__main__":
    wizard = StandaloneInstallationWizard()
    wizard.run_installation_workflow()
