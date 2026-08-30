import sqlite3
import os
from typing import Generator, Optional, List, Dict, Any
from pydantic import BaseModel, field_validator

class UserPreferencesSchema(BaseModel):
    user_id: int
    target_roles: Optional[str] = "Software Engineer"
    tech_stack: Optional[str] = "Full Stack"
    work_mode: Optional[str] = "Remote"
    geography: Optional[str] = "Global"
    min_salary: Optional[int] = 0

    @field_validator("target_roles", "tech_stack", "work_mode", "geography", mode="before")
    def sanitize_strings(cls, v):
        if isinstance(v, list):
            return ", ".join(v)
        if isinstance(v, str):
            return v.strip()
        return v or ""

    @field_validator("min_salary")
    def validate_salary(cls, v):
        if v is not None and v < 0:
            raise ValueError("Minimum salary cannot be negative.")
        return v or 0

def get_default_db_path() -> str:
    """Resolves permanent roaming AppData directory for non-volatile SQLite database persistence."""
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    db_dir = os.path.join(appdata, "LinkedInAgent")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "linkedin_agent.db")

def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dict-like row access and enforced foreign keys."""
    db_path = os.environ.get("DATABASE_PATH") or get_default_db_path()
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initializes SQLite database tables and indexes if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        full_name TEXT,
        is_verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # OTP table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        otp_code TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        is_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # User Preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        target_roles TEXT DEFAULT '',
        tech_stack TEXT DEFAULT '',
        work_mode TEXT DEFAULT 'Remote',
        geography TEXT DEFAULT 'Global',
        min_salary INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Resumes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content_json TEXT NOT NULL,
        is_default INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Job applications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        job_url TEXT NOT NULL,
        status TEXT DEFAULT 'APPLIED',
        match_score REAL DEFAULT 0.0,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Job listings harvester table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        job_url TEXT UNIQUE NOT NULL,
        ats_match_score REAL DEFAULT 0.0,
        status TEXT DEFAULT 'QUEUED_FOR_APPLICATION',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Agent execution logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        level TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Performance Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_otps_email_code ON otps(user_email, otp_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_apps_user ON job_applications(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_prefs_user_id ON user_preferences(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_listings_url ON job_listings(job_url);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_listings_user ON job_listings(user_id);")


    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized with foreign keys, user_preferences, and performance indexes.")
