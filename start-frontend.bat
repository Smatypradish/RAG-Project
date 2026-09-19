@echo off
title RAG Frontend - KEEP THIS WINDOW OPEN
cd /d "%~dp0frontend"

echo Starting frontend server...
echo.
npm run dev

echo.
echo ===================================================
echo  THE FRONTEND STOPPED. Read the error message above.
echo ===================================================
pause
