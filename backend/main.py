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
            dev_skills = set(json.loads(raw_dev_skills))
        except Exception:
            dev_skills = set([s.strip() for s in raw_dev_skills.split(",") if s.strip()])
    else:
        dev_skills = set(raw_dev_skills)

    tasks = cursor.execute("SELECT * FROM tasks WHERE status='OPEN'").fetchall()
    conn.close()
    
    recommendations = []
    for t in tasks:
        t_dict = dict(t)
        raw_req_skills = t_dict["required_skills"]
        
        if isinstance(raw_req_skills, str):
            try:
                req_skills = set(json.loads(raw_req_skills))
            except Exception:
                req_skills = set([s.strip() for s in raw_req_skills.split(",") if s.strip()])
        else:
            req_skills = set(raw_req_skills)
        
        match_count = len(dev_skills.intersection(req_skills))
        total_req = len(req_skills) if req_skills else 1
        score = round((match_count / total_req) * 100, 2)
        
        t_dict["match_score"] = score
        t_dict["required_skills"] = list(req_skills)
        recommendations.append(t_dict)
        
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:top_n]