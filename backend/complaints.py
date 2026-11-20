# Complaint APIs: list, add (students), change status / priority (staff).
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ai.classifier import classify
from ai.priority import recommend_priority
from backend.auth import user
from backend.db import sql

router = APIRouter()
CHOICES = {"status": ["Open", "In Progress", "Resolved"], "priority": ["Critical", "High", "Medium", "Low"]}


class Complaint(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    affected_students: int = Field(ge=1)
    severity: Literal["minor", "moderate", "severe"]
    academic_impact: Literal["low", "medium", "high"]
    duration_hours: float = Field(ge=0)


class Change(BaseModel):
    value: str


# Students get their own complaints, staff get everyone's. Most urgent first, then newest.
@router.get("/api/complaints")
def list_complaints(request: Request):
    u = user(request)
    rows = sql("SELECT c.id, u.name, c.title, c.category, c.priority, c.score, c.location, c.description, "
               "c.status, to_char(c.created_at, 'DD Mon YYYY') FROM complaints c JOIN users u ON u.id = c.student_id "
               "WHERE %s OR c.student_id = %s "
               "ORDER BY array_position(ARRAY['Critical', 'High', 'Medium', 'Low'], c.priority), c.id DESC",
               (u["role"] == "staff", u["id"]))
    keys = ["id", "student", "title", "category", "priority", "score", "location", "description", "status", "date"]
    return [dict(zip(keys, r)) for r in rows]


# Students add a complaint. The AI classifier finds the category, the priority engine the priority.
@router.post("/api/complaints")
def add_complaint(c: Complaint, request: Request):
    student = user(request, "student")
    category = classify(c.title + " " + c.description)
    score, priority = recommend_priority(c.affected_students, c.severity, c.academic_impact, c.duration_hours)
    sql("INSERT INTO complaints (student_id, title, location, description, affected_students, severity, "
        "academic_impact, duration_hours, category, score, priority) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (student["id"], c.title, c.location, c.description, c.affected_students, c.severity,
         c.academic_impact, c.duration_hours, category, score, priority))
    return {"category": category, "score": score, "priority": priority}


# Staff change the status or the priority (staff override) of one complaint
@router.post("/api/complaints/{complaint_id}/{field}")
def change(complaint_id: int, field: str, data: Change, request: Request):
    user(request, "staff")
    if data.value not in CHOICES.get(field, []):
        raise HTTPException(400, "Not allowed")
    sql(f"UPDATE complaints SET {field} = %s WHERE id = %s", (data.value, complaint_id))  # field is checked above
