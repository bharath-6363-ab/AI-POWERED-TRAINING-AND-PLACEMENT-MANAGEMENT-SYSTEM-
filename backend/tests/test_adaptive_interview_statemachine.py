import pytest
import os
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.all_models import (
    Interview, InterviewQuestion, InterviewAnswer, SpeechAnalysis, Student, PerformanceMetric
)
from backend.app.ai.interview.state_machine import AdaptiveInterviewStateMachine, InterviewState

client = TestClient(app)

@pytest.fixture
def student_aditi_token():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "aditi.rao@student.edu", "password": "Student@123"}
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]

@pytest.fixture
def student_rohan_token():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "rohan.mehta@student.edu", "password": "Student@123"}
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


def test_start_adaptive_session_success(student_aditi_token):
    """Verifies that an adaptive interview session starts properly with database persistence."""
    headers = {"Authorization": f"Bearer {student_aditi_token}"}
    payload = {
        "job_role": "Python Backend Engineer",
        "skills": ["Python", "FastAPI", "SQL"],
        "question_count": 2
    }
    resp = client.post("/api/v1/interviews/session/start", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    session = data["session"]
    assert "session_id" in session
    assert session["state"] == InterviewState.QUESTION_ACTIVE.value
    assert session["current_question_number"] == 1
    assert session["total_questions"] == 2
    assert "question_text" in session["question"]
    assert session["is_follow_up"] is False
    assert session.get("db_interview_id") is not None

    # Verify Interview record created in SQLite DB
    db = SessionLocal()
    try:
        db_interview = db.query(Interview).filter(Interview.id == session["db_interview_id"]).first()
        assert db_interview is not None
        assert db_interview.status == "in_progress"
    finally:
        db.close()


def test_submit_turn_triggers_adaptive_follow_up_on_weak_answer(student_aditi_token):
    """When a candidate gives a weak or incomplete answer, the state machine triggers follow-up probing."""
    headers = {"Authorization": f"Bearer {student_aditi_token}"}
    start_resp = client.post(
        "/api/v1/interviews/session/start",
        json={"job_role": "Python Backend Engineer", "skills": ["Python"], "question_count": 2},
        headers=headers
    )
    session_id = start_resp.json()["session"]["session_id"]

    # Candidate provides an intentionally deficient, vague answer
    weak_answer = "I write simple code and use basic variables."
    turn_resp = client.post(
        "/api/v1/interviews/session/turn",
        json={"session_id": session_id, "answer_text": weak_answer, "duration_seconds": 15.0},
        headers=headers
    )
    assert turn_resp.status_code == 200
    turn_data = turn_resp.json()["data"]
    
    # State should shift to FOLLOW_UP_PROBING
    assert turn_data["state"] == InterviewState.FOLLOW_UP_PROBING.value
    assert turn_data["is_follow_up"] is True
    assert "Probing deficit in" in turn_data["follow_up_reason"]
    assert "next_question" in turn_data
    assert turn_data["next_question"]["is_adaptive"] is True

    # Check 4-part transparent rubric
    eval_info = turn_data["turn_evaluation"]
    assert "rubric" in eval_info
    rubric = eval_info["rubric"]
    assert "correctness_score" in rubric
    assert "depth_score" in rubric
    assert "relevance_score" in rubric
    assert "clarity_rating" in rubric
    assert rubric["scoring_engine"] == "deterministic_rule_based_rubric"
    assert eval_info["weakest_concept"] is not None


def test_follow_up_advances_to_next_primary_question(student_aditi_token):
    """Submitting the follow-up answer must strictly advance to the next primary question (no infinite loop)."""
    headers = {"Authorization": f"Bearer {student_aditi_token}"}
    start_resp = client.post(
        "/api/v1/interviews/session/start",
        json={"job_role": "Python Backend Engineer", "skills": ["Python"], "question_count": 2},
        headers=headers
    )
    session_id = start_resp.json()["session"]["session_id"]

    # Turn 1: Weak answer -> triggers follow-up
    client.post(
        "/api/v1/interviews/session/turn",
        json={"session_id": session_id, "answer_text": "I write code.", "duration_seconds": 12.0},
        headers=headers
    )

    # Turn 1.1: Answer the follow-up probing question
    follow_up_answer = "To handle cyclic references, generational garbage collection periodically runs mark-and-sweep."
    turn_resp2 = client.post(
        "/api/v1/interviews/session/turn",
        json={"session_id": session_id, "answer_text": follow_up_answer, "duration_seconds": 20.0},
        headers=headers
    )
    assert turn_resp2.status_code == 200
    data2 = turn_resp2.json()["data"]

    # Must transition back to primary question 2 (no second follow-up)
    assert data2["is_follow_up"] is False
    assert data2["state"] == InterviewState.QUESTION_ACTIVE.value
    assert data2["current_question_number"] == 2


def test_avoid_repeated_questions_across_session(student_aditi_token):
    """Verifies that questions asked during an interview are tracked and never repeated."""
    headers = {"Authorization": f"Bearer {student_aditi_token}"}
    start_resp = client.post(
        "/api/v1/interviews/session/start",
        json={"job_role": "Full-Stack Engineer", "skills": ["Python", "FastAPI"], "question_count": 2},
        headers=headers
    )
    session_id = start_resp.json()["session"]["session_id"]
    q1 = start_resp.json()["session"]["question"]["question_text"]

    turn_resp = client.post(
        "/api/v1/interviews/session/turn",
        json={"session_id": session_id, "answer_text": "Partial explanation of APIs.", "duration_seconds": 15.0},
        headers=headers
    )
    q_follow_up = turn_resp.json()["data"]["next_question"]["question_text"]
    assert q1 != q_follow_up

    # Session tracking check
    session = AdaptiveInterviewStateMachine.get_session(session_id)
    assert q1 in session["asked_question_texts"]
    assert q_follow_up in session["asked_question_texts"]


def test_gemini_fallback_resilience(monkeypatch, student_aditi_token):
    """When GEMINI_API_KEY is unset or fails, heuristic fallback probing engine succeeds seamlessly."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from backend.app.core.config import settings
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    headers = {"Authorization": f"Bearer {student_aditi_token}"}
    start_resp = client.post(
        "/api/v1/interviews/session/start",
        json={"job_role": "Backend Engineer", "skills": ["SQL"], "question_count": 2},
        headers=headers
    )
    session_id = start_resp.json()["session"]["session_id"]

    turn_resp = client.post(
        "/api/v1/interviews/session/turn",
        json={"session_id": session_id, "answer_text": "I use queries.", "duration_seconds": 10.0},
        headers=headers
    )
    assert turn_resp.status_code == 200
    next_q = turn_resp.json()["data"]["next_question"]
    assert next_q["engine"] == "heuristic_probing_engine"
    assert next_q["is_adaptive"] is True
    assert "handle" in next_q["question_text"] or "elaborate" in next_q["question_text"] or "patterns" in next_q["question_text"]


def test_database_persistence_of_interview_turns(student_aditi_token):
    """Checks that every question and answer turn is persisted into SQLite tables."""
    headers = {"Authorization": f"Bearer {student_aditi_token}"}
    start_resp = client.post(
        "/api/v1/interviews/session/start",
        json={"job_role": "Cloud Engineer", "skills": ["Docker"], "question_count": 1},
        headers=headers
    )
    session_id = start_resp.json()["session"]["session_id"]
    db_interview_id = start_resp.json()["session"]["db_interview_id"]

    # Submit answer
    client.post(
        "/api/v1/interviews/session/turn",
        json={
            "session_id": session_id,
            "answer_text": "Docker images are built with layers and multi-stage builds optimize production size.",
            "duration_seconds": 18.0
        },
        headers=headers
    )

    db = SessionLocal()
    try:
        # Check questions persisted
        questions = db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == db_interview_id).all()
        assert len(questions) >= 1
        q_id = questions[0].id

        # Check answers persisted
        answer = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q_id).first()
        assert answer is not None
        assert "Docker images" in answer.transcribed_text
        assert answer.technical_score > 0.0

        # Check speech analysis persisted
        speech = db.query(SpeechAnalysis).filter(SpeechAnalysis.answer_id == answer.id).first()
        assert speech is not None
        assert speech.words_per_minute > 0.0
    finally:
        db.close()


def test_prevent_unauthorized_access_to_session(student_aditi_token, student_rohan_token):
    """A student must NOT be able to view, submit turns to, or conclude another student's interview session."""
    aditi_headers = {"Authorization": f"Bearer {student_aditi_token}"}
    rohan_headers = {"Authorization": f"Bearer {student_rohan_token}"}

    # Aditi starts an interview
    start_resp = client.post(
        "/api/v1/interviews/session/start",
        json={"job_role": "Python Engineer", "skills": ["Python"], "question_count": 2},
        headers=aditi_headers
    )
    aditi_session_id = start_resp.json()["session"]["session_id"]

    # Rohan attempts to hijack Aditi's session by submitting a turn
    turn_resp = client.post(
        "/api/v1/interviews/session/turn",
        json={"session_id": aditi_session_id, "answer_text": "Rohan answering Aditi session"},
        headers=rohan_headers
    )
    assert turn_resp.status_code == 403
    assert "Access denied" in turn_resp.json()["detail"]

    # Rohan attempts to view Aditi's session status
    status_resp = client.get(f"/api/v1/interviews/session/{aditi_session_id}/status", headers=rohan_headers)
    assert status_resp.status_code == 403

    # Rohan attempts to conclude Aditi's session
    conclude_resp = client.post(f"/api/v1/interviews/session/{aditi_session_id}/conclude", headers=rohan_headers)
    assert conclude_resp.status_code == 403


def test_conclude_session_scorecard_and_recommendations(student_aditi_token):
    """Concludes session and asserts strengths, weak areas, practice topics, and performance metric update."""
    headers = {"Authorization": f"Bearer {student_aditi_token}"}
    start_resp = client.post(
        "/api/v1/interviews/session/start",
        json={"job_role": "Python Backend Engineer", "skills": ["Python"], "question_count": 1},
        headers=headers
    )
    session_data = start_resp.json()["session"]
    session_id = session_data["session_id"]
    db_interview_id = session_data["db_interview_id"]
    expected_concepts = session_data["question"].get("expected_concepts", ["reference counting", "garbage collection"])
    comprehensive_answer = f"In technical engineering, we address {' and '.join(expected_concepts)} to ensure optimal memory safety, execution speed, and architectural reliability."

    # Submit comprehensive answer
    client.post(
        "/api/v1/interviews/session/turn",
        json={
            "session_id": session_id,
            "answer_text": comprehensive_answer,
            "duration_seconds": 22.0
        },
        headers=headers
    )

    conclude_resp = client.post(f"/api/v1/interviews/session/{session_id}/conclude", headers=headers)
    assert conclude_resp.status_code == 200
    data = conclude_resp.json()["data"]
    assert data["state"] == InterviewState.COMPLETED.value
    assert data["is_completed"] is True
    summary = data["summary"]
    assert summary["overall_score"] > 50.0
    assert summary["verdict"] in ["PASSED", "TRAINING_REQUIRED"]
    assert "strengths" in summary
    assert "weak_areas" in summary
    assert "recommendations" in summary
    assert len(summary["recommendations"]) > 0

    # Verify SQLite Interview and Student Performance update
    db = SessionLocal()
    try:
        db_interview = db.query(Interview).filter(Interview.id == db_interview_id).first()
        assert db_interview.status == "completed"
        assert db_interview.overall_score > 0.0

        student = db.query(Student).filter(Student.id == 1).first()
        if student and student.performance:
            assert student.performance.interview_avg_score > 0.0
    finally:
        db.close()


def test_preserve_existing_direct_evaluation(student_aditi_token):
    """Verifies that the original direct evaluation route continues to operate without regression."""
    headers = {"Authorization": f"Bearer {student_aditi_token}"}
    payload = {
        "question_id": 1,
        "answer_text": "Python uses reference counting and generational garbage collection.",
        "duration_seconds": 15.0
    }
    resp = client.post("/api/v1/interviews/evaluate-direct", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "nlp_evaluation" in data
    assert "speech_analysis" in data
    assert data["nlp_evaluation"]["technical_score"] > 60.0
