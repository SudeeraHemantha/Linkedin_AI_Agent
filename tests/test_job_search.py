import os
import pytest
from src.backend.database import get_db_connection, init_db
from src.agent.job_search_engine import (
    generate_linkedin_search_url,
    generate_topjobs_search_url,
    evaluate_job_prerequisites,
    save_harvested_job,
    harvest_and_evaluate_jobs
)

def test_search_url_generation():
    """Verify URL generation for LinkedIn Jobs and TopJobs."""
    linkedin_url = generate_linkedin_search_url("Senior Python Engineer", location="Remote", remote_only=True)
    assert "linkedin.com/jobs/search" in linkedin_url
    assert "keywords=Senior+Python+Engineer" in linkedin_url or "keywords=Senior%20Python%20Engineer" in linkedin_url
    assert "f_WT=2" in linkedin_url
    assert "f_TPR=r86400" in linkedin_url

    topjobs_url = generate_topjobs_search_url("Software Architect")
    assert "topjobs.lk" in topjobs_url
    assert "keywords=Software+Architect" in topjobs_url or "keywords=Software%20Architect" in topjobs_url

def test_evaluate_job_prerequisites():
    """Verify prerequisite ATS evaluation and qualification threshold filtering."""
    resume_text = "Experienced Python Full Stack Developer skilled in FastAPI, React, SQLite, Docker, and Playwright."

    # Matching High-Quality Job
    good_job = {
        "job_title": "Lead Python Developer",
        "company": "ScaleTech",
        "job_url": "https://linkedin.com/jobs/view/9901",
        "description": "Seeking Lead Python Developer with expertise in FastAPI, React, Docker, and SQLite."
    }
    good_res = evaluate_job_prerequisites(good_job, resume_text, min_ats_threshold=70.0)
    assert good_res["qualified"] is True
    assert good_res["status"] == "QUEUED_FOR_APPLICATION"
    assert good_res["ats_match_score"] >= 70.0

    # Non-Matching Legacy Job
    bad_job = {
        "job_title": "Fortran Mainframe Maintainer",
        "company": "Legacy Systems",
        "job_url": "https://linkedin.com/jobs/view/9902",
        "description": "Requires 15 years experience in COBOL, Fortran, Pascal mainframe assembly."
    }
    bad_res = evaluate_job_prerequisites(bad_job, resume_text, min_ats_threshold=85.0)
    assert bad_res["qualified"] is False
    assert bad_res["status"] == "REJECTED_LOW_MATCH"

def test_sqlite_job_deduplication(tmp_path):
    """Verify SQLite UNIQUE(job_url) constraint prevents duplicate job persistence."""
    db_file = tmp_path / "test_jobs.db"
    old_db = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = str(db_file)

    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES ('jobuser', 'job@test.com', 'hash')")
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        eval_data = {
            "job_title": "Python Architect",
            "company": "AI Scale Corp",
            "location": "Remote",
            "job_url": "https://linkedin.com/jobs/view/unique-101",
            "ats_match_score": 92.5,
            "status": "QUEUED_FOR_APPLICATION"
        }

        # First save succeeds
        first_id = save_harvested_job(user_id=user_id, eval_result=eval_data)
        assert first_id is not None

        # Second save with exact same job_url is ignored (deduplicated)
        second_id = save_harvested_job(user_id=user_id, eval_result=eval_data)
        assert second_id is None

        # Verify database row count is exactly 1
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM job_listings WHERE job_url = ?", ("https://linkedin.com/jobs/view/unique-101",))
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1
    finally:
        if old_db is not None:
            os.environ["DATABASE_PATH"] = old_db
        elif "DATABASE_PATH" in os.environ:
            del os.environ["DATABASE_PATH"]

def test_full_harvesting_pipeline(tmp_path):
    """Verify full harvesting and prerequisite evaluation pipeline."""
    db_file = tmp_path / "test_pipeline.db"
    old_db = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = str(db_file)

    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES ('pipeuser', 'pipe@test.com', 'hash')")
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        prefs = {
            "target_roles": "Backend Engineer",
            "geography": "Global",
            "work_mode": "Remote"
        }
        resume = "Senior Python Engineer experienced in FastAPI, SQL, and Playwright."

        result = harvest_and_evaluate_jobs(user_id=user_id, preferences=prefs, resume_text=resume)
        assert result["status"] == "success"
        assert result["harvested_count"] > 0
        assert "linkedin" in result["search_urls"]
        assert "topjobs" in result["search_urls"]
    finally:
        if old_db is not None:
            os.environ["DATABASE_PATH"] = old_db
        elif "DATABASE_PATH" in os.environ:
            del os.environ["DATABASE_PATH"]

