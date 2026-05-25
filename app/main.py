import os
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class StudentCreate(BaseModel):
    name: str


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "labdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "123456"),
    )


@app.on_event("startup")
def start():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


@app.get("/health")
def health():
    return {"status": "oke"}


@app.get("/students")
def get_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name FROM students ORDER BY id;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [{"id": row[0], "name": row[1]} for row in rows]


@app.post("/students")
def create_students(student: StudentCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (name) VALUES (%s) RETURNING id, name;",
        (student.name,),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return {"id": row[0], "name": row[1]}
