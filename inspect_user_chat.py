"""
AI-TPMS Chat History Inspector
Prints stored conversation sessions and AI mentor interactions.
"""

import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.core.database import SessionLocal
from backend.app.models.all_models import StudentChatMessage, User

def inspect_chats(limit=20):
    db = SessionLocal()
    print("=" * 75)
    print("           AI-TPMS STUDENT CHATBOT CONVERSATION LOGS")
    print("=" * 75)

    try:
        messages = db.query(StudentChatMessage).order_by(StudentChatMessage.created_at.desc()).limit(limit).all()
        if not messages:
            print("[INFO] No chat messages recorded in database yet.")
            print("[INFO] Start a conversation in the Mitra AI Mentor widget to see records here.")
            return

        print(f"Showing {len(messages)} most recent messages:\n")
        for m in reversed(messages):
            user = db.query(User).filter(User.id == m.user_id).first()
            sender = user.full_name if user else f"User {m.user_id}"
            role_badge = "[STUDENT]" if m.role == "user" else "[MITRA AI]"
            time_str = m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "N/A"
            print(f"{time_str} | {role_badge:<10} {sender}:")
            preview = m.message[:120] + "..." if len(m.message) > 120 else m.message
            print(f"  {preview}\n")

    except Exception as e:
        print(f"[ERROR] Chat inspection failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_chats()
