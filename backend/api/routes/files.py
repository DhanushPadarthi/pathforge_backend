from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
import io

from services.gridfs_service import GridFSService
from database.connection import get_collection

router = APIRouter()

@router.get("/{user_id}/resume")
async def download_resume(user_id: str):
    """Download user's resume file"""
    try:
        # Get user to find resume file ID
        users_collection = await get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.get("has_resume") or not user.get("resume_file_id"):
            raise HTTPException(status_code=404, detail="Resume not found")
        
        file_id = user.get("resume_file_id")
        filename = user.get("resume_filename", "resume.pdf")
        
        # Download from GridFS
        file_data = await GridFSService.download_file(file_id)
        
        # Determine content type based on file extension
        content_type = "application/pdf"
        if filename.endswith('.docx'):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename.endswith('.doc'):
            content_type = "application/msword"
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download resume: {str(e)}")

@router.delete("/{user_id}/resume")
async def delete_resume(user_id: str):
    """Delete user's resume file"""
    try:
        users_collection = await get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.get("has_resume") and user.get("resume_file_id"):
            # Delete from GridFS
            await GridFSService.delete_file(user.get("resume_file_id"))
            
            # Update user record
            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "has_resume": False,
                        "resume_file_id": None,
                        "resume_filename": None
                    }
                }
            )
        
        return {"message": "Resume deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete resume: {str(e)}")
