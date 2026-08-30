import os
import shutil
import pytest
from pathlib import Path
from src.installer.updater import GitHubReleaseUpdater
from src.installer.wizard import StandaloneInstallationWizard
from build import build_package

def test_github_release_updater_fetch():
    updater = GitHubReleaseUpdater()
    info = updater.fetch_latest_release_info()
    assert isinstance(info, dict)
    assert "status" in info
    assert "tag_name" in info

def test_build_package_creation(tmp_path):
    zip_path = build_package()
    assert os.path.exists(zip_path)
    assert zip_path.suffix == ".zip"
    assert os.path.getsize(zip_path) > 0

def test_installer_wizard_workflow(tmp_path):
    test_install_dir = tmp_path / "LinkedInAgentTestDir"
    wizard = StandaloneInstallationWizard(target_dir=str(test_install_dir))
    
    # Run installation workflow using freshly built zip bundle
    release_zip = Path("dist/release_v1.0.0.zip")
    success = wizard.run_installation_workflow(mock_archive_path=str(release_zip) if release_zip.exists() else None)
    
    assert success is True
    assert (test_install_dir / "linkedin_agent.db").exists()
    assert (test_install_dir / "boot_agent.bat").exists()
