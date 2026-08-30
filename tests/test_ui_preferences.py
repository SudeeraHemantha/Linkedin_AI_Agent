import os
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.database import init_db, get_db_connection

client = TestClient(app)

def test_get_and_post_preferences_api(tmp_path):
    """Verify GET and POST /api/preferences endpoints for preference serialization and deserialization."""
    db_file = tmp_path / "test_ui_pref.db"
    old_db = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = str(db_file)

    try:
        init_db()

        # Seed user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES ('uiprefuser', 'ui@test.com', 'hash')")
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # 1. GET /api/preferences returns defaults
        get_res = client.get(f"/api/preferences?user_id={user_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["user_id"] == user_id
        assert get_data["work_mode"] == "Remote"

        # 2. POST /api/preferences updates preference record
        post_payload = {
            "user_id": user_id,
            "target_roles": "Lead Systems Architect",
            "tech_stack": "Backend",
            "work_mode": "Hybrid",
            "geography": "US",
            "min_salary": 180000
        }
        post_res = client.post("/api/preferences", json=post_payload)
        assert post_res.status_code == 200
        post_data = post_res.json()
        assert post_data["status"] == "success"
        assert post_data["preferences"]["target_roles"] == "Lead Systems Architect"
        assert post_data["preferences"]["min_salary"] == 180000

        # 3. GET /api/preferences reflects updated record
        verify_res = client.get(f"/api/preferences?user_id={user_id}")
        assert verify_res.status_code == 200
        verify_data = verify_res.json()
        assert verify_data["target_roles"] == "Lead Systems Architect"
        assert verify_data["tech_stack"] == "Backend"
        assert verify_data["work_mode"] == "Hybrid"
        assert verify_data["geography"] == "US"
        assert verify_data["min_salary"] == 180000
    finally:
        if old_db is not None:
            os.environ["DATABASE_PATH"] = old_db
        elif "DATABASE_PATH" in os.environ:
            del os.environ["DATABASE_PATH"]
