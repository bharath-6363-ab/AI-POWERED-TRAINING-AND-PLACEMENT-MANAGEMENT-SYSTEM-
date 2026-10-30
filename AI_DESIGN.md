# AI SUBSYSTEMS DESIGN & SPECIFICATION

## AI-Powered Training & Placement Management System (AITPMS)

---

## 1. AI Core Philosophy & Scientific Grounding

In compliance with IEEE ethics and academic engineering standards:
* **No Pseudo-Science**: We never claim to detect "honesty", "deception", "personality", or "psychological intent" from facial expressions or vocal pitch.
* **Observable Signals Only**: All metrics represent physical, observable acoustic or visual phenomena (e.g., face presence %, head orientation angle, filler word counts, words per minute).
* **Guaranteed Reliability**: Every AI pipeline implements a 3-tier fallback hierarchy:
  1. Primary Model (Sentence Transformers / YOLO / MediaPipe / Whisper)
  2. Lightweight Local Model (Spacy / TF-IDF / Haar Cascades / PocketSphinx)
  3. Deterministic Heuristic Fallback (Regex, Bag-of-Words, Local Question Bank)
* The system will **never crash or halt** due to missing model weights, missing GPU, or network disconnection.

---

## 2. Detailed Pipeline Specifications

### 2.1 Resume Intelligence Pipeline

`
[Resume PDF File]
       │
       ▼
[PDF Text & Layout Extractor] (pypdf / pdfplumber)
       │
       ▼
[Text Normalization & Cleansing] (Unicode, hyphenation, regex cleanup)
       │
       ▼
[Section Classifier] (Rule-based heading matching: Skills, Education, Experience, Projects)
       │
       ▼
[Taxonomy-Grounded Skill Extraction]
  ├── Programming Languages (Python, Java, C++, JS, TypeScript...)
  ├── Frameworks & Libraries (FastAPI, Django, React, Express, PyTorch...)
  ├── Databases & Cloud (MySQL, PostgreSQL, MongoDB, Docker, AWS...)
  └── Tools & Methodologies (Git, CI/CD, Agile, REST APIs...)
       │
       ▼
[Candidate Profile JSON] ──> [Student Verification & Correction UI]
`

### 2.2 NLP Answer Evaluation Pipeline

`
[Transcribed Answer]  +  [Question Reference & Expected Concept Keywords]
       │                                     │
       ├─────────────────────────────────────┤
       ▼                                     ▼
[Concept Coverage Engine]           [Semantic Similarity Engine]
  - Lemmatized Token Matching         - Embedding Generation (Sentence-Transformers / TF-IDF)
  - Synonyms & Acronym Expansion      - Cosine Similarity Calculation
       │                                     │
       ▼                                     ▼
Concept Coverage Score (0-100)      Semantic Similarity Score (0-100)
       │                                     │
       └──────────────────┬──────────────────┘
                          ▼
            [Completeness & Relevance Check]
              - Answer Length Bounds Check
              - Off-topic Penalty Detection
                          ▼
            [Explainable Feedback Synthesis]
              - Technical Score Formula:
                Score = 0.40 * ConceptCov + 0.40 * SemSim + 0.20 * Relevance
              - Concepts Covered: [List]
              - Concepts Missing: [List]
              - Constructive Suggestion
`

### 2.3 Speech & Acoustic Fluency Pipeline

`
[Audio Answer File (WAV/WebM)]
       │
       ▼
[Audio Duration & Silence Segments] (AudioSegment / wave)
       │
       ▼
[Speech-to-Text Engine] (Whisper / SpeechRecognition / WebSpeech API)
       │
       ▼
[Transcribed Text Stream]
       │
       ├──> Word Count & Words-Per-Minute (WPM)
       │      - Normal speaking rate: 120 - 160 WPM
       │      - Fast: > 175 WPM | Slow: < 100 WPM
       │
       ├──> Filler Word Detection (Regex Tokenizer)
       │      - Fillers: 'um', 'uh', 'er', 'ah', 'like', 'you know', 'basically', 'actually'
       │      - Metric: Fillers per 100 words
       │
       └──> Pause & Hesitation Analysis
              - Number of pauses > 2.0 seconds
`

### 2.4 Computer Vision & Interview Integrity Pipeline

`
[Webcam Video Stream / Periodic Keyframes (1-2 FPS)]
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
[YOLOv8 / MobileNet SSD Object Detector]  [MediaPipe Face & Pose Tracking]
  - Detects 'person' instances             - 468 Face Landmarks
  - Detects prohibited/distracting items    - Head Pose Estimation (Pitch, Yaw, Roll)
    (cell phone, second laptop/monitor)    - Face Presence & Bounding Box Center
       │                                         │
       └────────────────────┬────────────────────┘
                            ▼
              [Observable Integrity Event Engine]
                ├── Candidate Present: Normal
                ├── Candidate Out of Frame: > 3 sec absence
                ├── Multiple Persons: > 1 person bounding box
                ├── Distracting Device: Mobile phone detected
                └── Extreme Head Turn: Yaw angle > 35 degrees
                            ▼
              [Session Integrity Metrics]
                - Face Visibility: (Frames with face / Total frames) * 100%
                - Stable Head Orientation: (Frames facing screen / Total) * 100%
                - Logged Event Timeline with exact timestamps
`

### 2.5 Training Recommendation & Performance Engine

The performance engine computes weighted domain proficiencies:

\text{Overall Score} = w_a \cdot S_{\text{attendance}} + w_t \cdot S_{\text{aptitude}} + w_c \cdot S_{\text{technical}} + w_m \cdot S_{\text{communication}} + w_p \cdot S_{\text{coding}}

Default Institutional Weights:
*  = 0.15$ (Attendance)
*  = 0.20$ (Aptitude)
*  = 0.25$ (Technical MCQs)
*  = 0.20$ (Interview Communication & Fluency)
*  = 0.20$ (Coding / Problem Solving)

**Trigger Rules for Recommendations:**
* If {\text{technical}}(\text{Topic } X) < 65\% \implies \text{Priority 1 Recommendation: Focused Practice in Topic } X$.
* If  < 100 \text{ or Fillers} > 8 \implies \text{Priority 2 Recommendation: Verbal Fluency & Pacing Workshop}$.
* If {\text{attendance}} < 75\% \implies \text{Institutional Warning: Attendance Deficit Remediation}$.
* If $\text{Overall Score} < 60\% \implies \text{Flag "Training Support Recommended"}$ for faculty mentor dashboard.

---

## 3. Graceful Fallback Matrix

| AI Component | Primary Engine | Secondary Engine | Deterministic Fallback |
| :--- | :--- | :--- | :--- |
| **Resume Parser** | NLP / Section NER | PyPDF2 Regex Matcher | Controlled Skill Dictionary Matcher |
| **Question Gen** | Dynamic Role Engine | Skill-based Template Generator | Local Curated Question Bank (100+ items) |
| **Answer Eval** | Sentence-Transformers | Spacy / TF-IDF Vectorizer | Token-overlap & Keyword Coverage Ratio |
| **Speech STT** | OpenAI Whisper | Google Speech API | Client-side Web Speech API / Text Input |
| **Vision Detector** | YOLOv8n (Ultralytics) | OpenCV Haar Cascades | Browser Canvas Landmark Tracking |
| **Head Posture** | MediaPipe Face Mesh | OpenCV Dlib / Haar Face | Canvas Face Detection / User self-check |
