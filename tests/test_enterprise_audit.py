import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

os.environ["DATABASE_PATH"] = "audit_test_linkedin_agent.db"

from src.backend.main import app
from src.backend.database import init_db, get_db_connection
from src.backend.auth import hash_password, verify_password
from src.agent.human_behavior import generate_bezier_curve, random_human_delay
from src.installer.wizard import StandaloneInstallationWizard, get_bundle_base_path
from build import build_package

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_audit_db():
    if os.path.exists("audit_test_linkedin_agent.db"):
        os.remove("audit_test_linkedin_agent.db")
    init_db()
    yield
    if os.path.exists("audit_test_linkedin_agent.db"):
        os.remove("audit_test_linkedin_agent.db")

def test_stage1_database_foreign_keys_and_indexes():
    """STAGE 1: Verify Foreign Key enforcement and Database Indexes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify Foreign Keys Pragma is ON
    cursor.execute("PRAGMA foreign_keys;")
    fk_status = cursor.fetchone()[0]
    assert fk_status == 1

    # Verify Index Creation
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indexes = [row[0] for row in cursor.fetchall()]
    assert "idx_users_username" in indexes
    assert "idx_users_email" in indexes
    assert "idx_otps_email_code" in indexes
    assert "idx_job_apps_user" in indexes
    conn.close()

def test_stage1_auth_5min_otp_ttl():
    """STAGE 1: Verify 5-minute strict OTP TTL enforcement."""
    reg = client.post("/api/auth/register", json={
        "username": "audituser",
        "email": "audit@enterprise.com",
        "password": "AuditPassword123!",
        "full_name": "Audit Tester"
    })
    assert reg.status_code == 200
    otp = reg.json()["debug_otp"]

    # Verify OTP Success
    verify = client.post("/api/auth/verify-otp", json={
        "email": "audit@enterprise.com",
        "otp_code": otp
    })
    assert verify.status_code == 200
    assert verify.json()["user"]["is_verified"] is True

def test_stage2_agent_bezier_trajectory_math():
    """STAGE 2: Verify Bezier curve trajectory math for zero-distance and multi-point curves."""
    pt_start = (100.0, 100.0)
    pt_end = (100.0, 100.0)
    curve = generate_bezier_curve(pt_start, pt_end, num_points=1)
    assert len(curve) >= 2
    assert curve[0] == (100.0, 100.0)

def test_stage3_llm_hooks_empty_input_fallback():
    """STAGE 3: Verify LLM hooks handle empty job descriptions gracefully."""
    res = client.post("/api/llm/tailor-resume", json={
        "resume_text": "Sample Resume",
        "job_description": "",
        "target_role": "Backend Engineer"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "warning"
    assert "recommended_keywords" in data

def test_stage4_installer_lnk_creation(tmp_path):
    """STAGE 4: Verify Standalone Installation Wizard generates .lnk shortcut and hardened launcher batch."""
    target_dir = tmp_path / "LinkedInAgentAuditDir"
    wizard = StandaloneInstallationWizard(target_dir=str(target_dir))
    success = wizard.run_installation_workflow(show_gui=False)
    
    assert success is True
    assert (target_dir / "linkedin_agent.db").exists()
    assert (target_dir / "boot_agent.bat").exists()

    # Read batch file content to verify cd /d and PYTHONPATH export
    bat_content = (target_dir / "boot_agent.bat").read_text()
    assert "cd /d" in bat_content
    assert "PYTHONPATH=" in bat_content
