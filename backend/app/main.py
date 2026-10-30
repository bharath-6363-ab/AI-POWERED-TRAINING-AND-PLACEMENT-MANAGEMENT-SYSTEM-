import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.core.database import Base, engine
from backend.app.routes import (
    auth_routes, student_routes, academic_routes, attendance_routes,
    test_routes, placement_routes, resume_routes, interview_routes,
    analytics_routes, report_routes, chatbot_routes, debugging_routes
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Training & Placement Management System with Intelligent Student Performance, Personalized Interview Analytics and Placement Support"
)

# CORS configuration for responsive modern frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for downloads and uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend/public"), name="static")

# Modular API Routing
app.include_router(auth_routes.router, prefix=settings.API_V1_STR)
app.include_router(student_routes.router, prefix=settings.API_V1_STR)
app.include_router(academic_routes.router, prefix=settings.API_V1_STR)
app.include_router(attendance_routes.router, prefix=settings.API_V1_STR)
app.include_router(test_routes.router, prefix=settings.API_V1_STR)
app.include_router(placement_routes.router, prefix=settings.API_V1_STR)
app.include_router(resume_routes.router, prefix=settings.API_V1_STR)
app.include_router(interview_routes.router, prefix=settings.API_V1_STR)
app.include_router(analytics_routes.router, prefix=settings.API_V1_STR)
app.include_router(report_routes.router, prefix=settings.API_V1_STR)
app.include_router(chatbot_routes.router, prefix=settings.API_V1_STR)
app.include_router(debugging_routes.router, prefix=settings.API_V1_STR)

from fastapi.responses import FileResponse

@app.get("/")
def serve_portal():
    index_path = os.path.join("frontend", "public", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/login")
def serve_login():
    login_path = os.path.join("frontend", "public", "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return FileResponse(os.path.join("frontend", "public", "index.html"))

@app.get("/register")
def serve_register():
    reg_path = os.path.join("frontend", "public", "register.html")
    if os.path.exists(reg_path):
        return FileResponse(reg_path)
    return FileResponse(os.path.join("frontend", "public", "index.html"))

@app.get("/health")
def root_status():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "database": "SQLite Local Engine" if settings.USE_SQLITE_FALLBACK else "MySQL 8+ Engine"
    }

