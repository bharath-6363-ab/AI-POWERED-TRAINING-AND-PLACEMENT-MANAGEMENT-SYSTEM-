import re
import os
import hashlib
from typing import Dict, List, Any
from pypdf import PdfReader

SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "java", "c++", "c", "c#", "javascript", "typescript", "ruby", "go", "golang",
        "rust", "kotlin", "swift", "php", "r", "scala", "dart"
    ],
    "Frameworks & Libraries": [
        "react", "angular", "vue", "next.js", "express", "nodejs", "node.js", "django", "flask",
        "fastapi", "spring boot", "springboot", "asp.net", "laravel", "pytorch", "tensorflow",
        "keras", "pandas", "numpy", "scikit-learn", "tailwind", "bootstrap"
    ],
    "Databases & Cloud": [
        "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis", "oracle", "sql server",
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "git", "github", "linux"
    ],
    "Concepts & Tools": [
        "rest api", "restful", "graphql", "oop", "object oriented", "data structures",
        "algorithms", "ci/cd", "microservices", "unit testing", "agile", "scrum"
    ]
}

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            text = f"Error reading PDF: {str(e)}"
        return text

    @staticmethod
    def parse_resume(raw_text: str) -> Dict[str, Any]:
        lowered = raw_text.lower()
        extracted_skills = []
        categorized_skills = {}

        for category, skills in SKILL_TAXONOMY.items():
            categorized_skills[category] = []
            for skill in skills:
                # Regex lookarounds for non-word programming symbols (C++, C#, C) alongside standard languages
                if skill in ["c++", "c#"]:
                    pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9+#])'
                elif skill == "c":
                    pattern = r'(?<![a-zA-Z0-9+#])c(?![a-zA-Z0-9+#])'
                else:
                    pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
                if re.search(pattern, lowered):
                    display_name = skill.upper() if skill in ["c++", "c#", "c", "sql", "aws", "gcp", "r", "php"] else (skill.title() if len(skill) > 3 else skill.upper())
                    extracted_skills.append({
                        "name": display_name,
                        "category": category
                    })
                    categorized_skills[category].append(display_name)

        # Basic Section Extraction
        sections = {
            "education": ResumeParser._extract_section(raw_text, ["education", "academics", "qualifications"]),
            "projects": ResumeParser._extract_section(raw_text, ["projects", "academic projects", "key projects"]),
            "experience": ResumeParser._extract_section(raw_text, ["experience", "internships", "work experience"])
        }

        return {
            "skills": extracted_skills,
            "categorized_skills": categorized_skills,
            "categorized": categorized_skills,
            "sections": sections,
            "skill_count": len(extracted_skills)
        }

    @staticmethod
    def _extract_section(text: str, keywords: List[str]) -> List[str]:
        lines = text.split("\n")
        capturing = False
        captured_lines = []
        
        for line in lines:
            clean = line.strip().lower()
            if any(k in clean for k in keywords) and len(clean) < 35:
                capturing = True
                continue
            elif capturing and (clean.isupper() or any(h in clean for h in ["skills", "certifications", "projects", "education", "experience"]) and len(clean) < 30):
                # Another header started
                break
            elif capturing and clean:
                captured_lines.append(line.strip())
                if len(captured_lines) > 8:
                    break

        return captured_lines
