from datetime import date, datetime
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.core.security import get_password_hash
from backend.app.models.all_models import (
    Role, User, Student, Trainer, Course, Batch, BatchStudent, Attendance,
    Company, JobRole, JobRequirement, Test, Question, PerformanceMetric,
    Recommendation, ResumeSkill
)

def seed_demo_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Roles
    roles = {}
    for r_name in ["admin", "trainer", "student"]:
        role = db.query(Role).filter(Role.name == r_name).first()
        if not role:
            role = Role(name=r_name, description=f"{r_name.capitalize()} Role")
            db.add(role)
            db.commit()
            db.refresh(role)
        roles[r_name] = role

    # 2. Admin User
    admin_user = db.query(User).filter(User.email == "admin@college.edu").first()
    if not admin_user:
        admin_user = User(
            email="admin@college.edu",
            hashed_password=get_password_hash("Admin@123"),
            full_name="Placement Director Dr. Sharma",
            role_id=roles["admin"].id
        )
        db.add(admin_user)
        db.commit()

    # 3. Trainer User
    trainer_user = db.query(User).filter(User.email == "trainer@college.edu").first()
    if not trainer_user:
        trainer_user = User(
            email="trainer@college.edu",
            hashed_password=get_password_hash("Trainer@123"),
            full_name="Prof. Rajesh Verma",
            role_id=roles["trainer"].id
        )
        db.add(trainer_user)
        db.commit()
        db.refresh(trainer_user)

        trainer = Trainer(
            user_id=trainer_user.id,
            employee_id="EMP-T101",
            specialization="Full-Stack & Cloud Architecture",
            department="Computer Science & Engineering"
        )
        db.add(trainer)
        db.commit()

    trainer = db.query(Trainer).first()

    # 4. Courses & Batches
    course = db.query(Course).filter(Course.course_code == "CS-401").first()
    if not course:
        course = Course(
            title="Advanced Enterprise Software Engineering",
            course_code="CS-401",
            description="Full-stack development, distributed databases, REST APIs & placement interview preparation"
        )
        db.add(course)
        db.commit()
        db.refresh(course)

    batch = db.query(Batch).filter(Batch.name == "Batch 2026 Alpha").first()
    if not batch:
        batch = Batch(
            name="Batch 2026 Alpha",
            course_id=course.id,
            trainer_id=trainer.id,
            start_date=date(2026, 1, 10),
            is_active=True
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)

    # 5. Demo Students (Aditi Rao, Rohan Mehta, Sneha Patil)
    students_demo = [
        {"name": "Aditi Rao", "email": "aditi.rao@student.edu", "roll": "2026-CSE-001", "cgpa": 8.75, "skills": ["Python", "FastAPI", "SQL", "React", "Docker"]},
        {"name": "Rohan Mehta", "email": "rohan.mehta@student.edu", "roll": "2026-CSE-002", "cgpa": 6.80, "skills": ["Java", "Spring Boot", "MySQL"]},
        {"name": "Sneha Patil", "email": "sneha.patil@student.edu", "roll": "2026-CSE-003", "cgpa": 9.10, "skills": ["Python", "Machine Learning", "Pandas", "SQL", "PyTorch"]}
    ]

    for s_info in students_demo:
        u = db.query(User).filter(User.email == s_info["email"]).first()
        if not u:
            u = User(
                email=s_info["email"],
                hashed_password=get_password_hash("Student@123"),
                full_name=s_info["name"],
                phone="+91 9876543210",
                role_id=roles["student"].id
            )
            db.add(u)
            db.commit()
            db.refresh(u)

            stud = Student(
                user_id=u.id,
                roll_number=s_info["roll"],
                college="University Institute of Technology",
                branch="Computer Science & Engineering",
                semester=7,
                cgpa=s_info["cgpa"]
            )
            db.add(stud)
            db.commit()
            db.refresh(stud)

            # Enroll in batch
            enroll = BatchStudent(batch_id=batch.id, student_id=stud.id)
            db.add(enroll)

            # Performance metric
            perf = PerformanceMetric(
                student_id=stud.id,
                attendance_pct=88.5 if s_info["cgpa"] > 7.0 else 68.0,
                aptitude_score=82.0 if s_info["cgpa"] > 7.0 else 55.0,
                technical_test_score=85.0 if s_info["cgpa"] > 7.0 else 58.0,
                interview_avg_score=78.0 if s_info["cgpa"] > 7.0 else 54.0,
                overall_score=83.5 if s_info["cgpa"] > 7.0 else 59.2,
                support_recommended=(s_info["cgpa"] < 7.0)
            )
            db.add(perf)

            # Skills
            for sk in s_info["skills"]:
                r_sk = ResumeSkill(
                    resume_id=1,
                    student_id=stud.id,
                    skill_name=sk,
                    category="Technical",
                    is_verified_by_student=True
                )
                db.add(r_sk)

            db.commit()

    # 6. Corporate Placement Companies & Jobs
    companies_data = [
        {"name": "Cognitive Cloud Tech", "role": "Python Cloud Backend Engineer", "salary": 14.5, "skills": ["Python", "FastAPI", "SQL", "Docker"], "min_cgpa": 7.5, "min_att": 75.0},
        {"name": "FinTech Innovations Global", "role": "Associate Software Engineer", "salary": 9.0, "skills": ["Java", "SQL", "Git"], "min_cgpa": 6.5, "min_att": 70.0}
    ]

    for c_data in companies_data:
        comp = db.query(Company).filter(Company.name == c_data["name"]).first()
        if not comp:
            comp = Company(
                name=c_data["name"],
                website="https://" + c_data["name"].lower().replace(" ", "") + ".com",
                industry="Information Technology",
                location="Bengaluru / Hyderabad"
            )
            db.add(comp)
            db.commit()
            db.refresh(comp)

            job = JobRole(
                company_id=comp.id,
                title=c_data["role"],
                description=f"Design, develop and scale enterprise cloud solutions using {', '.join(c_data['skills'])}.",
                salary_lpa=c_data["salary"],
                location="Bengaluru"
            )
            db.add(job)
            db.commit()
            db.refresh(job)

            req = JobRequirement(
                job_role_id=job.id,
                min_cgpa=c_data["min_cgpa"],
                min_attendance_pct=c_data["min_att"],
                required_skills=c_data["skills"],
                eligible_branches=["Computer Science & Engineering", "Information Technology"]
            )
            db.add(req)
            db.commit()

    # 7. Standard Assessments (Aptitude & Technical)
    test = db.query(Test).filter(Test.title == "Technical Core Assessment: Python & SQL").first()
    if not test:
        test = Test(
            title="Technical Core Assessment: Python & SQL",
            test_type="technical_mcq",
            category="Python & Relational DB",
            duration_minutes=25,
            total_marks=3,
            pass_percentage=60.00,
            created_by=admin_user.id
        )
        db.add(test)
        db.commit()
        db.refresh(test)

        questions = [
            Question(
                test_id=test.id,
                question_text="What is the primary difference between a list and a tuple in Python?",
                option_a="Lists are immutable, tuples are mutable",
                option_b="Lists are mutable, tuples are immutable",
                option_c="Tuples can only store integers",
                option_d="Lists have higher memory efficiency than tuples",
                correct_option="B",
                explanation="Tuples are immutable sequences in Python, whereas lists are dynamic arrays.",
                topic="Python",
                marks=1
            ),
            Question(
                test_id=test.id,
                question_text="Which index type in MySQL 8 InnoDB determines the physical on-disk storage order of records?",
                option_a="Secondary Index",
                option_b="Full-Text Index",
                option_c="Clustered Index",
                option_d="Hash Index",
                correct_option="C",
                explanation="In InnoDB, the primary key clustered index defines the physical order of table rows.",
                topic="SQL",
                marks=1
            ),
            Question(
                test_id=test.id,
                question_text="In REST API design, which HTTP method is non-idempotent by specification?",
                option_a="GET",
                option_b="PUT",
                option_c="DELETE",
                option_d="POST",
                correct_option="D",
                explanation="POST creates new subordinate resources upon each invocation, hence it is non-idempotent.",
                topic="REST API",
                marks=1
            )
        ]
        for q in questions:
            db.add(q)
        db.commit()

    db.close()
    print("Demo dataset seeded successfully!")

if __name__ == "__main__":
    seed_demo_data()
