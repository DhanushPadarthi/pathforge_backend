from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from models.resource import Resource, ResourceCreate, ResourceUpdate
from database.connection import get_collection
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_all_resources(skip: int = 0, limit: int = 50):
    """Get all learning resources"""
    try:
        resources_collection = await get_collection("resources")
        cursor = resources_collection.find().skip(skip).limit(limit)
        resources = await cursor.to_list(length=limit)
        
        for resource in resources:
            resource["_id"] = str(resource["_id"])
        
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{resource_id}")
async def get_resource(resource_id: str):
    """Get a specific resource"""
    try:
        resources_collection = await get_collection("resources")
        resource = await resources_collection.find_one({"_id": ObjectId(resource_id)})
        
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        resource["_id"] = str(resource["_id"])
        return resource
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/by-skills")
async def search_resources_by_skills(skills: str):
    """Search resources by skill tags"""
    try:
        skill_list = [s.strip() for s in skills.split(",")]
        resources_collection = await get_collection("resources")
        
        cursor = resources_collection.find({
            "skill_tags": {"$in": skill_list}
        })
        resources = await cursor.to_list(length=100)
        
        for resource in resources:
            resource["_id"] = str(resource["_id"])
        
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_resource(resource: ResourceCreate, admin_id: str):
    """Create a new learning resource (Admin only)"""
    try:
        resources_collection = await get_collection("resources")
        
        new_resource = Resource(
            **resource.dict(),
            created_by=admin_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await resources_collection.insert_one(
            new_resource.dict(by_alias=True, exclude={"id"})
        )
        
        return {
            "message": "Resource created successfully",
            "resource_id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{resource_id}")
async def update_resource(resource_id: str, resource_update: ResourceUpdate):
    """Update a learning resource (Admin only)"""
    try:
        resources_collection = await get_collection("resources")
        
        update_data = {k: v for k, v in resource_update.dict(exclude_unset=True).items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await resources_collection.update_one(
            {"_id": ObjectId(resource_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {"message": "Resource updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{resource_id}")
async def delete_resource(resource_id: str):
    """Delete a learning resource (Admin only)"""
    try:
        resources_collection = await get_collection("resources")
        result = await resources_collection.delete_one({"_id": ObjectId(resource_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {"message": "Resource deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
