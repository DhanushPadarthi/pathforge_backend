from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.models.skill import CareerRole, Skill, SkillGapAnalysis
from app.core.database import get_collection
from app.services.ai_service import AIService
from datetime import datetime

router = APIRouter()
ai_service = AIService()

@router.get("/career-roles")
async def get_all_career_roles():
    """Get all available career roles"""
    try:
        roles_collection = await get_collection("career_roles")
        cursor = roles_collection.find()
        roles = await cursor.to_list(length=100)
        
        for role in roles:
            role["_id"] = str(role["_id"])
        
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/career-roles/{role_id}")
async def get_career_role(role_id: str):
    """Get specific career role details"""
    try:
        roles_collection = await get_collection("career_roles")
        role = await roles_collection.find_one({"_id": ObjectId(role_id)})
        
        if not role:
            raise HTTPException(status_code=404, detail="Career role not found")
        
        role["_id"] = str(role["_id"])
        return role
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-gap")
async def analyze_skill_gap(current_skills: List[str], target_role: str):
    """Analyze skill gap for a target role"""
    try:
        # Get role requirements
        roles_collection = await get_collection("career_roles")
        role = await roles_collection.find_one({"title": target_role})
        
        if not role:
            raise HTTPException(status_code=404, detail="Career role not found")
        
        required_skills = role.get("required_skills", [])
        
        # Use AI to analyze gap
        analysis = await ai_service.analyze_skill_gap(
            current_skills=current_skills,
            target_role=target_role,
            required_skills=required_skills
        )
        
        gap_analysis = SkillGapAnalysis(
            current_skills=current_skills,
            required_skills=required_skills,
            skill_gaps=analysis["skill_gaps"],
            matching_skills=analysis["matching_skills"],
            match_percentage=analysis["match_percentage"]
        )
        
        return gap_analysis.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_all_skills():
    """Get all skills in the database"""
    try:
        skills_collection = await get_collection("skills")
        cursor = skills_collection.find()
        skills = await cursor.to_list(length=500)
        
        for skill in skills:
            skill["_id"] = str(skill["_id"])
        
        return skills
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
