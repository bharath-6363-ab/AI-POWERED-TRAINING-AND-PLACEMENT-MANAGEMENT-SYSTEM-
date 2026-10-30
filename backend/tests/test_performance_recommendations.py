import pytest
from backend.app.ai.recommendation.engine import TrainingRecommendationEngine

def test_recommendation_weak_technical():
    recs = TrainingRecommendationEngine.generate_recommendations(
        attendance_pct=90.0,
        aptitude_score=85.0,
        technical_test_score=55.0,  # Below 65%
        interview_score=80.0,
        coding_score=80.0,
        words_per_minute=120.0,
        filler_count=2
    )
    categories = [r["category"] for r in recs]
    assert "Technical MCQs & Architecture" in categories
    assert recs[0]["priority"] == 1

def test_recommendation_speech_fluency():
    recs = TrainingRecommendationEngine.generate_recommendations(
        attendance_pct=90.0,
        aptitude_score=85.0,
        technical_test_score=80.0,
        interview_score=80.0,
        coding_score=80.0,
        words_per_minute=70.0,  # Below 95 WPM
        filler_count=8         # > 6 fillers
    )
    categories = [r["category"] for r in recs]
    assert "Verbal Communication" in categories

def test_recommendation_attendance_deficit():
    recs = TrainingRecommendationEngine.generate_recommendations(
        attendance_pct=68.0,  # Below 75%
        aptitude_score=85.0,
        technical_test_score=80.0,
        interview_score=80.0,
        coding_score=80.0,
        words_per_minute=120.0,
        filler_count=2
    )
    categories = [r["category"] for r in recs]
    assert "Institutional Eligibility" in categories

def test_recommendation_high_performer():
    recs = TrainingRecommendationEngine.generate_recommendations(
        attendance_pct=95.0,
        aptitude_score=90.0,
        technical_test_score=90.0,
        interview_score=90.0,
        coding_score=90.0,
        words_per_minute=130.0,
        filler_count=1
    )
    assert len(recs) == 1
    assert recs[0]["title"] == "Advanced Mock Interview Polish"
