import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class NLPEvaluator:
    @staticmethod
    def evaluate_answer(
        answer_text: str,
        expected_concepts: List[str],
        ideal_summary: str = ""
    ) -> Dict[str, Any]:
        if not answer_text or not answer_text.strip():
            return {
                "technical_score": 0.0,
                "semantic_similarity": 0.0,
                "concept_coverage_pct": 0.0,
                "relevance_score": 0.0,
                "concepts_covered": [],
                "concepts_missing": expected_concepts,
                "feedback": "No answer was provided. Please explain the core concepts."
            }

        cleaned_answer = answer_text.lower()
        
        # 1. Concept Coverage Evaluation with stemming/lemmatization flexibility
        concepts_covered = []
        concepts_missing = []

        for concept in expected_concepts:
            concept_clean = concept.lower().strip()
            # Tokenize concept words
            words = concept_clean.split()
            # Check if full phrase or primary root words match
            phrase_matched = concept_clean in cleaned_answer
            roots_matched = all(
                (w in cleaned_answer or (w.rstrip('s') in cleaned_answer if len(w) > 4 else False) or (w.rstrip('ion') in cleaned_answer if w.endswith('ion') else False) or (w.rstrip('ing') in cleaned_answer if w.endswith('ing') else False))
                for w in words
            )
            if phrase_matched or roots_matched:
                concepts_covered.append(concept)
            else:
                concepts_missing.append(concept)

        total_concepts = len(expected_concepts)
        concept_coverage_pct = round((len(concepts_covered) / total_concepts * 100.0), 2) if total_concepts > 0 else 100.0

        # 2. Semantic Similarity using TF-IDF & Cosine Similarity
        benchmark_text = f"{ideal_summary} {' '.join(expected_concepts)}"
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([benchmark_text, answer_text])
            similarity = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            semantic_score = round(min(100.0, similarity * 150.0), 2)
        except Exception:
            semantic_score = 50.0

        # 3. Relevance & Completeness bounds
        word_count = len(answer_text.split())
        relevance_score = 100.0
        if word_count < 10:
            relevance_score = 40.0
        elif word_count < 20:
            relevance_score = 75.0

        # 4. Explainable Technical Score Formula
        # 50% Concept Coverage + 30% Semantic Similarity + 20% Relevance
        technical_score = round(
            (0.50 * concept_coverage_pct) +
            (0.30 * semantic_score) +
            (0.20 * relevance_score),
            2
        )

        # 5. Constructive Feedback
        feedback_parts = []
        if concepts_covered:
            feedback_parts.append(f"Well articulated key concepts: {', '.join(concepts_covered)}.")
        if concepts_missing:
            feedback_parts.append(f"Consider elaborating on: {', '.join(concepts_missing)}.")
        if word_count < 20:
            feedback_parts.append("Answer was somewhat brief. Providing practical examples strengthens technical explanation.")

        return {
            "technical_score": technical_score,
            "semantic_similarity": semantic_score,
            "concept_coverage_pct": concept_coverage_pct,
            "relevance_score": relevance_score,
            "concepts_covered": concepts_covered,
            "concepts_missing": concepts_missing,
            "feedback": " ".join(feedback_parts)
        }
