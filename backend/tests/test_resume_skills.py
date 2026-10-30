import pytest
from backend.app.ai.resume.parser import ResumeParser

def test_resume_parser_symbol_skills():
    raw_text = "Proficient in C++, C#, Python, SQL, Docker, Kubernetes and FastAPI microservices."
    parsed = ResumeParser.parse_resume(raw_text)
    
    skill_names = [s["name"] for s in parsed["skills"]]
    assert "C++" in skill_names
    assert "C#" in skill_names
    assert "Python" in skill_names
    assert "Docker" in skill_names
    assert "Fastapi" in skill_names or "FastAPI" in skill_names

def test_resume_parser_categorization():
    raw_text = "Experienced in Python, React, MySQL, AWS, Git, and REST API development."
    parsed = ResumeParser.parse_resume(raw_text)
    categorized = parsed["categorized"]
    
    assert "Programming Languages" in categorized
    assert "Frameworks & Libraries" in categorized
    assert "Databases & Cloud" in categorized
    assert len(parsed["skills"]) >= 5

def test_resume_parser_boundary_avoidance():
    # 'c' shouldn't falsely trigger for words like 'cloud' or 'clear'
    raw_text = "Cloud architecture and clear documentation."
    parsed = ResumeParser.parse_resume(raw_text)
    skill_names = [s["name"] for s in parsed["skills"]]
    assert "C" not in skill_names

def test_comprehensive_ats_audit():
    from backend.app.ai.resume.skill_gap_analyzer import ResumeSkillGapAnalyzer
    sample_resume = """
    Aditi Rao
    aditi.rao@student.edu | +91 98765 43210
    linkedin.com/in/aditi-rao | github.com/aditi-rao

    EDUCATION:
    B.Tech Computer Science | CGPA: 8.75
    National Institute of Technology

    TECHNICAL SKILLS:
    Python, FastAPI, React, SQL, Docker, Linux, Git

    PROJECTS:
    AI Campus Recruitment Platform
    Engineered asynchronous FastAPI microservices, reducing candidate evaluation latency by 35%.
    Architected automated ATS resume parsing engine with 92% taxonomy keyword coverage.
    Deployed Dockerized container clusters scaling to 5,000 active requests.

    EXPERIENCE:
    Software Engineering Intern
    Developed automated test suites increasing branch coverage to 88%.
    """
    res = ResumeSkillGapAnalyzer.comprehensive_ats_audit(sample_resume)
    assert res["total_ats_score"] >= 80
    assert res["grade"] in ["A+", "A"]
    assert res["pillars"]["contact"]["email"] == "aditi.rao@student.edu"
    assert res["pillars"]["sections"]["has_skills"] is True
    assert res["pillars"]["sections"]["has_projects"] is True
    assert len(res["pillars"]["action_impact"]["action_verbs_detected"]) >= 3
    assert len(res["strengths"]) > 0

def test_ats_audit_api_endpoint():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    resp = client.post(
        "/api/v1/resume/audit",
        json={"resume_text": "John Doe\njohn@example.com | 1234567890\nSkills: Python, SQL\nEngineered backend services reducing latency by 25%."}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "audit" in data
    assert "total_ats_score" in data["audit"]
    assert "grade" in data["audit"]

