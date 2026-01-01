"""
GridFS service for storing resume files in MongoDB
"""
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from app.core.database import get_database
import os
from typing import BinaryIO

class GridFSService:
    """Service to handle file storage in MongoDB GridFS"""
    
    @staticmethod
    async def get_bucket():
        """Get GridFS bucket for file storage"""
        db = await get_database()
        return AsyncIOMotorGridFSBucket(db, bucket_name="resumes")
    
    @staticmethod
    async def upload_file(file_data: bytes, filename: str, user_id: str, content_type: str) -> str:
        """
        Upload a file to GridFS
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_id: User ID
            content_type: MIME type of file
            
        Returns:
            file_id: GridFS file ID as string
        """
        bucket = await GridFSService.get_bucket()
        
        file_id = await bucket.upload_from_stream(
            filename,
            file_data,
            metadata={
                "user_id": user_id,
                "content_type": content_type,
                "original_filename": filename
            }
        )
        
        return str(file_id)
    
    @staticmethod
    async def download_file(file_id: str) -> bytes:
        """
        Download a file from GridFS
        
        Args:
            file_id: GridFS file ID
            
        Returns:
            File data as bytes
        """
        from bson import ObjectId
        bucket = await GridFSService.get_bucket()
        
        grid_out = await bucket.open_download_stream(ObjectId(file_id))
        file_data = await grid_out.read()
        
        return file_data
    
    @staticmethod
    async def delete_file(file_id: str):
        """
        Delete a file from GridFS
        
        Args:
            file_id: GridFS file ID
        """
        from bson import ObjectId
        bucket = await GridFSService.get_bucket()
        await bucket.delete(ObjectId(file_id))
    
    @staticmethod
    async def get_file_info(file_id: str) -> dict:
        """
        Get file metadata from GridFS
        
        Args:
            file_id: GridFS file ID
            
        Returns:
            File metadata dictionary
        """
        from bson import ObjectId
        bucket = await GridFSService.get_bucket()
        
        cursor = bucket.find({"_id": ObjectId(file_id)})
        files = await cursor.to_list(length=1)
        
        if files:
            file_doc = files[0]
            return {
                "filename": file_doc.filename,
                "length": file_doc.length,
                "upload_date": file_doc.upload_date,
                "metadata": file_doc.metadata
            }
        return None
