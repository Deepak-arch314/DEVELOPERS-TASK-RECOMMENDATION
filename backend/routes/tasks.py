from typing import List
from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_db, task_out
from backend.schemas import TaskIn, TaskOut

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def _get_or_404(db, task_id: int):
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task_out(row)

@router.get("", response_model=List[TaskOut])
def list_tasks(db=Depends(get_db)):
    rows = db.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    return [task_out(r) for r in rows]

@router.post("", response_model=TaskOut, status_code=201)
def create_task(task: TaskIn, db=Depends(get_db)):
    skills_str = ", ".join(task.required_skills) if isinstance(task.required_skills, list) else task.required_skills
    cur = db.execute(
        "INSERT INTO tasks (title, description, required_skills, difficulty, estimated_hours, status) VALUES (?, ?, ?, ?, ?, ?)",
        (task.title.strip(), task.description, skills_str, task.difficulty, task.estimated_hours, task.status)
    )
    db.commit()
    return _get_or_404(db, cur.lastrowid)

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db=Depends(get_db)):
    return _get_or_404(db, task_id)

@router.delete("/{task_id}")
def delete_task(task_id: int, db=Depends(get_db)):
    _get_or_404(db, task_id)
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return {"message": f"Task {task_id} deleted"}