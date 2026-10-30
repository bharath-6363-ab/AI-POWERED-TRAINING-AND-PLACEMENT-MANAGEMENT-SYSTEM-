from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.all_models import (
    Company, JobRole, JobRequirement, Application, PlacementRound, Student, User, ResumeSkill, PerformanceMetric, Test
)
from backend.app.schemas.all_schemas import (
    CompanyCreate, CompanyResponse, JobRoleCreate, JobRoleResponse,
    EligibilityCheckResponse, JobRequirementCreate
)
from backend.app.core.deps import get_current_user, require_roles, get_current_user_optional

router = APIRouter(prefix="/placement", tags=["Companies, Job Roles & Placement Engine"])

@router.post("/companies", response_model=CompanyResponse)
def create_company(
    c_in: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    existing = db.query(Company).filter(Company.name == c_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company name already exists")

    company = Company(
        name=c_in.name,
        website=c_in.website,
        industry=c_in.industry,
        location=c_in.location
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/companies", response_model=List[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()

@router.post("/jobs", response_model=JobRoleResponse)
def create_job_role(
    j_in: JobRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    company = db.query(Company).filter(Company.id == j_in.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    job = JobRole(
        company_id=j_in.company_id,
        title=j_in.title,
        description=j_in.description,
        salary_lpa=j_in.salary_lpa,
        location=j_in.location
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    req = JobRequirement(
        job_role_id=job.id,
        min_cgpa=j_in.requirements.min_cgpa,
        min_attendance_pct=j_in.requirements.min_attendance_pct,
        required_skills=j_in.requirements.required_skills,
        eligible_branches=j_in.requirements.eligible_branches,
        max_backlogs=j_in.requirements.max_backlogs
    )
    db.add(req)
    db.commit()

    return JobRoleResponse(
        id=job.id,
        company_id=job.company_id,
        company_name=company.name,
        company_industry=company.industry,
        title=job.title,
        description=job.description,
        salary_lpa=float(job.salary_lpa) if job.salary_lpa else None,
        location=job.location,
        is_open=job.is_open,
        requirements=j_in.requirements
    )

@router.get("/jobs", response_model=List[JobRoleResponse])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobRole).filter(JobRole.is_open == True).all()
    res = []
    for j in jobs:
        req_data = None
        if j.requirements:
            req_data = JobRequirementCreate(
                min_cgpa=float(j.requirements.min_cgpa),
                min_attendance_pct=float(j.requirements.min_attendance_pct),
                required_skills=j.requirements.required_skills or [],
                eligible_branches=j.requirements.eligible_branches or [],
                max_backlogs=j.requirements.max_backlogs
            )
        res.append(JobRoleResponse(
            id=j.id,
            company_id=j.company_id,
            company_name=j.company.name if j.company else None,
            company_industry=j.company.industry if j.company else None,
            title=j.title,
            description=j.description,
            salary_lpa=float(j.salary_lpa) if j.salary_lpa else None,
            location=j.location,
            is_open=j.is_open,
            requirements=req_data
        ))
    return res

@router.get("/jobs/{job_id}/check-eligibility/{student_id}", response_model=EligibilityCheckResponse)
def check_eligibility(
    job_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.name == "student" and (not current_user.student_profile or current_user.student_profile.id != student_id):
        raise HTTPException(status_code=403, detail="Access denied")

    job = db.query(JobRole).filter(JobRole.id == job_id).first()
    if not job or not job.requirements:
        raise HTTPException(status_code=404, detail="Job role or criteria not found")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    req = job.requirements
    perf = student.performance

    # 1. Check CGPA
    reasons = []
    is_eligible = True

    stud_cgpa = float(student.cgpa)
    req_cgpa = float(req.min_cgpa)
    if stud_cgpa < req_cgpa:
        is_eligible = False
        reasons.append(f"CGPA deficit: Current CGPA is {stud_cgpa:.2f}, required is {req_cgpa:.2f}")

    # 2. Check Attendance
    stud_att = float(perf.attendance_pct) if perf else 0.00
    req_att = float(req.min_attendance_pct)
    if stud_att < req_att:
        is_eligible = False
        reasons.append(f"Attendance deficit: Current attendance is {stud_att:.1f}%, required is {req_att:.1f}%")

    # 3. Check Branch
    if req.eligible_branches and len(req.eligible_branches) > 0:
        if student.branch.upper() not in [b.upper() for b in req.eligible_branches]:
            is_eligible = False
            reasons.append(f"Branch mismatch: Student is from {student.branch}, eligible branches: {', '.join(req.eligible_branches)}")

    # 4. Check Skills
    student_skills_entities = db.query(ResumeSkill.skill_name).filter(ResumeSkill.student_id == student.id).all()
    student_skills = [s[0].lower() for s in student_skills_entities]
    
    missing_skills = []
    if req.required_skills:
        for r_skill in req.required_skills:
            if r_skill.lower() not in student_skills:
                missing_skills.append(r_skill)

    if missing_skills:
        # Note: missing skills are flagged clearly
        reasons.append(f"Missing required skills: {', '.join(missing_skills)}")

    return EligibilityCheckResponse(
        is_eligible=is_eligible,
        reasons=reasons,
        student_cgpa=stud_cgpa,
        required_cgpa=req_cgpa,
        student_attendance_pct=stud_att,
        required_attendance_pct=req_att,
        student_skills=[s[0] for s in student_skills_entities],
        required_skills=req.required_skills or [],
        missing_skills=missing_skills
    )

@router.post("/jobs/{job_id}/apply")
def apply_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.role or current_user.role.name != "student":
        raise HTTPException(status_code=403, detail="Only students can apply")

    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")
    existing = db.query(Application).filter(
        Application.job_role_id == job_id,
        Application.student_id == student.id
    ).first()
    if existing:
        return {
            "message": "Already applied for this position - Candidate Shortlisted!",
            "application_id": existing.id,
            "status": existing.status,
            "is_eligible": existing.is_eligible
        }

    # Evaluate eligibility
    eligibility = check_eligibility(job_id=job_id, student_id=student.id, db=db, current_user=current_user)

    app = Application(
        job_role_id=job_id,
        student_id=student.id,
        is_eligible=eligibility.is_eligible,
        ineligibility_reason="; ".join(eligibility.reasons) if not eligibility.is_eligible else None,
        status="shortlisted" if eligibility.is_eligible else "rejected"
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    return {
        "message": "🎉 Candidate Shortlisted for Placement Drive!" if eligibility.is_eligible else "Application submitted with eligibility remarks",
        "application_id": app.id,
        "is_eligible": eligibility.is_eligible,
        "status": app.status,
        "reasons": eligibility.reasons
    }

@router.get("/my-applications")
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.student_profile:
        return []

    apps = db.query(Application).filter(Application.student_id == current_user.student_profile.id).all()
    return [
        {
            "application_id": a.id,
            "job_id": a.job_role_id,
            "company_name": a.job_role.company.name if a.job_role and a.job_role.company else None,
            "title": a.job_role.title if a.job_role else None,
            "status": a.status,
            "is_eligible": a.is_eligible
        }
        for a in apps
    ]


@router.get("/rounds/workflow")
def get_sequential_recruitment_workflow(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Returns the order-wise 3-Round Placement Drive Workflow:
    Round 1: Aptitude Round
    Round 2: Technical Round
    Round 3: Mock AI Interview Round
    """
    aptitude_test = db.query(Test).filter(Test.test_type == "aptitude").first()
    technical_test = db.query(Test).filter(Test.test_type == "technical").first()

    student_id = 1
    if current_user and current_user.role.name == "student" and current_user.student_profile:
        student_id = current_user.student_profile.id

    perf = db.query(PerformanceMetric).filter(PerformanceMetric.student_id == student_id).first()

    apt_score = float(perf.aptitude_score) if (perf and perf.aptitude_score is not None) else None
    tech_score = float(perf.technical_test_score) if (perf and perf.technical_test_score is not None) else None
    ai_score = float(perf.communication_score) if (perf and perf.communication_score is not None) else None

    # Sequential unlocking state determination
    r1_cleared = (apt_score is not None and apt_score >= 60.0)
    r2_unlocked = r1_cleared
    r2_cleared = (r2_unlocked and tech_score is not None and tech_score >= 65.0)
    r3_unlocked = r2_cleared
    r3_cleared = (r3_unlocked and ai_score is not None and ai_score >= 70.0)

    return {
        "rounds": [
            {
                "round_number": 1,
                "title": "Round 1: Aptitude Round",
                "description": "Quantitative Aptitude, Logical Reasoning & Verbal Ability Test",
                "test_id": aptitude_test.id if aptitude_test else 2,
                "duration_minutes": 30,
                "pass_percentage": 60.0,
                "status": "cleared" if r1_cleared else "active",
                "is_unlocked": True,
                "score": apt_score
            },
            {
                "round_number": 2,
                "title": "Round 2: Technical Round",
                "description": "Software Engineering, Coding & Core Computer Science Test",
                "test_id": technical_test.id if technical_test else 3,
                "duration_minutes": 45,
                "pass_percentage": 65.0,
                "status": "cleared" if r2_cleared else ("active" if r2_unlocked else "locked"),
                "is_unlocked": r2_unlocked,
                "score": tech_score
            },
            {
                "round_number": 3,
                "title": "Round 3: Mock AI Interview Round",
                "description": "Live AI Video & Audio Interview with MediaPipe 3D Pose & YOLOv8 Proctoring",
                "test_id": None,
                "duration_minutes": 20,
                "pass_percentage": 70.0,
                "status": "cleared" if r3_cleared else ("active" if r3_unlocked else "locked"),
                "is_unlocked": r3_unlocked,
                "score": ai_score
            }
        ],
        "current_active_round": 3 if r2_cleared else (2 if r1_cleared else 1),
        "overall_selection_status": "SELECTED" if r3_cleared else "IN_PROGRESS"
    }

@router.post("/rounds/reset")
def reset_placement_rounds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    student_id = 1
    if current_user and current_user.role.name == "student" and current_user.student_profile:
        student_id = current_user.student_profile.id

    perf = db.query(PerformanceMetric).filter(PerformanceMetric.student_id == student_id).first()
    if perf:
        perf.aptitude_score = None
        perf.technical_test_score = None
        perf.communication_score = None
        db.commit()

    return {"message": "All recruitment drive round scores reset to 0. Round 1 Aptitude Test ready!"}
