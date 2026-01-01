from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from typing import Optional
from bson import ObjectId
import os
import tempfile
from datetime import datetime
from pydantic import BaseModel

from app.models.user import User, UserProfile, UserUpdate, AddSkillRequest, UserSkill, UpdateNotificationPreferencesRequest
from app.core.database import get_collection
from app.services.resume_parser import ResumeParser
from app.services.ai_service import AIService
from app.services.gridfs_service import GridFSService

class UpdateSkillRequest(BaseModel):
    proficiency: str

router = APIRouter()
ai_service = AIService()

@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        users_collection = await get_collection("users")
        skills_collection = await get_collection("skills")
        
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["_id"] = str(user["_id"])
        
        # Populate skill names
        enriched_skills = []
        for user_skill in user.get("current_skills", []):
            skill = await skills_collection.find_one({"_id": ObjectId(user_skill["skill_id"])})
            if skill:
                enriched_skills.append({
                    "skill_id": user_skill["skill_id"],
                    "name": skill["name"],
                    "category": skill.get("category", ""),
                    "proficiency": user_skill["proficiency"],
                    "added_at": user_skill["added_at"]
                })
        
        user["current_skills"] = enriched_skills
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user profile"""
    try:
        users_collection = await get_collection("users")
        
        update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found or no changes made")
        
        return {"message": "User updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/upload-resume")
async def upload_resume(
    user_id: str,
    file: UploadFile = File(...)
):
    """Upload and process user resume"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file data
        file_data = await file.read()
        
        # Upload to MongoDB GridFS
        file_id = await GridFSService.upload_file(
            file_data=file_data,
            filename=file.filename,
            user_id=user_id,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Save to temporary file for parsing
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_data)
            temp_path = tmp_file.name
        
        try:
            # Extract text from resume
            resume_text = ResumeParser.parse_resume(temp_path, file_ext)
            cleaned_text = ResumeParser.clean_text(resume_text)
            
            # Extract skills using AI
            extracted_data = await ai_service.extract_skills_from_resume(cleaned_text)
            
            # Get skills collection to match extracted skill names with skill IDs
            skills_collection = await get_collection("skills")
            
            # Convert extracted skill names to UserSkill objects
            user_skills = []
            for skill_name in extracted_data.get("skills", []):
                # Find skill in database
                skill = await skills_collection.find_one({"name": {"$regex": f"^{skill_name}$", "$options": "i"}})
                if skill:
                    user_skills.append({
                        "skill_id": str(skill["_id"]),
                        "proficiency": "Intermediate",  # Default proficiency
                        "added_at": datetime.utcnow()
                    })
            
            # Update user profile
            users_collection = await get_collection("users")
            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "has_resume": True,
                        "resume_file_id": file_id,
                        "resume_filename": file.filename,
                        "current_skills": user_skills,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "message": "Resume uploaded and processed successfully",
                "file_id": file_id,
                "extracted_skills": user_skills,
                "experience_years": extracted_data.get("experience_years", 0),
                "education": extracted_data.get("education", "")
            }
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume processing failed: {str(e)}")

@router.post("/{user_id}/complete-profile")
async def complete_profile_without_resume(user_id: str, profile: UserProfile):
    """Complete profile for users without resume"""
    try:
        users_collection = await get_collection("users")
        skills_collection = await get_collection("skills")
        
        # Find skills in database for the interests
        user_skills = []
        for interest in profile.interests:
            skill = await skills_collection.find_one({"name": {"$regex": f"^{interest}$", "$options": "i"}})
            if skill:
                user_skills.append({
                    "skill_id": str(skill["_id"]),
                    "proficiency": "Beginner",
                    "added_at": datetime.utcnow()
                })
        
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "name": profile.name,
                    "target_role_id": profile.target_role,
                    "available_hours_per_week": profile.available_hours_per_week,
                    "current_skills": user_skills,
                    "profile_completed": True,
                    "has_resume": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Profile completed successfully",
            "added_skills": user_skills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/progress")
