import os
from pydantic import BaseModel
from typing import List

# Automatically load .env file into environment variables (backend/.env prioritized)
_config_dir = os.path.dirname(__file__)  # backend/app/core
_backend_dir = os.path.dirname(os.path.dirname(_config_dir))  # backend
_root_dir = os.path.dirname(_backend_dir)  # project root

_env_locations = [
    os.path.join(_backend_dir, ".env"),
    os.path.join(os.getcwd(), "backend", ".env"),
    os.path.join(_root_dir, ".env"),
    os.path.join(os.getcwd(), ".env"),
    "backend/.env",
    ".env"
]
for _p in _env_locations:
    if os.path.exists(_p):
        try:
            with open(_p, "r", encoding="utf-8") as _f:
                for _line in _f:
                    _line = _line.strip()
                    if _line and not _line.startswith("#") and "=" in _line:
                        _k, _v = _line.split("=", 1)
                        _k = _k.strip()
                        _v = _v.strip().strip("'\"")
                        if _k:
                            os.environ[_k] = _v
            break
        except Exception:
            pass

class Settings(BaseModel):
    PROJECT_NAME: str = "AI-Powered Training & Placement Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "academic-major-project-super-secret-key-2026-xyz987")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Google Gemini AI LLM Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # MySQL 8+ connection string with automatic SQLite fallback
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "aitpms_db")
    
    USE_SQLITE_FALLBACK: bool = os.getenv("USE_SQLITE_FALLBACK", "true").lower() == "true"
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "aitpms.db")
    
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    @property
    def DATABASE_URL(self) -> str:
        if self.USE_SQLITE_FALLBACK:
            return f"sqlite:///{self.SQLITE_DB_PATH}"
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"

settings = Settings()
