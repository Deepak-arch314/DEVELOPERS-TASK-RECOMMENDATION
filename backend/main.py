from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json

app = FastAPI(title="Software Developer Task Recommender")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "recommender.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS developers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skills TEXT NOT NULL,
            experience_years INTEGER NOT NULL
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
    conn.commit()

    # --- AUTO-SEED DATA IF TABLES ARE EMPTY ---
    dev_count = cursor.execute("SELECT COUNT(*) FROM developers").fetchone()[0]
    if dev_count == 0:
        initial_developers = [
            ("Alice Smith", json.dumps(["Python", "FastAPI", "SQLite"]), 4),
            ("Bob Jones", json.dumps(["JavaScript", "React", "Node.js"]), 3),
            ("Charlie Brown", json.dumps(["Python", "Django", "PostgreSQL"]), 5),
            ("Diana Prince", json.dumps(["Java", "Spring Boot", "Docker"]), 6),
            ("Evan Wright", json.dumps(["TypeScript", "Vue.js", "CSS"]), 2),
            ("Fiona Gallagher", json.dumps(["Python", "FastAPI", "React"]), 4),
            ("George Clark", json.dumps(["C++", "Qt", "Algorithms"]), 8),
            ("Hannah Abbott", json.dumps(["Ruby", "Ruby on Rails", "MySQL"]), 3),
            ("Ian Malcolm", json.dumps(["Go", "Kubernetes", "Docker"]), 5),
            ("Julia Roberts", json.dumps(["Python", "Machine Learning", "Pandas"]), 4),
            ("Kevin Bacon", json.dumps(["JavaScript", "HTML", "CSS"]), 1),
            ("Laura Croft", json.dumps(["Rust", "WebAssembly", "C++"]), 7),
            ("Michael Scott", json.dumps(["PHP", "Laravel", "MySQL"]), 5),
            ("Nina Nina", json.dumps(["Python", "Flask", "MongoDB"]), 2),
            ("Oscar Martinez", json.dumps(["SQL", "PostgreSQL", "Data Analysis"]), 6),
            ("Pam Beesly", json.dumps(["UI/UX Design", "Figma", "CSS"]), 3),
            ("Quentin Tarantino", json.dumps(["Python", "FastAPI", "Docker"]), 4),
            ("Rachel Green", json.dumps(["React", "Redux", "JavaScript"]), 3),
            ("Steve Rogers", json.dumps(["Java", "Kotlin", "Android"]), 7),
            ("Tony Stark", json.dumps(["Python", "AI", "C++", "FastAPI"]), 10),
            ("Umar Khan", json.dumps(["Go", "Microservices", "GRPC"]), 4),
            ("Victor Stone", json.dumps(["Cybersecurity", "Python", "Networking"]), 6),
            ("Wanda Maximoff", json.dumps(["TypeScript", "Angular", "Node.js"]), 5),
            ("Xavier Charles", json.dumps(["Data Science", "Python", "PyTorch"]), 8),
            ("Yara Shahidi", json.dumps(["Swift", "iOS", "UI/UX"]), 3)
        ]
        cursor.executemany(
            "INSERT INTO developers (name, skills, experience_years) VALUES (?, ?, ?)",
            initial_developers
        )

    task_count = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if task_count == 0:
        initial_tasks = [
            ("Build REST API Endpoints", json.dumps(["Python", "FastAPI"]), "Medium", 12, "OPEN"),
            ("Design Responsive Landing Page", json.dumps(["HTML", "CSS", "JavaScript"]), "Easy", 8, "OPEN"),
            ("Optimize SQLite Queries", json.dumps(["SQL", "SQLite", "Python"]), "Medium", 10, "OPEN"),
            ("Migrate Database to PostgreSQL", json.dumps(["PostgreSQL", "SQL"]), "Hard", 20, "OPEN"),
            ("Implement User Authentication", json.dumps(["Python", "Django", "Security"]), "Hard", 16, "OPEN"),
            ("Develop React Mobile View", json.dumps(["React", "JavaScript", "CSS"]), "Medium", 14, "OPEN"),
            ("Configure Docker Container", json.dumps(["Docker", "Linux"]), "Medium", 6, "OPEN"),
            ("Setup Kubernetes Cluster", json.dumps(["Kubernetes", "Docker", "DevOps"]), "Hard", 25, "OPEN"),
            ("Train Classification Model", json.dumps(["Python", "Machine Learning", "Pandas"]), "Hard", 30, "OPEN"),
            ("Create Figma Wireframes", json.dumps(["UI/UX Design", "Figma"]), "Easy", 8, "OPEN"),
            ("Fix Memory Leak in C++ Module", json.dumps(["C++", "Algorithms"]), "Hard", 18, "OPEN"),
            ("Build Spring Boot Microservice", json.dumps(["Java", "Spring Boot"]), "Medium", 15, "OPEN"),
            ("Write Unit Tests for Express App", json.dumps(["JavaScript", "Node.js"]), "Easy", 6, "OPEN"),
            ("Build Vue.js Admin Dashboard", json.dumps(["Vue.js", "JavaScript", "CSS"]), "Medium", 16, "OPEN"),
            ("Implement WebAssembly Module", json.dumps(["Rust", "WebAssembly"]), "Hard", 22, "OPEN"),
            ("Setup CI/CD Pipeline", json.dumps(["DevOps", "CI/CD", "Docker"]), "Medium", 10, "OPEN"),
            ("Build Flutter Cross-Platform App", json.dumps(["Flutter", "Dart", "Mobile"]), "Hard", 28, "OPEN"),
            ("Develop GraphQL API Schema", json.dumps(["GraphQL", "Node.js", "JavaScript"]), "Medium", 12, "OPEN"),
            ("Refactor Legacy Ruby Codebase", json.dumps(["Ruby", "Ruby on Rails"]), "Hard", 24, "OPEN"),
            ("Build iOS Swift Onboarding", json.dumps(["Swift", "iOS", "UI/UX"]), "Medium", 14, "OPEN"),
            ("Perform Penetration Testing", json.dumps(["Cybersecurity", "Linux", "Security"]), "Hard", 20, "OPEN"),
            ("Fine-tune Transformer AI Model", json.dumps(["Python", "PyTorch", "AI"]), "Hard", 35, "OPEN"),
            ("Build Next.js Static Site", json.dumps(["TypeScript", "Next.js", "React"]), "Easy", 8, "OPEN"),
            ("Configure AWS Terraform Infrastructure", json.dumps(["AWS", "Terraform", "DevOps"]), "Hard", 18, "OPEN"),
            ("Optimize Android App Memory", json.dumps(["Java", "Kotlin", "Android"]), "Medium", 12, "OPEN")
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, required_skills, difficulty, estimated_hours, status) VALUES (?, ?, ?, ?, ?)",
            initial_tasks
        )

    conn.commit()
    conn.close()

