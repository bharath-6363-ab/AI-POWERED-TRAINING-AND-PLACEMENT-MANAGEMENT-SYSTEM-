import os
import re
import json
import httpx
from typing import Dict, List, Any, Optional

# ==============================================================================
# COMPREHENSIVE OFFLINE PLACEMENT KNOWLEDGE BASE (115+ KB EQUIVALENT)
# ==============================================================================
OFFLINE_KNOWLEDGE_BASE = {
    "registration_help": {
        "title": "Registration & Profile Onboarding Guide",
        "keywords": ["registration", "register", "registration help", "how to register", "apply", "profile", "onboard", "deadline", "documents", "upload resume"],
        "summary": "Complete walkthrough of the AI-TPMS registration, document verification, and placement drive application process.",
        "content": """
### 📝 Campus Placement Drive: Registration & Onboarding Guide

Welcome to the AI-TPMS Placement Registration guide. Follow these essential steps to ensure error-free registration:

#### 1. Profile Completion & Academic Verification:
- **CGPA & Transcripts**: Ensure your current aggregate CGPA and semester credits are accurately synchronized with the institutional database.
- **Attendance Compliance**: Verify your overall laboratory and lecture attendance is $\\ge 75\\%$. Candidates with $<75\\%$ attendance are blocked by autonomous gating rules.
- **Backlog Status**: Confirm that all previous backlogs are cleared. Most Tier-1 drives require zero active backlogs.

#### 2. Resume & ATS Screening:
- Navigate to the **Resume Intelligence & Selection Pipeline** tab.
- Upload your single-column PDF or paste your profile text.
- Verify that your core skills (e.g., *Python, C++, Java, SQL, React, Docker*) are recognized by the symbol-aware parser with an ATS score $\\ge 70\\%$.

#### 3. Drive Application:
- Head to the **Jobs & Eligibility** tab to view all **47 Active Placement Drives**.
- Eligible drives will show a green **'Apply & Unlock Pipeline'** button.
- Ineligible drives will explicitly display which criteria (CGPA cutoff, skills, or attendance) you need to remediate.
"""
    },
    "eligibility_criteria": {
        "title": "Campus Placement Eligibility & Cutoff Matrix",
        "keywords": ["eligibility", "eligibility criteria", "criteria", "cutoff", "cgpa cutoff", "backlog", "attendance criteria", "minimum", "am i eligible"],
        "summary": "Deterministic institutional and corporate eligibility thresholds across all 47 campus placement drives.",
        "content": """
### 🎯 Placement Eligibility & Cutoff Architecture

Placement eligibility in AI-TPMS is enforced deterministically across 4 key gating parameters:

#### 1. Academic CGPA Thresholds:
- **Tier-1 Super Dream (20+ LPA - Google, Microsoft, Amazon, Stripe)**: $\\ge 8.00$ CGPA.
- **Tier-1 Dream (12 to 20 LPA - Oracle, Cisco, Walmart, Atlassian)**: $\\ge 7.50$ CGPA.
- **Tier-2 Core & FinTech (7 to 12 LPA - JP Morgan, Deloitte, Bosch)**: $\\ge 7.00$ CGPA.
- **Foundation & IT Consulting (3.5 to 7 LPA - TCS, Infosys, Wipro)**: $\\ge 6.00$ or $6.50$ CGPA.

#### 2. Institutional Mandatory Regulations:
- **Attendance**: Minimum **75.0%** aggregate attendance across all semesters.
- **Active Backlogs**: **0 active backlogs** at the time of application. (Historical cleared backlogs are permitted by select firms).
- **Secondary & Higher Secondary**: Minimum 60% or 65% aggregate in 10th and 12th standard.

#### 3. Skill & Project Alignment:
- Each job role matches your parsed resume skills against required taxonomies (e.g., Python + SQL + Docker). A skill overlap of $\\ge 60\\%$ unlocks Round 1.
"""
    },
    "three_rounds_info": {
        "title": "3-Round Sequential Placement Pipeline Architecture",
        "keywords": ["3-round", "3-rounds", "3-rounds info", "three rounds", "pipeline", "sequential", "rounds", "aptitude round", "technical round", "mock round"],
        "summary": "Deep dive into the 3-Round Sequential Selection Pipeline: Aptitude -> Technical MCQ -> AI Mock Interview.",
        "content": """
### 🔄 3-Round Sequential Placement Pipeline

The AI-TPMS portal operates a strict sequential 3-round evaluation pipeline. Progression is strictly gated: you must qualify each round before the next round unlocks.

```
+---------------------+       +---------------------+       +---------------------+
|      ROUND 1        |       |      ROUND 2        |       |      ROUND 3        |
| Aptitude & Quant    | ----> | Technical Core MCQ  | ----> | AI Mock Interview   |
| Cutoff: >= 65%      |       | Cutoff: >= 70%      |       | Camera & Speech     |
+---------------------+       +---------------------+       +---------------------+
```

#### 📌 Round 1: Cognitive Aptitude & Logical Reasoning
- **Format**: 20 Timed MCQs covering Quantitative Math, Data Interpretation, and Logical Syllogisms.
- **Time Limit**: 20 Minutes (60 seconds per question).
- **Advancement Threshold**: Score $\\ge 65.0\\%$ required to unlock Round 2.

#### 📌 Round 2: Technical & Domain Assessment
- **Format**: 20 Advanced MCQs covering Core CS (DSA time complexity, DBMS ACID & indexing, Operating Systems paging, and OOPs SOLID principles).
- **Advancement Threshold**: Score $\\ge 70.0\\%$ required to unlock Round 3.

#### 📌 Round 3: Multi-Modal AI Mock Interview & Proctoring
- **Format**: Real-time video & audio interview answering situational and technical questions using the **STAR Method**.
- **Proctoring**: YOLOv8 computer vision detects unauthorized phones or multiple people; MediaPipe calculates 3D head pose and gaze deflection.
- **Speech Audio**: Analyzes Words-Per-Minute (target: 120-150 WPM), pause frequency, and filler words.
- **Advancement Threshold**: Composite score $\\ge 75.0\\%$ earns official Campus Placement Recommendation Certification.
"""
    },
    "placement_stress_and_anxiety": {
        "title": "Placement Stress & Anxiety: Proven Breathing & 24-Hour Prep",
        "keywords": ["stress", "anxiety", "placement stress", "nervous", "breathing", "panic", "fear", "calm", "24-hour prep", "confidence"],
        "summary": "Scientifically validated stress reduction protocols, breathing exercises, and the 24-hour pre-placement readiness routine.",
        "content": """
### 💖 Placement Stress & Anxiety: The 24-Hour Master Strategy

Placement seasons are high-stakes, but anxiety is manageable with deliberate psychological and physical protocols.

#### 1. Emergency Physiological Calming Techniques:
- **The Physiological Sigh (Fastest nervous system reset)**:
  - Take two deep inhales through your nose (one full inhale + one quick top-up sniff).
  - Slowly exhale completely through your mouth for 6 seconds.
  - Repeat 3 times to immediately lower heart rate and reduce cortisol.
- **4-7-8 Box Breathing**:
  - Inhale quietly through nose for 4 seconds.
  - Hold breath for 7 seconds.
  - Exhale audibly through mouth for 8 seconds.

#### 2. The 24-Hour Pre-Drive Countdown Plan:
- **T-24 Hours to T-12 Hours**: Review high-level concept summary sheets (DSA cheat sheet, SQL window functions, STAR stories). *Do NOT start learning new complex algorithms.*
- **T-12 Hours to T-8 Hours**: Test your hardware setup: webcam at eye level, clean lighting, working microphone, quiet background.
- **T-8 Hours**: Strict shut-off! Get 7 to 8 hours of uninterrupted sleep. Sleep consolidation is when memory retrieval paths are reinforced.
- **T-1 Hour**: Drink water, perform 2 minutes of posture stretching, take 3 physiological sighs, and enter with a growth mindset.

#### 3. Overcoming Rejection & Impostor Syndrome:
- Every top engineer has faced rejections. Remember: rejection in campus placement is simply a matching outcome, not a reflection of your potential.
- Focus on process metrics (problems solved, interviews completed) rather than outcome anxiety.
"""
    },
    "explore_47_placement_drives": {
        "title": "Explore 47 Active Campus Placement Drives",
        "keywords": ["47 drives", "explore 47 drives", "47 companies", "companies list", "all drives", "job drives", "drive list", "placement drives"],
        "summary": "Overview of the 47 top-tier product, cloud, and consulting companies active in the AI-TPMS portal.",
        "content": """
### 🏢 Explore 47 Active Campus Placement Drives

The AI-TPMS portal hosts **47 verified corporate placement drives** spanning global tech giants, high-growth cloud leaders, and premier FinTech firms:

#### 1. Tier-1 Hyperscale & Systems (18 - 45+ LPA):
- **Google Cloud Platforms** (28.5 LPA), **Microsoft Azure** (22 LPA), **Amazon AWS** (19.5 LPA), **Apple Systems** (24 LPA), **Meta AI Infra** (32 LPA), **NVIDIA AI Systems** (26 LPA), **Stripe Payments** (26 LPA).

#### 2. Tier-1 FinTech & Quantitative Banking (14 - 24 LPA):
- **Goldman Sachs Engineering** (24 LPA), **Morgan Stanley** (18 LPA), **JP Morgan Chase** (16.5 LPA), **American Express** (15 LPA), **PayPal FinTech** (16 LPA).

#### 3. High-Growth Enterprise & Cloud Platforms (12 - 20 LPA):
- **Oracle Cloud Infra** (17 LPA), **Salesforce Cloud** (18.5 LPA), **Cisco Systems** (16 LPA), **Atlassian Tools** (19 LPA), **Adobe Systems** (20 LPA), **Uber Mobility** (22 LPA).

#### 4. Consulting & Global Technology Services (6.5 - 12 LPA):
- **Deloitte USI** (8.5 LPA), **Accenture Technology** (7.5 LPA), **Cognizant Digital** (6.8 LPA), **Capgemini** (7.2 LPA), **TCS Digital / Prime** (7.5 - 9 LPA), **Infosys DSE** (8 LPA).

👉 **Next Step**: Click on the **Jobs & Eligibility** tab in the top navigation bar to view full salary packages, eligibility cutoffs, and apply directly!
"""
    },
    "round_1_aptitude": {
        "title": "Round 1 Aptitude & Quantitative Strategy",
        "keywords": ["aptitude", "round 1", "round1", "quant", "logical", "reasoning", "verbal", "speed", "elimination"],
        "summary": "Mastering Round 1 requires speed, accuracy, and strategic question selection within time limits.",
        "content": """
### 🎯 Placement Drive: Round 1 (Aptitude & Logical Mastery)

Round 1 filters out 60-70% of applicants in campus recruitment drives. It measures fundamental analytical problem-solving speed.

#### Core Pillars of Aptitude:
1. **Quantitative Aptitude**:
   - *High-Yield Topics*: Time & Work, Time-Speed-Distance, Percentages, Profit & Loss, Ratio & Proportion, Permutations & Combinations, Probability.
   - *Key Strategy*: Solve high-confidence questions first. Never spend more than 90 seconds on a single problem.
2. **Logical & Analytical Reasoning**:
   - *High-Yield Topics*: Syllogisms, Blood Relations, Seating Arrangements, Coding-Decoding, Data Sufficiency, Direction Sense.
   - *Key Strategy*: Draw clear Venn diagrams for syllogisms and grid matrices for seating arrangements.
3. **Verbal Ability & Reading Comprehension**:
   - *High-Yield Topics*: Error Spotting, Sentence Correction (Subject-Verb agreement, Parallelism), Para Jumbles, Reading Comprehension.
   - *Key Strategy*: Read questions before reading long RC passages to scan for keywords directly.

#### Golden Rules for Clearing Round 1:
- **Negative Marking Calculation**: In tests with -0.25 penalty, guess ONLY if you can eliminate at least two options.
- **Speed Math Hacks**: Memorize squares up to 30, cubes up to 20, and fraction-to-percentage conversions (e.g., 1/7 = 14.28%, 1/8 = 12.5%).
- **Time Allocation**: If a test has 60 questions for 60 minutes, divide it into 3 phases: Phase 1 (Easy 0-25m), Phase 2 (Moderate 25-50m), Phase 3 (Review 50-60m).
"""
    },
    "round_2_technical": {
        "title": "Round 2 Technical MCQ & Core CS Strategy",
        "keywords": ["technical", "round 2", "round2", "mcq", "dsa", "oops", "dbms", "os", "cn", "sql", "networks"],
        "summary": "Round 2 assesses Core Computer Science fundamentals: DSA, DBMS, OS, Computer Networks, and OOPs.",
        "content": """
### 💻 Placement Drive: Round 2 (Technical Assessment)

Round 2 tests in-depth conceptual clarity across core Computer Science subjects.

#### 1. Data Structures & Algorithms (DSA):
- **Time Complexities to Know by Heart**:
  - Binary Search: $O(\\log N)$
  - Merge Sort / Quick Sort (Average): $O(N \\log N)$
  - Hash Table Lookup / Insertion: $O(1)$ amortized
  - BFS / DFS on Graphs: $O(V + E)$
- **Essential Data Structures**: HashMaps, Heaps (PriorityQueue for Top-K), Binary Search Trees, Tries (Prefix searching), and Disjoint Set Union (Kruskal's algorithm).

#### 2. Database Management Systems (DBMS & SQL):
- **ACID Properties**: Atomicity (all-or-nothing), Consistency (state integrity), Isolation (concurrency control), Durability (write-ahead log).
- **Indexing**: B-Tree vs. Hash Indexes. Why B-Trees are preferred for range queries ($O(\\log N)$ disk I/O).
- **Normalization**: 1NF (atomic values), 2NF (no partial dependency on composite key), 3NF (no transitive dependency), BCNF.
- **SQL Must-Knows**: `INNER JOIN` vs `LEFT JOIN`, `GROUP BY` with `HAVING`, Window functions (`ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`).

#### 3. Operating Systems (OS):
- **Process vs. Thread**: Processes have independent memory address spaces; threads share the same memory heap and code section but have private stacks.
- **Deadlock Conditions (Coffman)**: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait. Deadlock prevention via Banker's Algorithm.
- **Virtual Memory & Paging**: TLB (Translation Lookaside Buffer), Page Faults, LRU Page Replacement algorithm.

#### 4. Object-Oriented Programming (OOP):
- **4 Pillars**: Encapsulation (data hiding), Abstraction (interface vs implementation), Inheritance (code reuse), Polymorphism (runtime method overriding vs compile-time overloading).
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.
"""
    },
    "round_3_mock_interview": {
        "title": "Round 3 Technical & AI Mock Interview Mastery",
        "keywords": ["interview", "round 3", "round3", "mock interview", "hr", "behavioral", "star", "camera", "proctoring"],
        "summary": "Master the STAR method, technical live explanation, system design basics, and speech fluency.",
        "content": """
### 🎙️ Placement Drive: Round 3 (Technical & Multi-Modal AI Interview)

The final interview round combines deep technical problem-solving with communication clarity and professional composure.

#### The STAR Framework for Answering Scenario Questions:
- **S - Situation**: Set the scene. Give brief, relevant context (e.g., "During our 6th semester team placement project...").
- **T - Task**: What was the challenge or objective? (e.g., "We needed to reduce API response latency from 1.2s to sub-200ms under high load.").
- **A - Action**: Explain *what YOU specifically did*. Mention design patterns, frameworks, and tools used (e.g., "I implemented Redis caching and indexed foreign keys in PostgreSQL.").
- **R - Result**: Quantify the outcome! (e.g., "Latency dropped by 78%, and our system handled 1,500 concurrent connections during testing.").

#### Verbal Communication & Fluency Rules:
- **Optimal Pacing**: 120 to 150 Words Per Minute (WPM). Speaking too fast (>180 WPM) appears nervous; speaking too slow (<90 WPM) seems uncertain.
- **Pause Deliberately**: Replace filler words (*um, uh, like, basically*) with a 1-to-2-second pause while organizing your next sentence.
- **Eye Contact & Camera Demeanor**: Look directly at the webcam lens, maintain an upright posture, and ensure balanced lighting without back-glare.
"""
    },
    "resume_ats_optimization": {
        "title": "Resume Intelligence & ATS Optimization Guide",
        "keywords": ["resume", "ats", "score", "format", "cv", "projects", "skills", "bullet points", "pdf"],
        "summary": "Optimize your resume for Applicant Tracking Systems with symbol extraction, action verbs, and quantifiable metrics.",
        "content": """
### 📄 AI Resume Intelligence & ATS Scoring Secrets

Applicant Tracking Systems (ATS) parse resumes using keyword extraction and structural heuristics before any human recruiter reads them.

#### 1. Formatting for Maximum Parseability:
- **Single Column Layout**: Multi-column tables often scramble text when extracted by PDF tokenizers.
- **Standard Headings**: Use standard section titles: `Education`, `Technical Skills`, `Projects`, `Work Experience`, `Certifications`.
- **Symbol Precision**: Ensure non-word symbols like `C++`, `C#`, `.NET`, `REST APIs` are clearly spaced and not merged with punctuation.

#### 2. The Google X-Y-Z Bullet Point Formula:
*"Accomplished [X] as measured by [Y], by doing [Z]."*
- ❌ Weak: "Worked on a web application using Python and FastAPI."
- ✅ Strong: "Architected a high-throughput backend service using FastAPI and SQLAlchemy, reducing database query overhead by 42% for 5,000 active users."

#### 3. Essential Skill Taxonomy Categories:
- **Languages**: Python, Java, C++, TypeScript, SQL, Go.
- **Frameworks**: FastAPI, Django, React, Next.js, Spring Boot, Node.js.
- **Cloud & DevOps**: Docker, Kubernetes, AWS (S3, EC2, RDS), Git/GitHub CI/CD pipelines.
- **Concepts**: RESTful Microservices, System Architecture, Database Sharding & Caching.
"""
    },
    "tell_me_about_yourself": {
        "title": "Mastering 'Tell Me About Yourself'",
        "keywords": ["tell me about yourself", "introduction", "intro", "introduce", "self intro", "hr question"],
        "summary": "Craft a powerful 90-second professional pitch tailored to campus software engineering interviews.",
        "content": """
### 🌟 The Perfect 90-Second 'Tell Me About Yourself' Blueprint

This is the icebreaker in 95% of interviews. Never recite your resume linearly from high school. Use the **Past-Present-Future** model:

#### Step-by-Step Script Structure:
1. **The Hook (Present - 20 seconds)**:
   *"Hello! I'm [Your Name], a final-year Computer Science student at [College Name], passionate about architecting scalable web backends and intelligent data-driven applications."*
2. **The Highlights (Past - 45 seconds)**:
   *"Over the past three years, I've built strong foundations in Data Structures, Algorithms, and System Design. Most recently, I developed an AI-Powered Placement Portal with FastAPI and SQLAlchemy that analyzes candidate performance using machine learning and NLP. That project taught me deep concurrency patterns, database indexing, and writing clean, test-driven code."*
3. **The Target (Future - 25 seconds)**:
   *"I've been closely following [Company Name]'s innovations in cloud engineering and distributed systems. I am excited to contribute my problem-solving skills, learn from your senior engineers, and build high-impact production solutions here."*
"""
    },
    "weakness_recommendation_advice": {
        "title": "Remediating Weak Performance Scores (<65%)",
        "keywords": ["weak", "score", "remediation", "improve", "attendance", "directive", "intervention", "recommendation"],
        "summary": "Targeted corrective roadmaps for candidates scoring below the 65% placement eligibility threshold.",
        "content": """
### 📈 Weakness Remediation & Intervention Protocol

If your composite score or any sub-metric is flagged below 65.0%, here is your targeted intervention roadmap:

#### 1. If Technical MCQ is < 65%:
- **Root Cause**: Memorization without underlying mechanism comprehension.
- **Action Plan**: Take 3 topic-focused diagnostic quizzes per week on LeetCode/GeeksforGeeks. Focus on time complexity, recursion stacks, and relational index mechanics.

#### 2. If Verbal / Mock Interview is < 65%:
- **Root Cause**: Nervous speech pacing (>180 WPM or <90 WPM) or high filler frequency (>6 fillers per response).
- **Action Plan**: Use the portal's AI Mock Interview Room with camera and microphone enabled. Record 3 practice answers daily using the STAR method. Watch your speech meter and pause deliberately.

#### 3. If Attendance is < 75%:
- **Root Cause**: Missed training or lab sessions.
- **Action Plan**: Institutional compliance strictly gates placement drives at $\\ge 75\\%$. Meet your batch faculty trainer to complete makeup laboratory modules and regularize log records immediately.
"""
    },
    "company_specific_patterns": {
        "title": "Top Tech Recruiter Placement Patterns",
        "keywords": ["amazon", "google", "microsoft", "tcs", "infosys", "accenture", "cognizant", "wipro", "tier 1", "tier 2", "salary", "lpa"],
        "summary": "Hiring patterns, syllabus splits, and package expectations for Tier-1 Product and Service leaders.",
        "content": """
### 🏢 Company Placement Patterns & Preparation Matrix

#### Product-Based Companies (Amazon, Microsoft, Google, Adobe, Cisco):
- **Packages**: 14 to 45+ LPA.
- **Hiring Focus**: Strict DSA (Medium/Hard arrays, dynamic programming, trees, graphs) + System Design (High-Level and Low-Level) + Core CS (OS, Concurrency, Networking).
- **Drive Format**: 1 Online Coding Round (2-3 problems) $\\rightarrow$ 3-4 Rounds of Technical F2F / Whiteboarding $\\rightarrow$ 1 Bar Raiser / Leadership Principles round.

#### High-Growth Tech & Consulting (Deloitte, Accenture, Cognizant Digital, Capgemini):
- **Packages**: 6.5 to 12 LPA.
- **Hiring Focus**: Strong Aptitude + Pseudo-code analysis + Core OOPs (Java/Python) + Cloud/DevOps fundamentals + Business Case Study.
- **Drive Format**: Round 1 Cognitive & Technical MCQ $\\rightarrow$ Round 2 Coding Assessment $\\rightarrow$ Round 3 Technical & HR Combined Interview.

#### Mass Hiring & Foundation Drives (TCS NQT, Infosys DSE/SE, Wipro Turbo):
- **Packages**: 3.6 to 9 LPA (Tiered based on test percentile).
- **Hiring Focus**: Quantitative Aptitude speed + Basic Python/C++ syntax + English verbal clarity.
"""
    }
}

