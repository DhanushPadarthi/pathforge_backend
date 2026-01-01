from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class ResourceRating(BaseModel):
    user_id: str
    rating: float  # 1-5 stars
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Resource(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    url: str
    description: str
    resource_type: str  # video, article, course, practice, documentation
    skill_tags: list[str]
    estimated_hours: float
    difficulty_level: str  # beginner, intermediate, advanced
    is_free: bool = True
    rating: Optional[float] = None  # Average rating
    rating_count: int = 0  # Number of ratings
    ratings: List[ResourceRating] = []  # Individual ratings
    created_by: str  # admin user id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "React Complete Guide",
                "url": "https://example.com/react-course",
                "description": "Comprehensive React.js tutorial",
                "resource_type": "course",
                "skill_tags": ["React", "JavaScript", "Frontend"],
                "estimated_hours": 20,
                "difficulty_level": "intermediate",
                "is_free": True
            }
        }

class ResourceCreate(BaseModel):
    title: str
    url: str
    description: str
    resource_type: str
    skill_tags: list[str]
    estimated_hours: float
    difficulty_level: str
    is_free: bool = True

class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    skill_tags: Optional[list[str]] = None
    estimated_hours: Optional[float] = None
    difficulty_level: Optional[str] = None
    is_free: Optional[bool] = None

class RateResourceRequest(BaseModel):
    rating: float = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    skill_tags: Optional[list[str]] = None
    estimated_hours: Optional[float] = None
    difficulty_level: Optional[str] = None
    is_free: Optional[bool] = None
