"""
Test script to verify MongoDB GridFS resume storage
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pymongo.server_api import ServerApi
import os

async def check_mongodb_gridfs():
    """Check MongoDB and GridFS collections"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017/", server_api=ServerApi('1'))
    db = client["pathforge"]
    
    print("🔍 Checking MongoDB Collections...\n")
    
    # List all collections
    collections = await db.list_collection_names()
    print(f"📊 Total Collections: {len(collections)}")
    for col in sorted(collections):
        count = await db[col].count_documents({})
        print(f"  • {col}: {count} documents")
    
    print("\n📁 Checking GridFS for Resumes...")
    
    # Check GridFS bucket
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="resumes")
    
    # List all files in GridFS
    cursor = bucket.find()
    files = await cursor.to_list(length=100)
    
    if files:
        print(f"\n✅ Found {len(files)} resume files in GridFS:")
        for file_doc in files:
            print(f"\n  File: {file_doc.filename}")
            print(f"  ID: {file_doc._id}")
            print(f"  Size: {file_doc.length} bytes")
            print(f"  Upload Date: {file_doc.upload_date}")
            if file_doc.metadata:
                print(f"  User ID: {file_doc.metadata.get('user_id')}")
                print(f"  Content Type: {file_doc.metadata.get('content_type')}")
    else:
        print("\n⚠️  No resume files found in GridFS")
        print("\nGridFS Collections that should exist:")
        print("  • resumes.files - Stores file metadata")
        print("  • resumes.chunks - Stores file data")
        
        # Check if GridFS collections exist
        if "resumes.files" in collections:
            print("\n  ✓ resumes.files exists but is empty")
        else:
            print("\n  ✗ resumes.files doesn't exist yet (will be created on first upload)")
        
        if "resumes.chunks" in collections:
            print("  ✓ resumes.chunks exists but is empty")
        else:
            print("  ✗ resumes.chunks doesn't exist yet (will be created on first upload)")
    
    # Check users with resumes
    users = db["users"]
    users_with_resumes = await users.count_documents({"has_resume": True})
    
    print(f"\n👥 Users with resumes: {users_with_resumes}")
    
    if users_with_resumes > 0:
        cursor = users.find({"has_resume": True})
        user_list = await cursor.to_list(length=10)
        for user in user_list:
            print(f"\n  User: {user.get('name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Resume File ID: {user.get('resume_file_id')}")
            print(f"  Resume Filename: {user.get('resume_filename')}")
    
    client.close()
    print("\n✅ MongoDB check complete!")

if __name__ == "__main__":
    asyncio.run(check_mongodb_gridfs())
