import os
import sqlite3
import json
import uvicorn
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = os.path.abspath("recommender.db")

# ---------------------------------------------------------
# 1. DATABASE SETUP & SEEDING (25 DEVS & 25 TASKS)
# ---------------------------------------------------------
def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS developers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        skills TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        max_capacity INTEGER DEFAULT 40,
        current_load INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        estimated_hours INTEGER NOT NULL,
        status TEXT DEFAULT 'OPEN'
    )
    """)

    # Seed 25 Developers
    devs = [
        ("Alice Smith", json.dumps(["Python", "FastAPI", "React"]), 5, 40, 10),
        ("Bob Jones", json.dumps(["Java", "Spring Boot", "SQL"]), 4, 40, 20),
        ("Charlie Brown", json.dumps(["Python", "Machine Learning", "Docker"]), 6, 40, 15),
        ("Diana Prince", json.dumps(["JavaScript", "React", "Node.js", "CSS"]), 3, 40, 25),
        ("Evan Wright", json.dumps(["Go", "Kubernetes", "Docker", "Microservices"]), 5, 40, 30),
        ("Fiona Gallagher", json.dumps(["Python", "Django", "PostgreSQL"]), 2, 40, 10),
        ("George Clark", json.dumps(["C#", ".NET", "Azure", "SQL"]), 7, 40, 0),
        ("Hannah Abbott", json.dumps(["TypeScript", "Vue.js", "GraphQL"]), 3, 40, 12),
        ("Ian Malcolm", json.dumps(["Python", "Data Science", "Pandas", "SQL"]), 8, 40, 20),
        ("Julia Roberts", json.dumps(["Swift", "iOS", "Mobile Development"]), 4, 40, 15),
        ("Kevin Bacon", json.dumps(["Kotlin", "Android", "Java"]), 5, 40, 5),
        ("Laura Croft", json.dumps(["Rust", "C++", "System Architecture"]), 9, 40, 35),
        ("Michael Scott", json.dumps(["HTML", "CSS", "JavaScript"]), 2, 40, 5),
        ("Nina Nina", json.dumps(["PHP", "Laravel", "MySQL"]), 4, 40, 18),
        ("Oscar Martinez", json.dumps(["SQL", "PostgreSQL", "Database Design"]), 6, 40, 22),
        ("Pam Beesly", json.dumps(["Figma", "UI/UX", "CSS"]), 3, 40, 10),
        ("Quentin Tarantino", json.dumps(["Python", "Flask", "MongoDB"]), 5, 40, 8),
        ("Rachel Green", json.dumps(["React", "Redux", "Tailwind"]), 2, 40, 14),
        ("Steve Rogers", json.dumps(["Java", "Microservices", "Kafka"]), 10, 40, 40),
        ("Tony Stark", json.dumps(["Python", "AI", "PyTorch", "C++"]), 12, 40, 10),
        ("Ulysses Grant", json.dumps(["Linux", "Bash", "DevOps", "AWS"]), 6, 40, 28),
        ("Victoria Adams", json.dumps(["Ruby", "Ruby on Rails", "Redis"]), 4, 40, 16),
        ("Walter White", json.dumps(["Python", "FastAPI", "SQLAlchemy"]), 5, 40, 12),
        ("Xavier Charles", json.dumps(["Machine Learning", "NLP", "Python"]), 8, 40, 19),
        ("Yennefer Vengerberg", json.dumps(["TypeScript", "Next.js", "GraphQL"]), 4, 40, 22)
    ]

    # Seed 25 Tasks
    tasks = [
        ("Build REST API for Auth", json.dumps(["Python", "FastAPI"]), "Medium", 15, "OPEN"),
        ("Design Admin Dashboard UI", json.dumps(["React", "JavaScript", "CSS"]), "Easy", 10, "OPEN"),
        ("Database Query Optimization", json.dumps(["SQL", "PostgreSQL"]), "Hard", 20, "OPEN"),
        ("Kubernetes Cluster Setup", json.dumps(["Kubernetes", "Docker", "Go"]), "Hard", 25, "OPEN"),
        ("iOS App Crash Fixing", json.dumps(["Swift", "iOS"]), "Medium", 12, "OPEN"),
        ("ML Model Training for churn", json.dumps(["Python", "Machine Learning", "Pandas"]), "Hard", 30, "OPEN"),
        ("Migrate Backend to Spring Boot", json.dumps(["Java", "Spring Boot"]), "Hard", 35, "OPEN"),
        ("Implement GraphQL Gateway", json.dumps(["TypeScript", "GraphQL"]), "Medium", 18, "OPEN"),
        ("Flutter Cross-Platform Prototype", json.dumps(["Dart", "Flutter"]), "Easy", 14, "OPEN"),
        ("Android Push Notifications", json.dumps(["Kotlin", "Android"]), "Medium", 8, "OPEN"),
        ("Set up CI/CD Pipeline on AWS", json.dumps(["DevOps", "AWS", "Bash"]), "Medium", 16, "OPEN"),
        ("Redesign Landing Page UI/UX", json.dumps(["Figma", "UI/UX", "CSS"]), "Easy", 8, "OPEN"),
        ("Django Order Management API", json.dumps(["Python", "Django", "PostgreSQL"]), "Medium", 22, "OPEN"),
        ("High-Performance C++ Engine", json.dumps(["C++", "System Architecture"]), "Hard", 40, "OPEN"),
        ("Next.js Server-Side Rendering", json.dumps(["TypeScript", "Next.js"]), "Medium", 15, "OPEN"),
        ("Laravel Payment Gateway Sync", json.dumps(["PHP", "Laravel", "MySQL"]), "Medium", 12, "OPEN"),
        ("Kafka Event Streaming Pipeline", json.dumps(["Java", "Kafka", "Microservices"]), "Hard", 28, "OPEN"),
        ("Vue.js Customer Portal", json.dumps(["TypeScript", "Vue.js"]), "Easy", 10, "OPEN"),
        ("NLP Text Processing Pipeline", json.dumps(["Python", "NLP", "Machine Learning"]), "Hard", 24, "OPEN"),
        ("Flask Microservice Logging", json.dumps(["Python", "Flask", "MongoDB"]), "Easy", 6, "OPEN"),
        ("Redux Store Refactoring", json.dumps(["React", "Redux", "Tailwind"]), "Medium", 14, "OPEN"),
        ("Azure Active Directory Integration", json.dumps(["C#", ".NET", "Azure"]), "Medium", 18, "OPEN"),
        ("Ruby on Rails API Upgrade", json.dumps(["Ruby", "Ruby on Rails"]), "Medium", 16, "OPEN"),
        ("Redis Cache Layer Implementation", json.dumps(["Redis", "Python"]), "Easy", 8, "OPEN"),
        ("PyTorch Object Detection Model", json.dumps(["Python", "AI", "PyTorch"]), "Hard", 32, "OPEN")
    ]

    cursor.execute("DELETE FROM developers")
    cursor.execute("DELETE FROM tasks")
    cursor.executemany("INSERT INTO developers (name, skills, experience_years, max_capacity, current_load) VALUES (?, ?, ?, ?, ?)", devs)
    cursor.executemany("INSERT INTO tasks (title, required_skills, difficulty, estimated_hours, status) VALUES (?, ?, ?, ?, ?)", tasks)

    conn.commit()
    conn.close()

seed_database()

# ---------------------------------------------------------
# 2. FASTAPI & SCHEMAS
# ---------------------------------------------------------
app = FastAPI(title="Developer Task Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DeveloperSchema(BaseModel):
    name: str
    skills: List[str]
    experience_years: int
    max_capacity: Optional[int] = 40
    current_load: Optional[int] = 0

class TaskSchema(BaseModel):
    title: str
    required_skills: List[str]
    difficulty: str
    estimated_hours: int
    status: Optional[str] = "OPEN"

def get_db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def parse_json_list(val):
    if isinstance(val, list): return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list): return parsed
        except Exception: pass
        return [s.strip() for s in val.split(",") if s.strip()]
    return []

# ---------------------------------------------------------
# 3. GET / RECOMMENDATION ENDPOINTS
# ---------------------------------------------------------
@app.get("/api/stats")
def get_stats():
    c = get_db()
    devs_cnt = c.execute("SELECT COUNT(*) FROM developers").fetchone()[0]
    tasks_cnt = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    open_cnt = c.execute("SELECT COUNT(*) FROM tasks WHERE status='OPEN'").fetchone()[0]
    c.close()
    return {"total_developers": devs_cnt, "total_tasks": tasks_cnt, "open_tasks": open_cnt}

@app.get("/api/developers")
def get_developers():
    c = get_db()
    rows = c.execute("SELECT * FROM developers").fetchall()
    c.close()
    return [{**dict(r), "skills": parse_json_list(r["skills"])} for r in rows]

@app.get("/api/tasks")
def get_tasks():
    c = get_db()
    rows = c.execute("SELECT * FROM tasks").fetchall()
    c.close()
    return [{**dict(r), "required_skills": parse_json_list(r["required_skills"])} for r in rows]

@app.get("/api/recommendations/developer/{developer_id}")
def get_recommendations(developer_id: int, top_n: int = Query(10)):
    c = get_db()
    dev = c.execute("SELECT * FROM developers WHERE id=?", (developer_id,)).fetchone()
    if not dev:
        c.close()
        raise HTTPException(status_code=404, detail="Developer not found")

    dev_skills = set([s.lower() for s in parse_json_list(dev["skills"])])
    all_tasks = c.execute("SELECT * FROM tasks WHERE status='OPEN'").fetchall()
    c.close()

    recs = []
    for t in all_tasks:
        t_dict = dict(t)
        req_skills_list = parse_json_list(t_dict["required_skills"])
        req_skills_set = set([s.lower() for s in req_skills_list])

        match_count = len(dev_skills.intersection(req_skills_set))
        total_req = len(req_skills_set) if req_skills_set else 1
        score = round((match_count / total_req) * 100, 2)

        t_dict["match_score"] = score
        t_dict["required_skills"] = req_skills_list
        recs.append(t_dict)

    recs.sort(key=lambda x: x["match_score"], reverse=True)
    return recs[:top_n]

# ---------------------------------------------------------
# 4. CREATE / UPDATE / DELETE ENDPOINTS FOR FURTHER USE
# ---------------------------------------------------------
@app.post("/api/developers")
def create_developer(dev: DeveloperSchema):
    c = get_db()
    cursor = c.cursor()
    cursor.execute(
        "INSERT INTO developers (name, skills, experience_years, max_capacity, current_load) VALUES (?, ?, ?, ?, ?)",
        (dev.name, json.dumps(dev.skills), dev.experience_years, dev.max_capacity, dev.current_load)
    )
    c.commit()
    new_id = cursor.lastrowid
    c.close()
    return {"message": "Developer added successfully", "id": new_id}

@app.put("/api/developers/{dev_id}")
def update_developer(dev_id: int, dev: DeveloperSchema):
    c = get_db()
    cursor = c.cursor()
    cursor.execute(
        "UPDATE developers SET name=?, skills=?, experience_years=?, max_capacity=?, current_load=? WHERE id=?",
        (dev.name, json.dumps(dev.skills), dev.experience_years, dev.max_capacity, dev.current_load, dev_id)
    )
    c.commit()
    c.close()
    return {"message": "Developer updated successfully"}

@app.delete("/api/developers/{dev_id}")
def delete_developer(dev_id: int):
    c = get_db()
    c.execute("DELETE FROM developers WHERE id=?", (dev_id,))
    c.commit()
    c.close()
    return {"message": "Developer deleted successfully"}

@app.post("/api/tasks")
def create_task(task: TaskSchema):
    c = get_db()
    cursor = c.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, required_skills, difficulty, estimated_hours, status) VALUES (?, ?, ?, ?, ?)",
        (task.title, json.dumps(task.required_skills), task.difficulty, task.estimated_hours, task.status)
    )
    c.commit()
    new_id = cursor.lastrowid
    c.close()
    return {"message": "Task created successfully", "id": new_id}

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: TaskSchema):
    c = get_db()
    cursor = c.cursor()
    cursor.execute(
        "UPDATE tasks SET title=?, required_skills=?, difficulty=?, estimated_hours=?, status=? WHERE id=?",
        (task.title, json.dumps(task.required_skills), task.difficulty, task.estimated_hours, task.status, task_id)
    )
    c.commit()
    c.close()
    return {"message": "Task updated successfully"}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    c = get_db()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    c.commit()
    c.close()
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)