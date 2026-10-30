from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.all_models import User, Role, Student, Trainer, PerformanceMetric
from backend.app.schemas.all_schemas import (
    LoginRequest, Token, StudentRegisterRequest, TrainerRegisterRequest, UserResponse
)
from backend.app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & Authorization"])

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    clean_email = login_data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User account is deactivated")
    
    access_token = create_access_token(
        subject=user.id,
        role=user.role.name
    )

    student_id = user.student_profile.id if user.student_profile else user.id
    roll_number = user.student_profile.roll_number if user.student_profile else None
    college = user.student_profile.college if user.student_profile else None
    branch = user.student_profile.branch if user.student_profile else None
    semester = user.student_profile.semester if user.student_profile else None
    cgpa = float(user.student_profile.cgpa) if user.student_profile else None

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.name,
        "user_id": user.id,
        "student_id": student_id,
        "full_name": user.full_name,
        "email": user.email,
        "roll_number": roll_number,
        "college": college,
        "branch": branch,
        "semester": semester,
        "cgpa": cgpa
    }

@router.post("/register", response_model=Token)
@router.post("/register/student", response_model=Token)
def register_student(reg_data: StudentRegisterRequest, db: Session = Depends(get_db)):
    clean_email = reg_data.email.strip().lower()
    clean_name = reg_data.full_name.strip()
    clean_roll = reg_data.roll_number.strip().upper()
    clean_college = reg_data.college.strip()
    clean_branch = reg_data.branch.strip()

    # Password complexity validation
    if not reg_data.password or len(reg_data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain letters and numbers."
        )

    # Name validation
    if len(clean_name) < 2:
        raise HTTPException(status_code=400, detail="Full name must be at least 2 characters.")

    # Duplicate email check (case-insensitive)
    existing_user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")
    
    # Duplicate roll number check (case-insensitive)
    existing_roll = db.query(Student).filter(func.upper(Student.roll_number) == clean_roll).first()
    if existing_roll:
        raise HTTPException(status_code=400, detail="Roll number is already registered in the system.")

    # Enforce safe default role of student - NEVER allow public registration to create admin
    student_role = db.query(Role).filter(Role.name == "student").first()
    if not student_role:
        student_role = Role(name="student", description="Student candidate")
        db.add(student_role)
        db.commit()
        db.refresh(student_role)

    user = User(
        email=clean_email,
        hashed_password=get_password_hash(reg_data.password),
        full_name=clean_name,
        phone=reg_data.phone.strip() if reg_data.phone else None,
        role_id=student_role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Safe bounded CGPA
    safe_cgpa = min(max(float(reg_data.cgpa or 0.0), 0.0), 10.0)

    student = Student(
        user_id=user.id,
        roll_number=clean_roll,
        college=clean_college,
        branch=clean_branch,
        semester=reg_data.semester or 1,
        cgpa=safe_cgpa,
        github_url=reg_data.github_url.strip() if reg_data.github_url else None,
        linkedin_url=reg_data.linkedin_url.strip() if reg_data.linkedin_url else None
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    # Initialize blank performance metric record with valid student.id
    perf = PerformanceMetric(student_id=student.id)
    db.add(perf)
    db.commit()

    token = create_access_token(subject=user.id, role="student")
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "student",
        "user_id": user.id,
        "student_id": student.id,
        "full_name": user.full_name,
        "email": user.email,
        "roll_number": student.roll_number,
        "college": student.college,
        "branch": student.branch,
        "semester": student.semester,
        "cgpa": float(student.cgpa)
    }

@router.post("/register/trainer", response_model=Token)
def register_trainer(reg_data: TrainerRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == reg_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    trainer_role = db.query(Role).filter(Role.name == "trainer").first()
    if not trainer_role:
        trainer_role = Role(name="trainer", description="Faculty or Industry Trainer")
        db.add(trainer_role)
        db.commit()
        db.refresh(trainer_role)

    user = User(
        email=reg_data.email,
        hashed_password=get_password_hash(reg_data.password),
        full_name=reg_data.full_name,
        phone=reg_data.phone,
        role_id=trainer_role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    trainer = Trainer(
        user_id=user.id,
        employee_id=reg_data.employee_id,
        specialization=reg_data.specialization,
        department=reg_data.department
    )
    db.add(trainer)
    db.commit()

    token = create_access_token(subject=user.id, role="trainer")
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "trainer",
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    profile = None
    if current_user.role.name == "student" and current_user.student_profile:
        s = current_user.student_profile
        profile = {
            "student_id": s.id,
            "roll_number": s.roll_number,
            "college": s.college,
            "branch": s.branch,
            "semester": s.semester,
            "cgpa": float(s.cgpa)
        }
    elif current_user.role.name == "trainer" and current_user.trainer_profile:
        t = current_user.trainer_profile
        profile = {
            "trainer_id": t.id,
            "employee_id": t.employee_id,
            "specialization": t.specialization,
            "department": t.department
        }
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": current_user.role.name,
        "profile": profile
    }
