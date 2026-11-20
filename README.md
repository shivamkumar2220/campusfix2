# CampusFix 2 – Campus Complaint System

Students report campus problems (Wi-Fi, projector, broken bench, lab PC).
An **AI model** finds the category and a **priority engine** decides how urgent it is.
Staff see all complaints, most urgent first, and update them.

## How it works (one picture)

```
 Student                     Server (FastAPI)                         Database
 ───────                     ────────────────                         ────────
 Login page  ── email+pw ──▶ Module 2: Login & Security ──────────▶  users
 (Module 5)    or GitHub
                                    │ session cookie
                                    ▼
 Complaint   ── complaint ─▶ Module 4: Complaint APIs
 form                               ├─▶ Module 3: AI classifier → category
 (Module 6)                         ├─▶ Module 4: priority engine → score + priority
                                    └──────────────────────────────▶  complaints
                                                                      (Module 1)
 Staff table ◀── list ──────  Module 4  (staff can change status / priority)
 (Module 6)
```

## Modules

| # | Module | What it does | Files | Guide |
|---|--------|--------------|-------|-------|
| 1 | Database | Stores users and complaints | `database/database.sql`, `backend/db.py` | [docs/module1-database.md](docs/module1-database.md) |
| 2 | Login & Security | Password login, GitHub login, sessions, roles | `backend/auth.py`, `backend/main.py` | [docs/module2-login-security.md](docs/module2-login-security.md) |
| 3 | AI Classifier | Reads a complaint and predicts its category | `ai/classifier.py`, `ai/evaluate.py`, `ai/data/complaints.csv` | [docs/module3-ai-classifier.md](docs/module3-ai-classifier.md) |
| 4 | Complaint APIs & Priority | Add / list / update complaints, priority score | `backend/complaints.py`, `ai/priority.py` | [docs/module4-complaints-priority.md](docs/module4-complaints-priority.md) |
| 5 | Frontend – Login Page | Login screen, shared design and helpers | `frontend/index.html`, `login.js`, `login.css`, `common.js`, `style.css`, `start.bat` | [docs/module5-frontend-login.md](docs/module5-frontend-login.md) |
| 6 | Frontend – Complaints Page | Complaint form, complaint table, staff controls | `frontend/home.html`, `home.js`, `home.css` | [docs/module6-frontend-complaints.md](docs/module6-frontend-complaints.md) |

## Run it on your computer (Windows)

1. Install **Python 3.13** and **PostgreSQL**.
2. Create the database (once):
   ```
   createdb -U postgres campusfix2
   psql -U postgres -d campusfix2 -f database/database.sql
   ```
3. Copy `secrets.example.bat` to `secrets.bat` (GitHub login keys, optional – ask Member 2).
4. Double-click **`start.bat`**. It opens http://localhost:8002

**Demo logins** (password `Student@123`):
students `sanchita@campusfix.edu`, `shivam@campusfix.edu` … · staff `jay@campusfix.edu`, `anik@campusfix.edu` …

## Tech used

| Part | Technology |
|------|------------|
| Backend | Python, FastAPI, Uvicorn |
| Database | PostgreSQL (psycopg) |
| AI | scikit-learn (TF-IDF + Logistic Regression) |
| Security | bcrypt passwords, signed session cookie, GitHub OAuth |
| Frontend | HTML, CSS, plain JavaScript (no framework) |
