import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_sample_questions_endpoint():
    resp = client.get("/api/v1/interviews/questions/sample?topic=Python&count=3")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["questions"]) == 3
    for q in data["questions"]:
        assert "question_text" in q
        assert "expected_concepts" in q

def test_questions_from_resume_endpoint():
    resp = client.post("/api/v1/interviews/questions/from-resume", json={
        "skills": ["Python", "FastAPI", "SQL"],
        "job_title": "Backend Developer",
        "count": 3
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["questions"]) == 3
