import os
import pytest
import sqlite3
from pathlib import Path
from src.backend.database import (
    get_default_db_path,
    get_db_connection,
    init_db,
    UserPreferencesSchema
)

def test_permanent_roaming_appdata_path():
    """Verify that get_default_db_path resolves to %APPDATA%/LinkedInAgent/linkedin_agent.db."""
    default_path = get_default_db_path()
    assert "LinkedInAgent" in default_path
    assert default_path.endswith("linkedin_agent.db")

def test_user_preferences_persistence_and_schema(tmp_path):
    """Verify user_preferences table persistence across simulated restarts and schema migrations."""
    db_file = tmp_path / "test_persistence.db"
    old_db = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = str(db_file)

    try:
        # 1. First initialization
        init_db()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Create dummy user
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, full_name, is_verified) VALUES (?, ?, ?, ?, 1)",
            ("prefuser", "pref@enterprise.com", "dummyhash", "Pref User")
        )
        user_id = cursor.lastrowid

        # Insert user preference payload
        prefs = UserPreferencesSchema(
            user_id=user_id,
            target_roles=["Lead Architect", "Backend Engineer"],
            tech_stack="Python, FastAPI, React",
            work_mode="Remote",
            geography="Global",
            min_salary=150000
        )

        cursor.execute("""
        INSERT INTO user_preferences (user_id, target_roles, tech_stack, work_mode, geography, min_salary)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (prefs.user_id, prefs.target_roles, prefs.tech_stack, prefs.work_mode, prefs.geography, prefs.min_salary))

        conn.commit()
        conn.close()

        # 2. Simulate application restart and schema re-initialization (init_db)
        init_db()

        # 3. Verify data survived schema re-initialization cleanly
        conn2 = get_db_connection()
        cursor2 = conn2.cursor()
        cursor2.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
        row = cursor2.fetchone()

        assert row is not None
        assert row["user_id"] == user_id
        assert "Lead Architect" in row["target_roles"]
        assert row["work_mode"] == "Remote"
        assert row["min_salary"] == 150000

        conn2.close()
    finally:
        if old_db is not None:
            os.environ["DATABASE_PATH"] = old_db
        elif "DATABASE_PATH" in os.environ:
            del os.environ["DATABASE_PATH"]


def test_pydantic_preferences_validation():
    """Verify Pydantic validation rules for UserPreferencesSchema."""
    prefs = UserPreferencesSchema(
        user_id=1,
        target_roles=["Full Stack Developer", "AI Engineer"],
        min_salary=120000
    )
    assert prefs.target_roles == "Full Stack Developer, AI Engineer"
    assert prefs.min_salary == 120000

    # Negative salary validation error check
    with pytest.raises(ValueError):
        UserPreferencesSchema(user_id=1, min_salary=-500)
