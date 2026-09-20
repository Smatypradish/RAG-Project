@echo off
title RAG Backend - KEEP THIS WINDOW OPEN
cd /d "%~dp0backend"

echo Freeing port 8000 if something is stuck on it...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Starting backend server (accessible on your network)...
echo First start can take up to 60 seconds. Wait for "Application startup complete."
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000

echo.
echo ===================================================
echo  THE BACKEND STOPPED. Read the error message above.
echo ===================================================
pause
