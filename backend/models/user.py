from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"

class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    deadline_reminders: bool = True
    days_before_deadline: int = 3  # Send reminder X days before deadline
    weekly_summary: bool = True
    module_completion: bool = True

class UserSkill(BaseModel):
    skill_id: str
    proficiency: str  # Beginner, Intermediate, Advanced, Expert
    added_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    firebase_uid: str
    email: EmailStr
    name: str
    role: UserRole = UserRole.STUDENT
    profile_completed: bool = False
    has_resume: bool = False
    resume_file_id: Optional[str] = None  # GridFS file ID
    resume_filename: Optional[str] = None  # Original filename
    current_skills: List[UserSkill] = []
    target_role_id: Optional[str] = None
    saved_roadmaps: List[str] = []
    available_hours_per_week: Optional[int] = None
    notification_preferences: NotificationPreferences = Field(default_factory=NotificationPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "firebase_uid": "abc123xyz",
                "email": "student@example.com",
                "name": "John Doe",
                "role": "student",
                "current_skills": ["Python", "JavaScript"],
                "target_role": "Full Stack Developer",
                "available_hours_per_week": 15
            }
        }

class UserProfile(BaseModel):
    name: str
    target_role: Optional[str] = None
    available_hours_per_week: Optional[int] = None
    education: Optional[str] = None
    experience_years: Optional[int] = 0
    interests: List[str] = []

class UserUpdate(BaseModel):
    name: Optional[str] = None
    target_role_id: Optional[str] = None
    available_hours_per_week: Optional[int] = None

class UpdateNotificationPreferencesRequest(BaseModel):
    email_enabled: Optional[bool] = None
    deadline_reminders: Optional[bool] = None
    days_before_deadline: Optional[int] = None
    weekly_summary: Optional[bool] = None
    module_completion: Optional[bool] = None

class AddSkillRequest(BaseModel):
    skill_id: str
    proficiency: str
