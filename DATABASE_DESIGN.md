# DATABASE DESIGN & SCHEMA SPECIFICATION

## AI-Powered Training & Placement Management System (AITPMS)

---

## 1. Database Overview

* **Engine**: MySQL 8.0+ (InnoDB) / SQLite3 (Zero-setup local fallback)
* **Character Set**: utf8mb4
* **Collation**: utf8mb4_unicode_ci
* **Normalization**: 3rd Normal Form (3NF), minimizing redundancy while utilizing B-Tree indexing on all foreign keys and query search fields.

---

## 2. Entity Relationship Overview

`
[users] 1 --- 1 [roles]
   |
   +--- 1:1 --- [students] 1 --- M [attendance]
   |                |       1 --- M [test_attempts] 1 --- M [test_answers]
   |                |       1 --- M [resumes] 1 --- M [resume_skills]
   |                |       1 --- M [interviews] 1 --- M [interview_questions] 1 --- 1 [interview_answers]
   |                |       |                         1 --- M [speech_analysis]
   |                |       |                         1 --- M [vision_analysis]
   |                |       |                         1 --- M [interview_events]
   |                |       1 --- M [applications]
   |                |       1 --- M [performance_metrics]
   |                |       1 --- M [recommendations]
   |
   +--- 1:1 --- [trainers] 1 --- M [batches] 1 --- M [batch_students]
                                 1 --- M [courses]
                                 1 --- M [tests] 1 --- M [questions]

[companies] 1 --- M [job_roles] 1 --- M [job_requirements]
                        |
                        +--- 1 --- M [applications] 1 --- M [placement_rounds]
`

---

## 3. Detailed Relational Tables & Column Specifications

### 3.1 Authentication & RBAC

#### oles
* id: INT AUTO_INCREMENT PRIMARY KEY
* 
ame: VARCHAR(30) UNIQUE NOT NULL (dmin, 	rainer, student)
* description: VARCHAR(255) NULL
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### users
* id: INT AUTO_INCREMENT PRIMARY KEY
* ole_id: INT NOT NULL, FOREIGN KEY REFERENCES oles(id) ON DELETE RESTRICT
* email: VARCHAR(150) UNIQUE NOT NULL, INDEX idx_users_email
* hashed_password: VARCHAR(255) NOT NULL
* ull_name: VARCHAR(120) NOT NULL
* phone: VARCHAR(20) NULL
* is_active: BOOLEAN DEFAULT TRUE NOT NULL
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
* updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

---

### 3.2 Academic & Student Entities

#### students
* id: INT AUTO_INCREMENT PRIMARY KEY
* user_id: INT UNIQUE NOT NULL, FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE
* oll_number: VARCHAR(50) UNIQUE NOT NULL, INDEX idx_students_roll
* college: VARCHAR(150) NOT NULL
* ranch: VARCHAR(80) NOT NULL
* semester: INT NOT NULL
* cgpa: DECIMAL(4,2) NOT NULL DEFAULT 0.00
* github_url: VARCHAR(255) NULL
* linkedin_url: VARCHAR(255) NULL
* io: TEXT NULL
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
* updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

#### 	rainers
* id: INT AUTO_INCREMENT PRIMARY KEY
* user_id: INT UNIQUE NOT NULL, FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE
* employee_id: VARCHAR(50) UNIQUE NOT NULL
* specialization: VARCHAR(150) NOT NULL
* department: VARCHAR(100) NOT NULL
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### courses
* id: INT AUTO_INCREMENT PRIMARY KEY
* 	itle: VARCHAR(150) NOT NULL
* course_code: VARCHAR(50) UNIQUE NOT NULL
* description: TEXT NULL
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### atches
* id: INT AUTO_INCREMENT PRIMARY KEY
* 
ame: VARCHAR(100) NOT NULL
* course_id: INT NOT NULL, FOREIGN KEY REFERENCES courses(id) ON DELETE CASCADE
* 	rainer_id: INT NOT NULL, FOREIGN KEY REFERENCES 	rainers(id) ON DELETE CASCADE
* start_date: DATE NOT NULL
* end_date: DATE NULL
* is_active: BOOLEAN DEFAULT TRUE

#### atch_students
* id: INT AUTO_INCREMENT PRIMARY KEY
* atch_id: INT NOT NULL, FOREIGN KEY REFERENCES atches(id) ON DELETE CASCADE
* student_id: INT NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* UNIQUE KEY uq_batch_student (atch_id, student_id)

