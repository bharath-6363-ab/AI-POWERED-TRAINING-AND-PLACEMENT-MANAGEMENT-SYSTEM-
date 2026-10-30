import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_full_student_journey_simulation():
    # 1. Login as Student
    login_resp = client.post("/api/v1/auth/login", json={"email": "aditi.rao@student.edu", "password": "Student@123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check profile
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "aditi.rao@student.edu"

    # 3. Check Placement Jobs
    jobs_resp = client.get("/api/v1/placement/jobs", headers=headers)
    assert jobs_resp.status_code == 200
    jobs = jobs_resp.json()
    assert len(jobs) > 0
    job_id = jobs[0]["id"]

    # 4. Check Placement Eligibility
    elig_resp = client.get(f"/api/v1/placement/jobs/{job_id}/check-eligibility/1", headers=headers)
    assert elig_resp.status_code == 200

    # 5. Check Sequential Rounds Pipeline
    wf_resp = client.get("/api/v1/placement/rounds/workflow", headers=headers)
    assert wf_resp.status_code == 200
    assert "rounds" in wf_resp.json()

    # 6. AI Mock Interview Direct Evaluation
    eval_resp = client.post("/api/v1/interviews/evaluate-direct", json={
        "question_id": 1,
        "answer_text": "Python handles memory via reference counting and generational garbage collection.",
        "duration_seconds": 15.0
    }, headers=headers)
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["status"] == "success"
    assert "nlp_evaluation" in eval_data
    assert "speech_analysis" in eval_data
