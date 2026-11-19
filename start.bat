@echo off
REM CampusFix 2 - double-click to start. Opens http://localhost:8002
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    python -m venv venv
    venv\Scripts\python.exe -m pip install -r requirements.txt
)

start "" "http://localhost:8002"
venv\Scripts\python.exe -m uvicorn server:app --port 8002 --reload
