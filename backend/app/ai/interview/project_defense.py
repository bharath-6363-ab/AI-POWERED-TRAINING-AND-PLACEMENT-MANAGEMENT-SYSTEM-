import os
import json
import httpx
from typing import Dict, List, Any, Optional
from backend.app.ai.nlp.evaluator import NLPEvaluator

class ProjectDefenseSimulator:
    """
    Project-Defense Viva & Placement Panel Simulator.
    Generates targeted architectural, database, scaling, and security viva questions
    for academic major projects and provides rigorous evaluation with Senior Architect model answers.
    """

    @classmethod
    async def generate_viva_questions(
        cls,
        project_title: str,
        tech_stack: List[str],
        project_description: str,
        architecture_type: str = "Full-Stack Web & Microservices"
    ) -> Dict[str, Any]:
        from backend.app.core.config import settings
        gemini_key = (os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "") or "").strip()
        stack_str = ", ".join(tech_stack) if isinstance(tech_stack, list) else str(tech_stack)

        if gemini_key:
            models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
            system_instruction = (
                "You are the Lead Technical Interviewer and Senior Systems Architect evaluating a student's final year major project. "
                "Generate exactly 4 rigorous viva defense questions in JSON array format covering: "
                "1. Architecture Trade-offs, 2. Database & Data Integrity, 3. Scaling & Bottlenecks, 4. Security & Edge Cases. "
                "Each item must have: 'category', 'question_text', 'expected_concepts' (list of 3-4 strings), and 'ideal_architect_answer' (concise summary)."
            )
            user_prompt = (
                f"Project Title: {project_title}\n"
                f"Tech Stack: {stack_str}\n"
                f"Architecture Style: {architecture_type}\n"
                f"Description: {project_description}\n\n"
                f"Return ONLY a valid JSON array of 4 objects without extra conversational commentary."
            )
            payload = {
                "contents": [{"role": "user", "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024}
            }
            headers = {"Content-Type": "application/json", "x-goog-api-key": gemini_key}
            for model_name in models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                    async with httpx.AsyncClient(timeout=20.0) as client:
                        resp = await client.post(url, headers=headers, json=payload)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates:
                                raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                                s_idx = raw_text.find("[")
                                e_idx = raw_text.rfind("]")
                                clean_json = raw_text[s_idx:e_idx+1] if (s_idx != -1 and e_idx != -1) else raw_text.replace("```json", "").replace("```", "").strip()
                                questions_parsed = json.loads(clean_json)
                                if isinstance(questions_parsed, list) and len(questions_parsed) >= 4:
                                    return {
                                        "status": "success",
                                        "engine": "google_gemini_llm",
                                        "project_title": project_title,
                                        "questions": questions_parsed[:4]
                                    }
                except Exception:
                    pass

        # Robust Offline Fallback: Grounded in candidate's tech stack
        primary_tech = tech_stack[0] if tech_stack else "Python"
        sec_tech = tech_stack[1] if len(tech_stack) > 1 else "SQL"

        questions = [
            {
                "id": 1,
                "category": "Architecture Trade-offs & Decisions",
                "question_text": f"Why did you choose {primary_tech} and {architecture_type} for '{project_title}' instead of a serverless or monolithic alternative? What were the primary architectural trade-offs you accepted?",
                "expected_concepts": ["latency", "maintainability", "development velocity", "decoupling"],
                "ideal_architect_answer": f"Selected {primary_tech} due to rapid ASGI prototyping, modular endpoint organization, and asynchronous I/O capabilities, accepting the trade-off of managing state persistence and deployment orchestration."
            },
            {
                "id": 2,
                "category": "Database Modeling & Data Integrity",
                "question_text": f"How is data integrity guaranteed in your schema? How does your design handle race conditions or concurrent updates during peak writes?",
                "expected_concepts": ["foreign keys", "acid transactions", "indexes", "row locking", "isolation levels"],
                "ideal_architect_answer": "Data consistency is enforced using relational foreign key constraints with indexed lookup keys. Concurrent updates rely on database transactions with optimistic locking or SELECT FOR UPDATE to prevent dirty writes."
            },
            {
                "id": 3,
                "category": "Scalability, Latency & Bottlenecks",
                "question_text": f"If user traffic to '{project_title}' increases from 100 to 50,000 requests per minute, what is the exact single point of failure in your current setup, and how would you resolve it?",
                "expected_concepts": ["connection pooling", "database bottleneck", "caching", "horizontal scaling", "load balancer"],
                "ideal_architect_answer": "The relational database connection pool is the initial bottleneck. Remediation involves connection pooling (SQLAlchemy/PgBouncer), read-replicas for query offloading, in-memory caching for hot records, and container horizontal replication."
            },
            {
                "id": 4,
                "category": "Security, Failure Recovery & Edge Cases",
                "question_text": "How does your project handle sudden backend crashes or network partitions? What prevents an attacker from exploiting input endpoints or token replay?",
                "expected_concepts": ["jwt expiration", "input validation", "rate limiting", "try-except rollbacks", "graceful degradation"],
                "ideal_architect_answer": "Input schemas are strictly validated using Pydantic typing before touching business logic. JWT access tokens feature short expiry and cryptographic signature verification. Database transactions execute inside auto-rollback contexts to prevent corrupted intermediate state."
            }
        ]

        return {
            "status": "success",
            "engine": "heuristic_panel_engine",
            "project_title": project_title,
            "questions": questions
        }

    @classmethod
    async def evaluate_defense_answer(
        cls,
        question_text: str,
        expected_concepts: List[str],
        ideal_architect_answer: str,
        student_answer: str,
        project_title: str
    ) -> Dict[str, Any]:
        # 1. NLP Concept & Semantic Evaluation
        nlp_res = NLPEvaluator.evaluate_answer(
            answer_text=student_answer,
            expected_concepts=expected_concepts,
            ideal_summary=ideal_architect_answer
        )

        score = nlp_res["technical_score"]
        if score >= 75.0:
            verdict = "STRONG_DEFENSE (Convincing & Technically Sound)"
            panel_tone = "The candidate demonstrated solid architectural comprehension."
        elif score >= 55.0:
            verdict = "ACCEPTABLE_DEFENSE (Partially Sound, Missing Depth)"
            panel_tone = "The candidate grasps high-level concepts but lacked depth on production edge cases."
        else:
            verdict = "VULNERABLE_DEFENSE (Requires Immediate Review)"
            panel_tone = "The answer was vague or missed fundamental engineering trade-offs."

        # Actionable defense coaching
        strengths = nlp_res["concepts_covered"]
        deficits = nlp_res["concepts_missing"]

        panel_feedback = []
        if strengths:
            panel_feedback.append(f"Panel commended your explanation of: {', '.join(strengths)}.")
        if deficits:
            panel_feedback.append(f"Panel noted a gap regarding: {', '.join(deficits)}. In an actual defense, be specific about numbers, protocols, and failure modes.")

        return {
            "score": score,
            "verdict": verdict,
            "panel_tone": panel_tone,
            "nlp_evaluation": nlp_res,
            "panel_feedback": " ".join(panel_feedback),
            "concepts_covered": strengths,
            "concepts_missing": deficits,
            "model_architect_answer": ideal_architect_answer
        }