class MentorEngine:
    """
    Dual-Engine AI Placement Mentor:
    1. Primary: Google Gemini Generative AI (Live LLM API).
    2. Fallback: Heuristic Semantic Knowledge Base (100% Offline, Zero Cloud Dependency).
    """

    @classmethod
    async def generate_response(
        cls,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        student_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        user_clean = user_message.strip()
        if not user_clean:
            return {
                "source": "mentor_engine",
                "engine": "offline_fallback",
                "response": "Hello! I am your AI Placement & Career Mentor. You can ask me anything about aptitude preparation, resume ATS optimization, technical interviews, company placement patterns, or mock interview strategies!"
            }

        # Dynamically reload .env if changed (prioritizing backend/.env)
        _env_paths = [
            os.path.join(os.getcwd(), "backend", ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "backend", ".env"),
            os.path.join(os.getcwd(), ".env"),
            ".env"
        ]
        for _p in _env_paths:
            if os.path.exists(_p):
                try:
                    with open(_p, "r", encoding="utf-8") as _f:
                        for _line in _f:
                            _line = _line.strip()
                            if _line and not _line.startswith("#") and _line.startswith("GEMINI_API_KEY="):
                                val = _line.split("=", 1)[1].strip().strip("'\"")
                                if val:
                                    os.environ["GEMINI_API_KEY"] = val
                                    break
                    if os.environ.get("GEMINI_API_KEY"):
                        break
                except Exception:
                    pass

        # Try Google Gemini API if configured
        from backend.app.core.config import settings
        gemini_key = (os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "") or "").strip()
        if gemini_key:
            try:
                gemini_res = await cls._query_gemini(user_clean, chat_history, student_context, gemini_key)
                if gemini_res:
                    return {
                        "source": "mentor_engine",
                        "engine": "google_gemini_llm",
                        "response": gemini_res
                    }
            except Exception as e:
                print(f"[MentorAI] Gemini API call exception: {type(e).__name__}")

        # Fallback to Comprehensive Offline Placement Knowledge Base
        offline_res = cls._query_offline_knowledge_base(user_clean, student_context)
        return {
            "source": "mentor_engine",
            "engine": "offline_heuristic_kb",
            "response": offline_res
        }

    @classmethod
    async def _query_gemini(
        cls,
        message: str,
        history: Optional[List[Dict[str, str]]],
        student_context: Optional[Dict[str, Any]],
        api_key: str
    ) -> Optional[str]:
        system_instruction = (
            "You are the senior AI Placement Director and Career Mentor for an elite engineering college portal. "
            "Your role is to guide students to crack campus placement drives (Aptitude, Technical MCQs, Coding, and HR Interviews). "
            "Be encouraging, highly structured, practical, and provide actionable tips with examples. "
            "Format your answers with crisp markdown headings, bullet points, and code snippets when relevant."
        )

        if student_context:
            system_instruction += f"\nStudent Context: Name: {student_context.get('name', 'Student')}, CGPA: {student_context.get('cgpa', 'N/A')}, Skills: {', '.join(student_context.get('skills', []))}."

        contents = []
        if history:
            for h in history[-4:]:
                contents.append({
                    "role": "user" if h.get("role") in ["user", "student"] else "model",
                    "parts": [{"text": h.get("content") or h.get("message", "")}]
                })
        
        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": contents,
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1024
            }
        }

        # Supported active models in order of speed, quota stability and availability
        models = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.8-flash"
        ]
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            for model_name in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"]
                    else:
                        sanitized_body = resp.text.replace(api_key, "[REDACTED]")[:250]
                        print(f"[MentorAI] Gemini API ({model_name}) returned HTTP {resp.status_code}: {sanitized_body}")
                except Exception as e:
                    print(f"[MentorAI] HTTP request to Gemini ({model_name}) failed: {type(e).__name__}")
        return None

    @classmethod
    def _query_offline_knowledge_base(
        cls,
        message: str,
        student_context: Optional[Dict[str, Any]] = None
    ) -> str:
        msg_lowered = message.lower().strip()

        # 1. Direct Conversational Greeting & Introduction Detection
        greeting_patterns = [
            r"^(hi|hello|hey|heya|hlo|hllo|hii+|hola|namaste|good\s*(morning|afternoon|evening))\b",
            r"^who\s+are\s+you\b",
            r"^(what\s+can\s+you\s+do|help|how\s+can\s+you\s+help)\b"
        ]
        is_greeting = any(re.search(pat, msg_lowered) for pat in greeting_patterns)
        
        name_str = f" {student_context['name']}" if (student_context and student_context.get("name")) else ""
        if is_greeting:
            return f"""### 👋 Hello{name_str}! I am Mitra, your AI Placement & Career Mentor.

I'm here to help you navigate your placement journey and crack your dream company. Here is what we can do together:

1. **🎯 3-Round Placement Selection**: Get tips and formulas for **Round 1 (Aptitude)**, **Round 2 (Technical Core)**, and **Round 3 (AI Mock Interview)**.
2. **📄 Resume ATS Optimization**: Learn how to format your resume using the **Google X-Y-Z formula** and match company cutoffs.
3. **💼 Company-Specific Prep**: Ask me about hiring patterns for **Google, Microsoft, Amazon, TCS, Infosys, and Cognizant**.
4. **🧘 Placement Stress Management**: Ask for breathing exercises or the 24-hour pre-drive checklist.

**Ask me any question**, such as:
- *"How should I introduce myself in an interview?"*
- *"What are the most common SQL and Python interview questions?"*
- *"Am I eligible for Google or Microsoft drives?"*
- *"How can I improve my aptitude speed math?"*"""

        # Score matching modules
        best_match_key = None
        highest_score = 0

        for key, module in OFFLINE_KNOWLEDGE_BASE.items():
            score = 0
            for kw in module["keywords"]:
                if re.search(r'\b' + re.escape(kw) + r'\b', msg_lowered):
                    score += 3
                elif kw in msg_lowered:
                    score += 1
            if score > highest_score:
                highest_score = score
                best_match_key = key

        if best_match_key and highest_score > 0:
            module = OFFLINE_KNOWLEDGE_BASE[best_match_key]
            greeting = ""
            if student_context and student_context.get("name"):
                greeting = f"Hello {student_context['name']}! Here is the placement guidance for your query:\n\n"
            return f"{greeting}{module['content']}"

        # Default intelligent multi-topic guidance
        return f"""
### 🎓 AI Career Mentor Placement Advice

I received your question: *"**{message}**"*

Here are actionable guidelines to optimize your placement journey:

1. **Strategic Placement Drive Preparation**:
   - **Round 1 (Aptitude)**: Focus on speed math, high-yield quantitative formulas, and syllogisms. Avoid spending more than 90 seconds per question.
   - **Round 2 (Technical Core)**: Thoroughly review Data Structures ($O(N \\log N)$ vs $O(1)$ lookup), DBMS (ACID, Normalization, Joins), OS (Paging, Deadlocks), and OOPs (SOLID principles).
   - **Round 3 (Mock AI Interview)**: Practice technical responses aloud using the **STAR Method** (Situation, Task, Action, Result). Maintain eye contact with the camera and steady speech pacing (120-150 WPM).

2. **Resume & ATS Optimization**:
   - Use the **Google X-Y-Z formula**: *"Accomplished X as measured by Y, by doing Z."*
   - Make sure your resume lists technical keywords with correct symbols (`C++`, `Python`, `SQL`, `FastAPI`, `Docker`).

3. **Try Asking Me Specific Queries**:
   - *"How to prepare for Round 1 Aptitude?"*
   - *"What questions are asked in technical interviews?"*
   - *"How do I answer 'Tell me about yourself'?"*
   - *"How do I improve my resume ATS score?"*
   - *"What are the hiring patterns for Amazon and TCS?"*
"""
