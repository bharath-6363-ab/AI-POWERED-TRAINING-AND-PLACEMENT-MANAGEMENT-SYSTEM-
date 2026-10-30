from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False) # admin, trainer, student
    description = Column(String(255), nullable=True)
    
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trainer_profile = relationship("Trainer", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    college = Column(String(150), nullable=False)
    branch = Column(String(80), nullable=False)
    semester = Column(Integer, nullable=False, default=1)
    cgpa = Column(Numeric(4, 2), nullable=False, default=0.00)
    github_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="student_profile")
    batch_enrollments = relationship("BatchStudent", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    test_attempts = relationship("TestAttempt", back_populates="student", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="student", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    performance = relationship("PerformanceMetric", back_populates="student", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="student", cascade="all, delete-orphan")

class Trainer(Base):
    __tablename__ = "trainers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    specialization = Column(String(150), nullable=False)
    department = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trainer_profile")
    batches = relationship("Batch", back_populates="trainer")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    course_code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batches = relationship("Batch", back_populates="course")

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="batches")
    trainer = relationship("Trainer", back_populates="batches")
    students = relationship("BatchStudent", back_populates="batch", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="batch", cascade="all, delete-orphan")

class BatchStudent(Base):
    __tablename__ = "batch_students"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)

    batch = relationship("Batch", back_populates="students")
    student = relationship("Student", back_populates="batch_enrollments")

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="present") # present, absent, late, excused
    remarks = Column(String(255), nullable=True)
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("Batch", back_populates="attendance")
    student = relationship("Student", back_populates="attendance_records")

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    test_type = Column(String(30), nullable=False) # aptitude, technical_mcq, coding, custom
    category = Column(String(80), nullable=False)
    duration_minutes = Column(Integer, default=30, nullable=False)
    total_marks = Column(Integer, default=100, nullable=False)
    pass_percentage = Column(Numeric(5, 2), default=60.00)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    attempts = relationship("TestAttempt", back_populates="test", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String(5), nullable=False) # A, B, C, D
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium")
    topic = Column(String(80), nullable=False)
    marks = Column(Integer, default=1)

    test = relationship("Test", back_populates="questions")
    answers = relationship("TestAnswer", back_populates="question", cascade="all, delete-orphan")

class TestAttempt(Base):
    __tablename__ = "test_attempts"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    score = Column(Numeric(5, 2), default=0.00)
    total_possible = Column(Numeric(5, 2), default=0.00)
    percentage = Column(Numeric(5, 2), default=0.00)
    status = Column(String(20), default="in_progress") # in_progress, completed, timed_out

    test = relationship("Test", back_populates="attempts")
    student = relationship("Student", back_populates="test_attempts")
    answers = relationship("TestAnswer", back_populates="attempt", cascade="all, delete-orphan")

class TestAnswer(Base):
    __tablename__ = "test_answers"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_option = Column(String(5), nullable=True)
    is_correct = Column(Boolean, default=False)

    attempt = relationship("TestAttempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job_roles = relationship("JobRole", back_populates="company", cascade="all, delete-orphan")

class JobRole(Base):
    __tablename__ = "job_roles"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    salary_lpa = Column(Numeric(5, 2), nullable=True)
    location = Column(String(100), nullable=True)
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="job_roles")
    requirements = relationship("JobRequirement", back_populates="job_role", uselist=False, cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job_role", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="job_role")

class JobRequirement(Base):
    __tablename__ = "job_requirements"
    id = Column(Integer, primary_key=True, index=True)
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="CASCADE"), unique=True, nullable=False)
    min_cgpa = Column(Numeric(4, 2), default=6.00, nullable=False)
    min_attendance_pct = Column(Numeric(5, 2), default=75.00, nullable=False)
    required_skills = Column(JSON, nullable=False, default=list)
    eligible_branches = Column(JSON, nullable=False, default=list)
    max_backlogs = Column(Integer, default=0, nullable=False)

    job_role = relationship("JobRole", back_populates="requirements")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default="applied") # applied, shortlisted, in_rounds, selected, rejected
    is_eligible = Column(Boolean, default=True)
    ineligibility_reason = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)

    job_role = relationship("JobRole", back_populates="applications")
    student = relationship("Student", back_populates="applications")
    rounds = relationship("PlacementRound", back_populates="application", cascade="all, delete-orphan")

class PlacementRound(Base):
    __tablename__ = "placement_rounds"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    round_name = Column(String(80), nullable=False)
    round_order = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default="pending") # pending, cleared, failed
    score = Column(Numeric(5, 2), nullable=True)
    feedback = Column(Text, nullable=True)
    conducted_at = Column(DateTime, nullable=True)

    application = relationship("Application", back_populates="rounds")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)
    extracted_raw_text = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="resumes")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")

