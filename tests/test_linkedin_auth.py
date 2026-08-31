import os
import json
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.linkedin_auth import (
    get_cookies_file_path,
    save_stored_cookies,
    load_stored_cookies
)

client = TestClient(app)

def test_linkedin_status_endpoint(tmp_path):
    """Verifies GET /api/linkedin/status returns status and path."""
    response = client.get("/api/linkedin/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "cookie_count" in data
    assert "cookies_path" in data

def test_save_and_load_stored_cookies(tmp_path):
    """Verifies cookie serialization and deserialization functions."""
    sample_cookies = [
        {"name": "li_at", "value": "test_cookie_value_12345", "domain": ".linkedin.com", "path": "/"}
    ]
    
    # Test saving
    success = save_stored_cookies(sample_cookies)
    assert success is True
    
    # Test loading
    loaded = load_stored_cookies()
    assert isinstance(loaded, list)
    assert len(loaded) >= 1
    assert loaded[0]["name"] == "li_at"
