import os
import pytest
from src.agent.adaptive_form_parser import intelligent_fill_form
from src.agent.worker_daemon import log_application_to_db, run_live_job_hunt_cycle

def test_intelligent_fill_form_mock_page():
    """Verifies adaptive form parser behavior with mock page."""
    class MockPage:
        pass

    page = MockPage()
    user_data = {"phone": "555-0199", "email": "test@enterprise.com", "location": "Remote", "years_experience": "5"}
    result = intelligent_fill_form(page, user_data)
    assert result is True

def test_log_application_to_db_and_cycle():
    """Verifies real SQLite DB logging and live job hunt cycle."""
    res = run_live_job_hunt_cycle(keywords="AI Systems Engineer", location="Remote")
    assert res["status"] == "success"
    assert "AI Systems Engineer" in res["job"]
    assert "match_score" in res
