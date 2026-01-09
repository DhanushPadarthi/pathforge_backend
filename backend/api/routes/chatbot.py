"""
Chatbot API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Optional
from api.routes.auth import verify_token
from services.chatbot_service import chatbot_service
from database.connection import db
from bson import ObjectId

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    include_context: bool = True

class ChatResponse(BaseModel):
    response: str
    
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authorization: str = Header(None)
):
    """
    Send a message to the AI chatbot and get a response
    """
    try:
        # Get current user from token
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = authorization.replace("Bearer ", "")
        
        # Verify JWT token
        try:
            token_data = await verify_token(token)
            user_id = token_data.get("user_id")
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing user_id")
        
        # Convert messages to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get user context if requested
        user_context = None
        if request.include_context and user_id:
            user_context = await _get_user_context(str(user_id))
        
        # Get AI response
        response = await chatbot_service.chat(messages, user_context)
        
        return ChatResponse(response=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _get_user_context(user_id: str) -> Dict:
    """Get user context for personalized responses"""
    try:
        # Get user data using MongoDB ObjectId
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {}
        
        # Get current roadmap if any
        roadmap = await db.roadmaps.find_one(
            {"user_id": user_id, "is_deleted": False},
            sort=[("created_at", -1)]
        )
        
        context = {
            "skills": user.get("current_skills", []),
            "progress": roadmap.get("progress_percentage", 0) if roadmap else 0
        }
        
        if roadmap:
            context["current_roadmap"] = roadmap.get("title", "")
        
        return context
        
    except Exception:
        return {}
