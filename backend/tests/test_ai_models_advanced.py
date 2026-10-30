import pytest
from backend.app.ai.nlp.question_generator import QuestionGenerator

def test_question_generator_from_resume_skills():
    skills = ["Python", "Docker", "SQL", "FastAPI"]
    questions = QuestionGenerator.generate_interview_questions(
        job_title="Backend Engineer",
        resume_skills=skills,
        count=4
    )
    assert len(questions) == 4
    for q in questions:
        assert "question_text" in q
        assert "expected_concepts" in q
        assert "ideal_summary" in q
        assert len(q["expected_concepts"]) > 0

def test_question_generator_fallback_general():
    # If no matching skills, returns general software questions
    questions = QuestionGenerator.generate_interview_questions(
        job_title="Unknown Role",
        resume_skills=[],
        count=3
    )
    assert len(questions) == 3
    assert all("question_text" in q for q in questions)
