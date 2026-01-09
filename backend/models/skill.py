from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Skill(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    category: str  # programming, framework, tool, soft-skill
    description: Optional[str] = None
    related_skills: List[str] = []
    
    class Config:
        populate_by_name = True

class CareerRole(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    description: str
    required_skills: List[str]
    recommended_skills: List[str] = []
    average_learning_hours: int
    difficulty_level: str  # beginner, intermediate, advanced
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Full Stack Developer",
                "description": "Develops both frontend and backend applications",
                "required_skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB"],
                "recommended_skills": ["TypeScript", "Docker", "AWS"],
                "average_learning_hours": 200,
                "difficulty_level": "intermediate"
            }
        }

class SkillGapAnalysis(BaseModel):
    current_skills: List[str]
    required_skills: List[str]
    skill_gaps: List[str]
    matching_skills: List[str]
    match_percentage: float