#### ttendance
* id: INT AUTO_INCREMENT PRIMARY KEY
* atch_id: INT NOT NULL, FOREIGN KEY REFERENCES atches(id) ON DELETE CASCADE
* student_id: INT NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* date: DATE NOT NULL
* status: ENUM('present', 'absent', 'late', 'excused') DEFAULT 'present' NOT NULL
* emarks: VARCHAR(255) NULL
* marked_by: INT NOT NULL, FOREIGN KEY REFERENCES users(id)
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
* INDEX idx_attendance_student_date (student_id, date)

---

### 3.3 Assessment & Mock Tests

#### 	ests
* id: INT AUTO_INCREMENT PRIMARY KEY
* 	itle: VARCHAR(150) NOT NULL
* 	est_type: ENUM('aptitude', 'technical_mcq', 'coding', 'custom') NOT NULL
* category: VARCHAR(80) NOT NULL (e.g. 'Python', 'SQL', 'Quantitative')
* duration_minutes: INT NOT NULL DEFAULT 30
* 	otal_marks: INT NOT NULL DEFAULT 100
* pass_percentage: DECIMAL(5,2) DEFAULT 60.00
* created_by: INT NOT NULL, FOREIGN KEY REFERENCES users(id)
* is_active: BOOLEAN DEFAULT TRUE
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### questions
* id: INT AUTO_INCREMENT PRIMARY KEY
* 	est_id: INT NOT NULL, FOREIGN KEY REFERENCES 	ests(id) ON DELETE CASCADE
* question_text: TEXT NOT NULL
* option_a: TEXT NOT NULL
* option_b: TEXT NOT NULL
* option_c: TEXT NOT NULL
* option_d: TEXT NOT NULL
* correct_option: ENUM('A', 'B', 'C', 'D') NOT NULL
* explanation: TEXT NULL
* difficulty: ENUM('easy', 'medium', 'hard') DEFAULT 'medium'
* 	opic: VARCHAR(80) NOT NULL
* marks: INT DEFAULT 1

#### 	est_attempts
* id: INT AUTO_INCREMENT PRIMARY KEY
* 	est_id: INT NOT NULL, FOREIGN KEY REFERENCES 	ests(id) ON DELETE CASCADE
* student_id: INT NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* start_time: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
* end_time: TIMESTAMP NULL
* score: DECIMAL(5,2) NOT NULL DEFAULT 0.00
* 	otal_possible: DECIMAL(5,2) NOT NULL DEFAULT 0.00
* percentage: DECIMAL(5,2) NOT NULL DEFAULT 0.00
* status: ENUM('in_progress', 'completed', 'timed_out') DEFAULT 'in_progress'

#### 	est_answers
* id: INT AUTO_INCREMENT PRIMARY KEY
* ttempt_id: INT NOT NULL, FOREIGN KEY REFERENCES 	est_attempts(id) ON DELETE CASCADE
* question_id: INT NOT NULL, FOREIGN KEY REFERENCES questions(id) ON DELETE CASCADE
* selected_option: ENUM('A', 'B', 'C', 'D') NULL
* is_correct: BOOLEAN NOT NULL DEFAULT FALSE

---

### 3.4 Corporate Drives, Jobs & Eligibility

#### companies
* id: INT AUTO_INCREMENT PRIMARY KEY
* 
ame: VARCHAR(150) NOT NULL
* website: VARCHAR(255) NULL
* industry: VARCHAR(100) NULL
* location: VARCHAR(100) NULL
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### job_roles
* id: INT AUTO_INCREMENT PRIMARY KEY
* company_id: INT NOT NULL, FOREIGN KEY REFERENCES companies(id) ON DELETE CASCADE
* 	itle: VARCHAR(120) NOT NULL (e.g. 'Software Engineer', 'Data Analyst')
* description: TEXT NOT NULL
* salary_lpa: DECIMAL(5,2) NULL
* location: VARCHAR(100) NULL
* is_open: BOOLEAN DEFAULT TRUE
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### job_requirements
* id: INT AUTO_INCREMENT PRIMARY KEY
* job_role_id: INT UNIQUE NOT NULL, FOREIGN KEY REFERENCES job_roles(id) ON DELETE CASCADE
* min_cgpa: DECIMAL(4,2) DEFAULT 6.00 NOT NULL
* min_attendance_pct: DECIMAL(5,2) DEFAULT 75.00 NOT NULL
* equired_skills: JSON NOT NULL (e.g. ["Python", "SQL", "FastAPI"])
* eligible_branches: JSON NOT NULL (e.g. ["CSE", "IT", "ECE"])
* max_backlogs: INT DEFAULT 0 NOT NULL

