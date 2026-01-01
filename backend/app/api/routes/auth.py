from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, auth
import os

router = APIRouter()

# Initialize Firebase Admin (do this once)
try:
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization: {e}")

class TokenVerification(BaseModel):
    token: str

class UserRegistration(BaseModel):
    firebase_uid: str
    email: str
    name: str

async def verify_firebase_token(token: str) -> Dict:
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@router.post("/verify")
async def verify_token(data: TokenVerification):
    """Verify Firebase authentication token and return user data"""
    from app.core.database import get_collection
    
    try:
        decoded = await verify_firebase_token(data.token)
        users_collection = await get_collection("users")
        
        # Find user by Firebase UID
        user = await users_collection.find_one({"firebase_uid": decoded['uid']})
        
        if not user:
            # Auto-register user if they don't exist (e.g., Google sign-in)
            from app.models.user import User, UserRole
            from datetime import datetime
            
            new_user = User(
                firebase_uid=decoded['uid'],
                email=decoded.get('email', ''),
                name=decoded.get('name', decoded.get('email', 'User')),
                role=UserRole.STUDENT,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            result = await users_collection.insert_one(new_user.dict(by_alias=True, exclude={"id"}))
            user = await users_collection.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string
        user["_id"] = str(user["_id"])
        
        return {
            "valid": True,
            "user": user
        }
    except HTTPException as e:
        raise e

@router.post("/register")
async def register_user(user_data: UserRegistration):
    """Register a new user after Firebase authentication"""
    from app.core.database import get_collection
    
    try:
        users_collection = await get_collection("users")
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"firebase_uid": user_data.firebase_uid})
        if existing_user:
            return {"message": "User already exists", "user_id": str(existing_user["_id"])}
        
        # Create new user
        from app.models.user import User, UserRole
        from datetime import datetime
        
        new_user = User(
            firebase_uid=user_data.firebase_uid,
            email=user_data.email,
            name=user_data.name,
            role=UserRole.STUDENT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await users_collection.insert_one(new_user.dict(by_alias=True, exclude={"id"}))
        
        return {
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.get("/me")
async def get_current_user(token: str):
    """Get current user information"""
    decoded = await verify_firebase_token(token)
    
    from app.core.database import get_collection
    users_collection = await get_collection("users")
    
    user = await users_collection.find_one({"firebase_uid": decoded['uid']})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    return user
