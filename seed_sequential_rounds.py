import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.app.core.database import SessionLocal, engine
from backend.app.models.all_models import Test, Question, Application, PlacementRound, Student

def seed_10q_sequential_rounds():
    db = SessionLocal()
    try:
        print("Creating 10-Question Round 1 Aptitude and 10-Question Round 2 Technical tests...")

        # Delete existing questions for fresh 10-Q setup if needed
        db.query(Question).delete()
        db.query(Test).delete()
        db.commit()

        # 1. Round 1: Aptitude Test (10 Questions)
        aptitude_test = Test(
            title="Round 1: General Aptitude & Logical Reasoning Assessment",
            test_type="aptitude",
            category="General Aptitude",
            duration_minutes=30,
            total_marks=100,
            pass_percentage=60.0,
            is_active=True,
            created_by=1
        )
        db.add(aptitude_test)
        db.commit()
        db.refresh(aptitude_test)

        aptitude_questions = [
            {
                "question_text": "A train running at a speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train in meters?",
                "option_a": "120 meters", "option_b": "150 meters", "option_c": "180 meters", "option_d": "324 meters",
                "correct_option": "B",
                "explanation": "Speed = 60 * (5/18) = 50/3 m/sec. Distance = Speed * Time = (50/3) * 9 = 150 meters.",
                "topic": "Quantitative Aptitude", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "Complete the logical series: 2, 6, 12, 20, 30, ?",
                "option_a": "38", "option_b": "40", "option_c": "42", "option_d": "44",
                "correct_option": "C",
                "explanation": "Pattern differences: +4, +6, +8, +10, +12. Next term is 30 + 12 = 42.",
                "topic": "Logical Reasoning", "difficulty": "easy", "marks": 10
            },
            {
                "question_text": "If 12 men or 18 women can reap a field in 14 days, then 8 men and 16 women can reap it in how many days?",
                "option_a": "5 days", "option_b": "7 days", "option_c": "9 days", "option_d": "10 days",
                "correct_option": "C",
                "explanation": "12 men = 18 women => 1 man = 1.5 women. 8 men + 16 women = 12 + 16 = 28 women. Days = (18 * 14) / 28 = 9 days.",
                "topic": "Time and Work", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "Choose the word most nearly OPPOSITE in meaning to 'METICULOUS':",
                "option_a": "Careful", "option_b": "Careless", "option_c": "Precise", "option_d": "Methodical",
                "correct_option": "B",
                "explanation": "'Meticulous' means extremely careful and precise. The opposite is 'Careless'.",
                "topic": "Verbal Ability", "difficulty": "easy", "marks": 10
            },
            {
                "question_text": "A box contains 5 red, 8 green, and 7 white balls. A ball is drawn at random. What is the probability that it is white or red?",
                "option_a": "3/5", "option_b": "1/4", "option_c": "2/5", "option_d": "7/20",
                "correct_option": "A",
                "explanation": "Total balls = 20. Favorable outcomes = 5 (red) + 7 (white) = 12. Probability = 12/20 = 3/5.",
                "topic": "Probability", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "A sum of money at simple interest amounts to Rs. 815 in 3 years and to Rs. 854 in 4 years. The sum is:",
                "option_a": "Rs. 650", "option_b": "Rs. 690", "option_c": "Rs. 698", "option_d": "Rs. 700",
                "correct_option": "C",
                "explanation": "S.I. for 1 year = Rs. (854 - 815) = Rs. 39. S.I. for 3 years = 39 * 3 = Rs. 117. Principal = 815 - 117 = Rs. 698.",
                "topic": "Interest & Finance", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "Divide Rs. 782 into three parts proportional to 1/2 : 2/3 : 3/4. What is the first part?",
                "option_a": "Rs. 182", "option_b": "Rs. 204", "option_c": "Rs. 272", "option_d": "Rs. 306",
                "correct_option": "B",
                "explanation": "Ratios = 6:8:9. Total ratio sum = 23. First part = 782 * (6/23) = Rs. 204.",
                "topic": "Ratio & Proportion", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "If COMPUTER is written as RFUVQNPC, how is MEDICINE written in that code?",
                "option_a": "EOJDJEFM", "option_b": "EOJDEJFM", "option_c": "MFEJDJOE", "option_d": "MFEDJJOE",
                "correct_option": "A",
                "explanation": "Reverse the word and shift letters: MEDICINE -> ENICIDEM -> EOJDJEFM.",
                "topic": "Coding-Decoding", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "Pointing to a photograph of a boy, Suresh said, 'He is the son of the only son of my mother.' How is Suresh related to that boy?",
                "option_a": "Brother", "option_b": "Uncle", "option_c": "Cousin", "option_d": "Father",
                "correct_option": "D",
                "explanation": "Mother's only son is Suresh himself. So the boy is Suresh's son. Suresh is his father.",
                "topic": "Blood Relations", "difficulty": "easy", "marks": 10
            },
            {
                "question_text": "A trader marks his goods 20% above cost price and allows a discount of 10%. What is his gain percentage?",
                "option_a": "8%", "option_b": "10%", "option_c": "12%", "option_d": "15%",
                "correct_option": "A",
                "explanation": "Cost = 100, Marked = 120, Discount 10% = 12. Selling price = 108. Gain = 8%.",
                "topic": "Profit & Loss", "difficulty": "easy", "marks": 10
            }
        ]

        for q_data in aptitude_questions:
            q = Question(test_id=aptitude_test.id, **q_data)
            db.add(q)
        db.commit()
        print("[OK] Seeded Round 1 Aptitude Test with 10 Questions!")

        # 2. Round 2: Resume-Tailored Technical & Coding Test (10 Questions)
        tech_test = Test(
            title="Round 2: Technical & Coding Knowledge Assessment (Resume-Tailored)",
            test_type="technical",
            category="Software Engineering & Coding",
            duration_minutes=45,
            total_marks=100,
            pass_percentage=65.0,
            is_active=True,
            created_by=1
        )
        db.add(tech_test)
        db.commit()
        db.refresh(tech_test)

        tech_questions = [
            {
                "question_text": "In Python, what is the average time complexity of searching for an element in a set vs a list?",
                "option_a": "Set: O(1) average, List: O(n)", "option_b": "Set: O(n), List: O(1)", "option_c": "Set: O(log n), List: O(n)", "option_d": "Both are O(n)",
                "correct_option": "A",
                "explanation": "Python sets use hash tables allowing O(1) average lookup, whereas lists require O(n) linear search.",
                "topic": "Data Structures", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "Which FastAPI decorator parameter is used to define the HTTP status code returned for successful resource creation?",
                "option_a": "response_model", "option_b": "status_code=status.HTTP_201_CREATED", "option_c": "return_code=201", "option_d": "headers={'status': 201}",
                "correct_option": "B",
                "explanation": "In FastAPI, status_code=status.HTTP_201_CREATED sets the default HTTP response status code.",
                "topic": "FastAPI", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "What SQL clause is used to filter aggregated group results produced by a GROUP BY clause?",
                "option_a": "WHERE", "option_b": "ORDER BY", "option_c": "HAVING", "option_d": "FILTER",
                "correct_option": "C",
                "explanation": "The HAVING clause filters aggregated groups after GROUP BY, whereas WHERE filters individual rows before aggregation.",
                "topic": "Databases & SQL", "difficulty": "easy", "marks": 10
            },
            {
                "question_text": "What does the SOLID 'O' principle (Open/Closed Principle) state?",
                "option_a": "Software entities should be open for modification, closed for extension",
                "option_b": "Software entities should be open for extension, but closed for modification",
                "option_c": "Objects should only open one network socket at a time",
                "option_d": "Code should be open source and closed to commercial use",
                "correct_option": "B",
                "explanation": "Open/Closed Principle states that software components should be open for extension without modifying existing source code.",
                "topic": "Software Architecture", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "Which HTTP method is idempotent and used to replace an entire existing target resource with new content?",
                "option_a": "POST", "option_b": "PATCH", "option_c": "PUT", "option_d": "OPTIONS",
                "correct_option": "C",
                "explanation": "PUT is idempotent and replaces the target resource, while POST is non-idempotent and PATCH performs partial updates.",
                "topic": "RESTful Web APIs", "difficulty": "easy", "marks": 10
            },
            {
                "question_text": "What is the primary architectural difference between a Docker container and a Virtual Machine (VM)?",
                "option_a": "Containers share the host OS kernel; VMs run a full guest OS on a hypervisor",
                "option_b": "VMs share the host OS kernel; Containers require hypervisors",
                "option_c": "Containers can only run Python applications",
                "option_d": "VMs are faster to boot than Docker containers",
                "correct_option": "A",
                "explanation": "Docker containers virtualize the OS layer sharing the host kernel, making them lightweight compared to full guest OS VMs.",
                "topic": "Docker & DevOps", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "In React, how does the Virtual DOM reconciliation algorithm optimize UI re-rendering?",
                "option_a": "By reloading the entire browser page on state changes",
                "option_b": "By comparing the new Virtual DOM tree with a snapshot of the previous tree (diffing) and updating only changed real DOM nodes",
                "option_c": "By converting JavaScript code directly to WebAssembly",
                "option_d": "By bypassing CSS styles",
                "correct_option": "B",
                "explanation": "React uses diffing between Virtual DOM trees to minimize real DOM mutations for optimal rendering performance.",
                "topic": "React Frontend", "difficulty": "medium", "marks": 10
            },
            {
                "question_text": "How does Python's asyncio event loop handle non-blocking asynchronous I/O operations?",
                "option_a": "By spawning a new operating system thread for every single function call",
                "option_b": "By running a single-threaded cooperative event loop that yields execution when encountering `await` on I/O futures",
                "option_c": "By disabling Python's Global Interpreter Lock (GIL)",
                "option_d": "By converting async code into synchronous blocking loops",
                "correct_option": "B",
                "explanation": "Python asyncio uses a single-threaded cooperative event loop where `await` yields execution while waiting for I/O operations.",
                "topic": "Python Async & Concurrency", "difficulty": "hard", "marks": 10
            },
            {
                "question_text": "In relational databases, why are B-Tree indexes preferred over Hash indexes for range queries (`WHERE age BETWEEN 20 AND 30`)?",
                "option_a": "Hash indexes do not support exact equality lookups",
                "option_b": "B-Tree keys are kept in sorted order, enabling efficient range scans, whereas Hash indexes do not maintain key order",
                "option_c": "B-Tree indexes require zero disk space",
                "option_d": "Hash indexes are slower for single value lookups",
                "correct_option": "B",
                "explanation": "B-Trees preserve key order allowing log(n) range traversal, while hash tables bucket keys non-sequentially.",
                "topic": "Databases & Indexing", "difficulty": "hard", "marks": 10
            },
            {
                "question_text": "Which load balancing algorithm distributes incoming network requests to servers sequentially, wrapping around to the first server after the last?",
                "option_a": "Least Connections", "option_b": "Round-Robin", "option_c": "IP Hash", "option_d": "Random Selection",
                "correct_option": "B",
                "explanation": "Round-Robin distributes requests across a server pool in sequential rotational order.",
                "topic": "System Design", "difficulty": "easy", "marks": 10
            }
        ]

        for q_data in tech_questions:
            q = Question(test_id=tech_test.id, **q_data)
            db.add(q)
        db.commit()
        print("[OK] Seeded Round 2 Technical Test with 10 Questions!")

        print("\n====================================================================")
        print(">>> 10-QUESTION RESUME-DRIVEN SEQUENTIAL WORKFLOW SEEDER COMPLETE <<<")
        print("====================================================================")

    except Exception as e:
        print(f"Error seeding 10-Q sequential rounds: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_10q_sequential_rounds()