# Initialize tables and seed data on app startup
init_db()

# --- Pydantic Data Models ---
class DeveloperCreate(BaseModel):
    name: str
    skills: List[str]
    experience_years: int

class TaskCreate(BaseModel):
    title: str
    required_skills: List[str]
    difficulty: str
    estimated_hours: int
    status: Optional[str] = "OPEN"

# --- API Routes ---

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Software Developer Task Recommender API is running!",
        "docs": "/docs"
    }

@app.get("/api/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_devs = cursor.execute("SELECT COUNT(*) FROM developers").fetchone()[0]
    total_tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    open_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='OPEN'").fetchone()[0]
    
    conn.close()
    return {
        "total_developers": total_devs,
        "total_tasks": total_tasks,
        "open_tasks": open_tasks
    }

@app.get("/api/developers")
def get_developers():
    conn = get_db_connection()
    cursor = conn.cursor()
    devs = cursor.execute("SELECT * FROM developers").fetchall()
    conn.close()
    
    result = []
    for dev in devs:
        dev_dict = dict(dev)
        if isinstance(dev_dict.get("skills"), str):
            try:
                dev_dict["skills"] = json.loads(dev_dict["skills"])
            except Exception:
                dev_dict["skills"] = [s.strip() for s in dev_dict["skills"].split(",") if s.strip()]
        result.append(dev_dict)
    return result

@app.post("/api/developers")
def add_developer(dev: DeveloperCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    skills_json = json.dumps(dev.skills)
    cursor.execute(
        "INSERT INTO developers (name, skills, experience_years) VALUES (?, ?, ?)",
        (dev.name, skills_json, dev.experience_years)
    )
    conn.commit()
    conn.close()
    return {"message": "Developer added successfully"}

@app.delete("/api/developers/{developer_id}")
def delete_developer(developer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM developers WHERE id=?", (developer_id,))
    conn.commit()
    conn.close()
    return {"message": "Developer deleted successfully"}

@app.get("/api/tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    tasks = cursor.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    
    result = []
    for t in tasks:
        task_dict = dict(t)
        if isinstance(task_dict.get("required_skills"), str):
            try:
                task_dict["required_skills"] = json.loads(task_dict["required_skills"])
            except Exception:
                task_dict["required_skills"] = [s.strip() for s in task_dict["required_skills"].split(",") if s.strip()]
        result.append(task_dict)
    return result

@app.post("/api/tasks")
def add_task(task: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    skills_json = json.dumps(task.required_skills)
    cursor.execute(
        "INSERT INTO tasks (title, required_skills, difficulty, estimated_hours, status) VALUES (?, ?, ?, ?, ?)",
        (task.title, skills_json, task.difficulty, task.estimated_hours, task.status)
    )
    conn.commit()
    conn.close()
    return {"message": "Task added successfully"}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task deleted successfully"}

@app.get("/api/recommendations/{developer_id}")
def get_recommendations(developer_id: int, top_n: int = Query(5)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    dev = cursor.execute("SELECT * FROM developers WHERE id=?", (developer_id,)).fetchone()
    if not dev:
        conn.close()
        raise HTTPException(status_code=404, detail="Developer not found")
        
    raw_dev_skills = dev["skills"]
    if isinstance(raw_dev_skills, str):
        try:
            parsed_skills = json.loads(raw_dev_skills)
        except Exception:
            parsed_skills = [s.strip() for s in raw_dev_skills.split(",") if s.strip()]
    else:
        parsed_skills = raw_dev_skills

    dev_skills_lower = {s.lower() for s in parsed_skills}

    tasks = cursor.execute("SELECT * FROM tasks WHERE status='OPEN'").fetchall()
    conn.close()
    
    recommendations = []
    for t in tasks:
        t_dict = dict(t)
        raw_req_skills = t_dict["required_skills"]
        
        if isinstance(raw_req_skills, str):
            try:
                req_skills_list = json.loads(raw_req_skills)
            except Exception:
                req_skills_list = [s.strip() for s in raw_req_skills.split(",") if s.strip()]
        else:
            req_skills_list = raw_req_skills
        
        req_skills_lower = {s.lower() for s in req_skills_list}
        
        match_count = len(dev_skills_lower.intersection(req_skills_lower))
        total_req = len(req_skills_lower) if req_skills_lower else 1
        score = round((match_count / total_req) * 100, 2)
        
        t_dict["match_score"] = score
        t_dict["required_skills"] = req_skills_list
        recommendations.append(t_dict)
        
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:top_n]