#### pplications
* id: INT AUTO_INCREMENT PRIMARY KEY
* job_role_id: INT NOT NULL, FOREIGN KEY REFERENCES job_roles(id) ON DELETE CASCADE
* student_id: INT NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* status: ENUM('applied', 'shortlisted', 'in_rounds', 'selected', 'rejected') DEFAULT 'applied'
* is_eligible: BOOLEAN NOT NULL DEFAULT TRUE
* ineligibility_reason: TEXT NULL
* pplied_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
* UNIQUE KEY uq_student_job (job_role_id, student_id)

#### placement_rounds
* id: INT AUTO_INCREMENT PRIMARY KEY
* pplication_id: INT NOT NULL, FOREIGN KEY REFERENCES pplications(id) ON DELETE CASCADE
* ound_name: VARCHAR(80) NOT NULL (e.g. 'Online Aptitude', 'Technical Round 1', 'HR')
* ound_order: INT NOT NULL DEFAULT 1
* status: ENUM('pending', 'cleared', 'failed') DEFAULT 'pending'
* score: DECIMAL(5,2) NULL
* eedback: TEXT NULL
* conducted_at: TIMESTAMP NULL

---

### 3.5 Resume Intelligence

#### esumes
* id: INT AUTO_INCREMENT PRIMARY KEY
* student_id: INT NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* ile_path: VARCHAR(255) NOT NULL
* ile_hash: VARCHAR(64) NOT NULL
* extracted_raw_text: LONGTEXT NULL
* parsed_json: JSON NOT NULL
* is_active: BOOLEAN DEFAULT TRUE
* uploaded_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### esume_skills
* id: INT AUTO_INCREMENT PRIMARY KEY
* esume_id: INT NOT NULL, FOREIGN KEY REFERENCES esumes(id) ON DELETE CASCADE
* student_id: INT NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* skill_name: VARCHAR(80) NOT NULL, INDEX idx_skill_name
* category: VARCHAR(50) NOT NULL (e.g. 'Language', 'Database', 'Framework')
* is_verified_by_student: BOOLEAN DEFAULT FALSE

---

### 3.6 AI Mock Interview, NLP, Speech & Vision

#### interviews
* id: INT AUTO_INCREMENT PRIMARY KEY
* student_id: INT NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* job_role_id: INT NULL, FOREIGN KEY REFERENCES job_roles(id) ON DELETE SET NULL
* 	itle: VARCHAR(150) NOT NULL
* interview_type: ENUM('technical', 'hr', 'behavioral', 'communication') NOT NULL
* overall_score: DECIMAL(5,2) DEFAULT 0.00
* 	echnical_score: DECIMAL(5,2) DEFAULT 0.00
* communication_score: DECIMAL(5,2) DEFAULT 0.00
* integrity_score: DECIMAL(5,2) DEFAULT 100.00
* status: ENUM('scheduled', 'in_progress', 'completed', 'cancelled') DEFAULT 'scheduled'
* started_at: TIMESTAMP NULL
* completed_at: TIMESTAMP NULL

#### interview_questions
* id: INT AUTO_INCREMENT PRIMARY KEY
* interview_id: INT NOT NULL, FOREIGN KEY REFERENCES interviews(id) ON DELETE CASCADE
* question_text: TEXT NOT NULL
* 	opic: VARCHAR(80) NOT NULL
* difficulty: ENUM('easy', 'medium', 'hard') DEFAULT 'medium'
* expected_concepts: JSON NOT NULL (e.g. ["indexing", "B-Tree", "query optimization"])
* ideal_answer_summary: TEXT NULL
* is_resume_derived: BOOLEAN DEFAULT FALSE
* source_resume_keyword: VARCHAR(100) NULL
* order_index: INT NOT NULL

