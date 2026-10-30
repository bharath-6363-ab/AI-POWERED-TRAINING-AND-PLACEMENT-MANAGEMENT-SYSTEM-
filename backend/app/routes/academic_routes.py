from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.all_models import Course, Batch, BatchStudent, Trainer, Student, User
from backend.app.schemas.all_schemas import (
    CourseCreate, CourseResponse, BatchCreate, BatchResponse
)
from backend.app.core.deps import require_roles

router = APIRouter(prefix="/academic", tags=["Academic, Courses & Batches"])

@router.post("/courses", response_model=CourseResponse)
def create_course(
    c_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    existing = db.query(Course).filter(Course.course_code == c_in.course_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course code already exists")
    
    course = Course(
        title=c_in.title,
        course_code=c_in.course_code,
        description=c_in.description
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.get("/courses", response_model=List[CourseResponse])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@router.post("/batches", response_model=BatchResponse)
def create_batch(
    b_in: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    trainer = db.query(Trainer).filter(Trainer.id == b_in.trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    course = db.query(Course).filter(Course.id == b_in.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    batch = Batch(
        name=b_in.name,
        course_id=b_in.course_id,
        trainer_id=b_in.trainer_id,
        start_date=b_in.start_date,
        end_date=b_in.end_date
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    return BatchResponse(
        id=batch.id,
        name=batch.name,
        course_id=batch.course_id,
        trainer_id=batch.trainer_id,
        start_date=batch.start_date,
        end_date=batch.end_date,
        is_active=batch.is_active,
        course_title=course.title,
        trainer_name=trainer.user.full_name
    )

@router.get("/batches", response_model=List[BatchResponse])
def list_batches(db: Session = Depends(get_db)):
    batches = db.query(Batch).all()
    res = []
    for b in batches:
        res.append(BatchResponse(
            id=b.id,
            name=b.name,
            course_id=b.course_id,
            trainer_id=b.trainer_id,
            start_date=b.start_date,
            end_date=b.end_date,
            is_active=b.is_active,
            course_title=b.course.title if b.course else None,
            trainer_name=b.trainer.user.full_name if b.trainer else None
        ))
    return res

@router.post("/batches/{batch_id}/enroll/{student_id}")
def enroll_student_in_batch(
    batch_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "trainer"]))
):
    existing = db.query(BatchStudent).filter(
        BatchStudent.batch_id == batch_id,
        BatchStudent.student_id == student_id
    ).first()
    if existing:
        return {"message": "Student already enrolled in this batch"}

    enrollment = BatchStudent(batch_id=batch_id, student_id=student_id)
    db.add(enrollment)
    db.commit()
    return {"message": "Student successfully enrolled in batch"}
