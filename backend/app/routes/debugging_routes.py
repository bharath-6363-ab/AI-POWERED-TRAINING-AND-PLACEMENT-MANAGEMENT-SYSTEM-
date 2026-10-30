import os
import json
import uuid
import random
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.app.core.deps import get_current_user_optional, User
from backend.app.core.config import settings

router = APIRouter(prefix="/debugging", tags=["AI Code Debugging & Review Studio"])

# ==============================================================================
# CURATED REAL-WORLD PRODUCTION BUG REPOSITORY (FAANG & TIER-1 SDE ROUNDS)
# ==============================================================================
DEBUGGING_CHALLENGES: List[Dict[str, Any]] = [
    {
        "id": "py-mutable-default",
        "title": "E-Commerce Cart State Corruption",
        "language": "python",
        "category": "Memory & Global State",
        "difficulty": "Medium",
        "companies": ["Amazon", "Cisco", "Razorpay"],
        "buggy_line": 2,
        "bug_type": "Mutable Default Parameter Mutation",
        "hint": "In Python, default arguments are evaluated once when the function is defined, not each time it is called.",
        "code": """def add_to_cart(item_id: str, quantity: int = 1, cart_items: list = []):
    cart_items.append({"item_id": item_id, "qty": quantity})
    total_items = len(cart_items)
    return {
        "status": "success",
        "cart": cart_items,
        "count": total_items
    }

# Simulation: Two different users calling without cart_items
user_1_cart = add_to_cart("SKU-LAPTOP-01")
user_2_cart = add_to_cart("SKU-PHONE-99")
# Bug: user_2 receives user_1's item in their cart!""",
        "ideal_explanation": "Using a mutable object (list []) as a default parameter causes the same list instance to be shared across all subsequent invocations. In production web servers with concurrent user requests, this results in cross-user data leakage and session corruption.",
        "refactored_code": """def add_to_cart(item_id: str, quantity: int = 1, cart_items: list = None):
    # Fix: Guard against mutable default parameter
    if cart_items is None:
        cart_items = []
    
    cart_items.append({"item_id": item_id, "qty": quantity})
    total_items = len(cart_items)
    return {
        "status": "success",
        "cart": cart_items,
        "count": total_items
    }""",
        "expected_keywords": ["mutable", "default", "none", "shared", "leak", "evaluated once"]
    },
    {
        "id": "sql-injection-orm-bypass",
        "title": "Raw Query SQL Injection & Unsanitized Filter",
        "language": "sql",
        "category": "Security & Data Integrity",
        "difficulty": "Hard",
        "companies": ["Oracle", "Deloitte USI", "Goldman Sachs"],
        "buggy_line": 5,
        "bug_type": "Direct SQL String Interpolation (SQLi)",
        "hint": "Check how candidate_role and branch variables are appended into the raw SQL string.",
        "code": """def search_eligible_students(db_cursor, role_filter: str, min_cgpa: float):
    # Constructing dynamic query for campus placement drive
    base_query = "SELECT id, name, cgpa, branch FROM students WHERE cgpa >= %s"
    
    # Vulnerability on line 5: Unsafe format string injection
    final_query = base_query + f" AND target_role = '{role_filter}'"
    
    db_cursor.execute(final_query, (min_cgpa,))
    return db_cursor.fetchall()

# Exploit payload: role_filter = "SDE' OR '1'='1"
# Result: Entire unredacted student database dumped!""",
        "ideal_explanation": "Line 5 directly concatenates user-supplied input into the raw SQL statement using an f-string instead of parameterized query bindings (%s). An attacker can inject SQL syntax to bypass authentication, dump sensitive candidate data, or modify records.",
        "refactored_code": """def search_eligible_students(db_cursor, role_filter: str, min_cgpa: float):
    # Fix: Use parameterized placeholders for all dynamic inputs
    query = "SELECT id, name, cgpa, branch FROM students WHERE cgpa >= %s AND target_role = %s"
    
    db_cursor.execute(query, (min_cgpa, role_filter))
    return db_cursor.fetchall()""",
        "expected_keywords": ["parameterized", "sql injection", "sqli", "concatenation", "binding", "placeholder", "f-string"]
    },
    {
        "id": "js-async-race-condition",
        "title": "Async Payment Gateway Race Condition",
        "language": "javascript",
        "category": "Async & Concurrency",
        "difficulty": "Hard",
        "companies": ["Uber", "Flipkart", "Paytm"],
        "buggy_line": 6,
        "bug_type": "Missing Await in Async Wallet Deduction",
        "hint": "Look at how balance deduction is handled before confirming payment authorization.",
        "code": """async function processPlacementRegistration(studentId, feeAmount) {
    const student = await db.students.findById(studentId);
    if (student.walletBalance < feeAmount) {
        throw new Error("Insufficient funds for exam fee");
    }

    // Line 6: Non-blocking call without await creates critical race condition!
    db.students.updateBalance(studentId, student.walletBalance - feeAmount);

    const receipt = await paymentGateway.charge({
        studentId,
        amount: feeAmount,
        currency: "INR"
    });

    return { status: "registered", receiptId: receipt.id };
}""",
        "ideal_explanation": "Line 6 initiates a database balance update without an 'await' keyword. In high-traffic campus registration drives, concurrent requests can execute simultaneously before the wallet balance updates in the DB, leading to double-spending / race condition exploitation.",
        "refactored_code": """async function processPlacementRegistration(studentId, feeAmount) {
    const student = await db.students.findById(studentId);
    if (student.walletBalance < feeAmount) {
        throw new Error("Insufficient funds for exam fee");
    }

    // Fix: Await the database balance deduction within a transactional lock
    await db.students.updateBalance(studentId, student.walletBalance - feeAmount);

    const receipt = await paymentGateway.charge({
        studentId,
        amount: feeAmount,
        currency: "INR"
    });

    return { status: "registered", receiptId: receipt.id };
}""",
        "expected_keywords": ["await", "race condition", "promise", "async", "transaction", "double spending", "non-blocking"]
    },
    {
        "id": "java-concurrent-modification",
        "title": "Thread-Unsafe Active Drive List Cleanup",
        "language": "java",
        "category": "Collections & Concurrency",
        "difficulty": "Medium",
        "companies": ["TCS Digital", "Morgan Stanley", "Infosys DSE"],
        "buggy_line": 4,
        "bug_type": "Direct Collection Modification during Enhanced For-Loop",
        "hint": "Modifying an ArrayList while iterating over it via an enhanced for-loop throws a runtime exception.",
        "code": """public void purgeExpiredJobDrives(List<JobDrive> activeDrives) {
    LocalDate today = LocalDate.now();
    
    // Line 4: Attempting to remove element while traversing throws ConcurrentModificationException!
    for (JobDrive drive : activeDrives) {
        if (drive.getDeadline().isBefore(today)) {
            activeDrives.remove(drive);
        }
    }
}""",
        "ideal_explanation": "Line 4 attempts to remove elements directly from activeDrives inside an enhanced for-loop. The underlying iterator's modCount deviates from expectedModCount, instantly triggering ConcurrentModificationException at runtime.",
        "refactored_code": """public void purgeExpiredJobDrives(List<JobDrive> activeDrives) {
    LocalDate today = LocalDate.now();
    
    // Fix: Use Iterator.remove() or Java 8 removeIf predicate cleanly
    activeDrives.removeIf(drive -> drive.getDeadline().isBefore(today));
}""",
        "expected_keywords": ["concurrentmodificationexception", "removeif", "iterator", "modcount", "for-loop", "predicate"]
    },
    {
        "id": "cpp-dangling-pointer",
        "title": "Dangling Pointer / Stack Variable Return",
        "language": "cpp",
        "category": "Memory & Pointers",
        "difficulty": "Hard",
        "companies": ["Qualcomm", "NVIDIA", "Samsung R&D"],
        "buggy_line": 5,
        "bug_type": "Returning Address of Local Stack Variable",
        "hint": "What happens to stack-allocated variables when their enclosing function scope terminates?",
        "code": """int* generateCandidateTelemetryMatrix(int numRounds) {
    int scores[numRounds];
    for (int i = 0; i < numRounds; i++) {
        scores[i] = (i + 1) * 20;
    }
    // Line 5: Returning address of stack-allocated array that goes out of scope!
    return scores;
}

void evaluatePlacement() {
    int* telemetry = generateCandidateTelemetryMatrix(4);
    // Undefined behavior / segfault when accessing dereferenced memory!
    printf("Round 1 Score: %d\\n", telemetry[0]);
}""",
        "ideal_explanation": "Line 5 returns the memory address of 'scores', which is a local stack-allocated array. Once generateCandidateTelemetryMatrix returns, its stack frame is invalidated. Dereferencing 'telemetry' leads to undefined behavior, memory corruption, or segmentation faults.",
        "refactored_code": """#include <vector>
#include <memory>

// Fix: Return std::vector or allocate heap memory with std::unique_ptr
std::vector<int> generateCandidateTelemetryMatrix(int numRounds) {
    std::vector<int> scores(numRounds);
    for (int i = 0; i < numRounds; i++) {
        scores[i] = (i + 1) * 20;
    }
    return scores; // Clean Move Semantics (C++11/14/17)
}""",
        "expected_keywords": ["stack", "dangling pointer", "scope", "heap", "vector", "undefined behavior", "segfault"]
    },
    {
        "id": "py-algo-binary-search-overflow",
        "title": "Integer Overflow in Binary Search Indexing",
        "language": "python",
        "category": "Algorithms & Scalability",
        "difficulty": "Medium",
        "companies": ["Google", "Microsoft", "Adobe"],
        "buggy_line": 5,
        "bug_type": "Potential Integer Overflow / Inefficient Midpoint Calculation",
        "hint": "Check how the midpoint calculation handles extreme boundaries in strict typed environments.",
        "code": """def binary_search_job_id(job_ids: list, target_id: int) -> int:
    low = 0
    high = len(job_ids) - 1
    
    while low <= high:
        # Line 5: Traditional (low + high) // 2 causes integer overflow in 32-bit systems
        mid = (low + high) // 2
        
        if job_ids[mid] == target_id:
            return mid
        elif job_ids[mid] < target_id:
            low = mid + 1
        else:
            high = mid - 1
            
    return -1""",
        "ideal_explanation": "Line 5 computes mid using (low + high) // 2. When low and high are large integers near the maximum integer limit (2^31 - 1), their sum overflows to a negative integer in languages like C/Java/C++, producing an erroneous negative index. The safe industrial formula is low + (high - low) // 2.",
        "refactored_code": """def binary_search_job_id(job_ids: list, target_id: int) -> int:
    low = 0
    high = len(job_ids) - 1
    
    while low <= high:
        # Fix: Overflow-safe midpoint formula
        mid = low + (high - low) // 2
        
        if job_ids[mid] == target_id:
            return mid
        elif job_ids[mid] < target_id:
            low = mid + 1
        else:
            high = mid - 1
            
    return -1""",
        "expected_keywords": ["overflow", "integer overflow", "low + (high - low)", "midpoint", "boundary"]
    },
    {
        "id": "py-django-n-plus-one",
        "title": "Django ORM N+1 Database Query Storm",
        "language": "python",
        "category": "Databases & Performance",
        "difficulty": "Medium",
        "companies": ["Instagram", "Robinhood", "Swiggy"],
        "buggy_line": 5,
        "bug_type": "N+1 Query Waterfall (Missing select_related/prefetch_related)",
        "hint": "Watch what happens when iterating through candidate submissions and accessing sub.student.full_name in each loop iteration.",
        "code": """def get_recent_submission_summaries(drive_id: int):
    # Fetch all candidate submissions for current campus drive
    submissions = PlacementSubmission.objects.filter(drive_id=drive_id)
    
    summary_list = []
    # Bug on line 5: Traversing foreign key inside loop executes N separate SQL queries!
    for sub in submissions:
        student_name = sub.student.full_name  # Triggers individual SELECT per submission
        summary_list.append({"sub_id": sub.id, "name": student_name, "score": sub.score})
        
    return summary_list""",
        "ideal_explanation": "Line 5 traverses the foreign key relationship 'sub.student' inside a loop over 'submissions'. In an ORM like Django or SQLAlchemy, this triggers 1 initial query + N separate database queries for every single submission (the classic N+1 problem). With 10,000 candidates, this sends 10,001 SQL queries, exhausting connection pools and causing massive latency spikes.",
        "refactored_code": """def get_recent_submission_summaries(drive_id: int):
    # Fix: Pre-fetch related student entity in a single JOIN query
    submissions = PlacementSubmission.objects.filter(drive_id=drive_id).select_related('student')
    
    return [
        {"sub_id": sub.id, "name": sub.student.full_name, "score": sub.score}
        for sub in submissions
    ]""",
        "expected_keywords": ["n+1", "select_related", "prefetch_related", "join", "foreign key", "waterfall", "queries", "loop"]
    },
    {
        "id": "py-gil-thread-cpu-bound",
        "title": "Python GIL Bottleneck in Multi-Threaded Math",
        "language": "python",
        "category": "Concurrency & Parallelism",
        "difficulty": "Hard",
        "companies": ["Two Sigma", "Meta", "Jane Street"],
        "buggy_line": 4,
        "bug_type": "Misusing threading.Thread for CPU-Bound Work Under GIL",
        "hint": "CPython's Global Interpreter Lock (GIL) allows only one native thread to execute Python bytecode at a time.",
        "code": """import threading

def compute_heavy_hash_batch(chunks: list):
    # Line 4: Spawning standard threads for CPU-bound computations
    threads = [threading.Thread(target=hash_crunch, args=(c,)) for c in chunks]
    for t in threads: t.start()
    for t in threads: t.join()
    # Problem: Total execution time is SLOWER than single-threaded execution!
    return [c.result for c in chunks]""",
        "ideal_explanation": "Line 4 creates standard 'threading.Thread' workers for CPU-bound computation. Due to CPython's Global Interpreter Lock (GIL), only one thread executes Python bytecode at any instant. Multi-threading CPU-bound tasks in Python creates substantial thread switching overhead and contention, resulting in worse performance than sequential execution. Multiprocessing or ProcessPoolExecutor should be used instead.",
        "refactored_code": """from concurrent.futures import ProcessPoolExecutor

def compute_heavy_hash_batch(chunks: list):
    # Fix: Use ProcessPoolExecutor to utilize multiple distinct CPU cores
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(hash_crunch, chunks))
    return results""",
        "expected_keywords": ["gil", "global interpreter lock", "multiprocessing", "cpu-bound", "overhead", "threads", "single core"]
    },
    {
        "id": "js-event-loop-starvation",
        "title": "Node.js Event Loop Starvation & Synchronous Block",
        "language": "javascript",
        "category": "Async & Event Loop",
        "difficulty": "Medium",
        "companies": ["Netflix", "PayPal", "LinkedIn"],
        "buggy_line": 3,
        "bug_type": "Synchronous I/O in Async Express Handler",
        "hint": "Node.js runs single-threaded on the main event loop. What happens when synchronous disk I/O is called in a high-traffic endpoint?",
        "code": """app.post("/api/audit-logs", async (req, res) => {
    const { logData } = req.body;
    // Line 3: fs.readFileSync blocks the entire Node.js event loop!
    const existing = fs.readFileSync("/var/log/audit.log", "utf8");
    fs.writeFileSync("/var/log/audit.log", existing + "\\n" + logData);
    res.json({ success: true });
});""",
        "ideal_explanation": "Line 3 uses synchronous blocking disk operations ('fs.readFileSync' and 'fs.writeFileSync') inside an HTTP route handler. Because Node.js handles all client connections on a single thread, any synchronous I/O or heavy computation blocks all other incoming requests, creating widespread request timeouts across all users.",
        "refactored_code": """import fs from "fs/promises";

app.post("/api/audit-logs", async (req, res) => {
    const { logData } = req.body;
    // Fix: Use non-blocking async file appending
    await fs.appendFile("/var/log/audit.log", logData + "\\n", "utf8");
    res.json({ success: true });
});""",
        "expected_keywords": ["event loop", "blocking", "sync", "readfilesync", "appendfile", "async", "single-threaded"]
    },
    {
        "id": "react-stale-closure-hook",
        "title": "React Stale Closure in useEffect Timer Hook",
        "language": "javascript",
        "category": "Frontend State & Hooks",
        "difficulty": "Medium",
        "companies": ["Meta", "Airbnb", "Vercel"],
        "buggy_line": 4,
        "bug_type": "Stale State Closure in setInterval Dependency Array",
        "hint": "Notice the empty dependency array [] in useEffect while referencing the 'secondsLeft' state variable.",
        "code": """function InterviewCountdownTimer() {
    const [secondsLeft, setSecondsLeft] = useState(180);

    useEffect(() => {
        // Line 4: Stale closure captures initial secondsLeft value (180) forever!
        const timerId = setInterval(() => {
            setSecondsLeft(secondsLeft - 1); // Bug: Never decrements past 179!
        }, 1000);
        return () => clearInterval(timerId);
    }, []); // Empty dependency array

    return <span>Time: {secondsLeft}s</span>;
}""",
        "ideal_explanation": "Line 4 references 'secondsLeft' directly inside a setInterval callback while providing an empty dependency array '[]'. Due to JavaScript closures, the callback captures the initial state value (180) upon mount. On each tick, it computes 180 - 1 = 179 and gets stuck at 179 forever. The functional state updater form 'prev => prev - 1' resolves this.",
        "refactored_code": """function InterviewCountdownTimer() {
    const [secondsLeft, setSecondsLeft] = useState(180);

    useEffect(() => {
        // Fix: Use functional updater to read latest state without closure lock
        const timerId = setInterval(() => {
            setSecondsLeft(prev => (prev > 0 ? prev - 1 : 0));
        }, 1000);
        return () => clearInterval(timerId);
    }, []);

    return <span>Time: {secondsLeft}s</span>;
}""",
        "expected_keywords": ["closure", "stale", "functional updater", "prev", "dependency", "useeffect", "setinterval"]
    },
    {
        "id": "ts-any-runtime-type-bypass",
        "title": "Unsafe Type Casting & Runtime Undefined Crash",
        "language": "javascript",
        "category": "Type Safety & Reliability",
        "difficulty": "Medium",
        "companies": ["Stripe", "Microsoft", "Discord"],
        "buggy_line": 5,
        "bug_type": "Unvalidated 'as any' Type Casting",
        "hint": "TypeScript types only exist at compile time; using 'as' casting does not sanitize runtime JSON payloads.",
        "code": """interface CandidateScorecard {
    studentId: string;
    interviewScore: { overall: number; breakdown: { dsa: number } };
}

function processCandidateAssessment(apiPayload) {
    // Line 5: Blind cast bypasses compile-time checks without runtime validation
    const scorecard = apiPayload;
    
    // Crashes with TypeError: Cannot read property 'dsa' of undefined!
    const dsaRating = scorecard.interviewScore.breakdown.dsa;
    return dsaRating >= 75;
}""",
        "ideal_explanation": "Line 5 trusts unvalidated external JSON payloads. TypeScript type assertions disappear completely after compilation and perform zero runtime schema validation. If the backend API payload is malformed or missing the nested 'breakdown' object, line 8 immediately crashes the browser or node server with an unhandled TypeError.",
        "refactored_code": """function processCandidateAssessment(apiPayload) {
    // Fix: Guard nested properties with optional chaining & runtime validation
    if (!apiPayload || !apiPayload.interviewScore || !apiPayload.interviewScore.breakdown) {
        return false;
    }
    const dsaRating = apiPayload.interviewScore.breakdown.dsa ?? 0;
    return dsaRating >= 75;
}""",
        "expected_keywords": ["type assertion", "runtime", "validation", "undefined", "optional chaining", "typeerror", "schema"]
    },
    {
        "id": "sql-null-in-subquery-trap",
        "title": "SQL NOT IN Subquery Empty Result Set Trap",
        "language": "sql",
        "category": "SQL & Three-Valued Logic",
        "difficulty": "Hard",
        "companies": ["Snowflake", "Amazon", "Oracle"],
        "buggy_line": 4,
        "bug_type": "NOT IN Subquery Containing NULL Values (Three-Valued Logic)",
        "hint": "In SQL, 'x NOT IN (1, 2, NULL)' evaluates to UNKNOWN, which evaluates to FALSE for every record.",
        "code": """-- Retrieve all students who have NOT received a rejection letter
SELECT s.id, s.name, s.cgpa 
FROM students s
WHERE s.id NOT IN (
    -- Line 4: If rejected_candidates.candidate_id contains even ONE NULL value,
    -- this entire query returns ZERO records unexpectedly!
    SELECT candidate_id FROM rejected_candidates
);""",
        "ideal_explanation": "Line 4 uses 'NOT IN (SELECT ...)'. In SQL three-valued logic (TRUE, FALSE, UNKNOWN), comparing any value with NULL using != evaluates to UNKNOWN. If the subquery contains even a single NULL candidate_id, the expression evaluates to FALSE/UNKNOWN for ALL rows, causing the query to return zero results. Using 'NOT EXISTS' or filtering out NULLs fixes the flaw.",
        "refactored_code": """-- Fix: Use NOT EXISTS which safely handles NULLs without false positives
SELECT s.id, s.name, s.cgpa 
FROM students s
WHERE NOT EXISTS (
    SELECT 1 
    FROM rejected_candidates rc 
    WHERE rc.candidate_id = s.id
);""",
        "expected_keywords": ["not in", "not exists", "null", "three-valued logic", "unknown", "empty", "zero rows"]
    },
    {
        "id": "sql-missing-index-seq-scan",
        "title": "Deadlock & Sequential Table Scan Lock",
        "language": "sql",
        "category": "Database Performance & Concurrency",
        "difficulty": "Medium",
        "companies": ["Uber", "Salesforce", "Visa"],
        "buggy_line": 4,
        "bug_type": "Missing Index on Foreign Key / Unindexed Filter Column",
        "hint": "Updating records filtered by an unindexed column forces a full table scan and table-level locks.",
        "code": """-- High-throughput placement registration endpoint
BEGIN TRANSACTION;

-- Line 4: 'status' and 'drive_uuid' have no composite index
UPDATE placement_applications
SET application_status = 'PROCESSED'
WHERE drive_uuid = 'drive-8812-faang' AND application_status = 'PENDING';

COMMIT;""",
        "ideal_explanation": "Line 4 updates rows filtered on 'drive_uuid' and 'application_status' where no index exists. In databases like PostgreSQL or MySQL, this forces a full sequential table scan. Under concurrent traffic from thousands of students, it escalates to exclusive row or table locks, causing connection pool exhaustion and transaction deadlocks.",
        "refactored_code": """-- Fix: Create composite B-tree index on the filtered predicates
CREATE INDEX idx_placement_apps_drive_status 
ON placement_applications (drive_uuid, application_status);

-- The query now utilizes an Index Scan with minimal row-level locking
UPDATE placement_applications
SET application_status = 'PROCESSED'
WHERE drive_uuid = 'drive-8812-faang' AND application_status = 'PENDING';""",
        "expected_keywords": ["index", "table scan", "sequential scan", "deadlock", "composite index", "lock", "performance"]
    },
    {
        "id": "java-memory-leak-static-map",
        "title": "Unbounded Static HashMap Memory Leak (OOM)",
        "language": "java",
        "category": "JVM Memory & Garbage Collection",
        "difficulty": "Hard",
        "companies": ["Amazon AWS", "Goldman Sachs", "Intuit"],
        "buggy_line": 2,
        "bug_type": "Unbounded Static Cache Holding Strong References",
        "hint": "Objects held in static fields live in the Root Set of the Garbage Collector and are never reclaimed.",
        "code": """public class CandidateSessionManager {
    // Line 2: Unbounded static HashMap holds strong references indefinitely
    private static final Map<String, UserSession> sessionCache = new HashMap<>();

    public void registerSession(String token, UserSession session) {
        sessionCache.put(token, session);
        // Problem: No eviction policy (TTL / LRU / WeakReference)!
        // High production traffic leads to java.lang.OutOfMemoryError: Java heap space
    }
}""",
        "ideal_explanation": "Line 2 declares a static 'HashMap' without any eviction policy, TTL expiration, or max size. Because static fields are part of the JVM Garbage Collection Root Set, referenced 'UserSession' objects can never be garbage collected. Under sustained production traffic, memory consumption grows monotonically until JVM throws 'OutOfMemoryError: Java heap space'.",
        "refactored_code": """import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

public class CandidateSessionManager {
    // Fix: Use bounded LRU map or Cache with expiration
    private static final int MAX_ENTRIES = 10000;
    private static final Map<String, UserSession> sessionCache = 
        new java.util.LinkedHashMap<String, UserSession>(MAX_ENTRIES, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<String, UserSession> eldest) {
                return size() > MAX_ENTRIES;
            }
        };
}""",
        "expected_keywords": ["static", "memory leak", "outofmemoryerror", "oom", "garbage collection", "gc root", "eviction", "lru", "ttl"]
    },
    {
        "id": "java-string-equality-trap",
        "title": "Object Identity (==) vs Logical Equality Trap",
        "language": "java",
        "category": "Core Java & Identity",
        "difficulty": "Easy",
        "companies": ["Infosys", "Wipro", "Capgemini"],
        "buggy_line": 3,
        "bug_type": "Using '==' Reference Comparison on Strings/Objects",
        "hint": "In Java, '==' compares memory addresses, not the actual text contents of String objects.",
        "code": """public boolean isPlacementDriveApproved(String driveStatus, String roleCategory) {
    // Line 3: Comparing String instances using '==' instead of .equals()!
    if (driveStatus == "APPROVED" && roleCategory == "SDE") {
        return true;
    }
    return false;
}
// Calling with new String("APPROVED") evaluates to FALSE!""",
        "ideal_explanation": "Line 3 uses the '==' operator to compare String values. In Java, '==' checks reference equality (memory addresses), whereas '.equals()' checks character sequence equality. When Strings are dynamically created from HTTP requests or databases, they do not share the String pool address, causing legitimate approved drives to fail validation.",
        "refactored_code": """public boolean isPlacementDriveApproved(String driveStatus, String roleCategory) {
    // Fix: Use null-safe String .equals() comparison
    return "APPROVED".equalsIgnoreCase(driveStatus) && "SDE".equalsIgnoreCase(roleCategory);
}""",
        "expected_keywords": ["==", ".equals", "reference equality", "string pool", "memory address", "content equality"]
    },
    {
        "id": "cpp-memory-leak-no-virtual-destructor",
        "title": "Missing Virtual Destructor Polymorphic Leak",
        "language": "cpp",
        "category": "OOP & Memory Management",
        "difficulty": "Hard",
        "companies": ["Google", "Adobe", "Qualcomm"],
        "buggy_line": 3,
        "bug_type": "Non-Virtual Destructor in Polymorphic Base Class",
        "hint": "When deleting a derived object through a pointer to a base class, what happens if the base destructor is not virtual?",
        "code": """class TelemetryLogger {
public:
    // Line 3: Base destructor is not marked virtual!
    ~TelemetryLogger() { printf("Base destroyed\\n"); }
};

class CloudBufferLogger : public TelemetryLogger {
    int* buffer;
public:
    CloudBufferLogger() { buffer = new int[1024]; }
    ~CloudBufferLogger() { delete[] buffer; printf("Buffer freed\\n"); }
};

void runLogger() {
    TelemetryLogger* logger = new CloudBufferLogger();
    delete logger; // Bug: ~CloudBufferLogger() is NEVER called, leaking buffer!
}""",
        "ideal_explanation": "Line 3 declares a non-virtual destructor in the base class 'TelemetryLogger'. When deleting an instance of 'CloudBufferLogger' through a base pointer ('delete logger'), the compiler performs static binding and calls only the base destructor. The derived class destructor is completely bypassed, permanently leaking the heap-allocated buffer and causing undefined behavior.",
        "refactored_code": """class TelemetryLogger {
public:
    // Fix: Declare virtual destructor for polymorphic base classes
    virtual ~TelemetryLogger() = default;
};

class CloudBufferLogger : public TelemetryLogger {
    std::unique_ptr<int[]> buffer;
public:
    CloudBufferLogger() : buffer(std::make_unique<int[]>(1024)) {}
    ~CloudBufferLogger() override = default;
};""",
        "expected_keywords": ["virtual", "destructor", "polymorphic", "derived", "memory leak", "undefined behavior", "delete"]
    },
    {
        "id": "cpp-vector-iterator-invalidation",
        "title": "Vector Capacity Reallocation Iterator Invalidation",
        "language": "cpp",
        "category": "STL & Pointers",
        "difficulty": "Medium",
        "companies": ["Microsoft", "Bloomberg", "NVIDIA"],
        "buggy_line": 4,
        "bug_type": "Iterator Invalidation via push_back During Loop",
        "hint": "What happens to vector iterators when push_back causes the vector to reallocate internal storage?",
        "code": """void duplicateEvenScores(std::vector<int>& scores) {
    for (auto it = scores.begin(); it != scores.end(); ++it) {
        if (*it % 2 == 0) {
            // Line 4: push_back can trigger reallocation, invalidating 'it'!
            scores.push_back(*it); 
        }
    }
}""",
        "ideal_explanation": "Line 4 calls 'scores.push_back(*it)' while iterating over the vector using iterators. If adding an element exceeds current vector capacity, 'std::vector' reallocates its internal buffer in a new memory block. All existing iterators and pointers to the old buffer are immediately invalidated. Subsequent iterations dereference freed memory, causing segfaults or infinite loops.",
        "refactored_code": """void duplicateEvenScores(std::vector<int>& scores) {
    // Fix: Collect elements to add separately or reserve capacity and use indexing
    std::vector<int> evens;
    for (int score : scores) {
        if (score % 2 == 0) evens.push_back(score);
    }
    scores.insert(scores.end(), evens.begin(), evens.end());
}""",
        "expected_keywords": ["iterator invalidation", "reallocation", "push_back", "capacity", "segfault", "undefined behavior"]
    },
    {
        "id": "go-goroutine-leak-unbuffered-channel",
        "title": "Goroutine Leak on Unbuffered Channel & Timeout",
        "language": "go",
        "category": "Concurrency & Channels",
        "difficulty": "Hard",
        "companies": ["Uber", "HashiCorp", "Docker"],
        "buggy_line": 2,
        "bug_type": "Goroutine Blocked Forever on Unbuffered Channel Send",
        "hint": "If the context times out before the worker finishes, who receives from the channel?",
        "code": """func queryStudentRank(ctx context.Context, studentID int) (int, error) {
    // Line 2: Unbuffered channel causes goroutine to block forever on timeout!
    ch := make(chan int)
    
    go func() {
        rank := fetchFromRemoteService(studentID)
        ch <- rank // Blocks forever if ctx expires and nobody reads!
    }()
    
    select {
    case res := <-ch:
        return res, nil
    case <-ctx.Done():
        return 0, ctx.Err() // Goroutine above is leaked in memory permanently!
    }
}""",
        "ideal_explanation": "Line 2 creates an unbuffered channel 'make(chan int)'. If the context expires ('<-ctx.Done()'), the main function returns immediately. When the background goroutine finishes, its channel send operation 'ch <- rank' blocks indefinitely waiting for a reader that will never arrive. The goroutine remains frozen in memory forever (goroutine leak). Using a buffered channel 'make(chan int, 1)' fixes this.",
        "refactored_code": """func queryStudentRank(ctx context.Context, studentID int) (int, error) {
    // Fix: Buffered channel (size 1) ensures goroutine never blocks on send
    ch := make(chan int, 1)
    
    go func() {
        rank := fetchFromRemoteService(studentID)
        ch <- rank // Non-blocking send even if caller has timed out
    }()
    
    select {
    case res := <-ch:
        return res, nil
    case <-ctx.Done():
        return 0, ctx.Err()
    }
}""",
        "expected_keywords": ["goroutine leak", "unbuffered", "buffered channel", "timeout", "blocked", "context", "memory leak"]
    }
]

