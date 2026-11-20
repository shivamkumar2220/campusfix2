-- CampusFix 2 database: users (students + staff) and complaints.
-- Run once:  psql -U postgres -d campusfix2 -f database/database.sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- crypt() + gen_salt('bf') = bcrypt password hashes
DROP TABLE IF EXISTS complaints, users, students, staff;

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,          -- bcrypt hash, we never save the real password
    role          TEXT NOT NULL CHECK (role IN ('student', 'staff'))
);

CREATE TABLE complaints (
    id          SERIAL PRIMARY KEY,
    student_id  INT  NOT NULL REFERENCES users(id),
    title       TEXT NOT NULL,
    location    TEXT NOT NULL,
    description TEXT NOT NULL,
    -- answers used by the priority engine (ai/priority.py)
    affected_students INT  NOT NULL DEFAULT 1,
    severity          TEXT NOT NULL DEFAULT 'minor',      -- minor / moderate / severe
    academic_impact   TEXT NOT NULL DEFAULT 'low',        -- low / medium / high
    duration_hours    REAL NOT NULL DEFAULT 0,
    -- filled by the AI
    category    TEXT NOT NULL,                    -- ai/classifier.py: IT / Classroom / Maintenance / Lab Equipment
    score       INT  NOT NULL DEFAULT 4,          -- ai/priority.py score (4-13)
    priority    TEXT NOT NULL DEFAULT 'Low',      -- Critical / High / Medium / Low (staff can change it)
    status      TEXT NOT NULL DEFAULT 'Open',
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Demo logins, password for everyone: Student@123
INSERT INTO users (name, email, role, password_hash)
SELECT name, email, role, crypt('Student@123', gen_salt('bf', 12)) FROM (VALUES
    ('Priya Sharma', 'student@campusfix.edu',  'student'),
    ('Arjun Nair',   'student1@campusfix.edu', 'student'),
    ('Sanchita',     'sanchita@campusfix.edu', 'student'),
    ('Anmol',        'anmol@campusfix.edu',    'student'),
    ('Shalu',        'shalu@campusfix.edu',    'student'),
    ('Jiya',         'jiya@campusfix.edu',     'student'),
    ('Shivam',       'shivam@campusfix.edu',   'student'),
    ('Anjani',       'anjani@campusfix.edu',   'student'),
    ('Anik',         'anik@campusfix.edu',     'staff'),
    ('Jay',          'jay@campusfix.edu',      'staff'),
    ('Kush',         'kush@campusfix.edu',     'staff')
) AS demo(name, email, role);

-- Extra staff login (own password)
INSERT INTO users (name, email, role, password_hash)
VALUES ('Napasha', 'napasha@github', 'staff', crypt('napasha', gen_salt('bf', 12)));
