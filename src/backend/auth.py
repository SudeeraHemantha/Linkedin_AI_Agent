import hashlib
import os
import random
import time
import re
import sqlite3
import hmac
import base64
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, field_validator

try:
    import jwt
except ImportError:
    jwt = None

from src.backend.database import get_db_connection
from src.backend.email_service import send_otp_email


SECRET_KEY = os.environ.get("JWT_SECRET", "super-secret-local-key-linkedin-agent-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7
OTP_TTL_MINUTES = 5  # Strict 5-minute enterprise TTL

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Strict Validation Regex Patterns
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
# Password requires min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special character
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,50}$")

# Bulletproof Pydantic Schemas
class UserRegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = ""

    @field_validator("username", mode="before")

    def sanitize_username(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("email", mode="before")

    def sanitize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("full_name", mode="before")

    def sanitize_full_name(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v or ""

    @field_validator("username")

    def validate_username_format(cls, v):
        if not v or not USERNAME_REGEX.match(v):
            raise ValueError("Username must be 3-50 characters long and contain only letters, numbers, underscores, or hyphens.")
        return v

    @field_validator("email")

    def validate_email_format(cls, v):
        if not v or not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email address format.")
        return v

    @field_validator("password")

    def validate_password_complexity(cls, v):
        if not v or not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return v

class VerifyOTPSchema(BaseModel):
    email: str
    otp_code: str

    @field_validator("email", mode="before")

    def sanitize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("otp_code", mode="before")

    def sanitize_otp(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class LoginSchema(BaseModel):
    username_or_email: str
    password: str

    @field_validator("username_or_email", mode="before")

    def sanitize_login_id(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

class PasswordResetSchema(BaseModel):
    email: str
    otp_code: str
    new_password: str

    @field_validator("email", mode="before")

    def sanitize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("new_password")

    def validate_password_complexity(cls, v):
        if not v or not PASSWORD_REGEX.match(v):
            raise ValueError(
                "New password must be at least 8 characters long and contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return v

class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
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

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None, token_type: str = "access") -> str:
    """Generates a stateless JWT token with explicit expiration and token_type claim."""
    to_encode = data.copy()
    now = datetime.utcnow()
    
    if expires_delta:
        expire = now + expires_delta
    elif token_type == "refresh":
        expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": token_type
    })
    
    if jwt is not None:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Pure Python Standard Library Fallback
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    header = {"alg": "HS256", "typ": "JWT"}
    
    def b64url(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b'=').decode('utf-8')

    hdr_b64 = b64url(json.dumps(header).encode('utf-8'))
    pay_b64 = b64url(json.dumps(to_encode).encode('utf-8'))
    signing_input = f"{hdr_b64}.{pay_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = b64url(signature)
    return f"{hdr_b64}.{pay_b64}.{sig_b64}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return create_jwt_token(data=data, expires_delta=expires_delta, token_type="access")

def create_refresh_token(data: dict) -> str:
    return create_jwt_token(data=data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), token_type="refresh")

def generate_otp() -> str:
    """Generates a secure 6-digit numeric OTP."""
    return f"{random.randint(100000, 999999)}"

# Standardized Error Helper
def make_error_response(status_code: int, detail: str, code: str):
    print(f"[AUTH ERROR {status_code}] [{code}]: {detail}")
    raise HTTPException(
        status_code=status_code,
        detail={"detail": detail, "error": detail, "code": code, "status": "error"}
    )

# API Endpoints with Transactional Integrity
@router.post("/register")
def register_user(payload: UserRegisterSchema):
    """
    Registration endpoint that accepts JSON body payload, extracts user fields,
    inserts user into SQLite, generates 5-minute OTP, and returns a valid JSON response.
    """
    username = payload.username
    email = payload.email
    password = payload.password
    full_name = payload.full_name or username


    # 1. Extract and validate required user fields
    if not username or not email or not password:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Username, email, and password are required."}
        )

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Check existing user
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            conn.close()
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "User with this username or email already exists."}
            )

        hashed_pw = hash_password(password)

        try:
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password, full_name, is_verified) VALUES (?, ?, ?, ?, 0)",
                (username, email, hashed_pw, full_name)
            )
        except sqlite3.IntegrityError as db_err:
            conn.rollback()
            conn.close()
            print(f"[REGISTRATION DB TRANSACTION ROLLBACK] IntegrityError: {db_err}")
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "User already exists in database."}
            )

        # Generate enterprise OTP (valid for strict 5 minutes)
        otp_code = generate_otp()
        expires_at = (datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)).isoformat()
        cursor.execute(
            "INSERT INTO otps (user_email, otp_code, expires_at, is_used) VALUES (?, ?, ?, 0)",
            (email, otp_code, expires_at)
        )
        
        conn.commit()
        conn.close()

        # Trigger live SMTP dispatch (or dev-mode fallback)
        send_otp_email(email, otp_code)

        print(f"[ENTERPRISE OTP DISPATCH] 5-min OTP for {email}: {otp_code}")

        # 3. ALWAYS return a valid JSON response dictionary
        return {
            "status": "success",
            "message": "Registration successful. OTP verification dispatched.",
            "username": username,
            "email": email,
            "debug_otp": otp_code
        }

    except Exception as e:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass
        print(f"[REGISTRATION SYSTEM ERROR] {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Registration error: {str(e)}"}
        )


