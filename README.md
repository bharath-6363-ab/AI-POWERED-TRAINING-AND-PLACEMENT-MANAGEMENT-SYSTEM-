# AI-Powered Training & Placement Management System (AITPMS)

A comprehensive, production-quality academic major project integrating institutional training and placement management with explainable, multi-modal Artificial Intelligence subsystems.

---

## 1. System Overview & Core Capabilities
1. **Academic & Operational Management**:
   - Role-Based Access Control (dmin, 	rainer, student).
   - Batches, Courses, and Attendance tracking with real-time percentage recalculation.
   - Standardized assessments (Aptitude, Technical MCQs, Coding).
   - Placement drives, job roles, and corporate requirements.
2. **Deterministic Placement Eligibility Engine**:
   - Compares student CGPA, attendance %, and verified resume skills against job criteria.
   - Provides transparent, explainable pass/fail reasons without black-box opacity.
3. **Resume Intelligence Subsystem**:
   - PDF document extraction and section classification (Education, Projects, Experience).
   - Taxonomy-grounded skill extraction with candidate verification interface.
4. **AI Mock Interview Engine (Vision, Voice & NLP)**:
   - Dynamic question generation linked directly to the candidate's resume keywords.
   - NLP Technical answer evaluation (concept coverage, semantic cosine similarity, relevance bounds).
   - Acoustic speech fluency analysis (WPM, pause durations, filler word frequencies).
   - Computer Vision integrity monitoring (YOLO person/device detection & MediaPipe posture/face tracking).
5. **Personalized Training Recommendation Engine**:
   - Continuous weak-area identification (<65% benchmarks) producing prioritized action items.
   - Early intervention flagging (Training Support Recommended) for mentors.
6. **Report Generation & Research Dossier**:
   - Automated institutional PDF generation using ReportLab.

---

## 2. Technology Stack
* **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic v2, PyJWT, Bcrypt.
* **Database**: MySQL 8.0+ / SQLite3 (automatic zero-config fallback mode).
* **AI / ML**: Scikit-learn (TF-IDF & Cosine Similarity), PyPDF, Ultralytics YOLOv8, MediaPipe, OpenCV.
* **Reporting**: ReportLab PDF Engine.
* **Frontend**: Responsive modern dashboard (HTML5, Tailwind CSS, Lucide Icons, Chart.js).

---

## 3. Quickstart & Demonstration Instructions

### Prerequisites
* Python 3.10+ (Tested on Python 3.13)
* Dependencies in equirements.txt

### Step 1: Run Seed Data
`ash
python -m backend.app.utils.seed_data
`
* Seeds 3 sample students (Aditi Rao, Rohan Mehta, Sneha Patil), 2 companies, job roles with requirements, and assessment questions.

### Step 2: Run Automated Test Suite
`ash
python -m pytest backend/tests/test_core_system.py
`
* Executes 9 automated tests covering authentication, eligibility logic, NLP evaluation, speech analysis, and database integrity.

### Step 3: Start the Backend & Portal
`ash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
`
* **Swagger/OpenAPI Documentation**: http://127.0.0.1:8000/docs
* **Interactive Web Portal**: http://127.0.0.1:8000/static/index.html
* **Institutional PDF Dossier**: http://127.0.0.1:8000/api/v1/reports/student/1/download

---

## 4. Default Seeded Credentials
| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | dmin@college.edu | Admin@123 |
| **Trainer** | 	rainer@college.edu | Trainer@123 |
| **Student** | diti.rao@student.edu | Student@123 |
| **Student** | ohan.mehta@student.edu | Student@123 |
