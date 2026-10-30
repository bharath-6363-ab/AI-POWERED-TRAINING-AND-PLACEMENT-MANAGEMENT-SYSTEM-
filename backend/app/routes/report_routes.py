import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.all_models import Student
from backend.app.reports.report_generator import StudentPDFReportGenerator

router = APIRouter(prefix="/reports", tags=["PDF Dossier & Placement Reports"])

@router.get("/student/{student_id}/download")
def download_student_report(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter((Student.id == student_id) | (Student.user_id == student_id)).first()
    if not student:
        student = db.query(Student).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    reports_dir = os.path.join(settings.UPLOAD_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    pdf_path = os.path.join(reports_dir, f"report_student_{student.id}.pdf")

    StudentPDFReportGenerator.generate_report(student, pdf_path)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"Placement_Report_{student.roll_number}.pdf"
    )
