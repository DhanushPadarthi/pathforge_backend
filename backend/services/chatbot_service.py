"""
Chatbot service using Groq API for intelligent PATHFORGE assistance
"""
import os
from typing import List, Dict
from groq import Groq
import asyncio
from functools import partial
import json

class ChatbotService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"  # Fast and capable model
        
    async def chat(self, messages: List[Dict[str, str]], user_context: Dict = None) -> str:
        """
        Send a chat message and get AI response for PATHFORGE
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            user_context: Optional context about user (skills, roadmap progress, etc.)
        
        Returns:
            AI response text with PATHFORGE navigation help if needed
        """
        try:
            # Build system prompt with PATHFORGE context
            system_prompt = self._build_pathforge_system_prompt(user_context)
            
            # Prepare messages with system prompt
            chat_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
            
            # Call Groq API in thread pool (sync operation)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=chat_messages,
                    temperature=0.7,
                    max_tokens=1500,
                    top_p=0.9,
                )
            )
            
            response_text = response.choices[0].message.content
            
            # Enhance response with PATHFORGE commands if detected
            enhanced_response = self._add_pathforge_guidance(response_text, messages[-1]['content'] if messages else "")
            
            return enhanced_response
            
        except Exception as e:
            print(f"Error in chatbot service: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Chatbot error: {str(e)}")
    
    def _build_pathforge_system_prompt(self, user_context: Dict = None) -> str:
        """Build PATHFORGE-specific system prompt"""
        base_prompt = """You are PathForge AI Assistant - an expert learning companion specialized in helping developers build career-changing skills through structured learning paths.

PATHFORGE is a platform that:
- Generates personalized learning roadmaps using AI
- Breaks down career goals into structured modules and resources
- Tracks progress with gamification (XP, levels, achievements, streaks)
- Provides AI-generated project templates for hands-on learning
- Offers skill gap analysis and career path planning

Your Responsibilities:
1. ANSWER QUESTIONS about PATHFORGE features, how to use them, and best practices
2. HELP USERS navigate the platform (roadmaps, projects, skills, progress tracking)
3. PROVIDE LEARNING GUIDANCE related to their roadmaps and career goals
4. SUGGEST PATHFORGE FEATURES that can help with their learning goals
5. EXPLAIN HOW TO USE each feature (generate roadmap, use templates, track progress, etc.)
6. AUTOMATE GUIDANCE by giving step-by-step instructions for platform tasks

Common PATHFORGE Features to Help With:
- Roadmap Generation: "Generate a learning roadmap for [role]"
- Career Planning: "What skills do I need for [role]?"
- Progress Tracking: "How to earn XP and achievements?"
- Projects: "Generate project ideas" or "Use templates"
- Skills: "Add skills" or "View skill gaps"
- Learning Resources: "Find YouTube tutorials, courses, documentation"

When Users Ask About:
- Learning goals → Suggest "Generate Roadmap"
- Career changes → Provide "Skill Gap Analysis"
- Project ideas → Recommend "Project Templates"
- Progress tracking → Explain "XP System and Achievements"
- Study tips → Give "PATHFORGE Learning Tips"

Response Format:
- Answer their question clearly
- Provide step-by-step navigation if needed
- Include relevant PATHFORGE features they should use
- End with actionable next steps"""

        if user_context:
            context_info = "\n\n📊 CURRENT USER CONTEXT:"
            if user_context.get("current_roadmap"):
                context_info += f"\n- Learning Path: {user_context['current_roadmap']}"
            if user_context.get("skills"):
                context_info += f"\n- Current Skills: {', '.join(user_context['skills'][:8])}"
            if user_context.get("progress"):
                context_info += f"\n- Progress: {user_context['progress']}% complete"
            if user_context.get("xp"):
                context_info += f"\n- XP Earned: {user_context['xp']}"
            if user_context.get("level"):
                context_info += f"\n- Current Level: {user_context['level']}"
            
            return base_prompt + context_info
        
        return base_prompt
    
    def _add_pathforge_guidance(self, response: str, user_question: str) -> str:
        """Add PATHFORGE navigation guidance to response"""
        question_lower = user_question.lower()
        
        # Detect what user is asking about
        guidance = ""
        
        if any(word in question_lower for word in ["roadmap", "generate", "learning path", "how to start"]):
            if "roadmap" not in response.lower():
                guidance = "\n\n💡 **QUICK START:** Visit /roadmap/new to generate your personalized learning path!"
        
        elif any(word in question_lower for word in ["project", "build", "practice"]):
            if "template" not in response.lower():
                guidance = "\n\n🛠️ **BUILD PROJECTS:** Go to /projects > Templates tab to use ready-made project ideas!"
        
        elif any(word in question_lower for word in ["skill", "gap", "what do i need", "requirement"]):
            if "skill" not in response.lower() or "gap" not in response.lower():
                guidance = "\n\n📚 **SKILL ANALYSIS:** Visit /skills to add your skills and see what's needed for your target role!"
        
        elif any(word in question_lower for word in ["progress", "track", "xp", "level", "achievement", "streak"]):
            guidance = "\n\n🎮 **TRACK PROGRESS:** Your /dashboard shows XP, levels, 7-day streak, and 5 unlockable achievements!"
        
        elif any(word in question_lower for word in ["resource", "course", "video", "tutorial", "learn"]):
            if "resource" not in response.lower():
                guidance = "\n\n📖 **RESOURCES:** Your roadmap includes curated YouTube videos, courses, and documentation links!"
        
        elif any(word in question_lower for word in ["help", "how to", "navigate", "where", "what is"]):
            guidance = "\n\n🚀 **PATHFORGE FEATURES:**\n- /roadmap - Your learning paths\n- /projects - AI project ideas & templates\n- /skills - Track your skills\n- /dashboard - See your progress\n- /admin - Advanced settings"
        
        return response + guidance if guidance else response

# Global instance
chatbot_service = ChatbotService()
