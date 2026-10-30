import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_admin_rbac_access():
    resp = client.post("/api/v1/auth/login", json={"email": "admin@college.edu", "password": "Admin@123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "admin"
    assert "access_token" in data

def test_trainer_rbac_access():
    resp = client.post("/api/v1/auth/login", json={"email": "trainer@college.edu", "password": "Trainer@123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "trainer"

def test_student_rbac_access():
    resp = client.post("/api/v1/auth/login", json={"email": "aditi.rao@student.edu", "password": "Student@123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "student"

def test_invalid_credentials_rejected():
    resp = client.post("/api/v1/auth/login", json={"email": "nonexistent@college.edu", "password": "InvalidPassword"})
    assert resp.status_code in [400, 401]
