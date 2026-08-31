import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

os.environ["DATABASE_PATH"] = "e2e_test_linkedin_agent.db"

from src.backend.main import app
from src.backend.database import init_db
from src.agent.linkedin_bot import LinkedInAutonomousBot
from src.installer.wizard import StandaloneInstallationWizard
from build import build_package

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_e2e_db():
    os.environ["DATABASE_PATH"] = "e2e_test_linkedin_agent.db"
    if os.path.exists("e2e_test_linkedin_agent.db"):
        try:
            os.remove("e2e_test_linkedin_agent.db")
        except Exception:
            pass
    init_db()
    yield
    if os.path.exists("e2e_test_linkedin_agent.db"):
        try:
            os.remove("e2e_test_linkedin_agent.db")
        except Exception:
            pass


def test_full_e2e_system_acceptance(tmp_path):
    """
    End-to-End User Acceptance Test (UAT) verifying:
    Auth -> OTP -> JWT Login -> LLM Tailor -> Agent Bot -> Build Packaging -> Installer Wizard
    """
    print("\n--- [E2E STEP 1] User Registration ---")
    reg_res = client.post("/api/auth/register", json={
        "username": "e2euser",
        "email": "e2e@enterprise.com",
        "password": "E2ESecurePassword123!",
        "full_name": "E2E Acceptance Tester"
    })
    assert reg_res.status_code == 200
    otp_code = reg_res.json()["debug_otp"]

    print("--- [E2E STEP 2] OTP Verification & Token Issue ---")
    verify_res = client.post("/api/auth/verify-otp", json={
        "email": "e2e@enterprise.com",
        "otp_code": otp_code
    })
    assert verify_res.status_code == 200
    token = verify_res.json()["access_token"]
    assert len(token) > 10

    print("--- [E2E STEP 3] AI Resume Tailor API Call ---")
    tailor_res = client.post("/api/llm/tailor-resume", json={
        "resume_text": "Experienced Systems Engineer",
        "job_description": "Seeking Systems Engineer for distributed AI agent platform.",
        "target_role": "Systems Engineer"
    })
    assert tailor_res.status_code == 200
    assert tailor_res.json()["match_score"] > 80.0

    print("--- [E2E STEP 4] Playwright Bot Simulation ---")
    bot = LinkedInAutonomousBot(keywords="Systems Engineer", location="Remote")
    assert bot.applied_count == 0

    print("--- [E2E STEP 5] Release Packaging & Compilation ---")
    zip_path = build_package()
    assert zip_path.exists()

    print("--- [E2E STEP 6] Standalone Installer Wizard Execution ---")
    target_install_dir = tmp_path / "LinkedInAgentE2E"
    wizard = StandaloneInstallationWizard(target_dir=str(target_install_dir))
    success = wizard.run_installation_workflow(mock_archive_path=str(zip_path))
    assert success is True
    assert (target_install_dir / "linkedin_agent.db").exists()
    assert (target_install_dir / "boot_agent.bat").exists()

    print("\n=== E2E ACCEPTANCE TEST PASSED SUCCESSFULLY ===")
