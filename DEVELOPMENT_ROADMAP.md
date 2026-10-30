# DEVELOPMENT ROADMAP

## AI-Powered Training & Placement Management System (AITPMS)

---

## Roadmap Overview

This roadmap details the 8 phases of execution, their exact module dependencies, and verification criteria. Work strictly proceeds phase-by-phase.

`
PHASE 1 (Core System, DB, RBAC, Student/Trainer/Batch)
   ↓
PHASE 2 (Attendance, Tests, Companies, Jobs, Eligibility, Placement Tracking)
   ↓
PHASE 3 (Resume Intelligence Engine & Skills Extraction)
   ↓
PHASE 4 (AI Question Generation & NLP Answer Evaluation)
   ↓
PHASE 5 (Speech-to-Text & Acoustic Fluency Metrics)
   ↓
PHASE 6 (Computer Vision: YOLO Object Detection & MediaPipe Integrity Tracking)
   ↓
PHASE 7 (Performance Engine, Analytics & Personalized Recommendations)
   ↓
PHASE 8 (PDF Report Generator, Demo Mode, Security Hardening & Documentation)
`

---

## Phase Details

### Phase 1: Core Foundation & Entity Management
- **Components**:
  - FastAPI app skeleton, config, logging, exception handlers.
  - SQLAlchemy models for Users, Roles, Students, Trainers, Courses, Batches.
  - JWT Bearer Authentication & Role-Based Access Control (dmin, 	rainer, student).
  - Student & Trainer registration and CRUD operations.
- **Dependencies**: Python 3.13, FastAPI, SQLAlchemy, Pydantic v2, python-jose/PyJWT, passlib/bcrypt.
- **Testing Requirements**:
  - Pytest unit tests for password hashing and token generation.
  - Test login and role-restricted endpoints.
  - Test student profile retrieval and updates.

### Phase 2: Academic Operations & Placement Engine
- **Components**:
  - Attendance marking and calculation system (% calculation per batch/student).
  - Mock test builder (MCQs, topics, marks, automated scoring upon submission).
  - Companies, Job Roles, and Requirements (CGPA, Attendance %, required skills).
  - **Deterministic Eligibility Engine**: Evaluates a student against a job role and returns exact pass/fail reasons (e.g., "Attendance = 68%, Required = 75%").
  - Placement pipeline tracking (Applied -> Shortlisted -> Rounds -> Selected).
- **Dependencies**: Phase 1 completed.
- **Testing Requirements**:
  - Eligibility calculation tests for boundary conditions (equal, above, below CGPA/attendance).
  - Test attempt submission and automatic score computation.

### Phase 3: Resume Intelligence & Skill Parser
- **Components**:
  - PDF document upload with MIME validation & security hashing.
  - PDF text extraction (PyPDF / pdfplumber fallback).
  - Section classifier (Education, Skills, Experience, Projects).
  - Taxonomy-driven skill extractor and normalizer (Languages, Frameworks, DBs).
  - UI for student validation and manual correction of extracted data.
- **Dependencies**: Phase 1, Phase 2.
- **Testing Requirements**:
  - Unit tests parsing sample student PDF resumes.
  - Verify skills normalization against controlled taxonomy.

### Phase 4: AI Question Generation & NLP Answer Evaluator
- **Components**:
  - AI Question Generator (Role + Skill + Resume-derived questions).
  - Fallback local question bank (100+ curated technical and behavioral questions).
  - NLP Answer Evaluator:
    - Expected Concept / Keyword coverage calculator.
    - Semantic similarity (SentenceTransformers with TF-IDF/Spacy/Cosine fallback).
    - Technical Score formulation (.4 \times \text{Concepts} + 0.4 \times \text{Similarity} + 0.2 \times \text{Relevance}$).
- **Dependencies**: Phase 3.
- **Testing Requirements**:
  - Answer evaluation test cases with known model answers and varying candidate responses.
  - Verification that system operates smoothly with zero external internet/APIs via local fallback.

### Phase 5: Speech & Acoustic Fluency Analysis
- **Components**:
  - Audio upload handling (WAV/WebM blobs from browser MediaRecorder).
  - Speech-to-Text transcription (Whisper/SpeechRecognition with WebSpeech fallback).
  - Measurable speech metrics: Duration, Words Per Minute (WPM), Filler word count (um, uh, like, asically), Pause durations.
  - Purely observable metrics — zero pseudo-scientific psychological claims.
- **Dependencies**: Phase 4.
- **Testing Requirements**:
  - Mock audio file transcript and WPM calculation tests.

### Phase 6: Computer Vision & Integrity Monitoring
- **Components**:
  - Video frame processing endpoint.
  - YOLO object/person detector (Person count, mobile phone presence, book/laptop).
  - MediaPipe Face Mesh & Pose tracking (Head pitch/yaw/roll posture stability, face visibility %).
  - Observable "Interview Integrity Events" logger (Timestamped event timeline).
- **Dependencies**: Phase 4, Phase 5.
- **Testing Requirements**:
  - Test frames with single person, multiple persons, out-of-frame condition.
  - Verify graceful fallback if camera or OpenCV/YOLO weights are not loaded.

### Phase 7: Performance Engine & Recommendations
- **Components**:
  - Multi-factor student performance calculator with customizable weights.
  - Weakness identifier ($<65\%$ thresholding on specific subjects or communication).
  - Prioritized Training Recommendation generator with clear justifications.
  - Early-intervention "Training Support Recommended" flag.
  - Time-series performance trend aggregations.
- **Dependencies**: Phase 2 through Phase 6.
- **Testing Requirements**:
  - Comprehensive performance engine tests across diverse student profiles.

### Phase 8: PDF Reports, Admin Analytics, Demo Mode & Documentation
- **Components**:
  - Institutional PDF report generator (ReportLab) featuring student profile, breakdown, integrity timeline, and recommendations.
  - Admin Analytics Dashboard (charts, KPIs, placement funnel, batch comparisons).
  - One-click **Demo Mode Seeder** (populates 20 students, 3 batches, 5 companies, 10 jobs, 50 questions, mock attempts).
  - Complete README, OpenAPI specs, and viva presentation documentation.
- **Dependencies**: All prior phases.
- **Testing Requirements**:
  - End-to-end integration test of the entire workflow.
