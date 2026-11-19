# CampusFix 2 backend: student login + save complaints in PostgreSQL.
# Start:  uvicorn server:app --port 8002
import hashlib
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Database address: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
DB_URL = "postgresql://postgres:postgres@localhost:5432/campusfix2"

app = FastAPI()


# What the browser sends for login
class LoginData(BaseModel):
    email: str
    password: str


# What the browser sends for a new complaint
class ComplaintData(BaseModel):
    student_id: int
    title: str
    location: str
    description: str


# Run one SQL query and return the rows
def run_sql(query, values=()):
    with psycopg.connect(DB_URL) as connection:
        cursor = connection.execute(query, values)
        return cursor.fetchall() if cursor.description else []


# Check email + password, return the student's id and name
@app.post("/api/login")
def login(data: LoginData):
    password_hash = hashlib.sha256(data.password.encode()).hexdigest()
    rows = run_sql("SELECT id, name FROM students WHERE email = %s AND password_hash = %s",
                   (data.email, password_hash))
    if not rows:
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return {"id": rows[0][0], "name": rows[0][1]}


# Save a new complaint in the complaints table
@app.post("/api/complaints")
def add_complaint(data: ComplaintData):
    rows = run_sql("INSERT INTO complaints (student_id, title, location, description) "
                   "VALUES (%s, %s, %s, %s) RETURNING id",
                   (data.student_id, data.title, data.location, data.description))
    return {"id": rows[0][0], "message": "Complaint saved"}


# Get all complaints of one student (newest first)
@app.get("/api/complaints/{student_id}")
def my_complaints(student_id: int):
    rows = run_sql("SELECT id, title, location, status, created_at FROM complaints "
                   "WHERE student_id = %s ORDER BY id DESC", (student_id,))
    return [{"id": r[0], "title": r[1], "location": r[2], "status": r[3],
             "date": r[4].strftime("%d %b %Y")} for r in rows]


# Show the HTML pages from the "frontend" folder
app.mount("/", StaticFiles(directory=Path(__file__).parent / "frontend", html=True))
