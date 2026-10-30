import os
import shutil
import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from pydantic import BaseModel
from typing import Optional, List
from backend.app.models.all_models import Resume, ResumeSkill, Student, User, JobRole
from backend.app.ai.resume.parser import ResumeParser
from backend.app.ai.resume.skill_gap_analyzer import ResumeSkillGapAnalyzer
from backend.app.core.deps import get_current_user

router = APIRouter(prefix="/resume", tags=["Resume Intelligence Engine"])

@router.get("/my-resume")
def get_my_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves the authenticated student's active resume and extracted skills."""
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Only students have active resumes")
    
    student = current_user.student_profile
    resume = db.query(Resume).filter(
        Resume.student_id == student.id,
        Resume.is_active == True
    ).order_by(Resume.id.desc()).first()

    if not resume:
        return {
            "status": "empty",
            "has_resume": False,
            "filename": None,
            "skills": [],
            "sections": {},
            "raw_text": ""
        }

    skills = [
        {"skill_name": s.skill_name, "category": s.category, "verified": s.is_verified_by_student}
        for s in resume.skills
    ]

    return {
        "status": "success",
        "has_resume": True,
        "resume_id": resume.id,
        "filename": os.path.basename(resume.file_path),
        "uploaded_at": resume.uploaded_at.isoformat() if resume.uploaded_at else None,
        "skills": [s["skill_name"] for s in skills],
        "detailed_skills": skills,
        "sections": resume.parsed_json.get("sections", {}),
        "raw_text": resume.extracted_raw_text or ""
    }

