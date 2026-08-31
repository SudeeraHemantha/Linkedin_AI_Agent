from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.database import init_db
from src.backend.auth import router as auth_router
from src.backend.llm_hooks import router as llm_router
from src.backend.preferences import router as preferences_router
from src.backend.linkedin_auth import router as linkedin_auth_router

app = FastAPI(
    title="LinkedIn Autonomous Agent Backend",
    description="Local-First Hybrid Application Core Backend API",
    version="1.0.0"
)

# CORS Configuration for local frontend SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Router Registrations
app.include_router(auth_router)
app.include_router(llm_router)
app.include_router(preferences_router)
app.include_router(linkedin_auth_router)



@app.on_event("startup")
def on_startup():
    init_db()
    print("Backend server initialized & SQLite database connected.")

@app.get("/")
def root():
    return {
        "app": "LinkedIn Autonomous Agent",
        "version": "1.0.0",
        "status": "ONLINE",
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

@app.get("/api/applications")
def get_job_applications(user_id: int = 1):
    from src.backend.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_applications WHERE user_id = ? ORDER BY applied_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

from pydantic import BaseModel

class AgentStartPayload(BaseModel):
    keywords: str = "Full Stack Engineer"
    location: str = "Remote"

@app.post("/api/agent/start")
def start_agent_job_hunt(payload: AgentStartPayload):
    from src.agent.worker_daemon import run_live_job_hunt_cycle
    res = run_live_job_hunt_cycle(keywords=payload.keywords, location=payload.location)
    return res



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.main:app", host="127.0.0.1", port=8000, reload=True)
