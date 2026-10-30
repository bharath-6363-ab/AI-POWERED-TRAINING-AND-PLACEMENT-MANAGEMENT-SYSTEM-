import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.all_models import (
    Interview, InterviewQuestion, InterviewAnswer, SpeechAnalysis, VisionAnalysis,
    InterviewEvent, Student, ResumeSkill, JobRole, PerformanceMetric, Recommendation, User
)
from backend.app.ai.nlp.question_generator import QuestionGenerator
from backend.app.ai.nlp.evaluator import NLPEvaluator
from backend.app.ai.speech.fluency_analyzer import SpeechFluencyAnalyzer
from backend.app.ai.vision.integrity_analyzer import VisionIntegrityAnalyzer
from backend.app.ai.recommendation.engine import TrainingRecommendationEngine
from backend.app.core.deps import get_current_user_optional, get_current_user
from backend.app.ai.interview.state_machine import AdaptiveInterviewStateMachine
from backend.app.ai.interview.project_defense import ProjectDefenseSimulator


router = APIRouter(prefix="/interviews", tags=["AI Mock Interviews & Multi-Modal Evaluation"])

class DirectAnswerRequest(BaseModel):
    question_id: Optional[int] = 1
    question_text: Optional[str] = None
    expected_concepts: Optional[List[str]] = None
    ideal_summary: Optional[str] = None
    answer_text: str
    duration_seconds: float = 25.0
    student_id: Optional[int] = 1

class ResumeQuestionsRequest(BaseModel):
    skills: List[str] = []
    job_title: Optional[str] = "Software Engineer"
    count: Optional[int] = 4

@router.post("/questions/from-resume")
def generate_questions_from_resume(req: ResumeQuestionsRequest):
    """Dynamically generates interview questions tailored to extracted resume skills."""
    questions = QuestionGenerator.generate_interview_questions(
        job_title=req.job_title or "Software Engineer",
        resume_skills=req.skills,
        count=req.count or 4
    )
    return {
        "status": "success",
        "skills_analyzed": req.skills,
        "count": len(questions),
        "questions": questions
    }

@router.get("/questions/sample")
def get_sample_questions(topic: str = "Python", count: int = 4):
    """Directly testable question generation without requiring auth token in HTML forms."""
    questions = QuestionGenerator.generate_interview_questions(
        job_title=topic,
        resume_skills=[topic, "SQL", "FastAPI"],
        count=count
    )
    return {"status": "success", "count": len(questions), "questions": questions}

