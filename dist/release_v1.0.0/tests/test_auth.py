import os
import pytest
import sqlite3
from fastapi.testclient import TestClient

# Configure temporary test database environment variable before backend imports
os.environ["DATABASE_PATH"] = "test_linkedin_agent.db"

from src.backend.main import app
from src.backend.database import init_db, get_db_connection
from src.backend.auth import hash_password, verify_password, generate_otp

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_database():
    """Initializes clean database for each test run."""
    if os.path.exists("test_linkedin_agent.db"):
        os.remove("test_linkedin_agent.db")
    init_db()
    yield
    if os.path.exists("test_linkedin_agent.db"):
        os.remove("test_linkedin_agent.db")

def test_password_hashing():
    raw_pass = "EnterpriseSecret123!"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_otp_generation():
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()

def test_user_registration_and_otp_flow():
    # 1. Register User
    reg_response = client.post("/api/auth/register", json={
        "username": "testengineer",
        "email": "test@enterprise.com",
        "password": "SecurePassword123!",
        "full_name": "Test Engineer"
    })
    assert reg_response.status_code == 200
    data = reg_response.json()
    assert "debug_otp" in data
    otp_code = data["debug_otp"]

    # 2. Verify OTP
    verify_response = client.post("/api/auth/verify-otp", json={
        "email": "test@enterprise.com",
        "otp_code": otp_code
    })
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert "access_token" in verify_data
    assert verify_data["user"]["is_verified"] is True

def test_login_authentication():
    # Register & Verify
    reg = client.post("/api/auth/register", json={
        "username": "loginuser",
        "email": "login@enterprise.com",
        "password": "Password123!",
        "full_name": "Login User"
    })
    otp_code = reg.json()["debug_otp"]
    client.post("/api/auth/verify-otp", json={"email": "login@enterprise.com", "otp_code": otp_code})

    # Test Login
    login_response = client.post("/api/auth/login", json={
        "username_or_email": "loginuser",
        "password": "Password123!"
    })
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["user"]["username"] == "loginuser"
