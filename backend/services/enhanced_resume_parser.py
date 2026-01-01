"""
Enhanced Resume Parser - Combining current approach with LangChain RAG
Provides multiple extraction strategies with fallback mechanisms
"""

from typing import Dict, List
import os
from datetime import datetime

# Import existing services
from services.resume_parser import ResumeParser
from services.ai_service import AIService

# Import new LangChain service
try:
    from services.langchain_resume_parser import LangChainResumeParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not available. Install: pip install langchain langchain-groq faiss-cpu")


class EnhancedResumeParser:
    """
    Unified resume parser with multiple strategies:
    1. LangChain RAG (best accuracy) - NEW
    2. Direct LLM (current approach) - EXISTING
    3. Keyword matching (fastest) - FALLBACK
    """
    
    def __init__(self):
        self.basic_parser = ResumeParser()
        self.ai_service = AIService()
        
        # Initialize LangChain parser if available
        self.langchain_parser = None
        if LANGCHAIN_AVAILABLE:
            self.langchain_parser = LangChainResumeParser()
            print("✅ LangChain RAG enabled")
        else:
            print("⚠️ Using basic LLM extraction (install LangChain for better accuracy)")
    
    async def extract_skills(
        self, 
        resume_text: str,
        skill_database: List[Dict],
        method: str = "auto"  # auto, langchain, llm, keyword
    ) -> Dict:
        """
        Extract skills using specified method with intelligent fallback
        
        Args:
            resume_text: Extracted and cleaned resume text
            skill_database: List of skills from MongoDB
            method: Extraction strategy
                - "auto": Try langchain -> llm -> keyword
                - "langchain": Use LangChain RAG only
                - "llm": Use direct LLM only
                - "keyword": Use keyword matching only
        
        Returns:
            {
                "matched_skills": [...],
                "additional_skills": [...],
                "experience_years": int,
                "education": str,
                "method_used": str,
                "confidence": float,
                "processing_time": float
            }
        """
        
        start_time = datetime.now()
        result = None
        method_used = None
        
        # Strategy 1: Try LangChain RAG (best accuracy)
        if method in ["auto", "langchain"] and self.langchain_parser:
            try:
                print("🔗 [ENHANCED] Attempting LangChain RAG extraction...")
                result = await self.langchain_parser.extract_skills_with_langchain(
                    resume_text, 
                    skill_database
                )
                method_used = "langchain_rag"
                print(f"✅ [ENHANCED] LangChain succeeded: {len(result.get('matched_skills', []))} skills")
                
            except Exception as e:
                print(f"⚠️ [ENHANCED] LangChain failed: {e}")
                if method == "langchain":
                    raise  # Don't fallback if explicitly requested
                result = None
        
        # Strategy 2: Fallback to direct LLM (current approach)
        if result is None and method in ["auto", "llm"]:
            try:
                print("🤖 [ENHANCED] Attempting direct LLM extraction...")
                llm_result = await self.ai_service.extract_skills_from_resume(resume_text)
                
                # Convert to standard format
                result = self._convert_llm_to_standard_format(
                    llm_result, 
                    skill_database
                )
                method_used = "direct_llm"
                print(f"✅ [ENHANCED] LLM succeeded: {len(result.get('matched_skills', []))} skills")
                
            except Exception as e:
                print(f"⚠️ [ENHANCED] LLM failed: {e}")
                if method == "llm":
                    raise
                result = None
        
        # Strategy 3: Final fallback to keyword matching
        if result is None:
            print("📝 [ENHANCED] Using keyword matching fallback...")
            result = self._keyword_extraction(resume_text, skill_database)
            method_used = "keyword_fallback"
        
        # Add metadata
        processing_time = (datetime.now() - start_time).total_seconds()
        result['method_used'] = method_used
        result['processing_time'] = processing_time
        result['timestamp'] = datetime.now().isoformat()
        
        # Calculate confidence score
        result['confidence'] = self._calculate_confidence(result, method_used)
        
        print(f"✅ [ENHANCED] Complete! Method: {method_used}, Time: {processing_time:.2f}s")
        
        return result
    
    def _convert_llm_to_standard_format(
        self, 
        llm_result: Dict, 
        skill_database: List[Dict]
    ) -> Dict:
        """Convert current LLM format to standard format with proficiency"""
        
        matched_skills = []
        resume_skills = llm_result.get("skills", [])
        
        # Match extracted skills with database
        for skill_name in resume_skills:
            # Find in database
            db_skill = next(
                (s for s in skill_database 
                 if s['name'].lower() == skill_name.lower()),
                None
            )
            
            if db_skill:
                matched_skills.append({
                    "name": db_skill['name'],
                    "skill_id": str(db_skill.get('_id', '')),
                    "proficiency": "Intermediate",  # Default
                    "confidence": 0.8,
                    "evidence": "LLM extraction"
                })
        
        return {
            "matched_skills": matched_skills,
            "additional_skills": [],
            "experience_years": llm_result.get("experience_years", 0),
            "education": llm_result.get("education", ""),
            "job_titles": llm_result.get("job_titles", [])
        }
    
    def _keyword_extraction(
        self, 
        resume_text: str, 
        skill_database: List[Dict]
    ) -> Dict:
        """Simple keyword matching as last resort"""
        
        resume_lower = resume_text.lower()
        matched_skills = []
        
        for skill in skill_database[:100]:  # Limit for performance
            skill_name = skill['name']
            if skill_name.lower() in resume_lower:
                matched_skills.append({
                    "name": skill_name,
                    "skill_id": str(skill.get('_id', '')),
                    "proficiency": "Beginner",
                    "confidence": 0.5,
                    "evidence": "keyword match"
                })
        
        return {
            "matched_skills": matched_skills,
            "additional_skills": [],
            "experience_years": 0,
            "education": "",
            "job_titles": []
        }
    
    def _calculate_confidence(self, result: Dict, method: str) -> float:
        """Calculate overall confidence score based on method and results"""
        
        base_confidence = {
            "langchain_rag": 0.9,
            "direct_llm": 0.75,
            "keyword_fallback": 0.5
        }.get(method, 0.3)
        
        # Boost confidence if multiple skills found
        skill_count = len(result.get('matched_skills', []))
        if skill_count > 5:
            base_confidence = min(1.0, base_confidence + 0.05)
        
        # Individual skill confidences
        if 'matched_skills' in result and result['matched_skills']:
            avg_skill_confidence = sum(
                s.get('confidence', 0.5) for s in result['matched_skills']
            ) / len(result['matched_skills'])
            
            # Weighted average
            return (base_confidence * 0.6) + (avg_skill_confidence * 0.4)
        
        return base_confidence
    
    async def build_skill_knowledge_base(self, skill_database: List[Dict]):
        """Pre-build LangChain vector store for faster future extractions"""
        if self.langchain_parser:
            await self.langchain_parser.build_skill_knowledge_base(skill_database)
            self.langchain_parser.save_vector_store()
            print("✅ [ENHANCED] Skill knowledge base built and saved")
        else:
            print("⚠️ [ENHANCED] LangChain not available, cannot build knowledge base")
    
    async def load_skill_knowledge_base(self):
        """Load pre-built vector store"""
        if self.langchain_parser:
            success = self.langchain_parser.load_vector_store()
            if success:
                print("✅ [ENHANCED] Skill knowledge base loaded from disk")
            return success
        return False


# Global instance
enhanced_parser = EnhancedResumeParser()