async def get_user_progress(user_id: str):
    """Get user's overall learning progress"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        roadmap = await roadmaps_collection.find_one({"user_id": user_id})
        
        if not roadmap:
            return {
                "has_roadmap": False,
                "progress_percentage": 0
            }
        
        return {
            "has_roadmap": True,
            "progress_percentage": roadmap.get("progress_percentage", 0),
            "current_module": roadmap.get("current_module_index", 0),
            "total_modules": len(roadmap.get("modules", [])),
            "target_role": roadmap.get("target_role")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Skill Management Endpoints
@router.get("/{user_id}/skills")
async def get_user_skills(user_id: str):
    """Get all skills for a user with full skill details"""
    try:
        users_collection = await get_collection("users")
        skills_collection = await get_collection("skills")
        
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user skills with full details
        user_skills = []
        for user_skill in user.get("current_skills", []):
            skill = await skills_collection.find_one({"_id": ObjectId(user_skill["skill_id"])})
            if skill:
                user_skills.append({
                    "skill_id": user_skill["skill_id"],
                    "name": skill["name"],
                    "category": skill["category"],
                    "proficiency": user_skill["proficiency"],
                    "added_at": user_skill["added_at"]
                })
        
        return user_skills
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/skills")
async def add_user_skill(user_id: str, skill_request: AddSkillRequest):
    """Add a new skill to user's profile"""
    try:
        users_collection = await get_collection("users")
        skills_collection = await get_collection("skills")
        
        # Verify skill exists
        skill = await skills_collection.find_one({"_id": ObjectId(skill_request.skill_id)})
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        # Check if user already has this skill
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        for existing_skill in user.get("current_skills", []):
            if existing_skill["skill_id"] == skill_request.skill_id:
                raise HTTPException(status_code=400, detail="Skill already exists")
        
        # Add skill
        new_skill = {
            "skill_id": skill_request.skill_id,
            "proficiency": skill_request.proficiency,
            "added_at": datetime.utcnow()
        }
        
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$push": {"current_skills": new_skill},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "message": "Skill added successfully",
            "skill": {
                **new_skill,
                "name": skill["name"],
                "category": skill["category"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/skills/{skill_id}")
async def update_user_skill(user_id: str, skill_id: str, request: UpdateSkillRequest):
    """Update proficiency level of a user's skill"""
    try:
        users_collection = await get_collection("users")
        
        result = await users_collection.update_one(
            {
                "_id": ObjectId(user_id),
                "current_skills.skill_id": skill_id
            },
            {
                "$set": {
                    "current_skills.$.proficiency": request.proficiency,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User or skill not found")
        
        return {"message": "Skill updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/skills/{skill_id}")
async def delete_user_skill(user_id: str, skill_id: str):
    """Remove a skill from user's profile"""
    try:
        users_collection = await get_collection("users")
        
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$pull": {"current_skills": {"skill_id": skill_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User or skill not found")
        
        return {"message": "Skill removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/notifications")
async def get_notification_preferences(user_id: str):
    """Get user notification preferences"""
    try:
        users_collection = await get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return preferences or defaults
        preferences = user.get("notification_preferences", {
            "email_enabled": True,
            "deadline_reminders": True,
            "days_before_deadline": 3,
            "weekly_summary": True,
            "module_completion": True
        })
        
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/notifications")
async def update_notification_preferences(user_id: str, preferences: UpdateNotificationPreferencesRequest):
    """Update user notification preferences"""
    try:
        users_collection = await get_collection("users")
        
        # Build update document
        update_data = {}
        if preferences.email_enabled is not None:
            update_data["notification_preferences.email_enabled"] = preferences.email_enabled
        if preferences.deadline_reminders is not None:
            update_data["notification_preferences.deadline_reminders"] = preferences.deadline_reminders
        if preferences.days_before_deadline is not None:
            update_data["notification_preferences.days_before_deadline"] = preferences.days_before_deadline
        if preferences.weekly_summary is not None:
            update_data["notification_preferences.weekly_summary"] = preferences.weekly_summary
        if preferences.module_completion is not None:
            update_data["notification_preferences.module_completion"] = preferences.module_completion
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "Notification preferences updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