@router.post("/upload")
async def upload_student_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated resume upload:
    Parses resume text, extracts skills, and permanently records both
    into the database linked to the authenticated student's profile.
    """
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Only registered students can upload resumes")

    student = current_user.student_profile
    upload_dir = os.path.join(settings.UPLOAD_DIR, "resumes")
    os.makedirs(upload_dir, exist_ok=True)

    safe_name = os.path.basename(file.filename) if file.filename else f"student_{student.id}_resume.pdf"
    # Normalize filename for filesystem safety
    import re
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', safe_name)
    file_bytes = await file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    saved_file_name = f"student_{student.id}_{file_hash[:8]}_{safe_name}"
    file_path = os.path.join(upload_dir, saved_file_name)
    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)

    # Extract text from PDF or text
    lower_name = safe_name.lower()
    if lower_name.endswith(".pdf"):
        raw_text = ResumeParser.extract_text_from_pdf(file_path)
    else:
        try:
            raw_text = file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            raw_text = "Text extraction failed"

    # AI/NLP Skill and Section Parsing
    parsed_info = ResumeParser.parse_resume(raw_text)
    extracted_skills_raw = parsed_info.get("skills", [])
    categorized_skills = parsed_info.get("categorized_skills", {})

    # Extract flat string skill names for both database records and UI display
    flat_skill_names = []
    for s in extracted_skills_raw:
        if isinstance(s, dict):
            flat_skill_names.append(s.get("name", ""))
        elif isinstance(s, str):
            flat_skill_names.append(s)

    # Deactivate previous active resumes for this student
    db.query(Resume).filter(Resume.student_id == student.id).update({"is_active": False})

    # Create new Resume record
    resume_record = Resume(
        student_id=student.id,
        file_path=file_path,
        file_hash=file_hash,
        extracted_raw_text=raw_text,
        parsed_json=parsed_info,
        is_active=True
    )
    db.add(resume_record)
    db.flush()

    # Clear old ResumeSkill records for this student and insert newly parsed ones
    db.query(ResumeSkill).filter(ResumeSkill.student_id == student.id).delete()
    for category, skill_list in categorized_skills.items():
        for skill_name in skill_list:
            rs = ResumeSkill(
                resume_id=resume_record.id,
                student_id=student.id,
                skill_name=skill_name,
                category=category,
                is_verified_by_student=True
            )
            db.add(rs)

    # Also add any uncategorized skills safely
    existing_skill_names = {s.lower() for cat in categorized_skills.values() for s in cat}
    for s_item in extracted_skills_raw:
        s_name = s_item.get("name", "") if isinstance(s_item, dict) else str(s_item)
        s_cat = s_item.get("category", "Core Technical") if isinstance(s_item, dict) else "Core Technical"
        if s_name and s_name.lower() not in existing_skill_names:
            rs = ResumeSkill(
                resume_id=resume_record.id,
                student_id=student.id,
                skill_name=s_name,
                category=s_cat,
                is_verified_by_student=True
            )
            db.add(rs)
            existing_skill_names.add(s_name.lower())

    db.commit()

    return {
        "status": "success",
        "message": f"Successfully parsed and saved {len(flat_skill_names)} technical skills to your student profile.",
        "resume_id": resume_record.id,
        "filename": safe_name,
        "skills": flat_skill_names,
        "extracted_skills": flat_skill_names,
        "detailed_skills": extracted_skills_raw,
        "categorized_skills": categorized_skills,
        "sections": parsed_info.get("sections", {}),
        "raw_text": raw_text
    }

@router.post("/parse-text")
def parse_raw_text(text: str):
    """Parses raw text directly without needing a PDF upload for instant browser testing."""
    parsed_info = ResumeParser.parse_resume(text)
    return {"status": "success", "parsed_data": parsed_info}


@router.post("/upload-file")
async def upload_and_parse_resume_direct(
    file: UploadFile = File(...)
):
    """Uploads and parses a PDF or text resume directly without token requirement."""
    upload_dir = os.path.join(settings.UPLOAD_DIR, "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    
    safe_name = os.path.basename(file.filename) if file.filename else "resume.pdf"
    file_path = os.path.join(upload_dir, f"temp_{safe_name}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    lower_name = safe_name.lower()
    if lower_name.endswith(".pdf"):
        raw_text = ResumeParser.extract_text_from_pdf(file_path)
    else:
        # Default text/fallback reader
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
        except Exception as e:
            raw_text = f"Error reading text resume: {str(e)}"

    parsed_info = ResumeParser.parse_resume(raw_text)
    ext_skills_raw = parsed_info.get("skills", [])
    flat_skills = [s.get("name", "") if isinstance(s, dict) else str(s) for s in ext_skills_raw]

    return {
        "status": "success",
        "filename": file.filename,
        "raw_text": raw_text,
        "skills": flat_skills,
        "extracted_skills": flat_skills,
        "detailed_skills": ext_skills_raw,
        "categorized_skills": parsed_info.get("categorized_skills", {}),
        "sections": parsed_info.get("sections", {})
    }


class SkillGapAnalysisRequest(BaseModel):
    resume_text: Optional[str] = None
    job_id: Optional[int] = None
    job_description: Optional[str] = None
    required_skills: Optional[List[str]] = None

@router.post("/analyze-gap")
def analyze_resume_skill_gap(
    req: SkillGapAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Computes ATS compatibility score and identifies matched vs missing skills
    between candidate resume and a campus placement job description.
    """
    resume_text = req.resume_text or ""
    jd_text = req.job_description or ""
    req_skills = req.required_skills or []

    # If job_id is provided, pull requirements from database
    if req.job_id:
        job = db.query(JobRole).filter(JobRole.id == req.job_id).first()
        if job:
            if not jd_text:
                jd_text = f"{job.title}\n{job.description}"
            if job.requirements and job.requirements.required_skills:
                req_skills = list(set(req_skills + (job.requirements.required_skills or [])))

    if not resume_text and not jd_text and not req_skills:
        raise HTTPException(status_code=400, detail="Please provide either resume_text or a valid job_id/job_description")

    result = ResumeSkillGapAnalyzer.analyze_gap(
        resume_text=resume_text,
        job_description=jd_text,
        required_skills=req_skills
    )
    return {"status": "success", "analysis": result}


class ResumeAuditRequest(BaseModel):
    resume_text: str

@router.post("/audit")
def audit_resume_quality(req: ResumeAuditRequest):
    """
    Performs comprehensive multi-pillar automated ATS health and quality audit on candidate resume.
    """
    if not req.resume_text or not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required for ATS quality audit.")
    audit_res = ResumeSkillGapAnalyzer.comprehensive_ats_audit(req.resume_text)
    return {"status": "success", "audit": audit_res}


