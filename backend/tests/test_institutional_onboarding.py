import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_courses():
    resp = client.get("/api/v1/academic/courses")
    assert resp.status_code == 200
    courses = resp.json()
    assert len(courses) >= 1
    assert "course_code" in courses[0]

def test_list_batches():
    resp = client.get("/api/v1/academic/batches")
    assert resp.status_code == 200
    batches = resp.json()
    assert len(batches) >= 1
    assert "trainer_id" in batches[0]

def test_student_profiles_listing():
    resp = client.post("/api/v1/auth/login", json={"email": "admin@college.edu", "password": "Admin@123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    st_resp = client.get("/api/v1/students/", headers=headers)
    assert st_resp.status_code == 200
    students = st_resp.json()
    assert len(students) >= 2
    assert any(s["roll_number"] == "2026-CSE-001" for s in students)
