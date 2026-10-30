import pytest
from backend.app.ai.speech.fluency_analyzer import SpeechFluencyAnalyzer

def test_speech_fluency_wpm_calculation():
    text = "Machine learning models require robust preprocessing pipelines and cross validation."
    result = SpeechFluencyAnalyzer.analyze_speech(transcribed_text=text, duration_seconds=6.0)
    # 10 words in 6 seconds = 100 WPM
    assert result["words_per_minute"] == pytest.approx(100.0, rel=1e-1)
    assert result["word_count"] == 10

def test_speech_fluency_filler_words():
    text = "Um I basically implemented the backend with uh FastAPI and like PostgreSQL."
    result = SpeechFluencyAnalyzer.analyze_speech(transcribed_text=text, duration_seconds=8.0)
    assert result["filler_word_count"] >= 3
    assert "um" in result["filler_words_detected"]
    assert "basically" in result["filler_words_detected"]

def test_speech_fluency_empty_input():
    result = SpeechFluencyAnalyzer.analyze_speech(transcribed_text="", duration_seconds=0.0)
    assert result["words_per_minute"] == 0.0
    assert result["word_count"] == 0
    assert result["filler_word_count"] == 0
