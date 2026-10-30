import random
from typing import List, Dict, Any

FALLBACK_QUESTION_BANK = [
    # Python
    {
        "topic": "Python",
        "difficulty": "medium",
        "question_text": "Can you explain how Python manages memory, specifically focusing on reference counting and garbage collection?",
        "expected_concepts": ["reference counting", "garbage collection", "cyclic references", "memory leaks"],
        "ideal_summary": "Python uses reference counting as its primary memory management mechanism along with a generational garbage collector to detect reference cycles."
    },
    {
        "topic": "Python",
        "difficulty": "medium",
        "question_text": "What are Python generators and decorators, and how do yield statements improve memory performance during large data processing?",
        "expected_concepts": ["generators", "decorators", "yield", "memory efficiency", "iterators"],
        "ideal_summary": "Generators produce items lazily using yield, consuming low memory compared to lists. Decorators wrap functions to add cross-cutting behavior."
    },
    {
        "topic": "Python",
        "difficulty": "hard",
        "question_text": "Explain Python's Global Interpreter Lock (GIL), how it affects multi-threading, and how to achieve true concurrency with multiprocessing or async execution.",
        "expected_concepts": ["gil", "multithreading", "multiprocessing", "asyncio", "concurrency"],
        "ideal_summary": "The GIL prevents multiple threads from executing Python bytecode simultaneously. For CPU-bound tasks, use multiprocessing or native extensions; for I/O-bound tasks, use asyncio or threads."
    },
    {
        "topic": "Python",
        "difficulty": "easy",
        "question_text": "What is the difference between mutable and immutable data types in Python, and how does it impact function parameter passing?",
        "expected_concepts": ["mutable", "immutable", "pass by object reference", "lists", "tuples"],
        "ideal_summary": "Immutable objects like tuples/strings cannot be modified in-place, whereas mutable objects like lists/dicts pass references that can be modified inside functions."
    },

    # FastAPI
    {
        "topic": "FastAPI",
        "difficulty": "medium",
        "question_text": "What makes FastAPI so performant, and how does it utilize Pydantic and async/await syntax?",
        "expected_concepts": ["async", "await", "starlette", "pydantic", "validation"],
        "ideal_summary": "FastAPI leverages Starlette for asynchronous ASGI performance and Pydantic for automated data validation, type hints, and OpenAPI schema generation."
    },
    {
        "topic": "FastAPI",
        "difficulty": "medium",
        "question_text": "How does FastAPI handle dependency injection, background tasks, and custom middleware?",
        "expected_concepts": ["depends", "dependency injection", "backgroundtasks", "middleware", "asgi"],
        "ideal_summary": "FastAPI uses Depends() for hierarchical dependency injection and supports executing non-blocking background tasks after returning HTTP responses."
    },
    {
        "topic": "FastAPI",
        "difficulty": "hard",
        "question_text": "Explain how OAuth2 with Password hashing and JWT tokens is implemented securely in a production FastAPI application.",
        "expected_concepts": ["oauth2", "jwt", "passlib", "bcrypt", "bearer token", "authentication"],
        "ideal_summary": "OAuth2 password flow validates user credentials using passlib/bcrypt hashing and issues signed JSON Web Tokens (JWT) for stateless bearer authentication."
    },

    # SQL & Databases
    {
        "topic": "SQL & Databases",
        "difficulty": "medium",
        "question_text": "Explain the difference between clustered and non-clustered indexes in relational databases, and when would you avoid creating an index?",
        "expected_concepts": ["clustered index", "b-tree", "physical order", "write overhead"],
        "ideal_summary": "A clustered index determines the physical storage order of table data, while non-clustered indexes maintain a separate lookup pointer structure. Avoid over-indexing high write tables."
    },
    {
        "topic": "SQL & Databases",
        "difficulty": "hard",
        "question_text": "What are the ACID properties in relational databases, and how do isolation levels (Read Committed vs Serializable) handle concurrent transactions?",
        "expected_concepts": ["acid", "atomicity", "consistency", "isolation", "durability", "locking"],
        "ideal_summary": "ACID ensures transaction reliability. Isolation levels trade concurrency speed against phenomena like dirty reads, non-repeatable reads, and phantom reads."
    },
    {
        "topic": "SQL & Databases",
        "difficulty": "medium",
        "question_text": "Compare SQL relational databases with NoSQL document stores (like MongoDB/DynamoDB) in terms of schema flexibility and horizontal scalability.",
        "expected_concepts": ["relational", "nosql", "horizontal scaling", "sharding", "schema"],
        "ideal_summary": "SQL databases prioritize ACID compliance and schema rigidity, while NoSQL document stores enable dynamic schema flexibility and effortless horizontal partitioning."
    },

    # React
    {
        "topic": "React",
        "difficulty": "medium",
        "question_text": "How does React's Virtual DOM and reconciliation algorithm work, and why are keys essential when rendering dynamic lists?",
        "expected_concepts": ["virtual dom", "reconciliation", "diffing", "keys", "render"],
        "ideal_summary": "React maintains a virtual DOM tree and uses a diffing algorithm during reconciliation to apply minimal updates to the real DOM. Stable keys allow React to identify moved or changed elements."
    },
    {
        "topic": "React",
        "difficulty": "medium",
        "question_text": "Explain the React Component Lifecycle, state management, and the difference between useEffect, useMemo, and useCallback hooks.",
        "expected_concepts": ["useeffect", "usememo", "usecallback", "state", "hooks", "memoization"],
        "ideal_summary": "useEffect runs side effects after rendering. useMemo caches expensive calculated values, while useCallback memoizes function instances to avoid re-renders."
    },
    {
        "topic": "React",
        "difficulty": "hard",
        "question_text": "How do you optimize render performance in a large-scale React application dealing with heavy real-time data feeds?",
        "expected_concepts": ["react memo", "virtualization", "lazy loading", "code splitting", "state colocation"],
        "ideal_summary": "Use React.memo, windowing/virtualization libraries (react-window), code splitting with Suspense, and state colocation to minimize unnecessary component re-renders."
    },

    # Docker & DevOps
    {
        "topic": "Docker & DevOps",
        "difficulty": "medium",
        "question_text": "What is the difference between a Docker image and container, and how does multi-stage builds reduce image size?",
        "expected_concepts": ["image", "container", "layers", "multi-stage", "cache"],
        "ideal_summary": "A Docker image is a read-only template with application code and dependencies, while a container is an isolated running instance. Multi-stage builds discard build tools to keep production images lightweight."
    },
    {
        "topic": "Docker & DevOps",
        "difficulty": "medium",
        "question_text": "Explain CI/CD pipelines, container orchestration with Kubernetes, and how rolling deployments prevent downtime.",
        "expected_concepts": ["ci/cd", "kubernetes", "rolling update", "pods", "deployments"],
        "ideal_summary": "CI/CD automates testing and deployment. Kubernetes orchestrates containers across clusters using rolling updates to replace old pods with new ones without service interruption."
    },

    # Java
    {
        "topic": "Java",
        "difficulty": "medium",
        "question_text": "Explain how the Java Virtual Machine manages heap memory and the difference between minor and major garbage collection.",
        "expected_concepts": ["jvm", "heap", "stack", "garbage collection", "eden space"],
        "ideal_summary": "The JVM divides heap space into Young (Eden, Survivor) and Tenured/Old generation. Minor GC cleans short-lived objects in Young generation, while Major GC collects the Old generation."
    },
    {
        "topic": "Java",
        "difficulty": "hard",
        "question_text": "What is Java thread safety, synchronized blocks, and how do ConcurrentHashMap and Volatile keywords operate?",
        "expected_concepts": ["thread safety", "synchronized", "volatile", "concurrenthashmap", "atomic"],
        "ideal_summary": "Volatile guarantees memory visibility across threads. Synchronized blocks acquire monitor locks. ConcurrentHashMap provides fine-grained lock striping for concurrent access."
    },

    # Machine Learning & AI
    {
        "topic": "Machine Learning & AI",
        "difficulty": "medium",
        "question_text": "Explain the bias-variance tradeoff in machine learning and how regularization techniques prevent model overfitting.",
        "expected_concepts": ["bias", "variance", "overfitting", "regularization", "generalization"],
        "ideal_summary": "High bias leads to underfitting while high variance causes overfitting to training noise. Regularization penalties like L1/L2 constrain model complexity to achieve optimal generalization."
    },
    {
        "topic": "Machine Learning & AI",
        "difficulty": "hard",
        "question_text": "How do Transformer neural network architectures work, specifically focusing on self-attention mechanisms and positional encoding?",
        "expected_concepts": ["transformer", "self-attention", "positional encoding", "query key value", "llm"],
        "ideal_summary": "Transformers calculate parallel self-attention scores across sequence tokens using Query, Key, and Value matrices, augmented with positional encodings to model sequential dependencies."
    },

    # Cloud & AWS
    {
        "topic": "Cloud & AWS",
        "difficulty": "medium",
        "question_text": "How do you design a highly available and fault-tolerant system on cloud infrastructure using load balancers and auto-scaling?",
        "expected_concepts": ["load balancer", "auto scaling", "redundancy", "stateless", "failover"],
        "ideal_summary": "High availability is achieved by deploying stateless application tiers behind load balancers across multiple availability zones with automated health checks and auto-scaling."
    },

    # REST API
    {
        "topic": "REST API",
        "difficulty": "easy",
        "question_text": "Describe the key HTTP methods in RESTful architecture and what it means for an HTTP method to be idempotent.",
        "expected_concepts": ["get", "post", "put", "delete", "idempotent", "stateless"],
        "ideal_summary": "REST uses standard HTTP methods where GET, PUT, and DELETE are idempotent because executing them multiple times produces identical server state outcomes."
    },

    # Data Structures
    {
        "topic": "Data Structures",
        "difficulty": "medium",
        "question_text": "How does a hash table resolve hash collisions, and what is its average versus worst-case time complexity?",
        "expected_concepts": ["chaining", "open addressing", "hash function", "o(1)", "o(n)"],
        "ideal_summary": "Hash tables resolve collisions using separate chaining with linked lists or open addressing probing. Lookup is O(1) average but degrades to O(n) under severe collisions."
    },

    # HR & Behavioral
    {
        "topic": "HR & Behavioral",
        "difficulty": "medium",
        "question_text": "Tell me about a challenging project problem you faced, how you diagnosed it, and what technical steps resolved it.",
        "expected_concepts": ["problem", "root cause", "solution", "teamwork", "learning"],
        "ideal_summary": "The candidate outlines a clear STAR scenario articulating technical root-cause analysis, proactive debugging steps, and takeaways."
    },
    {
        "topic": "HR & Behavioral",
        "difficulty": "easy",
        "question_text": "How do you handle technical disagreements within a development team regarding architectural or code quality choices?",
        "expected_concepts": ["collaboration", "communication", "tradeoffs", "benchmarking", "consensus"],
        "ideal_summary": "Discuss tradeoffs objectively using data, benchmarks, and prototype proof-of-concepts, adhering to agreed team conventions once a consensus or decision is made."
    }
]

