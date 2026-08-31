from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from src.backend.database import get_db_connection, UserPreferencesSchema

router = APIRouter(prefix="/api/preferences", tags=["User Preferences"])

@router.get("", response_model=UserPreferencesSchema)
@router.get("/", response_model=UserPreferencesSchema)
def get_user_preferences(user_id: int = Query(1, description="User ID to fetch preferences for")):
    """Fetches saved career preferences for specified user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        # Create default preferences record if none exists
        cursor.execute("""
        INSERT INTO user_preferences (user_id, target_roles, tech_stack, work_mode, geography, min_salary)
        VALUES (?, 'Software Engineer', 'Full Stack', 'Remote', 'Global', 0)
        """, (user_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

    conn.close()
    return dict(row)

@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any])
def update_user_preferences(payload: UserPreferencesSchema):
    """Updates or creates saved career preferences for user in SQLite."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO user_preferences (user_id, target_roles, tech_stack, work_mode, geography, min_salary)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            target_roles = excluded.target_roles,
            tech_stack = excluded.tech_stack,
            work_mode = excluded.work_mode,
            geography = excluded.geography,
            min_salary = excluded.min_salary,
            updated_at = CURRENT_TIMESTAMP
        """, (
            payload.user_id,
            payload.target_roles,
            payload.tech_stack,
            payload.work_mode,
            payload.geography,
            payload.min_salary
        ))
        
        conn.commit()
        
        cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (payload.user_id,))
        updated_row = cursor.fetchone()
        conn.close()
        
        return {
            "status": "success",
            "message": "Career preferences saved successfully.",
            "preferences": dict(updated_row) if updated_row else payload.dict()
        }
    except Exception as err:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to save preferences: {str(err)}")

@router.get("/applications")
def get_user_job_applications(user_id: int = Query(1, description="User ID to fetch applications for")):
    """Fetches real job applications submitted by the autonomous agent from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM job_applications WHERE user_id = ? ORDER BY applied_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

