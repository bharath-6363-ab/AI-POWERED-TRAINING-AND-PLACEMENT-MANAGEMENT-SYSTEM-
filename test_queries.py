"""
AI-TPMS Query Execution Tester
Validates complex queries across students, eligibility, job drives, and proctoring.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.core.database import SessionLocal
from backend.app.models.all_models import Student, User, JobRole, Company, JobRequirement, InterviewEvent, StudentChatMessage

def run_query_tests():
    db = SessionLocal()
    print("=" * 70)
    print("             AI-TPMS COMPLEX QUERY VALIDATION")
    print("=" * 70)

    try:
        # 1. Query High Performer Students
        print("\n[Query 1] High-Performing Candidates (CGPA >= 8.0):")
        students = db.query(Student).join(User).filter(Student.cgpa >= 8.0).all()
        for s in students:
            print(f" - {s.user.full_name} | USN: {s.roll_number} | Branch: {s.branch} | CGPA: {s.cgpa}")

        # 2. Query Tier-1 Super Dream Drives (Salary >= 18 LPA)
        print("\n[Query 2] Tier-1 Super Dream Placement Drives (>= 18 LPA):")
        high_paying_jobs = db.query(JobRole).join(Company).filter(JobRole.salary_lpa >= 18.0).order_by(JobRole.salary_lpa.desc()).all()
        print(f" Total Found: {len(high_paying_jobs)}")
        for j in high_paying_jobs[:8]:
            print(f" - {j.company.name} | Role: {j.title} | CTC: {j.salary_lpa} LPA | Loc: {j.location}")

        # 3. Query Drives with strict 0 backlogs and high attendance
        print("\n[Query 3] Strict Gated Job Roles (0 Backlogs & >= 75% Attendance):")
        gated_jobs = db.query(JobRequirement).filter(
            JobRequirement.max_backlogs == 0,
            JobRequirement.min_attendance_pct >= 75.0
        ).count()
        print(f" Total Strictly Gated Roles: {gated_jobs}")

        # 4. Check Chat History & Proctoring Violations
        print("\n[Query 4] Recent System Activity Logs:")
        chats_count = db.query(StudentChatMessage).count()
        logs_count = db.query(InterviewEvent).count()
        print(f" - Stored Student Chat Messages: {chats_count}")
        print(f" - Stored Proctoring Integrity Events: {logs_count}")

        print("\n" + "=" * 70)
        print(" [SUCCESS] All database queries executed successfully without error.")
        print("=" * 70)

    except Exception as e:
        print(f"[ERROR] Query test failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_query_tests()
