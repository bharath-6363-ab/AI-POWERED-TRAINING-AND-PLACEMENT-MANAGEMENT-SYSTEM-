# PROJECT ARCHITECTURE

## AI-Powered Training & Placement Management System with Intelligent Student Performance, Personalized Interview Analytics and Placement Support

---

## 1. System Overview

The **AI-Powered Training & Placement Management System (AITPMS)** is an enterprise-grade academic major project designed to digitize and intelligently automate the training, mock assessment, placement tracking, and AI-assisted interview preparation lifecycle for higher education institutions.

The platform bridges institutional operational management (batches, attendance, courses, tests, placement drives) with **explainable, multi-modal AI subsystems** (Resume parsing, NLP answer evaluation, acoustic/speech fluency metrics, computer-vision interview integrity & non-verbal signal analytics, and weak-area training recommendation engines).

---

## 2. High-Level Architecture Diagram

`
+-----------------------------------------------------------------------------------+
|               Client Presentation Layer (Responsive Web / Modern UI)              |
|  - Admin Portal (Batches, Companies, Placement Drives, Analytics)                |
|  - Trainer Portal (Attendance, Tests, Reviews, Student Recommendations)          |
|  - Student Workspace (Profile, Resume, Practice Tests, AI Mock Interview, Reports)|
|  - Real-time Hardware APIs (Webcam Canvas Stream, Microphone MediaRecorder)       |
+-----------------------------------------+-----------------------------------------+
                                          | HTTPS / REST / WebSockets / Multi-part
                                          v
+-----------------------------------------------------------------------------------+
|               API Gateway & Application Server (FastAPI / Starlette)              |
|  - Auth & RBAC Middleware (JWT Bearer, Argon2/Bcrypt, Role-Guarded Dependencies)  |
|  - Pydantic v2 Request/Response Schemas (Strict Serialization & Input Validation) |
|  - Modular REST Endpoints (/auth, /students, /attendance, /tests, /interviews...) |
+-----------------------------------------+-----------------------------------------+
                                          |
        +---------------------------------+---------------------------------+
        v                                                                   v
+-----------------------------------+             +-----------------------------------+
|     Business Logic Services       |             |   Explainable AI & ML Pipeline    |
| - Student & Batch Service         | <---------> | - Resume Intelligence Engine      |
| - Attendance Tracking Service     |             | - NLP Answer Evaluation Service   |
| - Mock Test & Assessment Service  |             | - Speech & Fluency Analyzer       |
| - Company & Job Placement Engine  |             | - Computer Vision Pipeline        |
| - Eligibility Calculation Engine  |             | - Training Recommendation Engine  |
| - PDF Report Generation Service   |             | - Offline/Rule Fallback Engine    |
+-----------------+-----------------+             +-----------------+-----------------+
                  |                                                 |
                  +-----------------------+-------------------------+
                                          v
+-----------------------------------------------------------------------------------+
|                         Persistence & Storage Layer                               |
|  - SQLAlchemy 2.0 ORM Engine (Connection Pooling, Declarative Mapped Models)     |
|  - MySQL 8+ Normalized Relational Database (Strict FKs, B-Tree Indexes)           |
|  - SQLite Fallback Mode (Configurable via ENV for instant offline demonstrations)  |
|  - File System Storage (Secure PDF Storage, Uploaded Resumes, Rendered Reports)   |
+-----------------------------------------------------------------------------------+
`

---

## 3. Modular Architecture Breakdown

### 3.1 Frontend Architecture
* **Technology**: Modern Responsive Web Dashboard (HTML5, Tailwind CSS, Modern ES Modules, Chart.js for multi-axis performance trend visualization).
* **Media Capture Subsystem**:
  * 
avigator.mediaDevices.getUserMedia: Dual-stream capture for audio and video.
  * Real-time Canvas frame sampling for lightweight client-side or backend frame analysis.
  * MediaRecorder API for capturing speech audio chunks (WAV/WebM) with instant client feedback.
