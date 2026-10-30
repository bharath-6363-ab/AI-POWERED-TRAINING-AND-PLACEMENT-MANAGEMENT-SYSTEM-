import pytest
from backend.app.ai.nlp.evaluator import NLPEvaluator

def test_nlp_evaluator_high_score():
    answer = "Python uses reference counting as its primary memory management mechanism and a generational garbage collector to handle reference cycles."
    expected = ["reference counting", "garbage collection", "cyclic references"]
    result = NLPEvaluator.evaluate_answer(
        answer_text=answer,
        expected_concepts=expected,
        ideal_summary="Python uses reference counting and garbage collection."
    )
    assert result["technical_score"] >= 65.0
    assert result["concept_coverage_pct"] >= 60.0
    assert "reference counting" in result["concepts_covered"]
    assert "feedback" in result

def test_nlp_evaluator_empty_answer():
    result = NLPEvaluator.evaluate_answer(
        answer_text="",
        expected_concepts=["polymorphism", "inheritance"]
    )
    assert result["technical_score"] == 0.0
    assert result["concept_coverage_pct"] == 0.0
    assert len(result["concepts_missing"]) == 2
    assert "No answer was provided" in result["feedback"]

def test_nlp_evaluator_partial_coverage():
    answer = "Polymorphism allows objects to take multiple forms."
    expected = ["polymorphism", "encapsulation", "inheritance"]
    result = NLPEvaluator.evaluate_answer(
        answer_text=answer,
        expected_concepts=expected
    )
    assert "polymorphism" in result["concepts_covered"]
    assert "encapsulation" in result["concepts_missing"]
    assert len(result["concepts_covered"]) == 1
