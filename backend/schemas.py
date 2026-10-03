from typing import List, Optional
from pydantic import BaseModel

class DeveloperIn(BaseModel):
    name: str
    skills: List[str]
    experience_years: float
    max_capacity: int = 5
    current_load: int = 0

class DeveloperOut(BaseModel):
    id: int
    name: str
    skills: List[str]
    experience_years: float
    max_capacity: int
    current_load: int

class TaskIn(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: List[str]
    difficulty: str = "Medium"
    estimated_hours: float
    status: str = "Open"

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    required_skills: List[str]
    difficulty: str
    estimated_hours: float
    status: str

class RecommendationOut(BaseModel):
    task: TaskOut
    recommendation_score: float
    reason: str