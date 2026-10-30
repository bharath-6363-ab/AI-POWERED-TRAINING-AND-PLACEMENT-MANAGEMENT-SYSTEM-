import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_student_pdf_dossier_download():
    resp = client.get("/api/v1/reports/student/1/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    content = resp.content
    assert content.startswith(b"%PDF")
    assert len(content) > 1000
