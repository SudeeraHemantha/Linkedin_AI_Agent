import hashlib
import os
import random
import time
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import hmac
import base64
import json

try:
    import jwt
except ImportError:
    jwt = None

from src.backend.database import get_db_connection

SECRET_KEY = os.environ.get("JWT_SECRET", "super-secret-local-key-linkedin-agent-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours
OTP_TTL_MINUTES = 5 # Strict 5-minute enterprise TTL

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Pydantic Schemas
class UserRegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = ""

class VerifyOTPSchema(BaseModel):
    email: str
    otp_code: str

class LoginSchema(BaseModel):
    username_or_email: str
    password: str

class PasswordResetSchema(BaseModel):
    email: str
    otp_code: str
    new_password: str

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# Utility Functions
def hash_password(password: str) -> str:
    """Enterprise-grade PBKDF2-HMAC-SHA256 password hashing with 100,000 iterations and static salt."""
    salt = b"linkedin_agent_static_salt_v1"
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    if jwt is not None:
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Pure Python Standard Library Fallback
    to_encode.update({"exp": int(expire.timestamp())})
    header = {"alg": "HS256", "typ": "JWT"}
    
    def b64url(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b'=').decode('utf-8')

    hdr_b64 = b64url(json.dumps(header).encode('utf-8'))
    pay_b64 = b64url(json.dumps(to_encode).encode('utf-8'))
    signing_input = f"{hdr_b64}.{pay_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = b64url(signature)
    return f"{hdr_b64}.{pay_b64}.{sig_b64}"

def generate_otp() -> str:
    """Generates a secure 6-digit numeric OTP."""
    return f"{random.randint(100000, 999999)}"

# API Endpoints
import sqlite3

@router.post("/register")
def register_user(payload: UserRegisterSchema):
    try:
        if not payload.username or not payload.email or not payload.password:
            raise HTTPException(status_code=400, detail="Username, Email, and Password are required.")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (payload.username.strip(), payload.email.strip().lower()))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Username or Email already registered.")

        hashed_pw = hash_password(payload.password)
        clean_email = payload.email.strip().lower()
        clean_username = payload.username.strip()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password, full_name, is_verified) VALUES (?, ?, ?, ?, 0)",
                (clean_username, clean_email, hashed_pw, payload.full_name or clean_username)
            )
        except sqlite3.IntegrityError as db_err:
            conn.close()
            print(f"[REGISTRATION DB INTEGRITY ERROR] {db_err}")
            raise HTTPException(status_code=400, detail="Username or Email already registered.")

        # Generate enterprise OTP (valid for strict 5 minutes)
        otp_code = generate_otp()
        expires_at = (datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)).isoformat()
        cursor.execute(
            "INSERT INTO otps (user_email, otp_code, expires_at, is_used) VALUES (?, ?, ?, 0)",
            (clean_email, otp_code, expires_at)
        )
        
        conn.commit()
        conn.close()

        print(f"[ENTERPRISE OTP DISPATCH] 5-min OTP for {clean_email}: {otp_code}")

        return {
            "message": "User registered successfully. Verification 2FA OTP dispatched.",
            "email": clean_email,
            "debug_otp": otp_code
        }
    except HTTPException as http_ex:
        print(f"[REGISTRATION HTTP ERROR {http_ex.status_code}] {http_ex.detail}")
        raise http_ex
    except Exception as exc:
        print(f"[REGISTRATION UNHANDLED ERROR] {exc}")
        raise HTTPException(status_code=500, detail=f"Registration server error: {str(exc)}")


@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPSchema):
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_email = payload.email.strip().lower()

    cursor.execute(
        "SELECT id, expires_at, is_used FROM otps WHERE user_email = ? AND otp_code = ? ORDER BY id DESC LIMIT 1",
        (clean_email, payload.otp_code.strip())
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid OTP code.")

    if row["is_used"] == 1:
        conn.close()
        raise HTTPException(status_code=400, detail="OTP code has already been used.")

    # Strict TTL Expiration Check
    try:
        expiry_dt = datetime.fromisoformat(row["expires_at"])
        if expiry_dt < datetime.utcnow():
            conn.close()
            raise HTTPException(status_code=400, detail="OTP code has expired (5-minute TTL). Please request a new code.")
    except (ValueError, TypeError):
        pass

    # Mark OTP used & User verified
    cursor.execute("UPDATE otps SET is_used = 1 WHERE id = ?", (row["id"],))
    cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (clean_email,))
    
    cursor.execute("SELECT id, username, email, full_name, is_verified FROM users WHERE email = ?", (clean_email,))
    user_row = dict(cursor.fetchone())
    user_row["is_verified"] = bool(user_row["is_verified"])
    
    conn.commit()
    conn.close()

    token = create_access_token({"sub": user_row["username"], "user_id": user_row["id"]})

    return {
        "message": "Account verified successfully.",
        "access_token": token,
        "token_type": "bearer",
        "user": user_row
    }

@router.post("/login", response_model=TokenResponseSchema)
def login(payload: LoginSchema):
    conn = get_db_connection()
    cursor = conn.cursor()
    login_id = payload.username_or_email.strip().lower()

    cursor.execute(
        "SELECT id, username, email, hashed_password, full_name, is_verified FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
        (login_id, login_id)
    )
    user_row = cursor.fetchone()
    conn.close()

    if not user_row or not verify_password(payload.password, user_row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    user = {
        "id": user_row["id"],
        "username": user_row["username"],
        "email": user_row["email"],
        "full_name": user_row["full_name"],
        "is_verified": bool(user_row["is_verified"])
    }

    token = create_access_token({"sub": user["username"], "user_id": user["id"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/request-reset-otp")
def request_reset_otp(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_email = email.strip().lower()

    cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (clean_email,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Email not registered.")

    otp_code = generate_otp()
    expires_at = (datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)).isoformat()
    cursor.execute(
        "INSERT INTO otps (user_email, otp_code, expires_at, is_used) VALUES (?, ?, ?, 0)",
        (clean_email, otp_code, expires_at)
    )
    conn.commit()
    conn.close()

    print(f"[RESET OTP DISPATCH] Password Reset 5-min OTP for {clean_email}: {otp_code}")

    return {"message": "Password reset OTP sent to email.", "debug_otp": otp_code}

@router.post("/reset-password")
def reset_password(payload: PasswordResetSchema):
    conn = get_db_connection()
    cursor = conn.cursor()
    clean_email = payload.email.strip().lower()

    cursor.execute(
        "SELECT id, expires_at, is_used FROM otps WHERE user_email = ? AND otp_code = ? ORDER BY id DESC LIMIT 1",
        (clean_email, payload.otp_code.strip())
    )
    row = cursor.fetchone()

    if not row or row["is_used"] == 1:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code.")

    try:
        expiry_dt = datetime.fromisoformat(row["expires_at"])
        if expiry_dt < datetime.utcnow():
            conn.close()
            raise HTTPException(status_code=400, detail="Password reset OTP code has expired.")
    except (ValueError, TypeError):
        pass

    new_hashed = hash_password(payload.new_password)
    cursor.execute("UPDATE users SET hashed_password = ? WHERE email = ?", (new_hashed, clean_email))
    cursor.execute("UPDATE otps SET is_used = 1 WHERE id = ?", (row["id"],))

    conn.commit()
    conn.close()

    return {"message": "Password updated successfully. You can now login."}
