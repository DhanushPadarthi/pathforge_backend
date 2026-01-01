from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from database.connection import get_collection
import logging
import json
import re

router = APIRouter()

class ProjectRequest(BaseModel):
    skill_level: str
    focus_areas: List[str]
    project_count: Optional[int] = 3

class ProjectIdea(BaseModel):
    _id: Optional[str] = None
    title: str
    description: str
    difficulty: str
    technologies: List[str]
    estimated_duration: str
    learning_outcomes: List[str]
    resume_impact: str

class SaveProjectRequest(BaseModel):
    title: str
    description: str
    difficulty: str
    technologies: List[str]
    estimated_duration: str
    learning_outcomes: List[str]
    resume_impact: str

@router.post("/generate", response_model=List[ProjectIdea])
async def generate_projects(request: ProjectRequest):
    """Generate AI-powered project ideas"""
    try:
        logging.info(f"Generating projects for {request.skill_level}")
        
        try:
            from groq import Groq
            client = Groq()
            
            prompt = f"""Generate {request.project_count} project ideas for a {request.skill_level} developer interested in: {', '.join(request.focus_areas)}.

For each project provide JSON with: title, description, difficulty, technologies (array), estimated_duration, learning_outcomes (array), resume_impact.

Respond with only valid JSON array."""
            
            message = client.messages.create(
                model="mixtral-8x7b-32768",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            projects_data = json.loads(json_match.group() if json_match else response_text)
            
        except:
            # Fallback: return hardcoded projects
            projects_data = [
                {
                    "title": f"Build a {request.skill_level.capitalize()} {request.focus_areas[0] if request.focus_areas else 'Web'} Application",
                    "description": f"Create a full-featured application focusing on {', '.join(request.focus_areas)}.",
                    "difficulty": request.skill_level,
                    "technologies": request.focus_areas[:3] if request.focus_areas else ["JavaScript", "HTML", "CSS"],
                    "estimated_duration": "4 weeks",
                    "learning_outcomes": ["Core concepts", "Best practices", "Deployment"],
                    "resume_impact": "Demonstrates practical expertise"
                }
            ]
        
        projects = []
        for proj in projects_data:
            proj['difficulty'] = request.skill_level
            projects.append(ProjectIdea(**proj))
        
        return projects
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved")
async def get_saved_projects():
    """Get saved projects"""
    try:
        projects_collection = await get_collection("saved_projects")
        projects = await projects_collection.find({}).to_list(length=100)
        for project in projects:
            project["_id"] = str(project["_id"])
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/saved")
async def save_project(project: SaveProjectRequest):
    """Save a project"""
    try:
        projects_collection = await get_collection("saved_projects")
        project_data = project.dict()
        project_data["saved_at"] = datetime.utcnow()
        result = await projects_collection.insert_one(project_data)
        return {"message": "Project saved", "_id": str(result.inserted_id), "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/saved/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        projects_collection = await get_collection("saved_projects")
        try:
            project_oid = ObjectId(project_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid project ID")
        
        result = await projects_collection.delete_one({"_id": project_oid})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/saved/{project_id}")
async def update_project(project_id: str, project: SaveProjectRequest):
    """Update a project"""
    try:
        projects_collection = await get_collection("saved_projects")
        try:
            project_oid = ObjectId(project_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid project ID")
        
        project_data = project.dict()
        project_data["updated_at"] = datetime.utcnow()
        result = await projects_collection.update_one({"_id": project_oid}, {"$set": project_data})
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project updated", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
