from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date
from backend.app.core.database import get_db
from backend.app.models.all_models import Attendance, Batch, Student, User, PerformanceMetric
from backend.app.schemas.all_schemas import AttendanceBatchCreate, AttendanceStats
from backend.app.core.deps import get_current_user, require_roles

router = APIRouter(prefix="/attendance", tags=["Attendance Tracking"])

@router.post("/mark")
def mark_batch_attendance(
    data: AttendanceBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "trainer"]))
):
    batch = db.query(Batch).filter(Batch.id == data.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    saved_records = 0
    for record in data.records:
        # Check if record already exists for this student on this date
        att = db.query(Attendance).filter(
            Attendance.batch_id == data.batch_id,
            Attendance.student_id == record.student_id,
            Attendance.date == data.date
        ).first()

        if att:
            att.status = record.status
            att.remarks = record.remarks
            att.marked_by = current_user.id
        else:
            att = Attendance(
                batch_id=data.batch_id,
                student_id=record.student_id,
                date=data.date,
                status=record.status,
                remarks=record.remarks,
                marked_by=current_user.id
            )
            db.add(att)
        saved_records += 1

    db.commit()

    # Automatically recalculate student attendance percentage
    for record in data.records:
        recalculate_student_attendance(record.student_id, db)

    return {"message": f"Successfully marked attendance for {saved_records} students"}

def recalculate_student_attendance(student_id: int, db: Session):
    total = db.query(func.count(Attendance.id)).filter(Attendance.student_id == student_id).scalar() or 0
    present = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.status.in_(["present", "late"])
    ).scalar() or 0

    pct = round((present / total * 100.0), 2) if total > 0 else 0.00
    
    perf = db.query(PerformanceMetric).filter(PerformanceMetric.student_id == student_id).first()
    if not perf:
        perf = PerformanceMetric(student_id=student_id, attendance_pct=pct)
        db.add(perf)
    else:
        perf.attendance_pct = pct
    db.commit()

@router.get("/student/{student_id}/stats", response_model=AttendanceStats)
def get_student_attendance_stats(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(func.count(Attendance.id)).filter(Attendance.student_id == student_id).scalar() or 0
    present = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.status.in_(["present", "late"])
    ).scalar() or 0

    pct = round((present / total * 100.0), 2) if total > 0 else 0.00

    return AttendanceStats(
        student_id=student_id,
        total_classes=total,
        classes_attended=present,
        attendance_percentage=pct
    )
