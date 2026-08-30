from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.database import init_db
from src.backend.auth import router as auth_router
from src.backend.llm_hooks import router as llm_router

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.main:app", host="127.0.0.1", port=8000, reload=True)
