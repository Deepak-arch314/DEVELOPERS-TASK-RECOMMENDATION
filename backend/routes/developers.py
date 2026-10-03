from typing import List
from fastapi import APIRouter, Depends, HTTPException
from backend.database import developer_out, get_db
from backend.recommender import reset_ml_model
from backend.schemas import DeveloperIn, DeveloperOut

router = APIRouter(prefix="/developers", tags=["Developers"])

def _get_or_404(db, dev_id: int):
    row = db.execute("SELECT * FROM developers WHERE id = ?", (dev_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Developer {dev_id} not found")
    return developer_out(row)

@router.post("", response_model=DeveloperOut, status_code=201)
def create_developer(dev: DeveloperIn, db=Depends(get_db)):
    skills_str = ", ".join(dev.skills) if isinstance(dev.skills, list) else dev.skills
    cur = db.execute(
        "INSERT INTO developers (name, skills, experience_years, max_capacity, current_load) VALUES (?, ?, ?, ?, ?)",
        (dev.name.strip(), skills_str, dev.experience_years, dev.max_capacity, dev.current_load)
    )
    db.commit()
    return _get_or_404(db, cur.lastrowid)

@router.get("", response_model=List[DeveloperOut])
def list_developers(db=Depends(get_db)):
    rows = db.execute("SELECT * FROM developers ORDER BY id").fetchall()
    return [developer_out(r) for r in rows]

@router.get("/{dev_id}", response_model=DeveloperOut)
def get_developer(dev_id: int, db=Depends(get_db)):
    return _get_or_404(db, dev_id)

@router.put("/{dev_id}", response_model=DeveloperOut)
def update_developer(dev_id: int, dev: DeveloperIn, db=Depends(get_db)):
    _get_or_404(db, dev_id)
    skills_str = ", ".join(dev.skills) if isinstance(dev.skills, list) else dev.skills
    db.execute(
        "UPDATE developers SET name=?, skills=?, experience_years=?, max_capacity=?, current_load=? WHERE id=?",
        (dev.name.strip(), skills_str, dev.experience_years, dev.max_capacity, dev.current_load, dev_id)
    )
    db.commit()
    return _get_or_404(db, dev_id)

@router.delete("/{dev_id}")
def delete_developer(dev_id: int, db=Depends(get_db)):
    _get_or_404(db, dev_id)
    db.execute("DELETE FROM developers WHERE id = ?", (dev_id,))
    db.commit()
    reset_ml_model()
    return {"message": f"Developer {dev_id} deleted"}