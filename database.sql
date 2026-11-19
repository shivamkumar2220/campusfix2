-- CampusFix 2 database: 2 tables (students, complaints) + 1 demo student.
-- Run once:  psql -U postgres -d campusfix2 -f database.sql

DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL           -- we never save the real password
);

CREATE TABLE complaints (
    id          SERIAL PRIMARY KEY,
    student_id  INT  NOT NULL REFERENCES students(id),
    title       TEXT NOT NULL,
    location    TEXT NOT NULL,
    description TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'Open',
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Demo logins (password for both: Student@123)
INSERT INTO students (name, email, password_hash) VALUES
('Priya Sharma', 'student@campusfix.edu',  encode(sha256('Student@123'), 'hex')),
('Arjun Nair',   'student1@campusfix.edu', encode(sha256('Student@123'), 'hex'));
