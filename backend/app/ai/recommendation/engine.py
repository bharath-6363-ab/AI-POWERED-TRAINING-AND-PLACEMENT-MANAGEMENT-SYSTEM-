from typing import List, Dict, Any

class TrainingRecommendationEngine:
    @staticmethod
    def generate_recommendations(
        attendance_pct: float,
        aptitude_score: float,
        technical_test_score: float,
        interview_score: float,
        coding_score: float,
        words_per_minute: float,
        filler_count: int
    ) -> List[Dict[str, Any]]:
        recommendations = []

        # 1. Technical Practice Check
        if technical_test_score < 65.0:
            recommendations.append({
                "priority": 1,
                "title": "Core Technical & Concept Mastery",
                "category": "Technical MCQs & Architecture",
                "reason": f"Technical assessment average ({technical_test_score:.1f}%) is currently below the placement threshold (65.0%).",
                "actionable_steps": "Review modular REST principles, database index tuning, and complete 3 targeted topic practice tests."
            })

        # 2. Verbal Fluency & Communication Check
        if (words_per_minute > 0 and (words_per_minute < 95 or words_per_minute > 185)) or filler_count > 6:
            recommendations.append({
                "priority": 2,
                "title": "Interview Fluency & Speech Pacing",
                "category": "Verbal Communication",
                "reason": f"Speech rate ({words_per_minute:.1f} WPM) or frequent filler words ({filler_count}) indicate nervous pacing.",
                "actionable_steps": "Practice structured STAR answering method with 2-second deliberate pauses before key sentences."
            })

        # 3. Aptitude & Problem Solving Check
        if aptitude_score < 65.0:
            recommendations.append({
                "priority": 2,
                "title": "Quantitative & Logical Aptitude",
                "category": "Aptitude Tests",
                "reason": f"Aptitude test score ({aptitude_score:.1f}%) indicates need for enhanced speed and accuracy.",
                "actionable_steps": "Take daily 15-minute speed drill quizzes on probability, permutations, and analytical reasoning."
            })

        # 4. Attendance Deficit Remediation
        if attendance_pct < 75.0:
            recommendations.append({
                "priority": 1,
                "title": "Attendance Remediation Plan",
                "category": "Institutional Eligibility",
                "reason": f"Current attendance ({attendance_pct:.1f}%) disqualifies you from campus placement drives requiring >= 75%.",
                "actionable_steps": "Meet with your designated batch trainer to establish makeup sessions and regularize log records."
            })

        # 5. General Placement Readiness (if all are good)
        if not recommendations:
            recommendations.append({
                "priority": 3,
                "title": "Advanced Mock Interview Polish",
                "category": "Placement Readiness",
                "reason": "Overall metrics meet standard eligibility thresholds.",
                "actionable_steps": "Undertake advanced system design case studies and review company-specific interview archives."
            })

        return recommendations
