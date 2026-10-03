"""Script to seed SQLite database with initial CSV sample data."""
import csv
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "recommender.db"
DATA_DIR = BASE_DIR / "data" / "sample_data"

def seed_database():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Run 'python -m backend.database' first.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Seed Developers
    devs_csv = DATA_DIR / "developers.csv"
    if devs_csv.exists():
        with open(devs_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute(
                    "INSERT OR REPLACE INTO developers (id, name, skills, experience_years, max_capacity, current_load) VALUES (?, ?, ?, ?, ?, ?)",
                    (row["id"], row["name"], row["skills"], row["experience_years"], row["max_capacity"], row["current_load"])
                )

    # Seed Tasks
    tasks_csv = DATA_DIR / "tasks.csv"
    if tasks_csv.exists():
        with open(tasks_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute(
                    "INSERT OR REPLACE INTO tasks (id, title, description, required_skills, difficulty, estimated_hours, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (row["id"], row["title"], row["description"], row["required_skills"], row["difficulty"], row["estimated_hours"], row["status"])
                )

    conn.commit()
    conn.close()
    print("Database successfully seeded with sample data!")

if __name__ == "__main__":
    seed_database()