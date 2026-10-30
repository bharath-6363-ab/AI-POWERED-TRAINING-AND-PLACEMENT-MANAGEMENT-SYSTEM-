import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_all_30_companies_present():
    resp = client.get("/api/v1/placement/companies")
    assert resp.status_code == 200
    companies = resp.json()
    assert len(companies) >= 30

def test_job_drives_present():
    resp = client.get("/api/v1/placement/jobs")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) >= 30
    assert all("salary_lpa" in j for j in jobs)

def test_eligibility_criteria_evaluation():
    # Login as student Aditi (CGPA 8.75)
    login_resp = client.post("/api/v1/auth/login", json={"email": "aditi.rao@student.edu", "password": "Student@123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = client.get("/api/v1/placement/jobs/1/check-eligibility/1", headers=headers)
    assert resp.status_code == 200
    elig = resp.json()
    assert elig["is_eligible"] is True
    assert elig["student_cgpa"] >= elig["required_cgpa"]

def test_sequential_rounds_workflow():
    login_resp = client.post("/api/v1/auth/login", json={"email": "aditi.rao@student.edu", "password": "Student@123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = client.get("/api/v1/placement/rounds/workflow", headers=headers)
    assert resp.status_code == 200
    wf = resp.json()
    assert "current_active_round" in wf
    assert len(wf["rounds"]) == 3