# ==============================================================================
# SCHEMAS
# ==============================================================================
class DebuggingEvaluateRequest(BaseModel):
    challenge_id: str
    selected_line: int
    diagnosis: str

class DebuggingEvaluateResponse(BaseModel):
    status: str
    challenge_id: str
    is_correct_line: bool
    accuracy_score: int
    conceptual_grade: str
    feedback: str
    production_impact: str
    refactored_code: str
    engine: str

class DebuggingGenerateRequest(BaseModel):
    language: Optional[str] = "python"
    difficulty: Optional[str] = "Medium"
    topic: Optional[str] = None

# ==============================================================================
# ENDPOINTS
# ==============================================================================
@router.get("/challenges")
def list_debugging_challenges():
    """
    Returns the catalog of production code review & debugging challenges.
    """
    summary = []
    for c in DEBUGGING_CHALLENGES:
        summary.append({
            "id": c["id"],
            "title": c["title"],
            "language": c["language"],
            "category": c["category"],
            "difficulty": c["difficulty"],
            "companies": c["companies"],
            "code": c["code"],
            "hint": c["hint"]
        })
    return {
        "status": "success",
        "total": len(summary),
        "challenges": summary
    }

@router.post("/evaluate", response_model=DebuggingEvaluateResponse)
async def evaluate_debugging_answer(
    req: DebuggingEvaluateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Evaluates candidate's bug diagnosis using Gemini Live LLM (with deterministic heuristic fallback).
    """
    challenge = next((c for c in DEBUGGING_CHALLENGES if c["id"] == req.challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Debugging challenge not found")

    is_correct_line = (req.selected_line == challenge["buggy_line"])
    diag_text = (req.diagnosis or "").strip()
    
    gemini_key = (os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "") or "").strip()

    # Attempt Gemini Live LLM Evaluation
    if gemini_key:
        models = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.8-flash"
        ]
        system_instruction = (
            "You are a Principal Software Architect at Google/Amazon conducting a Senior Code Review & Debugging Interview. "
            "Evaluate the candidate's bug diagnosis and return ONLY a valid JSON object with the following schema: "
            "{"
            "  \"accuracy_score\": integer (0-100), "
            "  \"conceptual_grade\": string ('Mastery' | 'Proficient' | 'Needs Improvement'), "
            "  \"feedback\": string (2-3 sentences concise technical review), "
            "  \"production_impact\": string (what breaks at enterprise scale)"
            "}"
        )
        user_prompt = (
            f"Challenge Title: {challenge['title']}\n"
            f"Programming Language: {challenge['language']}\n"
            f"Source Code:\n{challenge['code']}\n\n"
            f"Actual Vulnerability: Line {challenge['buggy_line']} - {challenge['bug_type']}\n"
            f"Candidate Selected Line: {req.selected_line} (Correct: {is_correct_line})\n"
            f"Candidate Diagnosis: \"{diag_text}\"\n\n"
            f"Return ONLY valid JSON."
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500}
        }
        headers = {"Content-Type": "application/json", "x-goog-api-key": gemini_key}

        for model_name in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            raw = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                            s_idx = raw.find("{")
                            e_idx = raw.rfind("}")
                            if s_idx != -1 and e_idx != -1:
                                parsed = json.loads(raw[s_idx:e_idx+1])
                                return DebuggingEvaluateResponse(
                                    status="success",
                                    challenge_id=challenge["id"],
                                    is_correct_line=is_correct_line,
                                    accuracy_score=int(parsed.get("accuracy_score", 85 if is_correct_line else 40)),
                                    conceptual_grade=str(parsed.get("conceptual_grade", "Proficient")),
                                    feedback=str(parsed.get("feedback", challenge["ideal_explanation"])),
                                    production_impact=str(parsed.get("production_impact", "Causes service degradation under concurrent load.")),
                                    refactored_code=challenge["refactored_code"],
                                    engine="google_gemini_llm"
                                )
            except Exception:
                pass

    # Deterministic Offline Heuristic Evaluation
    diag_lower = diag_text.lower()
    keyword_matches = sum(1 for kw in challenge["expected_keywords"] if kw in diag_lower)
    keyword_score = min(50, keyword_matches * 18)
    line_score = 45 if is_correct_line else 10
    total_score = min(100, line_score + keyword_score)

    if total_score >= 80:
        grade = "Mastery"
        fb = f"Outstanding analysis! You accurately spotted the {challenge['bug_type']} flaw on Line {challenge['buggy_line']}. {challenge['ideal_explanation']}"
    elif total_score >= 50:
        grade = "Proficient"
        fb = f"Good technical observation. While you identified the general area, make sure to detail how {challenge['bug_type']} causes failure in production."
    else:
        grade = "Needs Improvement"
        fb = f"Line {challenge['buggy_line']} contains a critical {challenge['bug_type']}. Review: {challenge['ideal_explanation']}"

    return DebuggingEvaluateResponse(
        status="success",
        challenge_id=challenge["id"],
        is_correct_line=is_correct_line,
        accuracy_score=total_score,
        conceptual_grade=grade,
        feedback=fb,
        production_impact=challenge["ideal_explanation"],
        refactored_code=challenge["refactored_code"],
        engine="offline_heuristic_engine"
    )

@router.post("/generate")
async def generate_ai_debugging_challenge(
    req: DebuggingGenerateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Dynamically generates a brand new production debugging drill using Gemini Live LLM.
    The challenge is injected into the live challenge catalog so the candidate can inspect and solve it immediately.
    """
    lang = (req.language or "python").lower().strip()
    diff = req.difficulty or "Medium"
    topic = (req.topic or "").strip()
    
    gemini_key = (os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "") or "").strip()
    
    if gemini_key:
        models = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.8-flash"
        ]
        
        system_instruction = (
            "You are a Staff Software Engineer at Google/Meta creating real-world production code debugging challenges "
            "for senior campus placement coding interviews. "
            "Generate ONE concise (8-16 lines) realistic production code snippet with a critical, realistic defect. "
            "You must return ONLY a valid JSON object matching this schema:\n"
            "{\n"
            "  \"title\": \"Short Title describing the feature\",\n"
            "  \"language\": \"" + lang + "\",\n"
            "  \"category\": \"Category name (e.g. Memory, Concurrency, Security, Scalability)\",\n"
            "  \"difficulty\": \"" + diff + "\",\n"
            "  \"companies\": [\"Top Company 1\", \"Top Company 2\"],\n"
            "  \"buggy_line\": <1-indexed integer indicating exact line number of defect in the code>,\n"
            "  \"bug_type\": \"Name of flaw (e.g., Integer Overflow, Missing Lock, Null Dereference)\",\n"
            "  \"hint\": \"One subtle interviewer hint\",\n"
            "  \"code\": \"Multi-line code snippet with bug (include comments)\",\n"
            "  \"ideal_explanation\": \"2-3 sentences explaining why it fails in production\",\n"
            "  \"refactored_code\": \"Clean corrected code snippet without the bug\",\n"
            "  \"expected_keywords\": [\"keyword1\", \"keyword2\", \"keyword3\"]\n"
            "}"
        )
        
        user_prompt = f"Create a new {diff} level debugging challenge in {lang}."
        if topic:
            user_prompt += f" Focus on topic/technology: {topic}."
            
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1000}
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
                            raw = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                            s_idx = raw.find("{")
                            e_idx = raw.rfind("}")
                            if s_idx != -1 and e_idx != -1:
                                parsed = json.loads(raw[s_idx:e_idx+1])
                                new_id = f"ai-{lang[:3]}-{uuid.uuid4().hex[:6]}"
                                parsed["id"] = new_id
                                parsed["language"] = lang
                                parsed["difficulty"] = diff
                                if "buggy_line" not in parsed or not isinstance(parsed["buggy_line"], int):
                                    parsed["buggy_line"] = 3
                                if "expected_keywords" not in parsed or not isinstance(parsed["expected_keywords"], list):
                                    parsed["expected_keywords"] = ["bug", "fix", lang]
                                    
                                # Insert at the front of challenges catalog
                                DEBUGGING_CHALLENGES.insert(0, parsed)
                                
                                return {
                                    "status": "success",
                                    "total": len(DEBUGGING_CHALLENGES),
                                    "challenge": {
                                        "id": parsed["id"],
                                        "title": parsed["title"],
                                        "language": parsed["language"],
                                        "category": parsed.get("category", "Production Systems"),
                                        "difficulty": parsed["difficulty"],
                                        "companies": parsed.get("companies", ["FAANG"]),
                                        "code": parsed["code"],
                                        "hint": parsed.get("hint", "Review variable scope and memory lifecycles.")
                                    },
                                    "engine": "google_gemini_llm"
                                }
            except Exception:
                pass

    # Deterministic fallback challenge generator if Gemini is offline
    fallback_id = f"drill-{lang[:3]}-{uuid.uuid4().hex[:6]}"
    fallback_challenge = {
        "id": fallback_id,
        "title": f"Dynamic {lang.upper()} Resilience Verification",
        "language": lang,
        "category": "High Availability & I/O",
        "difficulty": diff,
        "companies": ["Amazon AWS", "Stripe", "Microsoft"],
        "buggy_line": 3,
        "bug_type": "Uncaught Exception in High-Concurrency Worker Loop",
        "hint": "Check how error handling handles transient connection resets.",
        "code": f"# Production {lang.upper()} worker pipeline\ndef execute_task_batch(queue_tasks):\n    for task in queue_tasks:\n        # Line 3: Unhandled network timeout aborts entire batch!\n        result = network_sync_client.dispatch(task)\n        logger.info(f'Task completed: {{result}}')\n    return True",
        "ideal_explanation": f"Line 3 dispatches network requests without an enclosing retry or try/catch block. In high-scale {lang} production services, a single transient network socket drop crashes the entire batch loop.",
        "refactored_code": f"# Fix: Enclose with retry backoff and circuit breaker\ndef execute_task_batch(queue_tasks):\n    results = []\n    for task in queue_tasks:\n        try:\n            res = retry_client.dispatch_with_retry(task, max_attempts=3)\n            results.append(res)\n        except NetworkTimeoutException as e:\n            logger.error(f'Task {{task}} queued to DLQ: {{e}}')\n    return results",
        "expected_keywords": ["try", "catch", "retry", "exception", "timeout", "batch", "dlq"]
    }
    DEBUGGING_CHALLENGES.insert(0, fallback_challenge)
    
    return {
        "status": "success",
        "total": len(DEBUGGING_CHALLENGES),
        "challenge": {
            "id": fallback_challenge["id"],
            "title": fallback_challenge["title"],
            "language": fallback_challenge["language"],
            "category": fallback_challenge["category"],
            "difficulty": fallback_challenge["difficulty"],
            "companies": fallback_challenge["companies"],
            "code": fallback_challenge["code"],
            "hint": fallback_challenge["hint"]
        },
        "engine": "offline_resilience_generator"
    }

