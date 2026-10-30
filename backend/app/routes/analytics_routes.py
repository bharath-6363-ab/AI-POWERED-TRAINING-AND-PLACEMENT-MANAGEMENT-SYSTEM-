from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from backend.app.core.database import get_db
from backend.app.models.all_models import (
    Student, Batch, Company, JobRole, Application, TestAttempt, Interview, PerformanceMetric, Recommendation, User
)
from backend.app.schemas.all_schemas import PerformanceMetricResponse, RecommendationResponse
from backend.app.core.deps import get_current_user, require_roles

router = APIRouter(prefix="/analytics", tags=["Performance & Executive Analytics"])

@router.get("/student/{student_id}", response_model=PerformanceMetricResponse)
def get_student_performance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    perf = db.query(PerformanceMetric).filter(PerformanceMetric.student_id == student_id).first()
    if not perf:
        raise HTTPException(status_code=404, detail="Performance metrics not found")

    return PerformanceMetricResponse(
        student_id=student_id,
        attendance_pct=float(perf.attendance_pct or 0.0),
        aptitude_score=float(perf.aptitude_score or 0.0),
        technical_test_score=float(perf.technical_test_score or 0.0),
        coding_score=float(perf.coding_score or 0.0),
        interview_avg_score=float(perf.interview_avg_score or 0.0),
        communication_score=float(perf.communication_score or 0.0),
        overall_score=float(perf.overall_score or 0.0),
        support_recommended=perf.support_recommended
    )

@router.get("/student/{student_id}/recommendations", response_model=List[RecommendationResponse])
def get_student_recommendations(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recs = db.query(Recommendation).filter(
        Recommendation.student_id == student_id
    ).order_by(Recommendation.priority.asc()).all()
    return recs

@router.get("/admin/overview")
def get_admin_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "trainer"]))
):
    total_students = db.query(func.count(Student.id)).scalar() or 0
    total_batches = db.query(func.count(Batch.id)).scalar() or 0
    total_companies = db.query(func.count(Company.id)).scalar() or 0
    total_jobs = db.query(func.count(JobRole.id)).scalar() or 0
    total_applications = db.query(func.count(Application.id)).scalar() or 0
    total_interviews = db.query(func.count(Interview.id)).scalar() or 0
    support_needed = db.query(func.count(PerformanceMetric.id)).filter(PerformanceMetric.support_recommended == True).scalar() or 0

    return {
        "total_students": total_students,
        "total_batches": total_batches,
        "total_companies": total_companies,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_interviews": total_interviews,
        "training_support_recommended_count": support_needed
    }
