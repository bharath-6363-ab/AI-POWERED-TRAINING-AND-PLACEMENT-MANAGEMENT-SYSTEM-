from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.all_models import Student, User, Batch, BatchStudent, Attendance
from backend.app.schemas.all_schemas import StudentResponse, StudentProfileCreate
from backend.app.core.deps import get_current_user, require_roles

router = APIRouter(prefix="/students", tags=["Student Management"])

@router.get("/", response_model=List[StudentResponse])
def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "trainer"]))
):
    students = db.query(Student).offset(skip).limit(limit).all()
    res = []
    for s in students:
        res.append(StudentResponse(
            id=s.id,
            user_id=s.user_id,
            roll_number=s.roll_number,
            college=s.college,
            branch=s.branch,
            semester=s.semester,
            cgpa=float(s.cgpa),
            github_url=s.github_url,
            linkedin_url=s.linkedin_url,
            bio=s.bio,
            full_name=s.user.full_name,
            email=s.user.email,
            phone=s.user.phone
        ))
    return res

@router.get("/{student_id}", response_model=StudentResponse)
def get_student_details(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Students can only view their own profile unless admin/trainer
    if current_user.role.name == "student" and current_user.student_profile.id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return StudentResponse(
        id=s.id,
        user_id=s.user_id,
        roll_number=s.roll_number,
        college=s.college,
        branch=s.branch,
        semester=s.semester,
        cgpa=float(s.cgpa),
        github_url=s.github_url,
        linkedin_url=s.linkedin_url,
        bio=s.bio,
        full_name=s.user.full_name,
        email=s.user.email,
        phone=s.user.phone
    )

@router.get("/me/dashboard")
def get_student_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns personalized dashboard metrics, performance, resume skills,
    and application status for the currently authenticated student.
    """
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Only students have a student dashboard")
    
    s = current_user.student_profile
    perf = s.performance
    
    # Active resume skills
    resume_skills = [
        {"skill_name": r_skill.skill_name, "category": r_skill.category}
        for r_skill in s.resumes[0].skills
    ] if s.resumes and s.resumes[0].skills else []

    # Recent interviews
    interviews = s.interviews[-5:] if s.interviews else []
    interview_history = [
        {
            "id": iv.id,
            "title": iv.title,
            "overall_score": float(iv.overall_score or 0.0),
            "technical_score": float(iv.technical_score or 0.0),
            "communication_score": float(iv.communication_score or 0.0),
            "status": iv.status,
            "date": iv.completed_at.strftime("%d %b %Y") if iv.completed_at else (iv.started_at.strftime("%d %b %Y") if iv.started_at else "Recent")
        }
        for iv in reversed(interviews)
    ]

    # Applications
    applications_count = len(s.applications) if s.applications else 0
    shortlisted_count = len([a for a in s.applications if a.status == "shortlisted"]) if s.applications else 0

    return {
        "status": "success",
        "student": {
            "id": s.id,
            "user_id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "phone": current_user.phone,
            "roll_number": s.roll_number,
            "college": s.college,
            "branch": s.branch,
            "semester": s.semester,
            "cgpa": float(s.cgpa or 0.0),
            "github_url": s.github_url,
            "linkedin_url": s.linkedin_url,
            "bio": s.bio
        },
        "performance": {
            "attendance_pct": float(perf.attendance_pct or 0.0) if perf else 0.0,
            "aptitude_score": float(perf.aptitude_score or 0.0) if perf else 0.0,
            "technical_test_score": float(perf.technical_test_score or 0.0) if perf else 0.0,
            "coding_score": float(perf.coding_score or 0.0) if perf else 0.0,
            "interview_avg_score": float(perf.interview_avg_score or 0.0) if perf else 0.0,
            "communication_score": float(perf.communication_score or 0.0) if perf else 0.0,
            "overall_score": float(perf.overall_score or 0.0) if perf else 0.0,
            "support_recommended": perf.support_recommended if perf else False
        },
        "resume": {
            "has_resume": len(s.resumes) > 0,
            "skills_count": len(resume_skills),
            "skills": resume_skills
        },
        "applications": {
            "total": applications_count,
            "shortlisted": shortlisted_count
        },
        "recent_interviews": interview_history
    }

@router.put("/{student_id}")
def update_student_profile(
    student_id: int,
    update_data: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user.role.name == "student" and current_user.student_profile.id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if update_data.roll_number:
        s.roll_number = update_data.roll_number.strip().upper()
    if update_data.college:
        s.college = update_data.college.strip()
    if update_data.branch:
        s.branch = update_data.branch.strip()
    if update_data.semester is not None:
        s.semester = update_data.semester
    if update_data.cgpa is not None:
        s.cgpa = min(max(float(update_data.cgpa or 0.0), 0.0), 10.0)
    if update_data.github_url is not None:
        s.github_url = update_data.github_url.strip() if update_data.github_url else None
    if update_data.linkedin_url is not None:
        s.linkedin_url = update_data.linkedin_url.strip() if update_data.linkedin_url else None
    if update_data.bio is not None:
        s.bio = update_data.bio.strip() if update_data.bio else None

    # Also update user full name and phone if provided
    if update_data.full_name and update_data.full_name.strip():
        s.user.full_name = update_data.full_name.strip()
    if update_data.phone is not None:
        s.user.phone = update_data.phone.strip() if update_data.phone else None

    db.commit()
    return {"message": "Profile updated successfully", "student_id": s.id}

