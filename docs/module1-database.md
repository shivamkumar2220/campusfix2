# Module 1 – Database

**Owner:** Member 1  **Files:** `database/database.sql`, `backend/db.py`

## What it does
Keeps all the data of the project in **PostgreSQL**: who can log in (users) and every complaint.

## Tables

```
users                                complaints
─────                                ──────────
id  (PK)  ◀───────────────────────── student_id (FK)
name                                 id (PK)
email (unique)                       title, location, description
password_hash  (bcrypt, never        affected_students, severity,
               the real password)    academic_impact, duration_hours  ← answers for priority engine
role  (student / staff)              category                         ← filled by AI (Module 3)
                                     score, priority                  ← filled by priority engine (Module 4)
                                     status  (Open / In Progress / Resolved)
                                     created_at
```

- **One user → many complaints** (one-to-many). `student_id` points to `users.id`.
- `CHECK (role IN ('student','staff'))` – only these two roles are allowed.
- Demo users are added at the end of the file. Password for all: `Student@123`.
- Passwords are hashed **inside the database** with `crypt('Student@123', gen_salt('bf', 12))` (bcrypt, from the `pgcrypto` extension).

## `backend/db.py` – the only database code
```python
def sql(query, values=()):
    with psycopg.connect(DB_URL) as connection:
        cursor = connection.execute(query, values)
        return cursor.fetchall() if cursor.description else []
```
Every other file runs SQL through this one function. Values are passed separately (`%s`), never joined into the text – this stops **SQL injection**.

The database address comes from the `DB_URL` environment variable (default: local PostgreSQL, user `postgres`, password `postgres`, database `campusfix2`).

## How to test
```
psql -U postgres -d campusfix2 -c "SELECT id, name, email, role FROM users;"
psql -U postgres -d campusfix2 -c "SELECT id, title, category, priority, status FROM complaints;"
```

## Viva questions
| Question | Answer |
|----------|--------|
| What is a foreign key here? | `complaints.student_id` → `users.id`. A complaint must belong to a real user. |
| Why store a hash, not the password? | If the database leaks, nobody can read the real passwords. |
| What is bcrypt? | A slow hashing method with a random salt, so the same password gives different hashes and guessing is slow. |
| What is SQL injection and how do you stop it? | Typing SQL code into a form to change the query. We pass values with `%s` so they are never run as SQL. |
| Why one `sql()` function? | All database code is in one place – easy to read and change. |
