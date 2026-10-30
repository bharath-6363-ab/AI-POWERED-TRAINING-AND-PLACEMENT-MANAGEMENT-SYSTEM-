from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.app.core.database import get_db
from backend.app.models.all_models import (
    Test, Question, TestAttempt, TestAnswer, User, Student, PerformanceMetric
)
from backend.app.schemas.all_schemas import (
    TestCreate, TestResponse, QuestionResponse, TestSubmissionRequest, TestSubmissionResponse
)
from backend.app.core.deps import get_current_user, require_roles, get_current_user_optional

router = APIRouter(prefix="/tests", tags=["Assessments & Mock Tests"])

@router.post("/", response_model=TestResponse)
def create_test(
    t_in: TestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "trainer"]))
):
    total_marks = sum(q.marks for q in t_in.questions)
    test = Test(
        title=t_in.title,
        test_type=t_in.test_type,
        category=t_in.category,
        duration_minutes=t_in.duration_minutes,
        total_marks=total_marks if total_marks > 0 else 100,
        pass_percentage=t_in.pass_percentage,
        created_by=current_user.id
    )
    db.add(test)
    db.commit()
    db.refresh(test)

    for q in t_in.questions:
        question = Question(
            test_id=test.id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            correct_option=q.correct_option.upper(),
            explanation=q.explanation,
            difficulty=q.difficulty,
            topic=q.topic,
            marks=q.marks
        )
        db.add(question)
    db.commit()

    return TestResponse(
        id=test.id,
        title=test.title,
        test_type=test.test_type,
        category=test.category,
        duration_minutes=test.duration_minutes,
        total_marks=test.total_marks,
        pass_percentage=float(test.pass_percentage),
        question_count=len(t_in.questions)
    )

@router.get("/", response_model=List[TestResponse])
def list_available_tests(db: Session = Depends(get_db)):
    tests = db.query(Test).filter(Test.is_active == True).all()
    res = []
    for t in tests:
        res.append(TestResponse(
            id=t.id,
            title=t.title,
            test_type=t.test_type,
            category=t.category,
            duration_minutes=t.duration_minutes,
            total_marks=t.total_marks,
            pass_percentage=float(t.pass_percentage),
            question_count=len(t.questions)
        ))
    return res

@router.get("/{test_id}/questions", response_model=List[QuestionResponse])
def get_test_questions(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Return questions without revealing correct_option to candidates
    return [
        QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            difficulty=q.difficulty,
            topic=q.topic,
            marks=q.marks
        )
        for q in test.questions
    ]

@router.post("/{test_id}/submit", response_model=TestSubmissionResponse)
def submit_test(
    test_id: int,
    sub: TestSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.role or current_user.role.name != "student":
        raise HTTPException(status_code=403, detail="Only students can submit tests")


    student = current_user.student_profile
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # Evaluate marks
    earned_score = 0
    total_possible = 0
    answers_map = {a.question_id: a.selected_option for a in sub.answers}

    attempt = TestAttempt(
        test_id=test.id,
        student_id=student.id,
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow(),
        status="completed"
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    for q in test.questions:
        total_possible += q.marks
        chosen = answers_map.get(q.id)
        is_correct = (chosen is not None and chosen.upper() == q.correct_option.upper())
        if is_correct:
            earned_score += q.marks

        t_ans = TestAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option=chosen,
            is_correct=is_correct
        )
        db.add(t_ans)

    pct = round((earned_score / total_possible * 100.0), 2) if total_possible > 0 else 0.00
    attempt.score = earned_score
    attempt.total_possible = total_possible
    attempt.percentage = pct
    db.commit()

    # Update student performance metric
    perf = db.query(PerformanceMetric).filter(PerformanceMetric.student_id == student.id).first()
    if perf:
        if test.test_type == "aptitude":
            perf.aptitude_score = pct
        elif test.test_type == "coding":
            perf.coding_score = pct
        else:
            perf.technical_test_score = pct
        db.commit()

    return TestSubmissionResponse(
        attempt_id=attempt.id,
        test_id=test.id,
        student_id=student.id,
        score=earned_score,
        total_possible=total_possible,
        percentage=pct,
        passed=(pct >= float(test.pass_percentage))
    )
