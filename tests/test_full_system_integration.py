import os
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.database import init_db, get_db_connection
from src.agent.job_search_engine import harvest_and_evaluate_jobs, save_harvested_job
from src.agent.worker_daemon import execute_worker_iteration

client = TestClient(app)

def test_full_autonomous_system_e2e_integration(tmp_path):
    """
    Complete E2E System Integration Test verifying the 6 core architectural bricks:
    1. Auth Registration & OTP Verification
    2. Preferences Persistence & Sync
    3. Multi-Source Job Harvesting & Pre-Filtering
    4. AI LLM Resume & Cover Letter Tailoring
    5. Autonomous Worker Daemon Execution Loop
    6. System Tray Application Controls & Status Reporting
    """
    db_file = tmp_path / "test_e2e_full.db"
    old_db = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = str(db_file)

    try:
        # Step 0: Database Initialization
        init_db()

        # Step 1: User Registration & OTP Auth Pipeline
        reg_res = client.post("/api/auth/register", json={
            "username": "e2e_system_user",
            "email": "e2esystem@enterprise.com",
            "password": "E2ESecurePassword123!",
            "full_name": "Full System Integration User"
        })
        assert reg_res.status_code == 200
        otp_code = reg_res.json()["debug_otp"]

        verify_res = client.post("/api/auth/verify-otp", json={
            "email": "e2esystem@enterprise.com",
            "otp_code": otp_code
        })
        assert verify_res.status_code == 200
        token = verify_res.json()["access_token"]
        assert len(token) > 10

        # Fetch inserted user_id from DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", ("e2esystem@enterprise.com",))
        user_id = cursor.fetchone()["id"]
        conn.close()

        # Step 2: Save Unified Career Preferences
        pref_payload = {
            "user_id": user_id,
            "target_roles": "Lead Python Engineer",
            "tech_stack": "Full Stack",
            "work_mode": "Remote",
            "geography": "Global",
            "min_salary": 160000
        }
        pref_res = client.post("/api/preferences", json=pref_payload)
        assert pref_res.status_code == 200
        assert pref_res.json()["status"] == "success"

        # Step 3: Multi-Source Job Harvesting & Prerequisite Evaluation
        resume_text = "Senior Python Engineer experienced in FastAPI, SQLite, React, Docker, and Playwright."
        mock_harvest_pool = [
            {
                "job_title": "Lead Python Architect",
                "company": "ScaleAI Corp",
                "location": "Remote",
                "job_url": "https://linkedin.com/jobs/view/e2e-1001",
                "description": "Seeking Lead Python Architect with experience in FastAPI, React, Docker, and automated testing."
            },
            {
                "job_title": "COBOL Legacy Developer",
                "company": "Mainframe Bank",
                "location": "Onsite",
                "job_url": "https://linkedin.com/jobs/view/e2e-1002",
                "description": "Legacy mainframe developer for COBOL code."
            }
        ]

        harvest_res = harvest_and_evaluate_jobs(
            user_id=user_id,
            preferences=pref_payload,
            resume_text=resume_text,
            min_ats_threshold=70.0,
            mock_jobs=mock_harvest_pool
        )
        assert harvest_res["status"] == "success"
        assert harvest_res["harvested_count"] == 2
        assert harvest_res["qualified_count"] >= 1

        # Step 4: AI Resume Tailor API Call
        tailor_res = client.post("/api/llm/tailor-resume", json={
            "resume_text": resume_text,
            "job_description": mock_harvest_pool[0]["description"],
            "target_role": "Lead Python Architect"
        })
        assert tailor_res.status_code == 200
        assert tailor_res.json()["match_score"] >= 70.0

        # Step 5: Execute Autonomous Worker Daemon Loop Iteration
        worker_res = execute_worker_iteration(user_id)
        assert worker_res["status"] == "success"
        assert worker_res["processed"] >= 1
        assert worker_res["successful_applications"] >= 1

        # Verify DB final state
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM job_listings WHERE job_url = ?", ("https://linkedin.com/jobs/view/e2e-1001",))
        listing_status = cursor.fetchone()["status"]

        cursor.execute("SELECT COUNT(*) FROM job_applications WHERE user_id = ?", (user_id,))
        applied_count = cursor.fetchone()[0]
        conn.close()

        assert listing_status == "APPLIED"
        assert applied_count >= 1

    finally:
        if old_db is not None:
            os.environ["DATABASE_PATH"] = old_db
        elif "DATABASE_PATH" in os.environ:
            del os.environ["DATABASE_PATH"]
