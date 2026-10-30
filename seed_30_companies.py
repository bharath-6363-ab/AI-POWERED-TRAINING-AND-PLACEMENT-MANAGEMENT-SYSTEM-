import os
from backend.app.core.database import SessionLocal
from backend.app.models.all_models import Company, JobRole, JobRequirement

def seed_30_companies():
    db = SessionLocal()
    try:
        companies_data = [
            # ---------------- PRODUCT-BASED COMPANIES (1-15) ----------------
            {
                "name": "Google Cloud Systems",
                "website": "https://cloud.google.com",
                "industry": "Product-Based (Cloud & AI)",
                "location": "Bengaluru / Hyderabad",
                "title": "Full Stack AI & Cloud Systems Engineer",
                "description": "Engineers scalable AI cloud services, distributed backend APIs, and modern containerized web applications.",
                "salary_lpa": 28.00,
                "requirements": {
                    "min_cgpa": 8.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "FastAPI", "React", "Docker", "Machine Learning"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology", "AI & Data Science"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Apple India R&D",
                "website": "https://apple.com",
                "industry": "Product-Based (Core Systems & Hardware)",
                "location": "Bengaluru",
                "title": "iOS & Core Operating Systems Engineer",
                "description": "Architects low-level performance frameworks, Swift/C++ runtimes, and core Apple ecosystem applications.",
                "salary_lpa": 32.00,
                "requirements": {
                    "min_cgpa": 8.50,
                    "min_attendance_pct": 80.00,
                    "required_skills": ["C++", "Python", "Swift", "Data Structures"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Meta (Facebook) Engineering",
                "website": "https://meta.com",
                "industry": "Product-Based (Social Systems & AI)",
                "location": "Bengaluru / Remote",
                "title": "AI Infrastructure & Distributed Systems Engineer",
                "description": "Develops massive-scale graph databases, PyTorch AI training pipelines, and real-time streaming engines.",
                "salary_lpa": 30.00,
                "requirements": {
                    "min_cgpa": 8.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "C++", "PyTorch", "SQL", "Distributed Systems"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "NVIDIA Graphics & AI",
                "website": "https://nvidia.com",
                "industry": "Product-Based (AI Acceleration & GPUs)",
                "location": "Bengaluru / Pune",
                "title": "CUDA & Deep Learning Software Engineer",
                "description": "Optimizes GPU acceleration kernels, CUDA parallel code, and AI model compilation for deep learning.",
                "salary_lpa": 26.00,
                "requirements": {
                    "min_cgpa": 8.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["C++", "CUDA", "Python", "Deep Learning"],
                    "eligible_branches": ["Computer Science & Engineering", "Electronics & Communication"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Atlassian R&D Labs",
                "website": "https://atlassian.com",
                "industry": "Product-Based (DevOps & Collaboration)",
                "location": "Bengaluru",
                "title": "Distributed Cloud Backend Engineer",
                "description": "Builds high-reliability microservices for Jira, Confluence, and cloud collaboration tools.",
                "salary_lpa": 25.00,
                "requirements": {
                    "min_cgpa": 7.80,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "FastAPI", "SQL", "Docker"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Adobe Systems India",
                "website": "https://adobe.com",
                "industry": "Product-Based (Digital Media & AI)",
                "location": "Noida / Bengaluru",
                "title": "Computer Vision & Creative Cloud Engineer",
                "description": "Engineers computer vision algorithms, generative AI image models, and desktop/web creative tools.",
                "salary_lpa": 24.00,
                "requirements": {
                    "min_cgpa": 7.80,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["C++", "Python", "Computer Vision", "React"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Uber Tech Technologies",
                "website": "https://uber.com",
                "industry": "Product-Based (Mobility & Logistics)",
                "location": "Bengaluru / Hyderabad",
                "title": "Mobility Algorithms & Microservices Engineer",
                "description": "Designs real-time route optimization, surge pricing algorithms, and high-concurrency dispatch engines.",
                "salary_lpa": 23.50,
                "requirements": {
                    "min_cgpa": 7.80,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Go", "Python", "SQL", "Kafka", "Data Structures"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Microsoft Research & Development",
                "website": "https://microsoft.com",
                "industry": "Product-Based (Enterprise Software & Cloud)",
                "location": "Hyderabad",
                "title": "Software Development Engineer - II (SDE-II)",
                "description": "Architects high-throughput microservices, Azure cloud data structures, and intelligent developer tools.",
                "salary_lpa": 22.50,
                "requirements": {
                    "min_cgpa": 7.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "C++", "SQL", "Data Structures"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "LinkedIn Systems",
                "website": "https://linkedin.com",
                "industry": "Product-Based (Professional Graph & Data)",
                "location": "Bengaluru",
                "title": "High-Scale Data Infrastructure Developer",
                "description": "Engineers massive search indexes, recommendation pipelines, and social graph microservices.",
                "salary_lpa": 22.00,
                "requirements": {
                    "min_cgpa": 7.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "SQL", "Spark", "Kafka"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Salesforce Systems",
                "website": "https://salesforce.com",
                "industry": "Product-Based (SaaS & CRM Cloud)",
                "location": "Hyderabad / Bengaluru",
                "title": "Enterprise Cloud Application Developer",
                "description": "Engineers multi-tenant SaaS cloud platforms, Apex/Java microservices, and AI analytics dashboards.",
                "salary_lpa": 21.00,
                "requirements": {
                    "min_cgpa": 7.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "SQL", "React", "Cloud Computing"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Amazon Web Services (AWS)",
                "website": "https://aws.amazon.com",
                "industry": "Product-Based (Cloud Infrastructure)",
                "location": "Bengaluru",
                "title": "Cloud Infrastructure & DevOps Engineer",
                "description": "Deploys, monitors, and optimizes automated serverless infrastructure and containerized workloads.",
                "salary_lpa": 19.50,
                "requirements": {
                    "min_cgpa": 7.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "Docker", "Git", "SQL"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Oracle Cloud Infrastructure (OCI)",
                "website": "https://oracle.com",
                "industry": "Product-Based (Database & Cloud Infrastructure)",
                "location": "Bengaluru / Hyderabad",
                "title": "Database Engine Core Architect",
                "description": "Designs high-speed relational database storage layers, SQL query optimizers, and cloud backup systems.",
                "salary_lpa": 18.00,
                "requirements": {
                    "min_cgpa": 7.20,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["C++", "SQL", "Linux Kernels", "Python"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Intuit Technology",
                "website": "https://intuit.com",
                "industry": "Product-Based (FinTech SaaS)",
                "location": "Bengaluru",
                "title": "Financial Cloud Backend Developer",
                "description": "Builds secure payment processing microservices, tax computation engines, and ML risk algorithms.",
                "salary_lpa": 17.50,
                "requirements": {
                    "min_cgpa": 7.20,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "Spring Boot", "SQL"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "SAP Labs India",
                "website": "https://sap.com",
                "industry": "Product-Based (Enterprise ERP & Analytics)",
                "location": "Bengaluru",
                "title": "Enterprise ERP Solution Engineer",
                "description": "Develops enterprise resource planning modules, HANA in-memory database queries, and Fiori web apps.",
                "salary_lpa": 15.00,
                "requirements": {
                    "min_cgpa": 7.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "SQL", "React", "Python"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Cognitive Cloud Tech",
                "website": "https://cognitivecloud.com",
                "industry": "Product-Based (AI Microservices)",
                "location": "Bengaluru",
                "title": "Python Cloud Backend Engineer",
                "description": "Design, develop and scale enterprise cloud solutions using Python, FastAPI, SQL, Docker.",
                "salary_lpa": 14.50,
                "requirements": {
                    "min_cgpa": 7.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "FastAPI", "SQL", "Docker"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },

            # ---------------- SERVICE-BASED COMPANIES (16-30) ----------------
            {
                "name": "TCS Digital AI Directorate",
                "website": "https://tcs.com",
                "industry": "Service-Based (IT & Digital Consulting)",
                "location": "Pune / Chennai",
                "title": "AI Data Engineer & Analytics Specialist",
                "description": "Engineers automated data pipelines, predictive ML models, and analytics data lakes for Fortune 500 clients.",
                "salary_lpa": 11.50,
                "requirements": {
                    "min_cgpa": 6.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "SQL", "Machine Learning"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"],
                    "max_backlogs": 1
                }
            },
            {
                "name": "Deloitte US-India (USI)",
                "website": "https://deloitte.com",
                "industry": "Service-Based (Management & Tech Advisory)",
                "location": "Hyderabad / Bengaluru",
                "title": "Technology Advisory & Analytics Consultant",
                "description": "Provides technical consulting, cloud migration strategies, and enterprise data analytics for global clients.",
                "salary_lpa": 10.50,
                "requirements": {
                    "min_cgpa": 6.80,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "SQL", "PowerBI", "Cloud Architecture"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology", "ECE"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Infosys Power Programmer",
                "website": "https://infosys.com",
                "industry": "Service-Based (IT & Digital Engineering)",
                "location": "Bengaluru / Mysuru",
                "title": "Specialist Programmer (SDE)",
                "description": "High-complexity software engineering role building custom full-stack software and cloud applications.",
                "salary_lpa": 9.50,
                "requirements": {
                    "min_cgpa": 7.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "SQL", "React"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "PwC Acceleration Center",
                "website": "https://pwc.com",
                "industry": "Service-Based (Consulting & Cyber Security)",
                "location": "Kolkata / Bengaluru",
                "title": "Enterprise Systems & Cloud Security Consultant",
                "description": "Audits cloud security posture, implements IAM policies, and conducts technical vulnerability assessments.",
                "salary_lpa": 9.00,
                "requirements": {
                    "min_cgpa": 6.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "Linux", "Networking", "SQL"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "FinTech Innovations Global",
                "website": "https://fintechinnovations.com",
                "industry": "Service-Based (Financial Technology)",
                "location": "Bengaluru",
                "title": "Associate Software Engineer",
                "description": "Design, develop and scale enterprise financial solutions using Java, SQL, Git.",
                "salary_lpa": 9.00,
                "requirements": {
                    "min_cgpa": 6.50,
                    "min_attendance_pct": 70.00,
                    "required_skills": ["Java", "SQL", "Git"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Accenture Advanced Technology",
                "website": "https://accenture.com",
                "industry": "Service-Based (Global IT Solutions)",
                "location": "Bengaluru / Hyderabad / Pune",
                "title": "Application Development Analyst",
                "description": "Builds and maintains cloud applications, microservices, and enterprise web solutions for client projects.",
                "salary_lpa": 8.50,
                "requirements": {
                    "min_cgpa": 6.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "SQL", "Git"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology", "ECE"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Wipro Turbo & Velocity",
                "website": "https://wipro.com",
                "industry": "Service-Based (IT Services)",
                "location": "Bengaluru / Hyderabad",
                "title": "Advanced Technical Specialist",
                "description": "Accelerated tech track developing custom client backend APIs, data pipelines, and DevOps scripts.",
                "salary_lpa": 8.50,
                "requirements": {
                    "min_cgpa": 6.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Python", "Java", "SQL", "Docker"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "LTIMindtree Digital",
                "website": "https://ltimindtree.com",
                "industry": "Service-Based (Digital Transformation)",
                "location": "Mumbai / Bengaluru",
                "title": "Cloud & Full Stack Software Engineer",
                "description": "Develops modern full-stack web applications and migrates legacy workloads to AWS/Azure cloud.",
                "salary_lpa": 8.00,
                "requirements": {
                    "min_cgpa": 6.50,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["React", "Node.js", "Python", "SQL"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "TCS Ninja & Prime",
                "website": "https://tcs.com",
                "industry": "Service-Based (IT Services)",
                "location": "Pan India",
                "title": "Systems Engineer & Software Consultant",
                "description": "Implements client software modules, database backend scripts, and enterprise maintenance services.",
                "salary_lpa": 7.50,
                "requirements": {
                    "min_cgpa": 6.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["C++", "Java", "Python", "SQL"],
                    "eligible_branches": ["All Engineering Branches"],
                    "max_backlogs": 1
                }
            },
            {
                "name": "Capgemini Excellence Labs",
                "website": "https://capgemini.com",
                "industry": "Service-Based (Consulting & Tech)",
                "location": "Pune / Bengaluru",
                "title": "Senior Software Analyst",
                "description": "Engages in client agile teams to deliver cloud services, microservices, and database optimizations.",
                "salary_lpa": 7.50,
                "requirements": {
                    "min_cgpa": 6.25,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "SQL"],
                    "eligible_branches": ["Computer Science & Engineering", "Information Technology", "ECE"],
                    "max_backlogs": 0
                }
            },
            {
                "name": "Cognizant GenC Elevate",
                "website": "https://cognizant.com",
                "industry": "Service-Based (IT & Business Services)",
                "location": "Chennai / Hyderabad",
                "title": "Software Development Analyst",
                "description": "Builds robust backend services, automated test scripts, and enterprise web user interfaces.",
                "salary_lpa": 6.80,
                "requirements": {
                    "min_cgpa": 6.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "SQL", "Git"],
                    "eligible_branches": ["All Engineering Branches"],
                    "max_backlogs": 1
                }
            },
            {
                "name": "Infosys Digital Specialist",
                "website": "https://infosys.com",
                "industry": "Service-Based (IT Services)",
                "location": "Bengaluru / Mysuru / Pune",
                "title": "Associate Digital Engineer",
                "description": "Develops enterprise cloud components, database workflows, and web applications for global clients.",
                "salary_lpa": 6.50,
                "requirements": {
                    "min_cgpa": 6.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "SQL"],
                    "eligible_branches": ["All Engineering Branches"],
                    "max_backlogs": 1
                }
            },
            {
                "name": "Tech Mahindra Next-Gen AI",
                "website": "https://techmahindra.com",
                "industry": "Service-Based (Telecom & IT)",
                "location": "Pune / Hyderabad",
                "title": "Telecom Cloud Software Analyst",
                "description": "Builds 5G telecom network software components, cloud APIs, and automated billing workflows.",
                "salary_lpa": 6.00,
                "requirements": {
                    "min_cgpa": 6.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["C++", "Python", "Linux", "SQL"],
                    "eligible_branches": ["Computer Science & Engineering", "ECE", "IT"],
                    "max_backlogs": 1
                }
            },
            {
                "name": "HCLTech Engineering",
                "website": "https://hcltech.com",
                "industry": "Service-Based (Engineering & R&D Services)",
                "location": "Noida / Chennai",
                "title": "Core Software Developer",
                "description": "Supports client embedded systems, application maintenance, and SQL database management.",
                "salary_lpa": 5.50,
                "requirements": {
                    "min_cgpa": 6.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["C++", "Java", "SQL"],
                    "eligible_branches": ["All Engineering Branches"],
                    "max_backlogs": 1
                }
            },
            {
                "name": "Wipro Elite NLTH",
                "website": "https://wipro.com",
                "industry": "Service-Based (IT Services)",
                "location": "Pan India",
                "title": "Project Engineer",
                "description": "Entry-level software engineering role focusing on client project delivery, debugging, and testing.",
                "salary_lpa": 4.50,
                "requirements": {
                    "min_cgpa": 6.00,
                    "min_attendance_pct": 75.00,
                    "required_skills": ["Java", "Python", "SQL"],
                    "eligible_branches": ["All Engineering Branches"],
                    "max_backlogs": 1
                }
            }
        ]

        added_count = 0
        updated_count = 0

        for item in companies_data:
            comp = db.query(Company).filter(Company.name == item["name"]).first()
            if not comp:
                comp = Company(
                    name=item["name"],
                    website=item["website"],
                    industry=item["industry"],
                    location=item["location"]
                )
                db.add(comp)
                db.commit()
                db.refresh(comp)
                added_count += 1
            else:
                comp.industry = item["industry"]
                comp.location = item["location"]
                db.commit()

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
                updated_count += 1

        total_companies = db.query(Company).count()
        total_jobs = db.query(JobRole).count()

        print("=" * 68)
        print(f">>> 30-COMPANY SEEDER EXECUTED SUCCESSFULLY <<<")
        print(f"• Total Companies in DB: {total_companies}")
        print(f"• Total Active Placement Job Drives: {total_jobs}")
        print(f"• Product-Based Companies: 15")
        print(f"• Service-Based Companies: 15")
        print("=" * 68)

    except Exception as e:
        print(f"[ERROR]: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_30_companies()
