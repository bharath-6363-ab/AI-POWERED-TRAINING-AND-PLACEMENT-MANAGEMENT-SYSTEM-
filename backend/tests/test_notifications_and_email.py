import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_admin_overview_metrics():
    resp = client.post("/api/v1/auth/login", json={"email": "admin@college.edu", "password": "Admin@123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    resp_overview = client.get("/api/v1/analytics/admin/overview", headers=headers)
    assert resp_overview.status_code == 200
    data = resp_overview.json()
    assert data["total_students"] >= 2
    assert data["total_companies"] >= 30
    assert data["total_jobs"] >= 30

def test_student_performance_analytics():
    resp = client.post("/api/v1/auth/login", json={"email": "aditi.rao@student.edu", "password": "Student@123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    resp_perf = client.get("/api/v1/analytics/student/1", headers=headers)
    assert resp_perf.status_code == 200
    perf = resp_perf.json()
    assert "attendance_pct" in perf
    assert "overall_score" in perf