* **State & Communication**:
  * Centralized API client (etch/xios) with JWT Bearer auto-injection and refresh interceptors.
  * Role-based UI view switching (dmin, 	rainer, student).

### 3.2 Backend Application Layer (FastAPI)
* **Framework**: FastAPI (Asynchronous, high-throughput ASGI architecture with Starlette and Uvicorn).
* **Security & Auth**:
  * Password hashing via crypt / passlib.
  * Access Tokens with JWT (HS256, configurable expiry).
  * Dependency-injected role verification (get_current_active_user, equire_role(["admin", "trainer"])).
* **Request & Response Integrity**: Pydantic v2 schemas with comprehensive field validation, sanitization, and OpenAPI/Swagger automatic documentation.

### 3.3 Relational Database Layer
* **ORM**: SQLAlchemy 2.0 with type-annotated Declarative Base (Mapped[...]).
* **Database Target**: MySQL 8.0+ (InnoDB engine, UTF8MB4 charset, strict foreign key enforcement, transactional integrity).
* **Portability**: Database connection string abstraction allows zero-code fallback to SQLite for local self-contained viva demonstrations when MySQL daemon is unconfigured.

---

## 4. Explainable AI Pipelines

Every AI feature strictly adheres to:
\text{Input} \longrightarrow \text{Processing} \longrightarrow \text{Explainable Metrics} \longrightarrow \text{Stored Result} \longrightarrow \text{Demonstrable UI}

1. **Resume Intelligence Engine**:
   - Input: Candidate PDF Resume.
   - Processing: PyPDF/pdfplumber text extraction -> Rule & NER skill recognition -> Section classification.
   - Output: Structured JSON candidate skills, projects, degrees, certifications.
   - User Editable: Candidate reviews and validates extracted profile before saving.

2. **NLP Answer Evaluator**:
   - Input: Candidate transcribed answer, question context, expected concept keywords.
   - Processing: Tokenization, Keyword/Concept Coverage ratio, Semantic Cosine Similarity (SentenceTransformer or TF-IDF/Spacy/Cosine fallback), Answer Length/Completeness weighting.
   - Output: Technical Score (0-100), Identified concepts, Missing concepts, Constructive feedback.

3. **Speech & Fluency Analyzer**:
   - Input: Audio answer recording (WAV/WebM).
   - Processing: Speech-to-text (Whisper/Vosk/SpeechRecognition/WebSpeech), pause length analysis, Words-Per-Minute (WPM), and filler word counts (um, uh, like, basically).
   - Output: Speech rate metric, filler frequency, clarity rating (observable acoustic signals only).

4. **Computer Vision & Integrity Analyzer**:
   - Input: Periodic webcam frames during interview.
   - Processing: YOLO object detection (person, mobile phone, laptop), MediaPipe Face Mesh & Pose landmarks (head pitch/yaw/roll stability, face presence ratio).
   - Output: Timestamped "Interview Integrity Events" (Candidate out of frame, Multiple persons detected, Stable posture %). Zero psychological or emotion claims.

5. **Weakness-Driven Training Recommendation Engine**:
   - Input: Aggregated scores across attendance, aptitude tests, technical MCQs, coding rounds, and interview scores.
   - Processing: Weighted multi-criteria analysis flagging topics falling below institutional thresholds (< 65%).
   - Output: Prioritized action items (Priority 1: SQL Practice, Priority 2: Technical Communication).

---

## 5. Security & Data Protection

1. **Least Privilege Principle**: Strict Role-Based Access Control (RBAC) enforced at router dependency level.
2. **Input Sanitization**: File uploads restricted by MIME type (pplication/pdf for resumes, bounded sizes), directory traversal protection using strict path resolution.
3. **Environment-driven Secrets**: Zero hardcoded credentials; all database passwords, token secrets, and environment profiles are isolated in .env.
4. **AI Ethics & Auditability**:
   - Zero psychological pseudo-science claims (no "dishonesty detection" or "emotion recognition").
   - Explicitly framed as **Observable Integrity & Fluency Indicators**.
   - Immutable audit logging for grade updates, test attempts, and drive decisions.
