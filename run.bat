@echo off
setlocal
title LungAI - Pneumonia CDSS
cd /d "%~dp0"

echo ============================================
echo   LungAI - Pneumonia CDSS
echo   Starting Backend (Flask :5000) and Frontend (Vite :5173)
echo ============================================
echo.

echo [1/2] Starting backend...
start "LungAI-Backend" /D "%~dp0backend" cmd /k "python app.py"

echo [2/2] Starting frontend...
start "LungAI-Frontend" /D "%~dp0frontend" cmd /k "npm run dev"

echo.
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:5173  (browser opens automatically)
echo   Close the two opened windows to stop each service.
echo.
endlocal
