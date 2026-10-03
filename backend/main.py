from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3
import pandas as pd
import json

app = FastAPI(title="Software Developer Task Recommender")

# Enable CORS for frontend running on port 3000
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
            except:
                dev_dict["skills"] = dev_dict["skills"].split(",")
        result.append(dev_dict)
    return result

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
            except:
                task_dict["required_skills"] = task_dict["required_skills"].split(",")
        result.append(task_dict)
    return result

@app.get("/api/recommendations/{developer_id}")
def get_recommendations(developer_id: int, top_n: int = Query(5)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    dev = cursor.execute("SELECT * FROM developers WHERE id=?", (developer_id,)).fetchone()
    if not dev:
        conn.close()
        raise HTTPException(status_code=404, detail="Developer not found")
        
    dev_skills = set(json.loads(dev["skills"]) if isinstance(dev["skills"], str) else dev["skills"])
    tasks = cursor.execute("SELECT * FROM tasks WHERE status='OPEN'").fetchall()
    conn.close()
    
    recommendations = []
    for t in tasks:
        t_dict = dict(t)
        req_skills = set(json.loads(t_dict["required_skills"]) if isinstance(t_dict["required_skills"], str) else t_dict["required_skills"])
        
        match_count = len(dev_skills.intersection(req_skills))
        total_req = len(req_skills) if req_skills else 1
        score = round((match_count / total_req) * 100, 2)
        
        t_dict["match_score"] = score
        t_dict["required_skills"] = list(req_skills)
        recommendations.append(t_dict)
        
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:top_n]