@router.post("/evaluate-direct")
def evaluate_direct(
    req: DirectAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates candidate answer text using:
    1. NLP Concept Coverage & Semantic Cosine Similarity
    2. Speech Fluency & Filler Detection
    AND persists the interview response, transcribed voice, and speech telemetry permanently into SQLite.
    """
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Only students can submit interview evaluations")

    if req.expected_concepts and len(req.expected_concepts) > 0:
        expected = req.expected_concepts
        ideal = req.ideal_summary or "Technical explanation of the key concepts."
    else:
        iq = db.query(InterviewQuestion).filter(InterviewQuestion.id == req.question_id).first()
        expected = iq.expected_concepts if iq and iq.expected_concepts else ["reference counting", "garbage collection", "memory management"]
        ideal = iq.ideal_answer_summary if iq and iq.ideal_answer_summary else "Python manages memory via reference counting and generational garbage collection."

    # 1. NLP Answer Evaluation
    nlp_res = NLPEvaluator.evaluate_answer(
        answer_text=req.answer_text,
        expected_concepts=expected,
        ideal_summary=ideal
    )

    # 2. Speech Fluency Analysis
    speech_res = SpeechFluencyAnalyzer.analyze_speech(
        transcribed_text=req.answer_text,
        duration_seconds=req.duration_seconds
    )

    # 3. Dynamic Training Recommendation
    recs = TrainingRecommendationEngine.generate_recommendations(
        attendance_pct=85.0,
        aptitude_score=75.0,
        technical_test_score=nlp_res["technical_score"],
        interview_score=nlp_res["technical_score"],
        coding_score=80.0,
        words_per_minute=speech_res["words_per_minute"],
        filler_count=speech_res["filler_word_count"]
    )

    # 4. DATABASE PERSISTENCE: Save Voice Answer & Telemetry permanently
    student = current_user.student_profile


    saved_record_id = None
    if student:
        # Get or create active interview record for student
        interview = db.query(Interview).filter(
            Interview.student_id == student.id
        ).order_by(Interview.id.desc()).first()

        if not interview:
            interview = Interview(
                student_id=student.id,
                title="AI Technical Mock Interview",
                interview_type="technical",
                overall_score=nlp_res["technical_score"],
                technical_score=nlp_res["technical_score"],
                communication_score=nlp_res["semantic_similarity"],
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.add(interview)
            db.flush()

        # Create or fetch question record
        question_text = req.question_text or "Technical Core Question"
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_id == interview.id,
            InterviewQuestion.question_text == question_text
        ).first()

        if not question:
            question = InterviewQuestion(
                interview_id=interview.id,
                question_text=question_text,
                topic="Technical Core",
                difficulty="medium",
                expected_concepts=expected,
                ideal_answer_summary=ideal,
                order_index=req.question_id or 1
            )
            db.add(question)
            db.flush()

        # Create virtual audio voice path
        audio_dir = os.path.join(settings.UPLOAD_DIR, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        audio_file_path = os.path.join(audio_dir, f"voice_recording_q{question.id}.txt")
        try:
            with open(audio_file_path, "w", encoding="utf-8") as f:
                f.write(f"Voice Transcript (Recorded Audio Stream):\n{req.answer_text}\n\nSpeech Telemetry:\nWPM: {speech_res['words_per_minute']}\nFillers: {speech_res['filler_word_count']}\nFluency: {speech_res['fluency_rating']}")
        except Exception:
            pass

        # Save or update InterviewAnswer with transcribed voice response
        answer = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == question.id).first()
        if not answer:
            answer = InterviewAnswer(
                question_id=question.id,
                transcribed_text=req.answer_text,
                audio_file_path=audio_file_path,
                semantic_similarity=nlp_res["semantic_similarity"],
                concept_coverage_pct=nlp_res["concept_coverage_pct"],
                relevance_score=nlp_res["relevance_score"],
                technical_score=nlp_res["technical_score"],
                concepts_covered=nlp_res["concepts_covered"],
                concepts_missing=nlp_res["concepts_missing"],
                feedback=nlp_res["feedback"]
            )
            db.add(answer)
            db.flush()
        else:
            answer.transcribed_text = req.answer_text
            answer.audio_file_path = audio_file_path
            answer.technical_score = nlp_res["technical_score"]
            answer.concepts_covered = nlp_res["concepts_covered"]
            answer.concepts_missing = nlp_res["concepts_missing"]
            answer.feedback = nlp_res["feedback"]

        # Save or update SpeechAnalysis
        speech = db.query(SpeechAnalysis).filter(SpeechAnalysis.answer_id == answer.id).first()
        if not speech:
            speech = SpeechAnalysis(
                answer_id=answer.id,
                duration_seconds=req.duration_seconds,
                words_per_minute=speech_res["words_per_minute"],
                filler_word_count=speech_res["filler_word_count"],
                filler_words_detected=speech_res["filler_words_detected"],
                pause_duration_seconds=speech_res["pause_duration_seconds"],
                fluency_rating=speech_res["fluency_rating"]
            )
            db.add(speech)
        else:
            speech.duration_seconds = req.duration_seconds
            speech.words_per_minute = speech_res["words_per_minute"]
            speech.filler_word_count = speech_res["filler_word_count"]
            speech.fluency_rating = speech_res["fluency_rating"]

        # Update Student Performance Metric
        if student.performance:
            student.performance.interview_avg_score = nlp_res["technical_score"]
            att = float(student.performance.attendance_pct or 88.5)
            apt = float(student.performance.aptitude_score or 82.0)
            tech = float(student.performance.technical_test_score or 85.0)
            mock = float(nlp_res["technical_score"])
            student.performance.overall_score = (att * 0.15) + (apt * 0.25) + (tech * 0.30) + (mock * 0.30)

        db.commit()
        saved_record_id = answer.id

    return {
        "status": "success",
        "saved_to_db": True,
        "answer_record_id": saved_record_id,
        "question_id": req.question_id,
        "nlp_evaluation": nlp_res,
        "speech_analysis": speech_res,
        "recommendations": recs
    }

class FrameBase64Request(BaseModel):
    image_base64: str

@router.post("/vision/analyze-frame")
async def analyze_frame(file: UploadFile = File(...)):
    """Receives a multipart image frame and runs YOLO, MediaPipe, and CNN pose analyzer."""
    contents = await file.read()
    res = VisionIntegrityAnalyzer.analyze_frame_bytes(contents)
    return {"status": "success", "analysis": res}

@router.post("/vision/analyze-frame-base64")
def analyze_frame_base64(req: FrameBase64Request):
    """Receives a base64 encoded frame from HTML5 canvas and evaluates multi-person count and 3D head pose."""
    res = VisionIntegrityAnalyzer.analyze_frame_base64(req.image_base64)
    return {"status": "success", "analysis": res}


class InterviewSessionStartRequest(BaseModel):
    job_role: Optional[str] = "Software Engineer"
    skills: Optional[List[str]] = None
    question_count: Optional[int] = 3

class InterviewTurnRequest(BaseModel):
    session_id: str
    answer_text: str
    duration_seconds: Optional[float] = 25.0

@router.post("/session/start")
def start_interview_session(
    req: InterviewSessionStartRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    student_id = current_user.student_profile.id if (current_user and current_user.student_profile) else 1
    session_data = AdaptiveInterviewStateMachine.start_session(
        student_id=student_id,
        job_role=req.job_role or "Software Engineer",
        skills=req.skills,
        question_count=req.question_count or 3
    )
    return {"status": "success", "session": session_data}

@router.post("/session/turn")
async def process_interview_turn(
    req: InterviewTurnRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    student_id = current_user.student_profile.id if (current_user and current_user.student_profile) else None
    try:
        result = await AdaptiveInterviewStateMachine.submit_turn(
            session_id=req.session_id,
            answer_text=req.answer_text,
            duration_seconds=req.duration_seconds or 25.0,
            authenticated_student_id=student_id
        )
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/session/{session_id}/status")
def get_session_status(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    student_id = current_user.student_profile.id if (current_user and current_user.student_profile) else None
    try:
        session = AdaptiveInterviewStateMachine.validate_session_owner(session_id, student_id)
        return {"status": "success", "session": session}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/session/{session_id}/conclude")
def conclude_interview_session(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    student_id = current_user.student_profile.id if (current_user and current_user.student_profile) else None
    try:
        result = AdaptiveInterviewStateMachine.conclude_session(session_id, authenticated_student_id=student_id)
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


class ProjectDefenseGenerateRequest(BaseModel):
    project_title: str
    tech_stack: List[str]
    project_description: str
    architecture_type: Optional[str] = "Full-Stack Web & Microservices"

class ProjectDefenseEvaluateRequest(BaseModel):
    question_text: str
    expected_concepts: List[str] = []
    ideal_architect_answer: Optional[str] = ""
    student_answer: str
    project_title: Optional[str] = "Major Project"

@router.post("/project-defense/generate")
async def generate_project_defense_questions(req: ProjectDefenseGenerateRequest):
    res = await ProjectDefenseSimulator.generate_viva_questions(
        project_title=req.project_title,
        tech_stack=req.tech_stack,
        project_description=req.project_description,
        architecture_type=req.architecture_type or "Full-Stack Web & Microservices"
    )
    return res

@router.post("/project-defense/evaluate")
async def evaluate_project_defense(req: ProjectDefenseEvaluateRequest):
    res = await ProjectDefenseSimulator.evaluate_defense_answer(
        question_text=req.question_text,
        expected_concepts=req.expected_concepts,
        ideal_architect_answer=req.ideal_architect_answer or "",
        student_answer=req.student_answer,
        project_title=req.project_title or "Major Project"
    )
    return {"status": "success", "data": res}


@router.get("/history")
def get_interview_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Interview)
    if current_user.role.name == "student":
        if not current_user.student_profile:
            return []
        query = query.filter(Interview.student_id == current_user.student_profile.id)

    interviews = query.order_by(Interview.id.desc()).all()
    res = []
    for iv in interviews:
        res.append({
            "id": iv.id,
            "student_id": iv.student_id,
            "student_name": iv.student.user.full_name if (iv.student and iv.student.user) else "Student",
            "title": iv.title,
            "interview_type": iv.interview_type,
            "overall_score": float(iv.overall_score or 0.0),
            "technical_score": float(iv.technical_score or 0.0),
            "communication_score": float(iv.communication_score or 0.0),
            "integrity_score": float(iv.integrity_score or 100.0),
            "status": iv.status,
            "started_at": iv.started_at.isoformat() if iv.started_at else None,
            "completed_at": iv.completed_at.isoformat() if iv.completed_at else None,
            "question_count": len(iv.questions)
        })
    return res


@router.get("/detail/{interview_id}")
def get_interview_detail(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    iv = db.query(Interview).filter(Interview.id == interview_id).first()
    if not iv:
        raise HTTPException(status_code=404, detail="Interview record not found")

    if current_user.role.name == "student":
        if not current_user.student_profile or iv.student_id != current_user.student_profile.id:
            raise HTTPException(status_code=403, detail="Access denied")


    questions_data = []
    for q in iv.questions:
        ans_data = None
        if q.answer:
            ans_data = {
                "transcribed_text": q.answer.transcribed_text,
                "technical_score": float(q.answer.technical_score or 0.0),
                "semantic_similarity": float(q.answer.semantic_similarity or 0.0),
                "concept_coverage_pct": float(q.answer.concept_coverage_pct or 0.0),
                "relevance_score": float(q.answer.relevance_score or 0.0),
                "concepts_covered": q.answer.concepts_covered or [],
                "concepts_missing": q.answer.concepts_missing or [],
                "feedback": q.answer.feedback,
                "speech_analysis": {
                    "words_per_minute": float(q.answer.speech_analysis.words_per_minute or 0.0),
                    "filler_word_count": q.answer.speech_analysis.filler_word_count or 0,
                    "fluency_rating": q.answer.speech_analysis.fluency_rating or "Normal"
                } if q.answer.speech_analysis else None
            }
        questions_data.append({
            "id": q.id,
            "order_index": q.order_index,
            "question_text": q.question_text,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "expected_concepts": q.expected_concepts or [],
            "ideal_answer_summary": q.ideal_answer_summary,
            "is_resume_derived": q.is_resume_derived,
            "source_resume_keyword": q.source_resume_keyword,
            "answer": ans_data
        })

    return {
        "id": iv.id,
        "title": iv.title,
        "interview_type": iv.interview_type,
        "overall_score": float(iv.overall_score or 0.0),
        "technical_score": float(iv.technical_score or 0.0),
        "communication_score": float(iv.communication_score or 0.0),
        "integrity_score": float(iv.integrity_score or 100.0),
        "status": iv.status,
        "started_at": iv.started_at.isoformat() if iv.started_at else None,
        "completed_at": iv.completed_at.isoformat() if iv.completed_at else None,
        "questions": questions_data
    }



