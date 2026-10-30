from datetime import datetime, date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field

# ----------------- AUTH & USER SCHEMAS -----------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    student_id: Optional[int] = None
    full_name: str
    email: str
    roll_number: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "student" # admin, trainer, student

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- STUDENT SCHEMAS -----------------
class StudentProfileCreate(BaseModel):
    roll_number: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    cgpa: Optional[float] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


class StudentRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    roll_number: str
    college: str = "Engineering College"
    branch: str = "Computer Science"
    department: Optional[str] = None
    role: Optional[str] = "student"
    semester: int = 1
    cgpa: float = 0.00
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    user_id: int
    roll_number: str
    college: str
    branch: str
    semester: int
    cgpa: float
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None
    full_name: str
    email: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------- TRAINER SCHEMAS -----------------
class TrainerRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    employee_id: str
    specialization: str
    department: str

class TrainerResponse(BaseModel):
    id: int
    user_id: int
    employee_id: str
    specialization: str
    department: str
    full_name: str
    email: str

    class Config:
        from_attributes = True

# ----------------- BATCH & COURSE SCHEMAS -----------------
class CourseCreate(BaseModel):
    title: str
    course_code: str
    description: Optional[str] = None

class CourseResponse(BaseModel):
    id: int
    title: str
    course_code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class BatchCreate(BaseModel):
    name: str
    course_id: int
    trainer_id: int
    start_date: date
    end_date: Optional[date] = None

class BatchResponse(BaseModel):
    id: int
    name: str
    course_id: int
    trainer_id: int
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    course_title: Optional[str] = None
    trainer_name: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------- ATTENDANCE SCHEMAS -----------------
class AttendanceMarkItem(BaseModel):
    student_id: int
    status: str = "present" # present, absent, late, excused
    remarks: Optional[str] = None

class AttendanceBatchCreate(BaseModel):
    batch_id: int
    date: date
    records: List[AttendanceMarkItem]

class AttendanceStats(BaseModel):
    student_id: int
    total_classes: int
    classes_attended: int
    attendance_percentage: float

# ----------------- ASSESSMENT & TEST SCHEMAS -----------------
class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: Optional[str] = None
    difficulty: str = "medium"
    topic: str
    marks: int = 1

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str
    topic: str
    marks: int

    class Config:
        from_attributes = True

class TestCreate(BaseModel):
    title: str
    test_type: str # aptitude, technical_mcq, coding, custom
    category: str
    duration_minutes: int = 30
    pass_percentage: float = 60.00
    questions: List[QuestionCreate]

class TestResponse(BaseModel):
    id: int
    title: str
    test_type: str
    category: str
    duration_minutes: int
    total_marks: int
    pass_percentage: float
    question_count: int = 0

    class Config:
        from_attributes = True

class TestSubmissionItem(BaseModel):
    question_id: int
    selected_option: Optional[str] = None

class TestSubmissionRequest(BaseModel):
    answers: List[TestSubmissionItem]

class TestSubmissionResponse(BaseModel):
    attempt_id: int
    test_id: int
    student_id: int
    score: float
    total_possible: float
    percentage: float
    passed: bool

# ----------------- COMPANY & PLACEMENT SCHEMAS -----------------
class JobRequirementCreate(BaseModel):
    min_cgpa: float = 6.00
    min_attendance_pct: float = 75.00
    required_skills: List[str] = []
    eligible_branches: List[str] = []
    max_backlogs: int = 0

class JobRoleCreate(BaseModel):
    company_id: int
    title: str
    description: str
    salary_lpa: Optional[float] = None
    location: Optional[str] = None
    requirements: JobRequirementCreate

class CompanyCreate(BaseModel):
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True

class JobRoleResponse(BaseModel):
    id: int
    company_id: int
    company_name: Optional[str] = None
    company_industry: Optional[str] = None
    title: str
    description: str
    salary_lpa: Optional[float] = None
    location: Optional[str] = None
    is_open: bool
    requirements: Optional[JobRequirementCreate] = None

    class Config:
        from_attributes = True

class EligibilityCheckResponse(BaseModel):
    is_eligible: bool
    reasons: List[str]
    student_cgpa: float
    required_cgpa: float
    student_attendance_pct: float
    required_attendance_pct: float
    student_skills: List[str]
    required_skills: List[str]
    missing_skills: List[str]

# ----------------- INTERVIEW SCHEMAS -----------------
class InterviewCreate(BaseModel):
    job_role_id: Optional[int] = None
    title: str
    interview_type: str = "technical" # technical, hr, behavioral, communication

class InterviewQuestionResponse(BaseModel):
    id: int
    order_index: int
    question_text: str
    topic: str
    difficulty: str
    is_resume_derived: bool
    source_resume_keyword: Optional[str] = None

class AnswerEvaluateRequest(BaseModel):
    question_id: int
    answer_text: str
    duration_seconds: float = 30.0

class AnswerEvaluateResponse(BaseModel):
    question_id: int
    technical_score: float
    semantic_similarity: float
    concept_coverage_pct: float
    relevance_score: float
    concepts_covered: List[str]
    concepts_missing: List[str]
    feedback: str
    words_per_minute: float
    filler_word_count: int
    filler_words_detected: Dict[str, int]
    fluency_rating: str

class VisionEventItem(BaseModel):
    timestamp_offset_seconds: float
    event_type: str # candidate_present, candidate_out_of_frame, multiple_persons, phone_detected
    confidence: float = 1.0
    details: Optional[str] = None

class VisionBatchSubmission(BaseModel):
    interview_id: int
    events: List[VisionEventItem]
    face_visibility_pct: float = 100.00
    stable_head_orientation_pct: float = 100.00
    posture_stability_pct: float = 100.00

# ----------------- PERFORMANCE & RECOMMENDATION -----------------
class PerformanceMetricResponse(BaseModel):
    student_id: int
    attendance_pct: float
    aptitude_score: float
    technical_test_score: float
    coding_score: float
    interview_avg_score: float
    communication_score: float
    overall_score: float
    support_recommended: bool

class RecommendationResponse(BaseModel):
    id: int
    priority: int
    title: str
    category: str
    reason: str
    actionable_steps: str
    is_resolved: bool

    class Config:
        from_attributes = True
