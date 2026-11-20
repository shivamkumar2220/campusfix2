# CampusFix 2 backend: joins all the parts together.
# Start (from the project folder):  venv\Scripts\python.exe -m uvicorn backend.main:app --port 8002
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend import auth, complaints

app = FastAPI(title="CampusFix API")
# Login cookie is signed with SECRET_KEY. On a real HTTPS server add https_only=True.
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "dev-only-secret"), same_site="lax")
app.include_router(auth.router)
app.include_router(complaints.router)

# Show the HTML pages from the "frontend" folder
app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "frontend", html=True))
