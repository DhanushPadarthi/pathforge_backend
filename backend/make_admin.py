#!/usr/bin/env python3
"""
Script to make a user an admin
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def make_admin(email):
    """Make a user an admin by email"""
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['pathforge']
    users_collection = db['users']
    
    # Find user by email
    user = await users_collection.find_one({"email": email})
    
    if not user:
        print(f"❌ User with email '{email}' not found")
        return
    
    # Update user role to admin
    result = await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"role": "admin"}}
    )
    
    if result.modified_count > 0:
        print(f"✅ User '{email}' is now an admin!")
        print(f"   User ID: {user['_id']}")
        print(f"   Name: {user.get('name', 'N/A')}")
    else:
        print(f"❌ Failed to update user role")
    
    client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email>")
        print("\nExample: python make_admin.py user@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    asyncio.run(make_admin(email))
