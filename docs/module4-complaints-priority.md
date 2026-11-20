# Module 4 – Complaint APIs & Priority Engine

**Owner:** Member 4  **Files:** `backend/complaints.py`, `ai/priority.py`

## What it does
- **Priority engine:** turns 4 simple answers into a score and a priority.
- **Complaint APIs:** add, list and update complaints. Joins the AI (Module 3), the priority engine and the database (Module 1).

## Priority engine – `ai/priority.py`

The student answers 4 questions. Each answer gives points:

| Question | Points |
|----------|--------|
| Students affected | 1–9 → **1** · 10–49 → **2** · 50–99 → **3** · 100+ → **4** |
| Severity | minor **1** · moderate **2** · severe **3** |
| Academic impact | low **1** · medium **2** · high **3** |
| Problem since (hours) | under 8 → **1** · 8–23 → **2** · 24+ → **3** |

**score = sum of the 4 → 4 to 13**

| Score | Priority |
|-------|----------|
| 11 – 13 | **Critical** |
| 8 – 10 | **High** |
| 5 – 7 | **Medium** |
| 4 | **Low** |

Example: 60 students (3) + severe (3) + high impact (3) + 10 hours (2) = **11 → Critical**

Staff can still change the priority by hand (**staff override**) – the score stays as the AI's suggestion.

Test: `venv\Scripts\python.exe -m ai.priority` → `(12, 'Critical')` and `(4, 'Low')`

## APIs – `backend/complaints.py`

| Method | URL | Who | What it does |
|--------|-----|-----|--------------|
| GET | `/api/complaints` | everyone | Students: only their own. Staff: all. Most urgent first, then newest. |
| POST | `/api/complaints` | students | Add a complaint |
| POST | `/api/complaints/{id}/status` | staff | Open / In Progress / Resolved |
| POST | `/api/complaints/{id}/priority` | staff | Critical / High / Medium / Low |

### Adding a complaint – step by step
```
form data ──▶ Complaint model checks it (422 error if wrong)
          ──▶ classify(title + description)          → category   (Module 3)
          ──▶ recommend_priority(4 answers)           → score, priority
          ──▶ INSERT INTO complaints ...              (Module 1)
          ──▶ reply {category, score, priority}       → shown to the student
```

### Input checks (Pydantic)
```python
class Complaint(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    affected_students: int = Field(ge=1)
    severity: Literal["minor", "moderate", "severe"]
    ...
```
Empty title, negative numbers or unknown severity → **422** error automatically.

### Staff update – safe even with a variable column name
```python
CHOICES = {"status": [...], "priority": [...]}
if data.value not in CHOICES.get(field, []):   # field must be status/priority, value must be allowed
    raise HTTPException(400, "Not allowed")
```
Only `status` and `priority` can be changed, so a request like `/api/complaints/1/title` is refused.

## How to test
- Log in as a student, add a complaint → message shows category, priority and score.
- Log in as staff → all complaints, change status → green "saved" message.
- Docs page with all APIs: http://localhost:8002/docs

## Viva questions
| Question | Answer |
|----------|--------|
| What is a REST API? | URLs the frontend calls to get or send data as JSON. |
| GET vs POST? | GET reads data. POST sends new data or changes something. |
| Why a score and not just AI? | The score is clear and explainable; staff can see why something is Critical. |
| What is staff override? | Staff can change the priority if the score is wrong for a special case. |
| How is sorting done? | SQL `ORDER BY array_position(['Critical','High','Medium','Low'], priority), id DESC`. |
| What is 422? | "Unprocessable" – the data sent does not match the rules. |