class QuestionGenerator:
    @staticmethod
    def generate_interview_questions(
        job_title: str = "Software Engineer",
        resume_skills: List[str] = None,
        count: int = 4
    ) -> List[Dict[str, Any]]:
        questions = []
        resume_skills_lower = [s.lower().strip() for s in (resume_skills or []) if s]

        # Randomize bank copy so questions are randomized on every call!
        bank_copy = list(FALLBACK_QUESTION_BANK)
        random.shuffle(bank_copy)

        matched_topics = set()
        matched_question_ids = set()

        # 1. Resume-Derived Question Matching
        for q in bank_copy:
            topic_lower = q["topic"].lower()
            is_match = False
            matched_skill = None
            for s in resume_skills_lower:
                if s in topic_lower or any(part in s for part in topic_lower.split('&')):
                    is_match = True
                    matched_skill = s.title()
                    break
            
            if is_match and q["topic"] not in matched_topics:
                matched_topics.add(q["topic"])
                resume_matched_q = dict(q)
                resume_matched_q["is_resume_derived"] = True
                resume_matched_q["source_resume_keyword"] = matched_skill or q["topic"]
                questions.append(resume_matched_q)
                matched_question_ids.add(q["question_text"])
                if len(questions) >= count - 1:
                    break

        # 2. General Technical & Core Questions from Bank
        for q in bank_copy:
            if len(questions) >= count:
                break
            if q["question_text"] not in matched_question_ids and q["topic"] not in matched_topics:
                general_q = dict(q)
                general_q["is_resume_derived"] = False
                general_q["source_resume_keyword"] = None
                questions.append(general_q)
                matched_topics.add(q["topic"])
                matched_question_ids.add(q["question_text"])

        # 3. Fallback if count not reached yet
        for q in bank_copy:
            if len(questions) >= count:
                break
            if q["question_text"] not in matched_question_ids:
                fallback_q = dict(q)
                fallback_q["is_resume_derived"] = False
                fallback_q["source_resume_keyword"] = None
                questions.append(fallback_q)
                matched_question_ids.add(q["question_text"])

        # Final shuffle of selected questions so order varies too
        random.shuffle(questions)
        return questions[:count]
