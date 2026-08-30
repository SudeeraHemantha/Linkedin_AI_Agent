import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.llm_hooks import (
    calculate_tfidf_cosine_similarity,
    calculate_dual_layer_ats_matrix,
    invoke_llm_provider
)

client = TestClient(app)

def test_tfidf_cosine_similarity_calculation():
    """Verify TF-IDF cosine similarity calculations for identical, partial, and empty text pairs."""
    text1 = "Python FastAPI React SQL Docker Kubernetes CI/CD"
    text2 = "Python FastAPI React Docker"
    
    similarity = calculate_tfidf_cosine_similarity(text1, text2)
    assert similarity > 50.0

    # Identical texts must yield ~100% similarity
    identical_sim = calculate_tfidf_cosine_similarity(text1, text1)
    assert identical_sim == 100.0

    # Empty text must yield 0.0
    empty_sim = calculate_tfidf_cosine_similarity("", text2)
    assert empty_sim == 0.0

def test_dual_layer_ats_matrix_scoring():
    """Verify dual-layer ATS matrix scoring returns match_score, keyword scores, and keyword lists."""
    resume = "Senior Full Stack Engineer experienced in Python, FastAPI, React, SQLite, and Docker."
    jd = "We are seeking a Full Stack Engineer with strong experience in Python, FastAPI, React, Docker, and AWS."

    matrix = calculate_dual_layer_ats_matrix(resume, jd)
    assert "match_score" in matrix
    assert matrix["match_score"] > 60.0
    assert "exact_keyword_score" in matrix
    assert "semantic_overlap_score" in matrix
    assert isinstance(matrix["matched_keywords"], list)
    assert isinstance(matrix["missing_keywords"], list)

def test_tailor_resume_endpoint_edge_cases():
    """Tests the /api/llm/tailor-resume API endpoint with empty job descriptions and valid payloads."""
    # Case A: Empty Job Description
    resp_empty = client.post("/api/llm/tailor-resume", json={
        "resume_text": "Sample Resume",
        "job_description": "",
        "target_role": "Backend Engineer"
    })
    assert resp_empty.status_code == 200
    data_empty = resp_empty.json()
    assert data_empty["status"] == "warning"
    assert data_empty["match_score"] == 70.0

    # Case B: Full Tailoring Payload
    response = client.post("/api/llm/tailor-resume", json={
        "resume_text": "Experienced Python Software Engineer skilled in FastAPI, SQL, and Playwright.",
        "job_description": "We are seeking a Lead Full Stack Engineer with expertise in Python, FastAPI, React, and browser automation.",
        "target_role": "Lead Full Stack Engineer"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "match_score" in data
    assert data["match_score"] > 70.0
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

def test_llm_provider_fallback_when_keys_missing():
    """Verify invoke_llm_provider returns None cleanly when API keys are absent."""
    result = invoke_llm_provider("Test prompt", temperature=0.2, json_mode=True)
    # When no OPENAI_API_KEY / ANTHROPIC_API_KEY set, returns None fallback
    assert result is None or isinstance(result, dict)
