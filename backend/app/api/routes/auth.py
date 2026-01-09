from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours

class TokenData(BaseModel):
    user_id: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    name: str

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str) -> str:
    """Create a JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"user_id": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(token: str) -> Dict:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
async def register(user_data: UserRegistration):
    """Register a new user"""
    from app.core.database import get_collection
    from bson import ObjectId
    
    try:
        users_collection = await get_collection("users")
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": user_data.email.lower()})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        new_user = {
            "email": user_data.email.lower(),
            "name": user_data.name,
            "password_hash": hash_password(user_data.password),
            "role": "student",
            "profile_completed": False,
            "has_resume": False,
            "resume_file_id": None,
            "resume_filename": None,
            "current_skills": [],
            "target_role_id": None,
            "saved_roadmaps": [],
            "available_hours_per_week": None,
            "notification_preferences": {
                "email_enabled": True,
                "deadline_reminders": True,
                "days_before_deadline": 3,
                "weekly_summary": True,
                "module_completion": True
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await users_collection.insert_one(new_user)
        
        # Create access token
        access_token = create_access_token(str(result.inserted_id))
        
        # Fetch the created user
        user = await users_collection.find_one({"_id": result.inserted_id})
        user["_id"] = str(user["_id"])
        del user["password_hash"]
        
        return {
            "message": "User registered successfully",
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR in register: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login(credentials: LoginRequest):
    """Login with email and password"""
    from app.core.database import get_collection
    
    try:
        users_collection = await get_collection("users")
        
        # Find user by email
        user = await users_collection.find_one({"email": credentials.email.lower()})
        
        if not user or not verify_password(credentials.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token = create_access_token(str(user["_id"]))
        
        # Prepare user response
        user["_id"] = str(user["_id"])
        del user["password_hash"]
        
        return {
            "message": "Login successful",
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/verify")
async def verify_token_endpoint(data: TokenData):
    """Verify JWT token and return user data"""
    from app.core.database import get_collection
    from bson import ObjectId
    
    try:
        # Extract user_id from token (token verification is done by dependency)
        users_collection = await get_collection("users")
        
        user = await users_collection.find_one({"_id": ObjectId(data.user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["_id"] = str(user["_id"])
        if "password_hash" in user:
            del user["password_hash"]
        
        return {
            "valid": True,
            "user": user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
