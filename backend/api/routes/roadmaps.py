from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from datetime import datetime, timedelta
import uuid
import logging
from models.roadmap import Roadmap, Module, LearningResource, ResourceStatus, ModuleSummary
from models.skill import SkillGapAnalysis
from models.resource import RateResourceRequest
from database.connection import get_collection
from services.ai_service import AIService
from pydantic import BaseModel
from typing import Optional
from logger_config import roadmap_logger, resource_logger, time_logger, combined_logger
router = APIRouter()
ai_service = AIService()
class GenerateRoadmapRequest(BaseModel):
    user_id: str
    target_role_id: Optional[str] = None
    custom_role: Optional[str] = None  # For custom career role input
    deadline_weeks: int = 12
    preferences: Optional[dict] = None  # For additional preferences like difficulty
@router.post("/generate")
async def generate_roadmap(request: GenerateRoadmapRequest):
    """Generate personalized learning roadmap for user"""
    try:
        # Get user data
        users_collection = await get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(request.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Use custom_role if provided, otherwise use target_role_id
        if request.custom_role:
            # Use custom role directly
            target_role = request.custom_role
            career_role = {
                "title": request.custom_role,
                "required_skills": [],
                "_id": None
            }
            target_role_id = None
        else:
            # Use target_role_id from request or user profile
            target_role_id = request.target_role_id or user.get("target_role_id")
            if not target_role_id:
                raise HTTPException(status_code=400, detail="User must set a target role first")
            # Get career role requirements
            roles_collection = await get_collection("career_roles")
            career_role = await roles_collection.find_one({"_id": ObjectId(target_role_id)})
            if not career_role:
                raise HTTPException(status_code=404, detail="Career role not found")
            target_role = career_role.get("title", "Developer")
        # Extract skill names from user skills (which are now objects)
        user_skills = user.get("current_skills", [])
        skills_collection = await get_collection("skills")
        current_skill_names = []
        for user_skill in user_skills:
            skill = await skills_collection.find_one({"_id": ObjectId(user_skill["skill_id"])})
            if skill:
                current_skill_names.append(skill["name"])
        required_skills = career_role.get("required_skills", [])
        skill_gap_analysis = await ai_service.analyze_skill_gap(
            current_skills=current_skill_names,
            target_role=career_role["title"],
            required_skills=required_skills
        )
        # Generate roadmap using AI
        available_hours = user.get("available_hours_per_week", 10)
        # Extract preferences
        preferences = request.preferences or {}
        difficulty_level = preferences.get("difficulty", "intermediate")
        duration_str = preferences.get("duration", "12 weeks")
        # Parse weeks from duration string (e.g., "12 weeks" -> 12)
        deadline_weeks = request.deadline_weeks
        if duration_str:
            try:
                deadline_weeks = int(duration_str.split()[0])
            except:
                pass
        roadmap_data = await ai_service.generate_learning_roadmap(
            skill_gaps=skill_gap_analysis["skill_gaps"],
            target_role=career_role["title"],
            available_hours_per_week=available_hours,
            deadline_weeks=deadline_weeks,
            difficulty_level=difficulty_level
        )
        # Validate YouTube videos in roadmap and replace unavailable ones
        roadmap_data = await ai_service.validate_and_fix_roadmap_resources(roadmap_data)
        # Validate roadmap data
        if not roadmap_data.get("modules"):
            raise HTTPException(
                status_code=500,
                detail="AI service failed to generate roadmap modules. Please try again or check OpenAI API status."
            )
        # Structure the roadmap with weekly organization
        modules = []
        total_weeks = deadline_weeks or 12
        total_modules = len(roadmap_data.get("modules", []))
        # Calculate week assignment for each module to evenly distribute across duration
        # Each module gets a proportional week range
        weeks_per_module = total_weeks / total_modules if total_modules > 0 else 1
        for idx, module_data in enumerate(roadmap_data.get("modules", [])):
            # Calculate module hours
            module_hours = module_data.get("estimated_hours")
            if module_hours is None:
                # Estimate from resources
                module_hours = sum(r.get("estimated_hours", 0) for r in module_data.get("resources", []))
            module_hours = float(module_hours) if module_hours else 0.0
            # Assign week number based on even distribution
            # Module 0 -> Week 1, Module 1 -> Week 3, etc. for 12 weeks / 6 modules
            current_week = int(idx * weeks_per_module) + 1
            previous_week = int((idx - 1) * weeks_per_module) + 1 if idx > 0 else 1
            # Now create resources with correct week-based unlocking
            resources = []
            for r_idx, resource_data in enumerate(module_data.get("resources", [])):
                # Unlock first resource of first module in each week
                is_week_start = (idx == 0 or current_week != previous_week)
                should_unlock = is_week_start and r_idx == 0
                resource = LearningResource(
                    id=str(uuid.uuid4()),
                    title=resource_data["title"],
                    url=resource_data["url"],
                    description=resource_data.get("description", ""),
                    estimated_hours=resource_data["estimated_hours"],
                    resource_type=resource_data["resource_type"],
                    status=ResourceStatus.UNLOCKED if should_unlock else ResourceStatus.LOCKED,
                    order=r_idx,
                    time_spent_seconds=0
                )
                resources.append(resource)
            # Module hours already calculated above, week already assigned
            module = Module(
                id=str(uuid.uuid4()),
                title=module_data["title"],
                description=module_data["description"],
                skills_covered=module_data["skills_covered"],
                resources=resources,
                estimated_total_hours=module_hours,
                week_number=current_week,
                order=idx,
                is_completed=False
            )
            modules.append(module)
        # Calculate total hours
        total_hours = sum(m.estimated_total_hours for m in modules)
        # Create roadmap
        roadmap = Roadmap(
            user_id=request.user_id,
            target_role=career_role["title"],
            skill_gaps=skill_gap_analysis["skill_gaps"],
            modules=modules,
            total_estimated_hours=total_hours,
            deadline=datetime.utcnow() + timedelta(weeks=request.deadline_weeks),
            progress_percentage=0.0,
            current_module_index=0
        )
        # Save to database
        roadmaps_collection = await get_collection("roadmaps")
        # Insert new roadmap (keeping existing ones)
        result = await roadmaps_collection.insert_one(
            roadmap.dict(by_alias=True, exclude={"id"})
        )
        return {
            "message": "Roadmap generated successfully",
            "_id": str(result.inserted_id),
            "roadmap_id": str(result.inserted_id),
            "total_modules": len(modules),
            "total_hours": total_hours,
            "skill_gaps": skill_gap_analysis["skill_gaps"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")
@router.get("/user/{user_id}")
async def get_user_roadmap(user_id: str, search: str = None, status: str = None, sort_by: str = "created_at"):
    """Get all roadmaps for a user with search and filter"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        # Build query
        query = {"user_id": user_id}
        # Add search filter (search in target_role and skill_gaps)
        # Skip search if it looks like a JWT token (starts with "eyJ")
        if search and not search.startswith("eyJ"):
            query["$or"] = [
                {"target_role": {"$regex": search, "$options": "i"}},
                {"skill_gaps.skill": {"$regex": search, "$options": "i"}}
            ]
        # Add status filter
        if status:
            if status == "completed":
                query["progress_percentage"] = {"$gte": 100}
            elif status == "in_progress":
                query["progress_percentage"] = {"$gt": 0, "$lt": 100}
            elif status == "not_started":
                query["progress_percentage"] = 0
        # Execute query
        roadmaps_cursor = roadmaps_collection.find(query)
        # Sort
        sort_order = -1 if sort_by in ["created_at", "updated_at"] else 1
        roadmaps_cursor = roadmaps_cursor.sort(sort_by, sort_order)
        roadmaps = await roadmaps_cursor.to_list(length=None)
        if not roadmaps:
            return []
        for roadmap in roadmaps:
            roadmap["_id"] = str(roadmap["_id"])
        return roadmaps
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/templates")
async def get_roadmap_templates(category: str = None):
    """Get all available roadmap templates"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        # Build query for templates
        query = {"is_template": True, "is_deleted": False}
        if category:
            query["category"] = category
        templates = await roadmaps_collection.find(query).to_list(length=100)
        # Convert ObjectId to string
        for template in templates:
            template["_id"] = str(template["_id"])
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/templates/{template_id}/clone")
async def clone_template(template_id: str, user_id: str):
    """Clone a template roadmap for a user"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        # Get template
        template = await roadmaps_collection.find_one({
            "_id": ObjectId(template_id),
            "is_template": True
        })
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        # Clone template for user
        new_roadmap = template.copy()
        new_roadmap.pop("_id")
        new_roadmap["user_id"] = user_id
        new_roadmap["is_template"] = False
        new_roadmap["is_public"] = False
        new_roadmap["progress_percentage"] = 0
        new_roadmap["current_module_index"] = 0
        new_roadmap["created_at"] = datetime.utcnow()
        new_roadmap["updated_at"] = datetime.utcnow()
        # Reset all progress
        for module in new_roadmap.get("modules", []):
            module["completed"] = False
            for resource in module.get("resources", []):
                resource["status"] = "not_started"
                resource["completed"] = False
                resource["time_spent_seconds"] = 0
                resource["rating"] = 0
                resource["notes"] = ""
        # Insert cloned roadmap
        result = await roadmaps_collection.insert_one(new_roadmap)
        return {
            "message": "Template cloned successfully",
            "_id": str(result.inserted_id),
            "roadmap_id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/{roadmap_id}")
async def get_roadmap(roadmap_id: str):
    """Get a specific roadmap by ID"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        try:
            roadmap_oid = ObjectId(roadmap_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid roadmap ID")
        roadmap = await roadmaps_collection.find_one({"_id": roadmap_oid})
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        roadmap["_id"] = str(roadmap["_id"])
        return roadmap
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/{roadmap_id}")
async def delete_roadmap(roadmap_id: str):
    """Delete a roadmap by ID"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        # Convert to ObjectId
        try:
            roadmap_oid = ObjectId(roadmap_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid roadmap ID format")
        # Delete the roadmap
        result = await roadmaps_collection.delete_one({"_id": roadmap_oid})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        return {"message": "Roadmap deleted successfully", "roadmap_id": roadmap_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete roadmap: {str(e)}")
@router.post("/{roadmap_id}/complete-resource")
async def complete_resource(roadmap_id: str, module_id: str, resource_id: str):
    """Mark a resource as completed"""
    try:
        from bson import ObjectId
        roadmaps_collection = await get_collection("roadmaps")
        roadmap = await roadmaps_collection.find_one({"_id": ObjectId(roadmap_id)})
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        # Find and update the resource
        updated = False
        for module in roadmap["modules"]:
            if module["id"] == module_id:
                for resource in module["resources"]:
                    if resource["id"] == resource_id:
                        resource["status"] = "completed"
                        resource["completed_at"] = datetime.utcnow()
                        # Unlock next resource
                        next_idx = resource["order"] + 1
                        if next_idx < len(module["resources"]):
                            module["resources"][next_idx]["status"] = "unlocked"
                        updated = True
                        break
            if updated:
                break
        if not updated:
            raise HTTPException(status_code=404, detail="Resource not found")
        # Recalculate progress and get newly completed modules
        newly_completed_modules = await recalculate_progress(roadmaps_collection, roadmap)
        # Generate AI summary for newly completed modules
        module_summaries = []
        if newly_completed_modules:
            for completed_module_id in newly_completed_modules:
                for module in roadmap["modules"]:
                    if module["id"] == completed_module_id:
                        # Calculate module stats
                        total_time = sum(r.get("time_spent_seconds", 0) for r in module["resources"]) / 3600
                        completed_count = sum(1 for r in module["resources"] if r["status"] == "completed")
                        skipped_count = sum(1 for r in module["resources"] if r["status"] == "skipped")
                        # Generate summary
                        summary = await ai_service.generate_module_summary(
                            module_data=module,
                            user_progress={
                                "time_spent_hours": round(total_time, 1),
                                "resources_completed": completed_count,
                                "resources_skipped": skipped_count
                            }
                        )
                        # Store summary in module
                        module["completion_summary"] = summary
                        module["summary_generated_at"] = datetime.utcnow()
                        module_summaries.append({
                            "module_id": module["id"],
                            "module_title": module["title"],
                            "summary": summary
                        })
        # CRITICAL: Save updated roadmap to database
        # Remove _id before saving to avoid MongoDB errors
        roadmap_to_save = {k: v for k, v in roadmap.items() if k != '_id'}
        await roadmaps_collection.update_one({"_id": ObjectId(roadmap_id)}, {"$set": roadmap_to_save})
        return {
            "message": "Resource marked as completed",
            "module_summaries": module_summaries
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/{roadmap_id}/skip-resource")
async def skip_resource(roadmap_id: str, module_id: str, resource_id: str):
    """Mark a resource as skipped (already known)"""
    try:
        from bson import ObjectId
        roadmaps_collection = await get_collection("roadmaps")
        roadmap = await roadmaps_collection.find_one({"_id": ObjectId(roadmap_id)})
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        # Find and update the resource
        updated = False
        for module in roadmap["modules"]:
            if module["id"] == module_id:
                for resource in module["resources"]:
                    if resource["id"] == resource_id:
                        resource["status"] = "skipped"
                        resource["skipped_at"] = datetime.utcnow()
                        # Unlock next resource
                        next_idx = resource["order"] + 1
                        if next_idx < len(module["resources"]):
                            module["resources"][next_idx]["status"] = "unlocked"
                        updated = True
                        break
            if updated:
                break
        if not updated:
            raise HTTPException(status_code=404, detail="Resource not found")
        # Recalculate progress and get newly completed modules
        newly_completed_modules = await recalculate_progress(roadmaps_collection, roadmap)
        # Generate AI summary for newly completed modules
        module_summaries = []
        if newly_completed_modules:
            for completed_module_id in newly_completed_modules:
                for module in roadmap["modules"]:
                    if module["id"] == completed_module_id:
                        # Calculate module stats
                        total_time = sum(r.get("time_spent_seconds", 0) for r in module["resources"]) / 3600
                        completed_count = sum(1 for r in module["resources"] if r["status"] == "completed")
                        skipped_count = sum(1 for r in module["resources"] if r["status"] == "skipped")
                        # Generate summary
                        summary = await ai_service.generate_module_summary(
                            module_data=module,
                            user_progress={
                                "time_spent_hours": round(total_time, 1),
                                "resources_completed": completed_count,
                                "resources_skipped": skipped_count
                            }
                        )
                        # Store summary in module
                        module["completion_summary"] = summary
                        module["summary_generated_at"] = datetime.utcnow()
                        module_summaries.append({
                            "module_id": module["id"],
                            "module_title": module["title"],
                            "summary": summary
                        })
        # CRITICAL: Save updated roadmap to database
        # Remove _id before saving to avoid MongoDB errors
        roadmap_to_save = {k: v for k, v in roadmap.items() if k != '_id'}
        await roadmaps_collection.update_one({"_id": ObjectId(roadmap_id)}, {"$set": roadmap_to_save})
        return {
            "message": "Resource skipped",
            "module_summaries": module_summaries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/{user_id}/module-summary/{module_id}")
async def get_module_summary(user_id: str, module_id: str):
    """Get summary after completing a module"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        roadmap = await roadmaps_collection.find_one({"user_id": user_id})
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        # Find the module
        module_data = None
        next_module_title = None
        for idx, module in enumerate(roadmap["modules"]):
            if module["id"] == module_id:
                module_data = module
                if idx + 1 < len(roadmap["modules"]):
                    next_module_title = roadmap["modules"][idx + 1]["title"]
                break
        if not module_data:
            raise HTTPException(status_code=404, detail="Module not found")
        # Calculate statistics
        resources_completed = sum(
            1 for r in module_data["resources"] 
            if r["status"] == "completed"
        )
        resources_skipped = sum(
            1 for r in module_data["resources"] 
            if r["status"] == "skipped"
        )
        time_spent = sum(
            r["estimated_hours"] for r in module_data["resources"]
            if r["status"] == "completed"
        )
        # Generate AI summary
        ai_summary = await ai_service.generate_module_summary(
            module_data=module_data,
            user_progress={
                "time_spent_hours": time_spent,
                "resources_completed": resources_completed,
                "resources_skipped": resources_skipped
            }
        )
        summary = ModuleSummary(
            module_id=module_id,
            module_title=module_data["title"],
            skills_covered=module_data["skills_covered"],
            time_spent_hours=time_spent,
            resources_completed=resources_completed,
            resources_skipped=resources_skipped,
            completion_date=datetime.utcnow(),
            next_module_title=next_module_title
        )
        return {
            **summary.dict(),
            "ai_summary": ai_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def recalculate_progress(collection, roadmap):
    """Recalculate overall progress percentage and unlock next module if current is complete"""
    total_resources = 0
    completed_resources = 0
    current_module_index = roadmap.get("current_module_index", 0)
    completed_module_ids = []  # Track newly completed modules for summary generation
    # Check each module's completion status
    for idx, module in enumerate(roadmap["modules"]):
        module_total = 0
        module_completed = 0
        was_completed = module.get("is_completed", False)
        for resource in module["resources"]:
            total_resources += 1
            module_total += 1
            # Compare strings since MongoDB stores status as string
            if resource["status"] in ["completed", "skipped"]:
                completed_resources += 1
                module_completed += 1
        # Mark module as completed if all resources are done
        if module_total > 0 and module_completed == module_total:
            module["is_completed"] = True
            # Track newly completed modules (for summary generation)
            if not was_completed:
                completed_module_ids.append(module["id"])
            # Unlock next module's first resource
            if idx + 1 < len(roadmap["modules"]):
                next_module = roadmap["modules"][idx + 1]
                # Compare string since MongoDB stores status as string
                if next_module["resources"] and next_module["resources"][0]["status"] == "locked":
                    next_module["resources"][0]["status"] = "unlocked"
        else:
            module["is_completed"] = False
    # Update current_module_index to the highest accessible module
    # (completed, unlocked, or in_progress)
    highest_accessible = 0
    for idx, module in enumerate(roadmap["modules"]):
        if module.get("is_completed") or (module["resources"] and module["resources"][0]["status"] in ["unlocked", "in_progress", "completed", "skipped"]):
            highest_accessible = idx
    roadmap["current_module_index"] = highest_accessible
    progress = (completed_resources / total_resources * 100) if total_resources > 0 else 0
    return completed_module_ids  # Return newly completed modules
    await collection.update_one(
        {"_id": roadmap["_id"]},
        {
            "$set": {
                "modules": roadmap["modules"],
                "current_module_index": roadmap.get("current_module_index", current_module_index),
                "progress_percentage": round(progress, 2),
                "updated_at": datetime.utcnow()
            }
        }
    )
@router.post("/{roadmap_id}/open-resource")
async def open_resource(roadmap_id: str, module_id: str, resource_id: str):
    """Mark resource as opened and start time tracking"""
    try:
        from bson import ObjectId
        msg = f"Roadmap: {roadmap_id[:8]}..., Module: {module_id[:8]}..., Resource: {resource_id[:8]}..."
        resource_logger.info(f"Opening resource - {msg}")
        combined_logger.info(f"[OPEN] {msg}")
        roadmaps_collection = await get_collection("roadmaps")
        roadmap = await roadmaps_collection.find_one({"_id": ObjectId(roadmap_id)})
        if not roadmap:
            resource_logger.error(f"Roadmap not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Roadmap not found")
        # Find and update the resource
        updated = False
        opened_time = None
        for module in roadmap["modules"]:
            if module["id"] == module_id:
                for resource in module["resources"]:
                    if resource["id"] == resource_id:
                        resource_logger.info(f"Found resource: {resource['title']}, Status: {resource['status']}")
                        if resource["status"] == "unlocked" or resource["status"] == "in_progress":
                            resource["status"] = "in_progress"
                            resource_logger.info(f"Changed status to in_progress for {resource['title']}")
                        if not resource.get("opened_at"):
                            resource["opened_at"] = datetime.utcnow()
                        else:
                            opened_time = resource["opened_at"]
                        updated = True
                        break
        if not updated:
            raise HTTPException(status_code=404, detail="Resource not found")
        await roadmaps_collection.update_one(
            {"_id": roadmap["_id"]},
            {"$set": {"modules": roadmap["modules"], "updated_at": datetime.utcnow()}}
        )
        return {"message": "Resource opened", "opened_at": str(opened_time) if opened_time else None, "status": "in_progress"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/{roadmap_id}/update-time")
async def update_time_spent(roadmap_id: str, module_id: str, resource_id: str, time_spent_seconds: int):
    """Update time spent on a resource"""
    try:
        from bson import ObjectId
        msg = f"Roadmap: {roadmap_id[:8]}..., Time: {time_spent_seconds}s ({time_spent_seconds//60}m {time_spent_seconds%60}s)"
        time_logger.info(msg)
        combined_logger.info(f"[TIME UPDATE] {msg}")
        roadmaps_collection = await get_collection("roadmaps")
        roadmap = await roadmaps_collection.find_one({"_id": ObjectId(roadmap_id)})
        if not roadmap:
            time_logger.error(f"Roadmap not found: {roadmap_id}")
            raise HTTPException(status_code=404, detail="Roadmap not found")
        # Find and update the resource
        updated = False
        auto_completed = False
        estimated_hours = 0
        for module in roadmap["modules"]:
            if module["id"] == module_id:
                for resource in module["resources"]:
                    if resource["id"] == resource_id:
                        resource["time_spent_seconds"] = time_spent_seconds
                        estimated_hours = resource["estimated_hours"]
                        # Auto-complete if time >= 90% of estimated time
                        estimated_seconds = estimated_hours * 3600
                        threshold = estimated_seconds * 0.9
                        if time_spent_seconds >= threshold and resource["status"] != "completed":
                            resource["status"] = "completed"
                            resource["completed_at"] = datetime.utcnow()
                            auto_completed = True
                            # Unlock next resource in same module
                            next_idx = resource["order"] + 1
                            if next_idx < len(module["resources"]):
                                module["resources"][next_idx]["status"] = "unlocked"
                            else:
                                # Module completed, unlock next module
                                module["is_completed"] = True
                                module_idx = next((i for i, m in enumerate(roadmap["modules"]) if m["id"] == module_id), None)
                                if module_idx is not None and module_idx + 1 < len(roadmap["modules"]):
                                    # Unlock first resource of next module
                                    roadmap["modules"][module_idx + 1]["resources"][0]["status"] = "unlocked"
                            updated = True
                            break
            if updated:
                break
        if not updated:
            raise HTTPException(status_code=404, detail="Resource not found")
        # Recalculate progress if auto-completed
        if auto_completed:
            await recalculate_progress(roadmaps_collection, roadmap)
        else:
            await roadmaps_collection.update_one(
                {"_id": roadmap["_id"]},
                {"$set": {"modules": roadmap["modules"], "updated_at": datetime.utcnow()}}
            )
        return {
            "message": "Time updated",
            "auto_completed": auto_completed,
            "time_spent_seconds": time_spent_seconds,
            "estimated_seconds": estimated_hours * 3600,
            "completion_percentage": round((time_spent_seconds / (estimated_hours * 3600)) * 100, 2) if estimated_hours > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/{user_id}/weeks")
async def get_weeks_overview(user_id: str):
    """Get roadmap organized by weeks"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        roadmap = await roadmaps_collection.find_one({"user_id": user_id})
        if not roadmap:
            raise HTTPException(status_code=404, detail="No roadmap found")
        # Organize modules by week
        weeks = {}
        for module in roadmap["modules"]:
            week_num = module.get("week_number", 1)
            if week_num not in weeks:
                weeks[week_num] = {
                    "week_number": week_num,
                    "modules": [],
                    "total_hours": 0,
                    "completed_modules": 0
                }
            weeks[week_num]["modules"].append({
                "id": module["id"],
                "title": module["title"],
                "description": module["description"],
                "skills_covered": module["skills_covered"],
                "estimated_hours": module["estimated_total_hours"],
                "is_completed": module.get("is_completed", False),
                "resources_count": len(module["resources"])
            })
            weeks[week_num]["total_hours"] += module["estimated_total_hours"]
            if module.get("is_completed"):
                weeks[week_num]["completed_modules"] += 1
        return {
            "weeks": list(weeks.values()),
            "total_weeks": len(weeks),
            "target_role": roadmap["target_role"],
            "overall_progress": roadmap.get("progress_percentage", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/{roadmap_id}/rate-resource")
async def rate_resource(roadmap_id: str, user_id: str, resource_url: str, rating_data: RateResourceRequest):
    """Rate a specific resource within a roadmap"""
    try:
        roadmaps_collection = await get_collection("roadmaps")
        # Find the roadmap and resource
        roadmap = await roadmaps_collection.find_one({
            "_id": ObjectId(roadmap_id),
            "user_id": user_id
        })
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        # Find the resource in modules
        resource_found = False
        resource_title = ""
        for module in roadmap.get("modules", []):
            for resource in module.get("resources", []):
                if resource.get("url") == resource_url:
                    resource_found = True
                    resource_title = resource.get("title", "")
                    # Add or update rating
                    if "ratings" not in resource:
                        resource["ratings"] = []
                    # Check if user already rated
                    existing_rating = None
                    for i, r in enumerate(resource["ratings"]):
                        if r.get("user_id") == user_id:
                            existing_rating = i
                            break
                    new_rating = {
                        "user_id": user_id,
                        "rating": rating_data.rating,
                        "comment": rating_data.comment,
                        "created_at": datetime.utcnow()
                    }
                    if existing_rating is not None:
                        # Update existing rating
                        resource["ratings"][existing_rating] = new_rating
                    else:
                        # Add new rating
                        resource["ratings"].append(new_rating)
                    # Calculate average rating
                    total_rating = sum(r.get("rating", 0) for r in resource["ratings"])
                    resource["rating"] = round(total_rating / len(resource["ratings"]), 1)
                    resource["rating_count"] = len(resource["ratings"])
                    break
            if resource_found:
                break
        if not resource_found:
            raise HTTPException(status_code=404, detail="Resource not found in roadmap")
        # Update roadmap in database
        await roadmaps_collection.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$set": {
                    "modules": roadmap["modules"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        resource_logger.info(f"Resource rated: {resource_title} - {rating_data.rating} stars by user {user_id}")
        return {
            "message": "Resource rated successfully",
            "resource_title": resource_title,
            "your_rating": rating_data.rating,
            "average_rating": resource["rating"],
            "total_ratings": resource["rating_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
