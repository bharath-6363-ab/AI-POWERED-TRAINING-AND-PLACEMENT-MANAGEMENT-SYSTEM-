from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models.all_models import StudentChatMessage, User, Student
from backend.app.core.deps import get_current_user_optional, get_current_user
from backend.app.ai.chatbot.mentor_engine import MentorEngine

router = APIRouter(prefix="/chatbot", tags=["AI Placement & Career Mentor"])

class ChatMessageRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []

class QuickPromptResponse(BaseModel):
    id: str
    category: str
    prompt: str

@router.post("/chat")
async def chat_with_mentor(
    req: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    student_ctx = None
    user_id = None
    if current_user:
        user_id = current_user.id
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            student_ctx = {
                "name": current_user.full_name,
                "cgpa": float(student.cgpa) if student.cgpa else "N/A",
                "branch": student.branch,
                "skills": [s.skill_name for s in student.resumes[0].skills] if student.resumes and student.resumes[0].skills else []
            }

    # Generate response via Dual-Engine (Gemini or Heuristic KB)
    mentor_data = await MentorEngine.generate_response(
        user_message=req.message,
        chat_history=req.history,
        student_context=student_ctx
    )

    # Persist message history if authenticated
    if user_id:
        try:
            msg_user = StudentChatMessage(user_id=user_id, role="user", message=req.message)
            msg_bot = StudentChatMessage(user_id=user_id, role="model", message=mentor_data["response"])
            db.add(msg_user)
            db.add(msg_bot)
            db.commit()
        except Exception:
            db.rollback()

    return {
        "status": "success",
        "response": mentor_data["response"],
        "engine": mentor_data.get("engine", "offline_heuristic_kb"),
        "source": mentor_data.get("source", "mentor_engine")
    }

@router.get("/history")
def get_chat_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(StudentChatMessage).filter(
        StudentChatMessage.user_id == current_user.id
    ).order_by(StudentChatMessage.created_at.asc()).limit(limit).all()
    
    return [
        {
            "id": m.id,
            "role": m.role,
            "message": m.message,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in messages
    ]

@router.delete("/history")
def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(StudentChatMessage).filter(StudentChatMessage.user_id == current_user.id).delete()
    db.commit()
    return {"status": "success", "message": "Conversation history cleared."}

@router.get("/quick-prompts")
def get_quick_prompts():
    return [
        {"id": "p_reg", "category": "Registration Help", "icon": "📝", "prompt": "Can you explain the registration process and document verification requirements for placement drives?"},
        {"id": "p_elig", "category": "Eligibility Criteria", "icon": "🎯", "prompt": "What are the eligibility criteria, CGPA cutoffs, and attendance requirements for Tier-1 companies?"},
        {"id": "p_rounds", "category": "3-Rounds Info", "icon": "🔄", "prompt": "Explain the 3-Round Sequential Pipeline and how gating works between Aptitude, Technical MCQ, and Mock Interview."},
        {"id": "p_drives", "category": "Explore 47 Drives", "icon": "🏢", "prompt": "What are the 47 active placement drives, top companies, and package tiers available?"},
        {"id": "p_mock", "category": "AI Mock Interview", "icon": "📹", "prompt": "Give me essential tips for the AI Mock Interview: STAR method, eye gaze proctoring, and speech pacing."},
        {"id": "p_resume", "category": "Resume Intelligence", "icon": "📄", "prompt": "How do I optimize my resume for ATS scoring and format technical skills with symbols?"},
        {"id": "p_stress", "category": "Placement Stress & Anxiety", "icon": "💖", "prompt": "What are proven breathing techniques and 24-hour prep plans to manage placement stress and anxiety?"}
    ]

