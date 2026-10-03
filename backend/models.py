"""Data models and helper classes."""
from typing import List, Optional

class Developer:
    def __init__(self, dev_id: int, name: str, skills: List[str], experience_years: float, max_capacity: int = 5, current_load: int = 0):
        self.id = dev_id
        self.name = name
        self.skills = skills
        self.experience_years = experience_years
        self.max_capacity = max_capacity
        self.current_load = current_load

class Task:
    def __init__(self, task_id: int, title: str, required_skills: List[str], difficulty: str = "Medium", estimated_hours: float = 8.0, status: str = "Open", description: Optional[str] = None):
        self.id = task_id
        self.title = title
        self.description = description
        self.required_skills = required_skills
        self.difficulty = difficulty
        self.estimated_hours = estimated_hours
        self.status = status