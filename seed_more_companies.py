import os
from backend.app.core.database import SessionLocal
from backend.app.models.all_models import Company, JobRole, JobRequirement

ADDITIONAL_17_DRIVES = [
    {
        "company_name": "Google Cloud Platforms",
        "website": "https://cloud.google.com",
        "industry": "Hyperscale Cloud & Distributed Systems",
        "location": "Bengaluru / Hyderabad",
        "title": "Cloud Systems & Distributed Backend Engineer",
        "description": "Architects high-availability microservices, Kubernetes clusters, and AI-optimized cloud infra.",
        "salary_lpa": 28.50,
        "requirements": {
            "min_cgpa": 8.00,
            "min_attendance_pct": 75.00,
            "required_skills": ["Python", "Go", "Docker", "Kubernetes", "SQL"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology", "AI & Data Science"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Microsoft Azure Engineering",
        "website": "https://microsoft.com",
        "industry": "Enterprise Cloud Software",
        "location": "Hyderabad / Bengaluru",
        "title": "Software Development Engineer - II (SDE-II)",
        "description": "Develops real-time distributed data structures, Azure core services, and resilient APIs.",
        "salary_lpa": 22.00,
        "requirements": {
            "min_cgpa": 7.80,
            "min_attendance_pct": 75.00,
            "required_skills": ["C++", "C#", "Python", "SQL", "Cloud Architecture"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Amazon Web Services (AWS)",
        "website": "https://aws.amazon.com",
        "industry": "Cloud Infrastructure & Serverless",
        "location": "Bengaluru / Chennai",
        "title": "Cloud Infrastructure & DevOps Engineer",
        "description": "Automates serverless architectures, event-driven microservices, and multi-region replication.",
        "salary_lpa": 19.50,
        "requirements": {
            "min_cgpa": 7.50,
            "min_attendance_pct": 75.00,
            "required_skills": ["Python", "Docker", "AWS", "Git", "Linux"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Apple Technology Labs",
        "website": "https://apple.com",
        "industry": "Consumer Tech & Operating Systems",
        "location": "Hyderabad",
        "title": "Systems Software & Core Frameworks Engineer",
        "description": "Builds high-performance low-level system services, memory management, and secure APIs.",
        "salary_lpa": 26.00,
        "requirements": {
            "min_cgpa": 8.20,
            "min_attendance_pct": 80.00,
            "required_skills": ["C++", "Python", "Operating Systems", "Data Structures"],
            "eligible_branches": ["Computer Science & Engineering", "Electronics & Communication"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Nvidia Graphics & AI",
        "website": "https://nvidia.com",
        "industry": "Accelerated Computing & AI Hardware",
        "location": "Pune / Bengaluru",
        "title": "CUDA Systems & Deep Learning Optimization Engineer",
        "description": "Accelerates deep learning inference pipelines, GPU kernels, and computer vision models.",
        "salary_lpa": 24.50,
        "requirements": {
            "min_cgpa": 8.00,
            "min_attendance_pct": 75.00,
            "required_skills": ["Python", "C++", "PyTorch", "Computer Vision"],
            "eligible_branches": ["Computer Science & Engineering", "AI & Data Science"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Meta Reality Labs",
        "website": "https://meta.com",
        "industry": "Social Computing & Spatial AI",
        "location": "Gurugram / Bengaluru",
        "title": "Full-Stack Distributed Systems Engineer",
        "description": "Designs real-time graph databases, GraphQL microservices, and highly concurrent APIs.",
        "salary_lpa": 25.00,
        "requirements": {
            "min_cgpa": 8.00,
            "min_attendance_pct": 75.00,
            "required_skills": ["Python", "React", "GraphQL", "SQL", "Docker"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Netflix Streaming Services",
        "website": "https://netflix.com",
        "industry": "Global Media Streaming",
        "location": "Mumbai / Remote",
        "title": "Edge Delivery & Backend Microservices Engineer",
        "description": "Engineers globally distributed CDN edge caching, adaptive bit-rate pipelines, and resilient services.",
        "salary_lpa": 27.00,
        "requirements": {
            "min_cgpa": 8.25,
            "min_attendance_pct": 75.00,
            "required_skills": ["Java", "Python", "Spring Boot", "Kafka", "Docker"],
            "eligible_branches": ["Computer Science & Engineering"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Uber Technologies",
        "website": "https://uber.com",
        "industry": "Urban Mobility & Marketplace Logistics",
        "location": "Hyderabad / Bengaluru",
        "title": "Marketplace Dynamic Pricing Backend Engineer",
        "description": "Develops real-time geospatial matching algorithms, routing optimizations, and fault-tolerant event streams.",
        "salary_lpa": 21.00,
        "requirements": {
            "min_cgpa": 7.75,
            "min_attendance_pct": 75.00,
            "required_skills": ["Go", "Python", "SQL", "Data Structures", "Redis"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Salesforce Cloud",
        "website": "https://salesforce.com",
        "industry": "Enterprise SaaS & CRM",
        "location": "Hyderabad",
        "title": "Platform Software Engineer (Enterprise Data)",
        "description": "Engineers multi-tenant cloud architectures, scalable REST APIs, and automated telemetry.",
        "salary_lpa": 17.50,
        "requirements": {
            "min_cgpa": 7.50,
            "min_attendance_pct": 75.00,
            "required_skills": ["Java", "Python", "SQL", "REST API", "Docker"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Adobe Experience Cloud",
        "website": "https://adobe.com",
        "industry": "Creative & Digital Experience Software",
        "location": "Noida / Bengaluru",
        "title": "Creative SDK & Cloud Full Stack Developer",
        "description": "Builds high-performance canvas rendering tools, cloud collaboration features, and React dashboards.",
        "salary_lpa": 18.00,
        "requirements": {
            "min_cgpa": 7.60,
            "min_attendance_pct": 75.00,
            "required_skills": ["React", "TypeScript", "Python", "FastAPI", "Docker"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Snowflake Data Cloud",
        "website": "https://snowflake.com",
        "industry": "Cloud Data Warehousing",
        "location": "Pune",
        "title": "Data Warehouse Query Engine Engineer",
        "description": "Optimizes columnar storage query engines, vectorized execution, and distributed transactions.",
        "salary_lpa": 23.00,
        "requirements": {
            "min_cgpa": 8.00,
            "min_attendance_pct": 75.00,
            "required_skills": ["C++", "SQL", "Database Systems", "Operating Systems"],
            "eligible_branches": ["Computer Science & Engineering"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Databricks Unified AI",
        "website": "https://databricks.com",
        "industry": "Data Intelligence & Lakehouse",
        "location": "Bengaluru",
        "title": "Distributed Spark & ML Platform Engineer",
        "description": "Develops enterprise Lakehouse query engines, Delta Lake storage optimizations, and MLflow integrations.",
        "salary_lpa": 24.00,
        "requirements": {
            "min_cgpa": 8.00,
            "min_attendance_pct": 75.00,
            "required_skills": ["Python", "Scala", "SQL", "Machine Learning", "Docker"],
            "eligible_branches": ["Computer Science & Engineering", "AI & Data Science"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Stripe Payments Infrastructure",
        "website": "https://stripe.com",
        "industry": "Financial Technology & Payment APIs",
        "location": "Bengaluru / Remote",
        "title": "FinTech Payment APIs & Security Engineer",
        "description": "Builds idempotent payment routing APIs, fraud detection microservices, and ledger consistency pipelines.",
        "salary_lpa": 22.50,
        "requirements": {
            "min_cgpa": 7.80,
            "min_attendance_pct": 75.00,
            "required_skills": ["Python", "SQL", "Cryptography", "REST API", "Docker"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Palantir Technologies",
        "website": "https://palantir.com",
        "industry": "Enterprise Big Data & Defense Analytics",
        "location": "Bengaluru",
        "title": "Forward Deployed Software Engineer (FDSE)",
        "description": "Solves complex operational problems by implementing large-scale data ontology platforms and analytics APIs.",
        "salary_lpa": 20.00,
        "requirements": {
            "min_cgpa": 7.50,
            "min_attendance_pct": 75.00,
            "required_skills": ["Python", "Java", "SQL", "Data Structures", "Docker"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Qualcomm Wireless Systems",
        "website": "https://qualcomm.com",
        "industry": "Semiconductors & Mobile 5G",
        "location": "Hyderabad / Chennai",
        "title": "Embedded Systems & Edge AI Firmware Engineer",
        "description": "Develops low-level firmware for Snapdragon neural processing engines and 5G baseband modems.",
        "salary_lpa": 16.50,
        "requirements": {
            "min_cgpa": 7.20,
            "min_attendance_pct": 75.00,
            "required_skills": ["C", "C++", "Operating Systems", "Computer Architecture"],
            "eligible_branches": ["Computer Science & Engineering", "Electronics & Communication"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Intel Architecture Labs",
        "website": "https://intel.com",
        "industry": "Semiconductors & Chipset Software",
        "location": "Bengaluru",
        "title": "Silicon Platform & Performance Tuning Engineer",
        "description": "Engineers compiler optimizations, Linux kernel drivers, and high-performance server benchmark suites.",
        "salary_lpa": 15.50,
        "requirements": {
            "min_cgpa": 7.20,
            "min_attendance_pct": 75.00,
            "required_skills": ["C++", "Python", "Linux", "Data Structures"],
            "eligible_branches": ["Computer Science & Engineering", "Electronics & Communication"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Atlassian Collaboration Tools",
        "website": "https://atlassian.com",
        "industry": "Productivity & Developer Tools",
        "location": "Bengaluru",
        "title": "Full Stack Cloud Collaboration Engineer",
        "description": "Develops real-time collaborative document editing engines, Jira microservices, and scalable React UI components.",
        "salary_lpa": 19.00,
        "requirements": {
            "min_cgpa": 7.50,
            "min_attendance_pct": 75.00,
            "required_skills": ["React", "TypeScript", "Python", "FastAPI", "SQL"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    },
    {
        "company_name": "Stripe Global Payments",
        "website": "https://stripe.com",
        "industry": "FinTech & Real-Time Global Payments",
        "location": "Bengaluru / Remote",
        "title": "FinTech Core Payment Infrastructure Engineer",
        "description": "Architects resilient payment processing gateways, ledger consistency models, and multi-tenant APIs.",
        "salary_lpa": 26.00,
        "requirements": {
            "min_cgpa": 7.80,
            "min_attendance_pct": 75.00,
            "required_skills": ["Python", "SQL", "Docker", "Distributed Systems", "REST API"],
            "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
            "max_backlogs": 0
        }
    }
]

def seed_to_47_drives():
    db = SessionLocal()
    try:
        added = 0
        for item in ADDITIONAL_17_DRIVES:
            comp = db.query(Company).filter(Company.name == item["company_name"]).first()
            if not comp:
                comp = Company(
                    name=item["company_name"],
                    website=item["website"],
                    industry=item["industry"],
                    location=item["location"]
                )
                db.add(comp)
                db.commit()
                db.refresh(comp)

            job = db.query(JobRole).filter(JobRole.company_id == comp.id, JobRole.title == item["title"]).first()
            if not job:
                job = JobRole(
                    company_id=comp.id,
                    title=item["title"],
                    description=item["description"],
                    salary_lpa=item["salary_lpa"],
                    location=item["location"]
                )
                db.add(job)
                db.commit()
                db.refresh(job)

                req = JobRequirement(
                    job_role_id=job.id,
                    min_cgpa=item["requirements"]["min_cgpa"],
                    min_attendance_pct=item["requirements"]["min_attendance_pct"],
                    required_skills=item["requirements"]["required_skills"],
                    eligible_branches=item["requirements"]["eligible_branches"],
                    max_backlogs=item["requirements"]["max_backlogs"]
                )
                db.add(req)
                db.commit()
                added += 1

        total_companies = db.query(Company).count()
        total_jobs = db.query(JobRole).count()
        print(f"\n====================================================================")
        print(f">>> 47-DRIVE EXPANSION SEEDER COMPLETE <<<")
        print(f"Added: {added} new drives")
        print(f"Total Companies in DB: {total_companies}")
        print(f"Total Active Placement Job Drives: {total_jobs}")
        print(f"====================================================================")
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_to_47_drives()
