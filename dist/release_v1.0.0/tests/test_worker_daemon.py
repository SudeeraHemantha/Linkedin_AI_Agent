import os
import pytest
from src.backend.database import get_db_connection, init_db
from src.agent.job_search_engine import save_harvested_job
from src.agent.worker_daemon import (
    exponential_backoff_retry,
    get_user_preferences_from_db,
    get_user_master_resume,
    execute_worker_iteration,
    run_autonomous_job_worker
)



def test_exponential_backoff_retry_success():
    """Verify exponential backoff retries transient failures and returns result upon success."""
    attempts = 0

    def flaky_func():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ConnectionError("Transient network timeout")
        return "SUCCESS"

    result = exponential_backoff_retry(flaky_func, max_retries=3, initial_delay=0.01)
    assert result == "SUCCESS"
    assert attempts == 2

def test_exponential_backoff_retry_exhaustion():
    """Verify exponential backoff raises exception when all retries fail."""
    def failing_func():
        raise TimeoutError("Persistent timeout")

    with pytest.raises(TimeoutError):
        exponential_backoff_retry(failing_func, max_retries=2, initial_delay=0.01)

def test_worker_daemon_iteration_flow(tmp_path):
    """Verify full worker daemon iteration processing queued jobs into APPLIED status."""
    db_file = tmp_path / "test_worker.db"
    old_db = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = str(db_file)

    try:
        init_db()

        # Create test user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES ('daemonuser', 'daemon@test.com', 'hash')")
        user_id = cursor.lastrowid

        # Insert user preferences
        cursor.execute("""
        INSERT INTO user_preferences (user_id, target_roles, tech_stack, work_mode, geography)
        VALUES (?, 'Python Developer', 'Python, FastAPI', 'Remote', 'Global')
        """, (user_id,))
        
        conn.commit()
        conn.close()

        # Seed pre-qualified job listing into queue
        eval_job = {
            "job_title": "Python Developer",
            "company": "TechScale Inc",
            "location": "Remote",
            "job_url": "https://linkedin.com/jobs/view/worker-101",
            "ats_match_score": 88.0,
            "status": "QUEUED_FOR_APPLICATION"
        }
        save_harvested_job(user_id, eval_job)

        # Run 1 worker iteration
        result = execute_worker_iteration(user_id)
        assert result["status"] == "success"
        assert result["processed"] >= 1
        assert result["successful_applications"] >= 1

        # Verify job_listings status updated to APPLIED
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM job_listings WHERE job_url = ?", ("https://linkedin.com/jobs/view/worker-101",))
        status = cursor.fetchone()["status"]

        # Verify record inserted into job_applications
        cursor.execute("SELECT COUNT(*) FROM job_applications WHERE user_id = ?", (user_id,))
        app_count = cursor.fetchone()[0]
        conn.close()

        assert status == "APPLIED"
        assert app_count >= 1
    finally:
        if old_db is not None:
            os.environ["DATABASE_PATH"] = old_db
        elif "DATABASE_PATH" in os.environ:
            del os.environ["DATABASE_PATH"]

def test_run_autonomous_job_worker_max_iterations(tmp_path):
    """Verify autonomous job worker daemon runs for fixed iterations without crashing."""
    db_file = tmp_path / "test_loop.db"
    old_db = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = str(db_file)

    try:
        init_db()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES ('loopuser', 'loop@test.com', 'hash')")
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Run worker loop for 2 iterations with 0 polling interval
        run_autonomous_job_worker(user_id, poll_interval_seconds=0, max_iterations=2)
    finally:
        if old_db is not None:
            os.environ["DATABASE_PATH"] = old_db
        elif "DATABASE_PATH" in os.environ:
            del os.environ["DATABASE_PATH"]
