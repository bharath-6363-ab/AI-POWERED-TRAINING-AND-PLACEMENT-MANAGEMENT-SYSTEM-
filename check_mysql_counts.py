"""
AI-TPMS Database Counts Inspector
Queries active database tables and prints verified entity counts.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.core.database import SessionLocal, engine
from backend.app.models.all_models import (
    Role, User, Student, Trainer, Attendance,
    Batch, Resume, ResumeSkill,
    Company, JobRole, JobRequirement, Application, PlacementRound,
    Interview, VisionAnalysis, InterviewEvent,
    PerformanceMetric, Recommendation, StudentChatMessage
)

def check_counts():
    db = SessionLocal()
    print("=" * 65)
    print("           AI-TPMS DATABASE ENTITY COUNT VERIFICATION")
    print(f" Database Engine: {engine.url.drivername}")
    print(f" Database URL:    {engine.url}")
    print("=" * 65)

    tables = [
        ("System Roles", Role),
        ("Institutional Users", User),
        ("Registered Students", Student),
        ("Faculty Trainers", Trainer),
        ("Training Batches", Batch),
        ("Attendance Records", Attendance),
        ("Candidate Resumes", Resume),
        ("Parsed Resume Skills", ResumeSkill),
        ("Recruiting Companies", Company),
        ("Active Job Drives", JobRole),
        ("Gating Job Requirements", JobRequirement),
        ("Placement Applications", Application),
        ("Placement Rounds Progress", PlacementRound),
        ("Interview Sessions", Interview),
        ("Vision Proctoring Analyses", VisionAnalysis),
        ("Proctoring Integrity Events", InterviewEvent),
        ("Performance Metrics", PerformanceMetric),
        ("Intervention Recommendations", Recommendation),
        ("Student Chat Messages", StudentChatMessage)
    ]

    print(f"{'Table / Entity Name':<35} | {'Count':>12}")
    print("-" * 65)

    total_records = 0
    for name, model in tables:
        try:
            cnt = db.query(model).count()
            total_records += cnt
            print(f"{name:<35} | {cnt:>12}")
        except Exception as e:
            print(f"{name:<35} | {'ERROR':>12} ({e})")

    print("=" * 65)
    print(f"{'Total Verified Records':<35} | {total_records:>12}")
    print("=" * 65)
    db.close()

if __name__ == "__main__":
    check_counts()
