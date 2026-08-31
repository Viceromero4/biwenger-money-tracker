@echo off
title Biwenger Money Tracker

cd /d "%~dp0"

echo Iniciando backend...
start "Biwenger Backend" cmd /k "cd /d "%~dp0backend" && call .venv\Scripts\activate.bat && uvicorn app.main:app --reload"

timeout /t 2 /nobreak >nul

echo Iniciando frontend...
start "Biwenger Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

timeout /t 3 /nobreak >nul

echo Abriendo aplicacion...
start "" "http://localhost:5173"

exit