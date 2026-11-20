# Database connection: one helper that runs a SQL query on PostgreSQL.
import os

import psycopg

DB_URL = os.environ.get("DB_URL", "postgresql://postgres:postgres@localhost:5432/campusfix2")


# Run one SQL query and return the rows
def sql(query, values=()):
    with psycopg.connect(DB_URL) as connection:
        cursor = connection.execute(query, values)
        return cursor.fetchall() if cursor.description else []
