import pytest
from backend.app.ai.nlp.question_generator import QuestionGenerator, FALLBACK_QUESTION_BANK

def test_offline_question_bank_resilience():
    # Tests that when offline (zero external API calls), the question generator reliably produces rich questions
    assert len(FALLBACK_QUESTION_BANK) >= 20
    topics = set(q["topic"] for q in FALLBACK_QUESTION_BANK)
    assert "Python" in topics
    assert "FastAPI" in topics
    assert "SQL & Databases" in topics

def test_question_generator_topic_coverage():
    questions = QuestionGenerator.generate_interview_questions(
        job_title="Data Scientist",
        resume_skills=["Python", "Machine Learning", "SQL"],
        count=3
    )
    assert len(questions) == 3
    assert all(len(q["expected_concepts"]) >= 2 for q in questions)
