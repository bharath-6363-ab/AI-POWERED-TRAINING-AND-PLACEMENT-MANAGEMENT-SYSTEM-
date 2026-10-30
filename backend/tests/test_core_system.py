import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_system_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "online"
    assert "AI-Powered" in data["system"]

def test_admin_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@college.edu", "password": "Admin@123"}
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["role"] == "admin"

def test_student_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "aditi.rao@student.edu", "password": "Student@123"}
    )
    assert response.status_code == 200
    token_data = response.json()
    assert token_data["role"] == "student"

def test_login_failure():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@college.edu", "password": "WrongPassword"}
    )
    assert response.status_code == 401

def test_companies_list():
    response = client.get("/api/v1/placement/companies")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) >= 2
    names = [c["name"] for c in companies]
    assert "Cognitive Cloud Tech" in names

def test_jobs_list():
    response = client.get("/api/v1/placement/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) >= 2
    assert jobs[0]["requirements"]["min_cgpa"] >= 6.0

def test_eligibility_engine():
    # Login as student Aditi (CGPA 8.75, high attendance, Python/SQL skills)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "aditi.rao@student.edu", "password": "Student@123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Check eligibility for Job 1 (Cognitive Cloud Tech, requires 7.5 CGPA, Python, SQL)
    check_resp = client.get(
        "/api/v1/placement/jobs/1/check-eligibility/1",
        headers=headers
    )
    assert check_resp.status_code == 200
    result = check_resp.json()
    assert result["is_eligible"] is True
    assert result["student_cgpa"] == 8.75

def test_nlp_answer_evaluator():
    from backend.app.ai.nlp.evaluator import NLPEvaluator

    answer = "Python manages memory automatically using reference counting for active objects and a generational garbage collector to identify and clear cyclic references."
    expected = ["reference counting", "garbage collection", "cyclic references"]

    eval_result = NLPEvaluator.evaluate_answer(
        answer_text=answer,
        expected_concepts=expected,
        ideal_summary="Python uses reference counting and garbage collection."
    )
    assert eval_result["technical_score"] >= 75.0
    assert "reference counting" in eval_result["concepts_covered"]
    assert len(eval_result["concepts_missing"]) == 0

def test_speech_fluency_analyzer():
    from backend.app.ai.speech.fluency_analyzer import SpeechFluencyAnalyzer

    text = "In my project I used FastAPI because it is basically asynchronous and um very fast with Pydantic validation."
    result = SpeechFluencyAnalyzer.analyze_speech(transcribed_text=text, duration_seconds=10.0)
    assert result["words_per_minute"] > 80.0
    assert result["filler_word_count"] >= 2
    assert "um" in result["filler_words_detected"]
