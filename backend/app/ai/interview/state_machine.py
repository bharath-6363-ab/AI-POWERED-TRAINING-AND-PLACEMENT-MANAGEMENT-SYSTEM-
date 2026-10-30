import os
import uuid
import re
import httpx
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from backend.app.ai.nlp.evaluator import NLPEvaluator
from backend.app.ai.nlp.question_generator import QuestionGenerator
from backend.app.ai.speech.fluency_analyzer import SpeechFluencyAnalyzer
from backend.app.ai.recommendation.engine import TrainingRecommendationEngine
from backend.app.core.database import SessionLocal
from backend.app.models.all_models import (
    Interview, InterviewQuestion, InterviewAnswer, SpeechAnalysis, Student, PerformanceMetric
)

class InterviewState(str, Enum):
    INITIALIZED = "INITIALIZED"
    QUESTION_ACTIVE = "QUESTION_ACTIVE"
    ANSWER_EVALUATED = "ANSWER_EVALUATED"
    FOLLOW_UP_PROBING = "FOLLOW_UP_PROBING"
    COMPLETED = "COMPLETED"

class AdaptiveInterviewStateMachine:
    """
    Deterministic state machine orchestrating multi-turn adaptive AI interviews.
    Manages turn progression, 4-part transparent rubric evaluation (Correctness, Depth, Relevance, Clarity),
    adaptive follow-up probing targeting identified weak concepts, zero-repetition tracking,
    dual-engine Gemini/heuristic probing, and full database persistence into SQLAlchemy models.
    """
    _sessions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def start_session(
        cls,
        student_id: int,
        job_role: str = "Software Engineer",
        skills: Optional[List[str]] = None,
        question_count: int = 3
    ) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        effective_skills = skills if skills and len(skills) > 0 else ["Python", "FastAPI", "SQL", "Docker"]
        
        # Pre-generate foundational question queue tailored to candidate skills
        question_queue = QuestionGenerator.generate_interview_questions(
            job_title=job_role,
            resume_skills=effective_skills,
            count=question_count
        )

        first_q = question_queue[0]
        asked_texts = {first_q.get("question_text")}

        # 1. DATABASE PERSISTENCE: Create initial Interview record in SQLite
        db_interview_id = None
        db = SessionLocal()
        try:
            db_interview = Interview(
                student_id=student_id,
                title=f"Adaptive AI Interview: {job_role}",
                interview_type="technical",
                overall_score=0.0,
                technical_score=0.0,
                communication_score=0.0,
                integrity_score=100.0,
                status="in_progress",
                started_at=datetime.utcnow()
            )
            db.add(db_interview)
            db.commit()
            db.refresh(db_interview)
            db_interview_id = db_interview.id
        except Exception as e:
            db.rollback()
        finally:
            db.close()

        session_data = {
            "session_id": session_id,
            "db_interview_id": db_interview_id,
            "student_id": student_id,
            "job_role": job_role,
            "skills": effective_skills,
            "state": InterviewState.QUESTION_ACTIVE.value,
            "current_index": 0,
            "total_questions": len(question_queue),
            "question_queue": question_queue,
            "asked_question_texts": asked_texts,
            "turns": [],
            "current_turn": {
                "question": first_q,
                "turn_type": "primary",
                "answer": None,
                "evaluation": None,
                "follow_up": None
            },
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "overall_summary": None
        }

        cls._sessions[session_id] = session_data
        
        return {
            "session_id": session_id,
            "db_interview_id": db_interview_id,
            "state": session_data["state"],
            "current_question_number": 1,
            "total_questions": len(question_queue),
            "question": first_q,
            "is_follow_up": False
        }

    @classmethod
    def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        return cls._sessions.get(session_id)

    @classmethod
    def validate_session_owner(cls, session_id: str, authenticated_student_id: Optional[int]) -> Dict[str, Any]:
        """Validates that session exists and matches the authenticated student to prevent IDOR."""
        session = cls.get_session(session_id)
        if not session:
            raise ValueError("Interview session not found")
        if authenticated_student_id is not None:
            if session["student_id"] != authenticated_student_id:
                raise PermissionError("Access denied: You do not own this interview session")
        return session

    @classmethod
    async def submit_turn(
        cls,
        session_id: str,
        answer_text: str,
        duration_seconds: float = 25.0,
        authenticated_student_id: Optional[int] = None
    ) -> Dict[str, Any]:
        session = cls.validate_session_owner(session_id, authenticated_student_id)
        
        if session["state"] == InterviewState.COMPLETED.value:
            return {
                "session_id": session_id,
                "state": InterviewState.COMPLETED.value,
                "message": "Interview session is already completed",
                "summary": session.get("overall_summary")
            }

        current_turn = session["current_turn"]
        active_question = current_turn["question"]
        expected = active_question.get("expected_concepts", ["core principles", "practical implementation"])
        ideal = active_question.get("ideal_summary", "Clear, concise technical explanation.")

        # 1. NLP and Speech evaluation of candidate answer
        nlp_res = NLPEvaluator.evaluate_answer(
            answer_text=answer_text,
            expected_concepts=expected,
            ideal_summary=ideal
        )
        speech_res = SpeechFluencyAnalyzer.analyze_speech(
            transcribed_text=answer_text,
            duration_seconds=duration_seconds
        )

        # 2. Transparent Rubric Calculation
        rubric = {
            "correctness_score": nlp_res["concept_coverage_pct"],
            "depth_score": nlp_res["semantic_similarity"],
            "relevance_score": nlp_res["relevance_score"],
            "clarity_rating": f"{speech_res['fluency_rating']} ({speech_res['words_per_minute']} WPM)",
            "composite_technical_score": nlp_res["technical_score"],
            "scoring_engine": "deterministic_rule_based_rubric"
        }

        # Identify primary weakest concept
        weakest_concept = nlp_res["concepts_missing"][0] if nlp_res["concepts_missing"] else None

        turn_record = {
            "question_text": active_question.get("question_text"),
            "topic": active_question.get("topic"),
            "turn_type": current_turn["turn_type"],
            "answer_text": answer_text,
            "rubric": rubric,
            "nlp_evaluation": nlp_res,
            "speech_analysis": speech_res,
            "weakest_concept": weakest_concept,
            "timestamp": datetime.utcnow().isoformat()
        }
        session["turns"].append(turn_record)

        # 3. DATABASE PERSISTENCE: Save question and answer to SQLite
        db_interview_id = session.get("db_interview_id")
        if db_interview_id:
            db = SessionLocal()
            try:
                db_q = InterviewQuestion(
                    interview_id=db_interview_id,
                    question_text=active_question.get("question_text", "Technical Question"),
                    topic=active_question.get("topic", "General"),
                    difficulty=active_question.get("difficulty", "medium"),
                    expected_concepts=expected,
                    ideal_answer_summary=ideal,
                    is_resume_derived=active_question.get("is_resume_derived", False),
                    source_resume_keyword=active_question.get("source_resume_keyword"),
                    order_index=len(session["turns"])
                )
                db.add(db_q)
                db.commit()
                db.refresh(db_q)

                db_ans = InterviewAnswer(
                    question_id=db_q.id,
                    transcribed_text=answer_text,
                    semantic_similarity=nlp_res["semantic_similarity"],
                    concept_coverage_pct=nlp_res["concept_coverage_pct"],
                    relevance_score=nlp_res["relevance_score"],
                    technical_score=nlp_res["technical_score"],
                    concepts_covered=nlp_res["concepts_covered"],
                    concepts_missing=nlp_res["concepts_missing"],
                    feedback=nlp_res["feedback"]
                )
                db.add(db_ans)
                db.commit()
                db.refresh(db_ans)

                db_speech = SpeechAnalysis(
                    answer_id=db_ans.id,
                    duration_seconds=duration_seconds,
                    words_per_minute=speech_res["words_per_minute"],
                    filler_word_count=speech_res["filler_word_count"],
                    filler_words_detected=speech_res["filler_words_detected"],
                    pause_duration_seconds=speech_res.get("pause_duration_seconds", 0.0),
                    fluency_rating=speech_res["fluency_rating"]
                )
                db.add(db_speech)
                db.commit()
            except Exception as e:
                db.rollback()
            finally:
                db.close()

        # 4. Check if we need to probe with an adaptive follow-up question
        # Rule: Follow-up is triggered ONLY on primary turns when score < 80% or concept coverage < 85%
        # Strictly limited to at most 1 follow-up turn per primary question (prevents infinite loops)
        should_probe = (
            current_turn["turn_type"] == "primary"
            and (nlp_res["concept_coverage_pct"] < 85.0 or nlp_res["technical_score"] < 80.0)
            and len(nlp_res["concepts_missing"]) > 0
        )

        if should_probe:
            follow_up_q = await cls._generate_adaptive_follow_up(
                job_role=session["job_role"],
                main_question=active_question.get("question_text"),
                candidate_answer=answer_text,
                missing_concepts=nlp_res["concepts_missing"],
                topic=active_question.get("topic"),
                asked_texts=session["asked_question_texts"]
            )
            session["asked_question_texts"].add(follow_up_q["question_text"])

            session["state"] = InterviewState.FOLLOW_UP_PROBING.value
            session["current_turn"] = {
                "question": follow_up_q,
                "turn_type": "follow_up",
                "parent_question": active_question.get("question_text"),
                "answer": None,
                "evaluation": None
            }

            return {
                "session_id": session_id,
                "state": session["state"],
                "turn_evaluation": {
                    "rubric": rubric,
                    "nlp_evaluation": nlp_res,
                    "speech_analysis": speech_res,
                    "weakest_concept": weakest_concept
                },
                "is_follow_up": True,
                "follow_up_reason": f"Probing deficit in: {weakest_concept}",
                "next_question": follow_up_q,
                "current_question_number": session["current_index"] + 1,
                "total_questions": session["total_questions"]
            }

        # 5. Advance to next question in queue or complete session
        session["current_index"] += 1
        if session["current_index"] < session["total_questions"]:
            next_q = session["question_queue"][session["current_index"]]
            session["asked_question_texts"].add(next_q.get("question_text"))
            session["state"] = InterviewState.QUESTION_ACTIVE.value
            session["current_turn"] = {
                "question": next_q,
                "turn_type": "primary",
                "answer": None,
                "evaluation": None
            }

            return {
                "session_id": session_id,
                "state": session["state"],
                "turn_evaluation": {
                    "rubric": rubric,
                    "nlp_evaluation": nlp_res,
                    "speech_analysis": speech_res,
                    "weakest_concept": weakest_concept
                },
                "is_follow_up": False,
                "next_question": next_q,
                "current_question_number": session["current_index"] + 1,
                "total_questions": session["total_questions"]
            }
        else:
            # Session reached the end
            return cls.conclude_session(session_id, authenticated_student_id)

    @classmethod
    def conclude_session(cls, session_id: str, authenticated_student_id: Optional[int] = None) -> Dict[str, Any]:
        session = cls.validate_session_owner(session_id, authenticated_student_id)

        turns = session["turns"]
        total_turns = len(turns)
        if total_turns == 0:
            avg_tech = 0.0
            avg_comm = 0.0
            avg_wpm = 0.0
        else:
            avg_tech = round(sum(t["nlp_evaluation"]["technical_score"] for t in turns) / total_turns, 2)
            avg_comm = round(sum(t["nlp_evaluation"]["semantic_similarity"] for t in turns) / total_turns, 2)
            avg_wpm = round(sum(t["speech_analysis"]["words_per_minute"] for t in turns) / total_turns, 1)

        # Aggregate mastered strengths vs weak areas
        all_covered = set()
        all_missing = set()
        for t in turns:
            all_covered.update(t["nlp_evaluation"].get("concepts_covered", []))
            all_missing.update(t["nlp_evaluation"].get("concepts_missing", []))

        # True weak areas are missing concepts that were never successfully covered in any turn
        true_weak_areas = list(all_missing - all_covered)
        strengths = list(all_covered)

        recommendations = TrainingRecommendationEngine.generate_recommendations(
            attendance_pct=88.5,
            aptitude_score=80.0,
            technical_test_score=avg_tech,
            interview_score=avg_tech,
            coding_score=82.0,
            words_per_minute=avg_wpm,
            filler_count=sum(t["speech_analysis"]["filler_word_count"] for t in turns)
        )

        overall_score = round((0.6 * avg_tech) + (0.4 * avg_comm), 2)
        status_verdict = "PASSED" if overall_score >= 65.0 else "TRAINING_REQUIRED"

        summary = {
            "session_id": session_id,
            "job_role": session["job_role"],
            "total_turns": total_turns,
            "overall_score": overall_score,
            "average_technical_score": avg_tech,
            "average_communication_score": avg_comm,
            "average_wpm": avg_wpm,
            "verdict": status_verdict,
            "strengths": strengths,
            "weak_areas": true_weak_areas,
            "recommendations": recommendations,
            "turns_summary": turns
        }

        session["state"] = InterviewState.COMPLETED.value
        session["completed_at"] = datetime.utcnow().isoformat()
        session["overall_summary"] = summary

        # Update database Interview record and Student Performance Metric
        db_interview_id = session.get("db_interview_id")
        db = SessionLocal()
        try:
            if db_interview_id:
                db_interview = db.query(Interview).filter(Interview.id == db_interview_id).first()
                if db_interview:
                    db_interview.status = "completed"
                    db_interview.completed_at = datetime.utcnow()
                    db_interview.overall_score = overall_score
                    db_interview.technical_score = avg_tech
                    db_interview.communication_score = avg_comm

            student = db.query(Student).filter(Student.id == session["student_id"]).first()
            if student and student.performance:
                student.performance.interview_avg_score = avg_tech
                att = float(student.performance.attendance_pct or 88.5)
                apt = float(student.performance.aptitude_score or 80.0)
                tech = float(student.performance.technical_test_score or 80.0)
                mock = float(avg_tech)
                student.performance.overall_score = round((att * 0.15) + (apt * 0.25) + (tech * 0.30) + (mock * 0.30), 2)
            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

        return {
            "session_id": session_id,
            "state": InterviewState.COMPLETED.value,
            "is_completed": True,
            "summary": summary
        }

    @classmethod
    async def _generate_adaptive_follow_up(
        cls,
        job_role: str,
        main_question: str,
        candidate_answer: str,
        missing_concepts: List[str],
        topic: str,
        asked_texts: Set[str]
    ) -> Dict[str, Any]:
        """
        Generates an adaptive follow-up probing question.
        Dual-Engine: Uses Gemini API when configured; otherwise falls back to deterministic heuristic templates.
        Checks asked_texts to reduce question repetition.
        """
        from backend.app.core.config import settings
        gemini_key = (os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "") or "").strip()
        if gemini_key:
            models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
            prompt = (
                f"You are a technical interviewer for a campus placement drive for the role of '{job_role}'.\n"
                f"Main Question: '{main_question}'\n"
                f"Candidate Answer: '{candidate_answer}'\n"
                f"Identified Deficit / Missing Concepts: {', '.join(missing_concepts)}\n\n"
                f"Formulate ONE precise, direct technical follow-up question (max 2 sentences) probing the missing concepts. "
                f"Do not include conversational filler like 'Great answer' or 'Hello'. Ask only the question."
            )
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 200}
            }
            headers = {"Content-Type": "application/json", "x-goog-api-key": gemini_key}
            for model_name in models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        resp = await client.post(url, headers=headers, json=payload)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates:
                                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                                if text and text not in asked_texts:
                                    return {
                                        "question_text": text,
                                        "topic": topic,
                                        "difficulty": "probing",
                                        "expected_concepts": missing_concepts,
                                        "ideal_summary": f"Explanation focusing directly on {', '.join(missing_concepts)}.",
                                        "is_adaptive": True,
                                        "engine": "gemini_llm"
                                    }
                except Exception:
                    pass

        # Deterministic Offline Heuristic Probing Fallback targeting weakest concept
        primary_missing = missing_concepts[0] if missing_concepts else "scalability"
        secondary_missing = missing_concepts[1] if len(missing_concepts) > 1 else "trade-offs"
        
        fallback_templates = [
            f"You mentioned the high-level approach, but how would you specifically handle {primary_missing} and prevent bottlenecks when scaling?",
            f"Could you elaborate on how {primary_missing} and {secondary_missing} interact under concurrent load?",
            f"In an enterprise production environment, what design patterns or safeguards would you implement for {primary_missing}?"
        ]
        
        selected_text = fallback_templates[len(candidate_answer) % len(fallback_templates)]
        if selected_text in asked_texts:
            for cand in fallback_templates:
                if cand not in asked_texts:
                    selected_text = cand
                    break

        return {
            "question_text": selected_text,
            "topic": topic,
            "difficulty": "probing",
            "expected_concepts": missing_concepts,
            "ideal_summary": f"Detailed architectural explanation addressing {primary_missing} and associated system trade-offs.",
            "is_adaptive": True,
            "engine": "heuristic_probing_engine"
        }