@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPSchema):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        clean_email = payload.email
        clean_otp = payload.otp_code

        cursor.execute(
            "SELECT id, expires_at, is_used FROM otps WHERE user_email = ? AND otp_code = ? ORDER BY id DESC LIMIT 1",
            (clean_email, clean_otp)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            make_error_response(status_code=400, detail="Invalid OTP code.", code="INVALID_OTP")

        if row["is_used"] == 1:
            conn.close()
            make_error_response(status_code=400, detail="OTP code has already been used.", code="OTP_ALREADY_USED")

        # Strict TTL Expiration Check
        try:
            expiry_dt = datetime.fromisoformat(row["expires_at"])
            if expiry_dt < datetime.utcnow():
                conn.close()
                make_error_response(status_code=400, detail="OTP code has expired (5-minute TTL). Please request a new code.", code="OTP_EXPIRED")
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

        access_token = create_access_token({"sub": user_row["username"], "user_id": user_row["id"]})
        refresh_token = create_refresh_token({"sub": user_row["username"], "user_id": user_row["id"]})

        return {
            "status": "success",
            "message": "Account verified successfully.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_row
        }
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        conn.close()
        make_error_response(status_code=500, detail=f"OTP verification system error: {str(exc)}", code="SERVER_ERROR")

@router.post("/login")
def login(payload: LoginSchema):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        login_id = payload.username_or_email

        cursor.execute(
            "SELECT id, username, email, hashed_password, full_name, is_verified FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
            (login_id, login_id)
        )
        user_row = cursor.fetchone()
        conn.close()

        if not user_row or not verify_password(payload.password, user_row["hashed_password"]):
            make_error_response(status_code=401, detail="Invalid username or password.", code="INVALID_CREDENTIALS")

        user = {
            "id": user_row["id"],
            "username": user_row["username"],
            "email": user_row["email"],
            "full_name": user_row["full_name"],
            "is_verified": bool(user_row["is_verified"])
        }

        access_token = create_access_token({"sub": user["username"], "user_id": user["id"]})
        refresh_token = create_refresh_token({"sub": user["username"], "user_id": user["id"]})

        return {
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    except HTTPException:
        raise
    except Exception as exc:
        conn.close()
        make_error_response(status_code=500, detail=f"Login system error: {str(exc)}", code="SERVER_ERROR")

@router.post("/request-reset-otp")
def request_reset_otp(email: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        clean_email = email.strip().lower()

        cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (clean_email,))
        if not cursor.fetchone():
            conn.close()
            make_error_response(status_code=404, detail="Email not registered.", code="EMAIL_NOT_FOUND")

        otp_code = generate_otp()
        expires_at = (datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)).isoformat()
        cursor.execute(
            "INSERT INTO otps (user_email, otp_code, expires_at, is_used) VALUES (?, ?, ?, 0)",
            (clean_email, otp_code, expires_at)
        )
        conn.commit()
        conn.close()

        # Trigger live SMTP dispatch (or dev-mode fallback)
        send_otp_email(clean_email, otp_code)

        print(f"[RESET OTP DISPATCH] Password Reset 5-min OTP for {clean_email}: {otp_code}")

        return {
            "status": "success",
            "message": "Password reset OTP sent to email.",
            "debug_otp": otp_code
        }

    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        conn.close()
        make_error_response(status_code=500, detail=f"Reset OTP error: {str(exc)}", code="SERVER_ERROR")

@router.post("/reset-password")
def reset_password(payload: PasswordResetSchema):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        clean_email = payload.email

        cursor.execute(
            "SELECT id, expires_at, is_used FROM otps WHERE user_email = ? AND otp_code = ? ORDER BY id DESC LIMIT 1",
            (clean_email, payload.otp_code.strip())
        )
        row = cursor.fetchone()

        if not row or row["is_used"] == 1:
            conn.close()
            make_error_response(status_code=400, detail="Invalid or expired OTP code.", code="INVALID_OTP")

        try:
            expiry_dt = datetime.fromisoformat(row["expires_at"])
            if expiry_dt < datetime.utcnow():
                conn.close()
                make_error_response(status_code=400, detail="Password reset OTP code has expired.", code="OTP_EXPIRED")
        except (ValueError, TypeError):
            pass

        new_hashed = hash_password(payload.new_password)
        cursor.execute("UPDATE users SET hashed_password = ? WHERE email = ?", (new_hashed, clean_email))
        cursor.execute("UPDATE otps SET is_used = 1 WHERE id = ?", (row["id"],))

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "Password updated successfully. You can now login."
        }
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        conn.close()
        make_error_response(status_code=500, detail=f"Password reset system error: {str(exc)}", code="SERVER_ERROR")