class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(80), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    is_verified_by_student = Column(Boolean, default=False)

    resume = relationship("Resume", back_populates="skills")

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    interview_type = Column(String(30), nullable=False) # technical, hr, behavioral, communication
    overall_score = Column(Numeric(5, 2), default=0.00)
    technical_score = Column(Numeric(5, 2), default=0.00)
    communication_score = Column(Numeric(5, 2), default=0.00)
    integrity_score = Column(Numeric(5, 2), default=100.00)
    status = Column(String(20), default="scheduled") # scheduled, in_progress, completed, cancelled
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="interviews")
    job_role = relationship("JobRole", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")
    vision_metrics = relationship("VisionAnalysis", back_populates="interview", uselist=False, cascade="all, delete-orphan")
    integrity_events = relationship("InterviewEvent", back_populates="interview", cascade="all, delete-orphan")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    topic = Column(String(80), nullable=False)
    difficulty = Column(String(20), default="medium")
    expected_concepts = Column(JSON, nullable=False, default=list)
    ideal_answer_summary = Column(Text, nullable=True)
    is_resume_derived = Column(Boolean, default=False)
    source_resume_keyword = Column(String(100), nullable=True)
    order_index = Column(Integer, nullable=False)

    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), unique=True, nullable=False)
    transcribed_text = Column(Text, nullable=True)
    audio_file_path = Column(String(255), nullable=True)
    semantic_similarity = Column(Numeric(5, 2), default=0.00)
    concept_coverage_pct = Column(Numeric(5, 2), default=0.00)
    relevance_score = Column(Numeric(5, 2), default=0.00)
    technical_score = Column(Numeric(5, 2), default=0.00)
    concepts_covered = Column(JSON, default=list)
    concepts_missing = Column(JSON, default=list)
    feedback = Column(Text, nullable=True)
    answered_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("InterviewQuestion", back_populates="answer")
    speech_analysis = relationship("SpeechAnalysis", back_populates="answer", uselist=False, cascade="all, delete-orphan")

class SpeechAnalysis(Base):
    __tablename__ = "speech_analysis"
    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("interview_answers.id", ondelete="CASCADE"), unique=True, nullable=False)
    duration_seconds = Column(Numeric(6, 2), default=0.00)
    words_per_minute = Column(Numeric(6, 2), default=0.00)
    filler_word_count = Column(Integer, default=0)
    filler_words_detected = Column(JSON, default=dict)
    pause_duration_seconds = Column(Numeric(6, 2), default=0.00)
    fluency_rating = Column(String(50), default="Normal")

    answer = relationship("InterviewAnswer", back_populates="speech_analysis")

class VisionAnalysis(Base):
    __tablename__ = "vision_analysis"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), unique=True, nullable=False)
    face_visibility_pct = Column(Numeric(5, 2), default=100.00)
    stable_head_orientation_pct = Column(Numeric(5, 2), default=100.00)
    posture_stability_pct = Column(Numeric(5, 2), default=100.00)
    out_of_frame_events_count = Column(Integer, default=0)
    multiple_persons_events_count = Column(Integer, default=0)
    phone_detected_events_count = Column(Integer, default=0)

    interview = relationship("Interview", back_populates="vision_metrics")

class InterviewEvent(Base):
    __tablename__ = "interview_events"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    timestamp_offset_seconds = Column(Numeric(8, 2), nullable=False)
    event_type = Column(String(80), nullable=False) # candidate_out_of_frame, multiple_persons, phone_detected, candidate_present
    confidence = Column(Numeric(4, 2), default=0.00)
    details = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    interview = relationship("Interview", back_populates="integrity_events")

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    attendance_pct = Column(Numeric(5, 2), default=0.00)
    aptitude_score = Column(Numeric(5, 2), default=0.00)
    technical_test_score = Column(Numeric(5, 2), default=0.00)
    coding_score = Column(Numeric(5, 2), default=0.00)
    interview_avg_score = Column(Numeric(5, 2), default=0.00)
    communication_score = Column(Numeric(5, 2), default=0.00)
    overall_score = Column(Numeric(5, 2), default=0.00)
    support_recommended = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="performance")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    priority = Column(Integer, default=1)
    title = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False)
    reason = Column(Text, nullable=False)
    actionable_steps = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="recommendations")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentChatMessage(Base):
    __tablename__ = "student_chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    role = Column(String(20), nullable=False)  # 'user' or 'model'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

