import os
import pytest
from io import BytesIO
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import settings

client = TestClient(app)

def test_invalid_token_job_application_returns_401():
    """Tampered or invalid Bearer token must receive HTTP 401 Unauthorized."""
    resp = client.post(
        "/api/v1/placement/jobs/1/apply",
        headers={"Authorization": "Bearer invalid_tampered_token_xyz"}
    )
    assert resp.status_code == 401
    assert "Invalid or expired" in resp.json()["detail"]

def test_malformed_auth_header_returns_401():
    """Malformed non-Bearer authorization header must receive HTTP 401 Unauthorized."""
    resp = client.post(
        "/api/v1/placement/jobs/1/apply",
        headers={"Authorization": "Basic YWRtaW46cGFzc3dvcmQ="}
    )
    assert resp.status_code == 401
    assert "Invalid authorization header format" in resp.json()["detail"]

def test_non_student_job_application_returns_403():
    """Trainers or admins applying for student jobs must receive HTTP 403 Forbidden."""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "trainer@college.edu", "password": "Trainer@123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    resp = client.post(
        "/api/v1/placement/jobs/1/apply",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403
    assert "Only students can apply" in resp.json()["detail"]

def test_student_job_application_success():
    """Authenticated student can apply and receives structured response."""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "aditi.rao@student.edu", "password": "Student@123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    resp = client.post(
        "/api/v1/placement/jobs/1/apply",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "application_id" in data
    assert "status" in data

def test_invalid_token_test_submission_returns_401():
    """Invalid token on test submission must receive HTTP 401 Unauthorized."""
    payload = {
        "answers": [{"question_id": 1, "selected_option": "A"}]
    }
    resp = client.post(
        "/api/v1/tests/1/submit",
        json=payload,
        headers={"Authorization": "Bearer forged_test_token"}
    )
    assert resp.status_code == 401
    assert "Invalid or expired" in resp.json()["detail"]

def test_unauthenticated_request_rejected_401():
    """Unauthenticated request to protected endpoint must be rejected with HTTP 401."""
    resp = client.get("/api/v1/placement/my-applications")
    assert resp.status_code == 401
    assert "detail" in resp.json()

def test_resume_upload_filename_sanitization():
    """Uploaded filename with directory traversal must be sanitized to prevent saving outside uploads/resumes."""
    traversal_filename = "../../../etc/passwd.txt"
    file_content = b"Python developer with FastAPI, SQL, Docker, and Git experience."
    
    files = {
        "file": (traversal_filename, BytesIO(file_content), "text/plain")
    }
    resp = client.post("/api/v1/resume/upload-file", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    
    # Verify the saved file is strictly in the resumes folder and does not escape
    expected_safe_path = os.path.join(settings.UPLOAD_DIR, "resumes", "temp_passwd.txt")
    assert os.path.exists(expected_safe_path)
    
    # Clean up test file
    if os.path.exists(expected_safe_path):
        os.remove(expected_safe_path)

def test_interview_evaluate_direct_authenticated_student():
    """Direct interview evaluation binds to active student session."""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "aditi.rao@student.edu", "password": "Student@123"}
    )
    token = login_resp.json()["access_token"]
    
    eval_payload = {
        "question_id": 1,
        "answer_text": "Python uses reference counting and generational garbage collection to free cyclical references.",
        "duration_seconds": 12.0
    }
    resp = client.post(
        "/api/v1/interviews/evaluate-direct",
        json=eval_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "nlp_evaluation" in data
    assert "speech_analysis" in data
    assert data["nlp_evaluation"]["technical_score"] > 50.0
