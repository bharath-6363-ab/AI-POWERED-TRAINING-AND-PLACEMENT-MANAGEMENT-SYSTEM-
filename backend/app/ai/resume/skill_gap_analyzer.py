import re
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.ai.resume.parser import ResumeParser, SKILL_TAXONOMY

class ResumeSkillGapAnalyzer:
    """
    ATS Resume & Job Description Skill-Gap Analyzer.
    Performs keyword extraction, category matching, TF-IDF cosine semantic similarity,
    and synthesizes actionable bullet points to maximize ATS pass rates.
    """

    @classmethod
    def analyze_gap(
        cls,
        resume_text: str,
        job_description: str,
        required_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        # 1. Parse Candidate Resume
        parsed_resume = ResumeParser.parse_resume(resume_text)
        cand_skill_names = {s["name"].lower(): s["name"] for s in parsed_resume.get("skills", [])}

        # 2. Extract JD Skills
        jd_skills_dict: Dict[str, str] = {}
        if required_skills and len(required_skills) > 0:
            for s in required_skills:
                jd_skills_dict[s.lower()] = s
        
        # Also parse JD text to discover implicit skills from taxonomy
        parsed_jd = ResumeParser.parse_resume(job_description)
        for s in parsed_jd.get("skills", []):
            jd_skills_dict[s["name"].lower()] = s["name"]

        total_jd_skills = len(jd_skills_dict)
        
        # 3. Categorized Skill Overlap
        matched = []
        missing = []
        
        for low_name, display_name in jd_skills_dict.items():
            if low_name in cand_skill_names:
                matched.append(display_name)
            else:
                missing.append(display_name)

        bonus_skills = [
            display_name for low_name, display_name in cand_skill_names.items()
            if low_name not in jd_skills_dict
        ]

        # 4. Keyword Coverage Percentage
        if total_jd_skills > 0:
            keyword_match_pct = round((len(matched) / total_jd_skills) * 100.0, 2)
        else:
            keyword_match_pct = 100.0

        # 5. Semantic Cosine Similarity (TF-IDF)
        semantic_sim = 0.0
        try:
            if resume_text.strip() and job_description.strip():
                vec = TfidfVectorizer(stop_words='english', max_features=500)
                mat = vec.fit_transform([job_description, resume_text])
                cos_sim = float(cosine_similarity(mat[0:1], mat[1:2])[0][0])
                semantic_sim = round(min(100.0, cos_sim * 140.0), 2)
        except Exception:
            semantic_sim = keyword_match_pct

        # 6. Overall ATS Compatibility Score
        # 70% direct skill keyword coverage + 30% semantic context alignment
        ats_score = round((0.70 * keyword_match_pct) + (0.30 * semantic_sim), 2)

        # 7. Actionable Recommendations & Tailored Bullet-Point Suggestions
        recommendations = []
        if missing:
            top_missing = missing[:4]
            recommendations.append(
                f"Critical Deficit: Add dedicated project bullet points or course certifications covering: {', '.join(top_missing)}."
            )
            for m in top_missing[:2]:
                recommendations.append(
                    f"Recommended X-Y-Z Bullet Point: 'Engineered high-throughput service components using {m}, reducing latency by 20% and improving test coverage to 90%.'"
                )
        if ats_score >= 80.0:
            verdict = "High ATS Match (Strong Placement Drive Candidate)"
        elif ats_score >= 60.0:
            verdict = "Moderate Match (Resume Tailoring Recommended)"
        else:
            verdict = "Low Match (Significant Skill Gap - Training Recommended)"

        return {
            "ats_score": ats_score,
            "keyword_match_pct": keyword_match_pct,
            "semantic_similarity_pct": semantic_sim,
            "verdict": verdict,
            "total_jd_skills_count": total_jd_skills,
            "matched_skills_count": len(matched),
            "missing_skills_count": len(missing),
            "matched_skills": matched,
            "missing_skills": missing,
            "candidate_bonus_skills": bonus_skills,
            "recommendations": recommendations,
            "categorized_skills": parsed_resume.get("categorized_skills", {})
        }

    @classmethod
    def comprehensive_ats_audit(cls, resume_text: str) -> Dict[str, Any]:
        """
        Conducts a multi-pillar automated ATS health, formatting, and impact audit.
        Evaluates Contact Information, Section Architecture, Action-Verb Impact,
        Quantifiable Metric Achievements, and Skill Density.
        """
        if not resume_text:
            resume_text = ""

        clean_text = resume_text.strip()
        lowered = clean_text.lower()
        word_count = len(clean_text.split())

        # Pillar 1: Contact & Professional Links (25 pts)
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', clean_text)
        phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', clean_text)
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+|linkedin\.com/[\w-]+', clean_text, re.IGNORECASE)
        github_match = re.search(r'github\.com/[\w-]+', clean_text, re.IGNORECASE)

        contact_score = 0
        if email_match:
            contact_score += 8
        if phone_match:
            contact_score += 7
        if linkedin_match:
            contact_score += 5
        if github_match:
            contact_score += 5

        # Pillar 2: Section Architecture & Content Parsing (25 pts)
        parsed_resume = ResumeParser.parse_resume(clean_text)
        skills_found = [s["name"] for s in parsed_resume.get("skills", [])]
        sections = parsed_resume.get("sections", {})

        has_skills = len(skills_found) > 0
        has_projects = bool(sections.get("projects")) or any(k in lowered for k in ["project", "projects", "key project", "portfolio"])
        has_education = bool(sections.get("education")) or any(k in lowered for k in ["education", "academics", "btech", "b.tech", "b.e", "degree", "university", "college", "cgpa", "gpa"])
        has_experience = bool(sections.get("experience")) or any(k in lowered for k in ["experience", "internship", "employment", "work experience"])

        section_score = 0
        if has_skills:
            section_score += 8
        if has_projects:
            section_score += 7
        if has_education:
            section_score += 5
        if has_experience:
            section_score += 5

        # Pillar 3: Action-Verb & Impact Power (25 pts)
        action_verbs_catalog = [
            "engineered", "developed", "architected", "implemented", "optimized",
            "spearheaded", "designed", "deployed", "scaled", "automated",
            "built", "reduced", "increased", "orchestrated", "refactored",
            "integrated", "benchmarked", "accelerated", "modeled", "streamlined"
        ]
        detected_verbs = [v for v in action_verbs_catalog if re.search(r'\b' + re.escape(v) + r'\b', lowered)]
        passive_phrases = [p for p in ["worked on", "helped", "responsible for", "assisted", "did"] if p in lowered]

        if len(detected_verbs) >= 5:
            action_score = 25
        elif len(detected_verbs) >= 3:
            action_score = 18
        elif len(detected_verbs) >= 1:
            action_score = 10
        else:
            action_score = 5

        # Pillar 4: Quantifiable Metrics & KPI Evidence (25 pts)
        metrics_found = re.findall(r'\b\d+(?:\.\d+)?%|\b\d+x\b|\b\d+(?:,\d{3})*\+?\s*(?:ms|seconds|users|requests|endpoints|queries|k|m|gb)\b', clean_text, re.IGNORECASE)
        unique_metrics = list(dict.fromkeys(metrics_found))

        if len(unique_metrics) >= 3:
            metrics_score = 25
        elif len(unique_metrics) >= 2:
            metrics_score = 18
        elif len(unique_metrics) >= 1:
            metrics_score = 12
        else:
            metrics_score = 5

        # Aggregate Score & Grade
        total_ats_score = contact_score + section_score + action_score + metrics_score
        total_ats_score = min(100, max(0, total_ats_score))

        if total_ats_score >= 85:
            grade = "A+"
            status = "ATS Optimized (Executive Ready)"
        elif total_ats_score >= 75:
            grade = "A"
            status = "Strong Candidate Profile"
        elif total_ats_score >= 60:
            grade = "B"
            status = "Moderate Match (Refinement Advised)"
        else:
            grade = "C"
            status = "Needs Improvement (Missing Critical Sections)"

        strengths = []
        improvements = []

        if email_match and phone_match:
            strengths.append("Direct recruiter contact channels (Email & Phone) detected.")
        else:
            improvements.append("Ensure your professional email and contact phone number are clearly visible at top.")

        if linkedin_match or github_match:
            strengths.append("Digital technical portfolio links (GitHub / LinkedIn) present.")
        else:
            improvements.append("Add your active GitHub or LinkedIn URL to boost technical credibility.")

        if len(skills_found) >= 5:
            strengths.append(f"Strong taxonomy footprint: {len(skills_found)} industry skills identified.")
        else:
            improvements.append("List more specific technical tools, libraries, or databases to improve ATS keyword index.")

        if len(detected_verbs) >= 3:
            strengths.append(f"Active leadership voice: {len(detected_verbs)} strong technical action verbs used.")
        else:
            improvements.append("Replace passive phrases ('worked on', 'helped') with active verbs ('Architected', 'Deployed', 'Engineered').")

        if unique_metrics:
            strengths.append(f"Measurable achievements included ({', '.join(unique_metrics[:3])}).")
        else:
            improvements.append("Adopt the Google X-Y-Z formula: 'Accomplished [X] as measured by [Y] by doing [Z]' with numbers or %.")

        return {
            "total_ats_score": total_ats_score,
            "grade": grade,
            "status": status,
            "word_count": word_count,
            "pillars": {
                "contact": {
                    "score": contact_score,
                    "max": 25,
                    "email": email_match.group(0) if email_match else None,
                    "phone": phone_match.group(0) if phone_match else None,
                    "linkedin": bool(linkedin_match),
                    "github": bool(github_match)
                },
                "sections": {
                    "score": section_score,
                    "max": 25,
                    "has_skills": has_skills,
                    "has_projects": has_projects,
                    "has_education": has_education,
                    "has_experience": has_experience
                },
                "action_impact": {
                    "score": action_score,
                    "max": 25,
                    "action_verbs_detected": detected_verbs,
                    "passive_phrases_detected": passive_phrases
                },
                "quantifiable_metrics": {
                    "score": metrics_score,
                    "max": 25,
                    "metrics_detected": unique_metrics[:5]
                }
            },
            "skills_extracted": skills_found,
            "categorized_skills": parsed_resume.get("categorized_skills", {}),
            "strengths": strengths,
            "improvements": improvements
        }
