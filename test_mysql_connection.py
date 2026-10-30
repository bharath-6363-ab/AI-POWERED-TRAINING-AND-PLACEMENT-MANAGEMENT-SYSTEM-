"""
AI-TPMS Database Connection Diagnostic Tool
Tests connection to MySQL or SQLite database, checks latency, and validates schema access.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import text, create_engine
from backend.app.core.config import settings

def test_connection():
    print("=" * 65)
    print("       AI-TPMS DATABASE CONNECTION DIAGNOSTIC")
    print("=" * 65)

    db_url = settings.DATABASE_URL
    print(f"Target Database URL: {db_url}")

    is_mysql = "mysql" in db_url.lower()

    if is_mysql:
        print("[INFO] Attempting connection to MySQL service...")
    else:
        print("[INFO] Testing default SQLite embedded database...")

    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        start_time = time.time()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS alive"))
            row = result.fetchone()
            latency = (time.time() - start_time) * 1000
            print(f"[SUCCESS] Database Connection OK! Ping Response: {row[0]}")
            print(f"[SUCCESS] Latency: {latency:.2f} ms")

            # Check existing tables
            if is_mysql:
                tables = conn.execute(text("SHOW TABLES")).fetchall()
                print(f"[SUCCESS] MySQL Tables detected: {len(tables)}")
            else:
                tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
                print(f"[SUCCESS] SQLite Tables detected: {len(tables)}")
                for t in tables[:8]:
                    print(f"   - {t[0]}")
    except Exception as e:
        print(f"[WARNING/ERROR] Connection failed: {e}")
        if is_mysql:
            print("[HINT] Ensure MySQL daemon is running on localhost:3306 or switch to SQLite in .env:")
            print("       DATABASE_URL=sqlite:///./aitpms.db")
        return False

    print("=" * 65)
    return True

if __name__ == "__main__":
    test_connection()
