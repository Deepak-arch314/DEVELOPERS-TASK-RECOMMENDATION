from typing import List
from fastapi import APIRouter, Depends, HTTPException
from backend.database import developer_out, get_db, task_out
from backend.recommender import get_recommendations_for_developer
from backend.schemas import RecommendationOut

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/developer/{dev_id}", response_model=List[RecommendationOut])
def get_developer_recommendations(dev_id: int, top_n: int = 5, db=Depends(get_db)):
    dev_row = db.execute("SELECT * FROM developers WHERE id = ?", (dev_id,)).fetchone()
    if not dev_row:
        raise HTTPException(status_code=404, detail=f"Developer {dev_id} not found")

    dev_data = developer_out(dev_row)
    task_rows = db.execute("SELECT * FROM tasks WHERE LOWER(status) = 'open'").fetchall()
    tasks_data = [task_out(r) for r in task_rows]

    if not tasks_data:
        return []

    return get_recommendations_for_developer(dev_data, tasks_data, top_n=top_n)