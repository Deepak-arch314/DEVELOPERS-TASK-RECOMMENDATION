import os
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(BASE_DIR / "data" / "recommender.db")

def _connect():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()

def developer_out(row):
    if not row:
        return None
    data = dict(row)
    if isinstance(data.get("skills"), str):
        data["skills"] = [s.strip() for s in data["skills"].split(",") if s.strip()]
    return data

def task_out(row):
    if not row:
        return None
    data = dict(row)
    if isinstance(data.get("required_skills"), str):
        data["required_skills"] = [s.strip() for s in data["required_skills"].split(",") if s.strip()]
    return data

def init_db():
    os.makedirs(os.path.dirname(str(DB_PATH)), exist_ok=True)
    conn = _connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS developers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        skills TEXT NOT NULL,
        experience_years REAL NOT NULL,
        max_capacity INTEGER DEFAULT 5,
        current_load INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        required_skills TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Medium',
        estimated_hours REAL NOT NULL,
        status TEXT DEFAULT 'Open'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS task_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        developer_id INTEGER NOT NULL,
        task_id INTEGER NOT NULL,
        completion_time_hours REAL NOT NULL,
        rating REAL NOT NULL,
        FOREIGN KEY(developer_id) REFERENCES developers(id),
        FOREIGN KEY(task_id) REFERENCES tasks(id)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()