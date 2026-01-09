"""
Test configuration and fixtures
"""
import pytest
import asyncio
from typing import Generator

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "role": "student",
        "current_skills": [],
        "target_role_id": None
    }

@pytest.fixture
def test_roadmap_data():
    """Sample roadmap data for testing"""
    return {
        "user_id": "test_user_id",
        "target_role": "Full Stack Developer",
        "skill_gaps": ["React", "Node.js"],
        "modules": [],
        "total_estimated_hours": 100,
        "progress_percentage": 0
    }

@pytest.fixture
def test_module_data():
    """Sample module data for testing"""
    return {
        "title": "Introduction to React",
        "description": "Learn React basics",
        "skills_covered": ["React", "JavaScript"],
        "estimated_total_hours": 20,
        "week_number": 1,
        "order": 0,
        "is_completed": False,
        "resources": []
    }
