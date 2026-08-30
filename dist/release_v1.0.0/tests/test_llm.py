import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)

def test_tailor_resume_endpoint():
    """Tests the /api/llm/tailor-resume API endpoint for ATS match scoring and bullet generation."""
    response = client.post("/api/llm/tailor-resume", json={
        "resume_text": "Experienced Python Software Engineer skilled in FastAPI, SQL, and Playwright.",
        "job_description": "We are seeking a Lead Full Stack Engineer with expertise in Python, FastAPI, React, and browser automation.",
        "target_role": "Lead Full Stack Engineer"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "match_score" in data
    assert data["match_score"] > 80.0
    assert "recommended_keywords" in data
    assert isinstance(data["recommended_keywords"], list)
    assert len(data["recommended_keywords"]) > 0
    assert "suggested_bullet_points" in data
    assert isinstance(data["suggested_bullet_points"], list)

def test_generate_cover_letter_endpoint():
    """Tests the /api/llm/generate-cover-letter API endpoint."""
    response = client.post("/api/llm/generate-cover-letter", json={
        "resume_text": "Software Engineer with 5 years experience.",
        "company_name": "TechScale Systems",
        "job_title": "Senior AI Platform Engineer",
        "job_description": "Looking for AI Platform Engineers."
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["company_name"] == "TechScale Systems"
    assert data["job_title"] == "Senior AI Platform Engineer"
    assert "TechScale Systems" in data["cover_letter"]
    assert "Senior AI Platform Engineer" in data["cover_letter"]