#### interview_answers
* id: INT AUTO_INCREMENT PRIMARY KEY
* question_id: INT UNIQUE NOT NULL, FOREIGN KEY REFERENCES interview_questions(id) ON DELETE CASCADE
* 	ranscribed_text: TEXT NULL
* udio_file_path: VARCHAR(255) NULL
* semantic_similarity: DECIMAL(5,2) DEFAULT 0.00 (0-100)
* concept_coverage_pct: DECIMAL(5,2) DEFAULT 0.00 (0-100)
* elevance_score: DECIMAL(5,2) DEFAULT 0.00 (0-100)
* 	echnical_score: DECIMAL(5,2) DEFAULT 0.00 (0-100)
* concepts_covered: JSON NULL
* concepts_missing: JSON NULL
* eedback: TEXT NULL
* nswered_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### speech_analysis
* id: INT AUTO_INCREMENT PRIMARY KEY
* nswer_id: INT UNIQUE NOT NULL, FOREIGN KEY REFERENCES interview_answers(id) ON DELETE CASCADE
* duration_seconds: DECIMAL(6,2) NOT NULL DEFAULT 0.00
* words_per_minute: DECIMAL(6,2) NOT NULL DEFAULT 0.00
* iller_word_count: INT DEFAULT 0
* iller_words_detected: JSON NULL (e.g. {"um": 3, "uh": 1, "like": 4})
* pause_duration_seconds: DECIMAL(6,2) DEFAULT 0.00
* luency_rating: VARCHAR(50) DEFAULT 'Normal'

#### ision_analysis
* id: INT AUTO_INCREMENT PRIMARY KEY
* interview_id: INT NOT NULL, FOREIGN KEY REFERENCES interviews(id) ON DELETE CASCADE
* ace_visibility_pct: DECIMAL(5,2) DEFAULT 100.00
* stable_head_orientation_pct: DECIMAL(5,2) DEFAULT 100.00
* posture_stability_pct: DECIMAL(5,2) DEFAULT 100.00
* out_of_frame_events_count: INT DEFAULT 0
* multiple_persons_events_count: INT DEFAULT 0
* phone_detected_events_count: INT DEFAULT 0

#### interview_events
* id: INT AUTO_INCREMENT PRIMARY KEY
* interview_id: INT NOT NULL, FOREIGN KEY REFERENCES interviews(id) ON DELETE CASCADE
* 	imestamp_offset_seconds: DECIMAL(8,2) NOT NULL
* event_type: VARCHAR(80) NOT NULL (e.g. 'candidate_out_of_frame', 'multiple_persons', 'phone_detected', 'candidate_present')
* confidence: DECIMAL(4,2) NOT NULL DEFAULT 0.00
* details: VARCHAR(255) NULL
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
* INDEX idx_events_interview (interview_id, created_at)

---

### 3.7 Performance Analytics & Recommendations

#### performance_metrics
* id: INT AUTO_INCREMENT PRIMARY KEY
* student_id: INT UNIQUE NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* ttendance_pct: DECIMAL(5,2) DEFAULT 0.00
* ptitude_score: DECIMAL(5,2) DEFAULT 0.00
* 	echnical_test_score: DECIMAL(5,2) DEFAULT 0.00
* coding_score: DECIMAL(5,2) DEFAULT 0.00
* interview_avg_score: DECIMAL(5,2) DEFAULT 0.00
* communication_score: DECIMAL(5,2) DEFAULT 0.00
* overall_score: DECIMAL(5,2) DEFAULT 0.00
* support_recommended: BOOLEAN DEFAULT FALSE
* updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

#### ecommendations
* id: INT AUTO_INCREMENT PRIMARY KEY
* student_id: INT NOT NULL, FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
* priority: INT NOT NULL DEFAULT 1 (1=High, 2=Medium, 3=Low)
* 	itle: VARCHAR(150) NOT NULL
* category: VARCHAR(80) NOT NULL (e.g. 'SQL Practice', 'Verbal Fluency', 'Data Structures')
* eason: TEXT NOT NULL
* ctionable_steps: TEXT NOT NULL
* is_resolved: BOOLEAN DEFAULT FALSE
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### udit_logs
* id: INT AUTO_INCREMENT PRIMARY KEY
* user_id: INT NULL, FOREIGN KEY REFERENCES users(id) ON DELETE SET NULL
* ction: VARCHAR(100) NOT NULL
* entity_type: VARCHAR(80) NOT NULL
* entity_id: INT NULL
* details: JSON NULL
* ip_address: VARCHAR(45) NULL
* created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
