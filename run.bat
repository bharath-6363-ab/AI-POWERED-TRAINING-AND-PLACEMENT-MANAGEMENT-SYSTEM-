@echo off
echo ===================================================================
echo   AI-Powered Training & Placement Management System (Port 8080)
echo ===================================================================
echo.
echo 1. Seeding database...
python -m backend.app.utils.seed_data
echo.
echo 2. Starting server on http://127.0.0.1:8080 ...
echo.
echo    - Web Portal:   http://127.0.0.1:8080/static/index.html
echo    - API Docs:     http://127.0.0.1:8080/docs
echo.
python start.py
pause
