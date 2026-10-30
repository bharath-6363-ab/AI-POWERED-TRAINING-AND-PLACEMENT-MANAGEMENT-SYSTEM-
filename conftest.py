import pytest
import os
import sys
from fastapi.testclient import TestClient

# Ensure root workspace is on python sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.main import app
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.all_models import User, Student

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="session")
def demo_student_credentials():
    return {
        "email": "aditi.rao@student.edu",
        "password": "Student@123"
    }

@pytest.fixture(scope="session")
def demo_admin_credentials():
    return {
        "email": "admin@college.edu",
        "password": "Admin@123"
    }

@pytest.fixture(scope="session")
def sample_resume_text():
    return """
    Aditi Rao
    Email: aditi.rao@student.edu | Phone: +91-9876543210 | Bengaluru, India
    
    Professional Summary:
    Full Stack Software Engineer with deep expertise in Python, FastAPI, React, SQL, and Docker containerization.
    
    Technical Skills:
    - Programming Languages: Python, C++, Java, JavaScript, TypeScript, SQL
    - Frameworks & Libraries: FastAPI, Django, React.js, TailwindCSS, PyTorch
    - Tools & DevOps: Docker, Kubernetes, Git, GitHub Actions, Linux, Redis
    - Core CS: Data Structures, Algorithms, Object-Oriented Design, DBMS, Computer Networks
    
    Projects:
    1. AI-Powered Training & Placement Management System (FastAPI, React, SQLite, YOLOv8)
       - Implemented 3-round sequential placement drive pipeline with automated eligibility gating.
       - Built real-time vision proctoring with YOLOv8 device detection and 3D head pose estimation.
    """
