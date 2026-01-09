"""
Unit tests for AI Service
"""
import pytest
from services.ai_service import AIService
from unittest.mock import Mock, patch

@pytest.fixture
def ai_service():
    return AIService()

@pytest.mark.asyncio
async def test_extract_skills_from_resume(ai_service):
    """Test resume skill extraction"""
    resume_text = """
    John Doe
    Software Engineer
    
    Skills: Python, JavaScript, React, Node.js
    Experience: 3 years
    """
    
    with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
        mock_create.return_value = Mock(
            choices=[Mock(message=Mock(content='{"skills": ["Python", "JavaScript", "React"], "experience_years": 3, "education": "Bachelor", "job_titles": ["Software Engineer"]}'))]
        )
        
        result = await ai_service.extract_skills_from_resume(resume_text)
        
        assert "skills" in result
        assert "Python" in result["skills"]
        assert result["experience_years"] == 3

@pytest.mark.asyncio
async def test_analyze_skill_gap(ai_service):
    """Test skill gap analysis"""
    current_skills = ["Python", "JavaScript"]
    target_role = "Full Stack Developer"
    required_skills = ["Python", "JavaScript", "React", "Node.js", "SQL"]
    
    with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
        mock_create.return_value = Mock(
            choices=[Mock(message=Mock(content='{"skill_gaps": [{"skill": "React", "priority": "high"}, {"skill": "Node.js", "priority": "high"}, {"skill": "SQL", "priority": "medium"}], "recommendations": ["Learn React first"]}'))]
        )
        
        result = await ai_service.analyze_skill_gap(current_skills, target_role, required_skills)
        
        assert "skill_gaps" in result
        assert len(result["skill_gaps"]) == 3
        assert result["skill_gaps"][0]["skill"] == "React"

@pytest.mark.asyncio
async def test_generate_module_summary(ai_service):
    """Test module summary generation"""
    module_data = {
        "title": "Introduction to Python",
        "skills_covered": ["Python", "Programming Basics"]
    }
    user_progress = {
        "time_spent_hours": 5,
        "resources_completed": 3,
        "resources_skipped": 1
    }
    
    with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
        mock_create.return_value = Mock(
            choices=[Mock(message=Mock(content="Great job! You've learned Python basics."))]
        )
        
        result = await ai_service.generate_module_summary(module_data, user_progress)
        
        assert isinstance(result, str)
        assert len(result) > 0
