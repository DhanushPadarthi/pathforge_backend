from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

from app.models.user import User, UserRole
from app.models.skill import CareerRole, Skill
from app.models.resource import Resource, ResourceCreate
from app.core.database import get_collection

router = APIRouter()

# Request models
class UpdateUserRoleRequest(BaseModel):
    user_id: str
    new_role: str

class CreateCareerRoleRequest(BaseModel):
    title: str
    required_skills: List[str]
    experience_level: str
    description: Optional[str] = ""

class UpdateCareerRoleRequest(BaseModel):
    role_id: str
    title: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    description: Optional[str] = None

class CreateSkillRequest(BaseModel):
    name: str
    category: Optional[str] = "General"

# Simple admin check (in production, use proper authentication)
async def verify_admin(user_id: str):
    """Verify if user is admin"""
    users_collection = await get_collection("users")
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user or user.get("role") != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/users")
async def get_all_users(admin_id: str):
    """Get all users (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        users_collection = await get_collection("users")
        cursor = users_collection.find()
        users = await cursor.to_list(length=1000)
        
        for user in users:
            user["_id"] = str(user["_id"])
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_dashboard_stats(admin_id: str):
    """Get dashboard statistics (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        users_collection = await get_collection("users")
        roadmaps_collection = await get_collection("roadmaps")
        resources_collection = await get_collection("resources")
        
        total_users = await users_collection.count_documents({})
        total_roadmaps = await roadmaps_collection.count_documents({})
        total_resources = await resources_collection.count_documents({})
        
        # Average progress
        cursor = roadmaps_collection.find()
        roadmaps = await cursor.to_list(length=1000)
        avg_progress = sum(r.get("progress_percentage", 0) for r in roadmaps) / len(roadmaps) if roadmaps else 0
        
        return {
            "total_users": total_users,
            "total_roadmaps": total_roadmaps,
            "total_resources": total_resources,
            "average_progress": round(avg_progress, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/career-roles")
async def create_career_role(admin_id: str, role: CareerRole):
    """Create a new career role (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        roles_collection = await get_collection("career_roles")
        
        # Check if role already exists
        existing = await roles_collection.find_one({"title": role.title})
        if existing:
            raise HTTPException(status_code=400, detail="Career role already exists")
        
        result = await roles_collection.insert_one(
            role.dict(by_alias=True, exclude={"id"})
        )
        
        return {
            "message": "Career role created successfully",
            "role_id": str(result.inserted_id)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/career-roles/{role_id}")
async def update_career_role(admin_id: str, role_id: str, role: CareerRole):
    """Update a career role (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        roles_collection = await get_collection("career_roles")
        
        update_data = role.dict(by_alias=True, exclude={"id"})
        update_data["updated_at"] = datetime.utcnow()
        
        result = await roles_collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Career role not found")
        
        return {"message": "Career role updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/career-roles/{role_id}")
async def delete_career_role(admin_id: str, role_id: str):
    """Delete a career role (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        roles_collection = await get_collection("career_roles")
        result = await roles_collection.delete_one({"_id": ObjectId(role_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Career role not found")
        
        return {"message": "Career role deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Management
@router.put("/users/role")
async def update_user_role(admin_id: str, request: UpdateUserRoleRequest):
    """Update user role (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        if request.new_role not in [UserRole.STUDENT, UserRole.ADMIN]:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        users_collection = await get_collection("users")
        result = await users_collection.update_one(
            {"_id": ObjectId(request.user_id)},
            {"$set": {"role": request.new_role, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User role updated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(admin_id: str, user_id: str):
    """Delete user and their data (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        # Delete user's roadmaps first
        roadmaps_collection = await get_collection("roadmaps")
        await roadmaps_collection.delete_many({"user_id": user_id})
        
        # Delete user
        users_collection = await get_collection("users")
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User and associated data deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Skill Management
@router.post("/skills")
async def create_skill(admin_id: str, request: CreateSkillRequest):
    """Create a new skill (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        skills_collection = await get_collection("skills")
        
        # Check if skill already exists
        existing = await skills_collection.find_one({"name": request.name})
        if existing:
            raise HTTPException(status_code=400, detail="Skill already exists")
        
        result = await skills_collection.insert_one({
            "name": request.name,
            "category": request.category,
            "created_at": datetime.utcnow()
        })
        
        return {
            "message": "Skill created successfully",
            "skill_id": str(result.inserted_id)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/skills/{skill_id}")
async def delete_skill(admin_id: str, skill_id: str):
    """Delete a skill (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        skills_collection = await get_collection("skills")
        result = await skills_collection.delete_one({"_id": ObjectId(skill_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return {"message": "Skill deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Career Role Management (Enhanced)
@router.post("/career-roles/create")
async def create_career_role_new(admin_id: str, request: CreateCareerRoleRequest):
    """Create a new career role (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        roles_collection = await get_collection("career_roles")
        
        # Check if role already exists
        existing = await roles_collection.find_one({"title": request.title})
        if existing:
            raise HTTPException(status_code=400, detail="Career role already exists")
        
        result = await roles_collection.insert_one({
            "title": request.title,
            "required_skills": request.required_skills,
            "experience_level": request.experience_level,
            "description": request.description,
            "created_at": datetime.utcnow()
        })
        
        return {
            "message": "Career role created successfully",
            "role_id": str(result.inserted_id)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/career-roles/update")
async def update_career_role_new(admin_id: str, request: UpdateCareerRoleRequest):
    """Update a career role (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        roles_collection = await get_collection("career_roles")
        
        update_data = {}
        if request.title:
            update_data["title"] = request.title
        if request.required_skills:
            update_data["required_skills"] = request.required_skills
        if request.experience_level:
            update_data["experience_level"] = request.experience_level
        if request.description is not None:
            update_data["description"] = request.description
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await roles_collection.update_one(
            {"_id": ObjectId(request.role_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Career role not found")
        
        return {"message": "Career role updated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(admin_id: str, user_id: str):
    """Delete a user (Admin only)"""
    await verify_admin(admin_id)
    
    try:
        users_collection = await get_collection("users")
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Also delete user's roadmap
        roadmaps_collection = await get_collection("roadmaps")
        await roadmaps_collection.delete_many({"user_id": user_id})
        
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
