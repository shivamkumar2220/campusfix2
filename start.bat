@echo off
REM CampusFix 2 - double-click to start. Opens http://localhost:8002
cd /d "%~dp0"

REM Google / GitHub login keys are in secrets.bat (never upload that file)
if exist secrets.bat call secrets.bat

if not exist venv\Scripts\python.exe python -m venv venv
venv\Scripts\python.exe -m pip install -q -r requirements.txt

start "" "http://localhost:8002"
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8002 --reload
