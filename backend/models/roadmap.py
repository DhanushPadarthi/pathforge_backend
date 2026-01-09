from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SkillGap(BaseModel):
    skill: str
    current_level: str
    required_level: str
    gap_severity: str
    learning_priority: str

class ResourceStatus(str, Enum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class LearningResource(BaseModel):
    id: str
    title: str
    url: str
    description: Optional[str] = None
    estimated_hours: float
    resource_type: str  # video, article, course, practice
    status: ResourceStatus = ResourceStatus.LOCKED
    completed_at: Optional[datetime] = None
    skipped_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    time_spent_seconds: int = 0
    order: int

class Module(BaseModel):
    id: str
    title: str
    description: str
    skills_covered: List[str]
    resources: List[LearningResource]
    estimated_total_hours: float
    week_number: int  # Which week this module belongs to
    order: int
    is_completed: bool = False
    completion_percentage: float = 0.0

class Roadmap(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    target_role: str
    skill_gaps: List[SkillGap]
    modules: List[Module]
    total_estimated_hours: float
    deadline: datetime
    progress_percentage: float = 0.0
    current_module_index: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "target_role": "Full Stack Developer",
                "skill_gaps": ["React", "Node.js", "MongoDB"],
                "total_estimated_hours": 120,
                "deadline": "2024-06-30T00:00:00"
            }
        }

class ModuleSummary(BaseModel):
    module_id: str
    module_title: str
    skills_covered: List[str]
    time_spent_hours: float
    resources_completed: int
    resources_skipped: int
    completion_date: datetime
    next_module_title: Optional[str] = None
