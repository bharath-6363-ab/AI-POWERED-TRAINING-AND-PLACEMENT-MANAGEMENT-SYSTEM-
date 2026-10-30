import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_student_registration_success():
    """Registering a new student with valid data returns access_token and student role."""
    reg_payload = {
        "full_name": "Kavya Nair",
        "email": "kavya.nair@student.edu",
        "password": "Password@123",
        "role": "student",
        "roll_number": "1RV21CS099",
        "department": "Computer Science & Engineering",
        "cgpa": 8.75,
        "graduation_year": 2025,
        "college": "RV College of Engineering",
        "branch": "CSE",
        "semester": 8
    }
    resp = client.post("/api/v1/auth/register", json=reg_payload)
    # 200 on first run, or 400 if already exists
    if resp.status_code == 200:
        data = resp.json()
        assert data["role"] == "student"
        assert "access_token" in data
        assert data["email"] == "kavya.nair@student.edu"
    else:
        assert resp.status_code == 400
        detail = resp.json()["detail"].lower()
        assert "already exists" in detail or "already registered" in detail

def test_registration_safe_role_enforcement():
    """Public registration must NEVER allow creating an admin or trainer account."""
    admin_attempt = {
        "full_name": "Rogue Admin",
        "email": "rogue.admin@college.edu",
        "password": "Password@123",
        "role": "admin",  # Attacker attempts privilege escalation
        "roll_number": "1RV21CS100",
        "college": "RV College of Engineering",
        "branch": "CSE",
        "cgpa": 9.0,
        "semester": 8
    }
    resp = client.post("/api/v1/auth/register", json=admin_attempt)
    if resp.status_code == 200:
        data = resp.json()
        # MUST be forced to student role
        assert data["role"] == "student"
    else:
        assert resp.status_code == 400

def test_duplicate_email_rejected():
    """Duplicate email registration must return HTTP 400."""
    dup_payload = {
        "full_name": "Aditi Clone",
        "email": "ADITI.RAO@student.edu",  # uppercase variation of existing student
        "password": "Password@123",
        "role": "student",
        "roll_number": "1RV21CS999",
        "college": "RV College of Engineering",
        "branch": "CSE",
        "cgpa": 8.0,
        "semester": 8
    }
    resp = client.post("/api/v1/auth/register", json=dup_payload)
    assert resp.status_code == 400
    detail = resp.json()["detail"].lower()
    assert "already exists" in detail or "already registered" in detail

import time

def test_duplicate_roll_number_rejected():
    """Duplicate roll number registration must return HTTP 400."""
    dup_roll = {
        "full_name": "Unique Name",
        "email": f"unique_roll_test_{int(time.time() * 1000)}@student.edu",
        "password": "Password@123",
        "role": "student",
        "roll_number": "2026-CSE-001",  # Aditi Rao's seeded roll number
        "college": "RV College of Engineering",
        "branch": "CSE",
        "cgpa": 8.5,
        "semester": 8
    }
    resp = client.post("/api/v1/auth/register", json=dup_roll)
    assert resp.status_code == 400
    assert "roll number" in resp.json()["detail"].lower()

def test_weak_password_rejected():
    """Passwords shorter than 8 characters must be rejected."""
    weak_payload = {
        "full_name": "Weak User",
        "email": "weak.user@student.edu",
        "password": "short",  # only 5 chars
        "role": "student",
        "roll_number": "1RV21CS101",
        "college": "RV College of Engineering",
        "branch": "CSE",
        "cgpa": 7.5,
        "semester": 8
    }
    resp = client.post("/api/v1/auth/register", json=weak_payload)
    assert resp.status_code in [400, 422]

def test_registered_user_can_login():
    """Registered student can authenticate and receive JWT."""
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "kavya.nair@student.edu",
        "password": "Password@123"
    })
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["role"] == "student"
    assert "access_token" in data
    assert data["email"] == "kavya.nair@student.edu"

def test_invalid_password_rejected():
    """Invalid password returns HTTP 401."""
    resp = client.post("/api/v1/auth/login", json={
        "email": "kavya.nair@student.edu",
        "password": "WrongPassword!999"
    })
    assert resp.status_code in [400, 401]

def test_protected_endpoints_reject_unauthenticated():
    """Protected endpoints reject requests without valid Bearer token."""
    endpoints = [
        ("GET", "/api/v1/students/me/dashboard"),
        ("GET", "/api/v1/placement/my-applications"),
        ("GET", "/api/v1/interviews/history"),
        ("GET", "/api/v1/resume/my-resume"),
    ]
    for method, endpoint in endpoints:
        if method == "GET":
            r = client.get(endpoint)
        else:
            r = client.post(endpoint, json={})
        assert r.status_code == 401, f"{endpoint} did not return 401 for unauthenticated request"

def test_data_isolation_between_students():
    """Student A can only retrieve their own dashboard data and not Student B's."""
    # Login as Student A (Aditi Rao)
    login_a = client.post("/api/v1/auth/login", json={"email": "aditi.rao@student.edu", "password": "Student@123"})
    assert login_a.status_code == 200
    token_a = login_a.json()["access_token"]

    dash_a = client.get("/api/v1/students/me/dashboard", headers={"Authorization": f"Bearer {token_a}"})
    assert dash_a.status_code == 200
    data_a = dash_a.json()
    assert data_a["student"]["email"] == "aditi.rao@student.edu"
    assert data_a["student"]["full_name"] == "Aditi Rao"

    # Login as Student B (Kavya Nair)
    login_b = client.post("/api/v1/auth/login", json={"email": "kavya.nair@student.edu", "password": "Password@123"})
    assert login_b.status_code == 200
    token_b = login_b.json()["access_token"]

    dash_b = client.get("/api/v1/students/me/dashboard", headers={"Authorization": f"Bearer {token_b}"})
    assert dash_b.status_code == 200
    data_b = dash_b.json()
    assert data_b["student"]["email"] == "kavya.nair@student.edu"
    assert data_b["student"]["full_name"] == "Kavya Nair"

    # Ensure Student B cannot tamper with Student A's profile
    student_a_id = data_a["student"]["id"]
    tamper_attempt = client.put(
        f"/api/v1/students/{student_a_id}",
        json={"cgpa": 5.0, "full_name": "Hacked Name"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert tamper_attempt.status_code == 403
