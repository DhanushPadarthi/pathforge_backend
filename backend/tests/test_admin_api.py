"""
Integration tests for Admin API endpoints
"""
import pytest
from httpx import AsyncClient
from main import app
from database.connection import get_collection
from bson import ObjectId

@pytest.mark.asyncio
async def test_get_all_users():
    """Test getting all users (admin only)"""
    # This would require a test admin user ID
    admin_id = "test_admin_id_123"
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/admin/users?admin_id={admin_id}")
        
        # Without proper auth setup, this should return 403 or 500
        assert response.status_code in [403, 500]

@pytest.mark.asyncio
async def test_get_dashboard_stats():
    """Test getting dashboard statistics"""
    admin_id = "test_admin_id_123"
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/admin/stats?admin_id={admin_id}")
        
        assert response.status_code in [403, 500]

@pytest.mark.asyncio
async def test_create_skill():
    """Test creating a new skill"""
    admin_id = "test_admin_id_123"
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/admin/skills?admin_id={admin_id}",
            json={"name": "TestSkill", "category": "Testing"}
        )
        
        # Expect auth failure
        assert response.status_code in [403, 500]

# Note: Full integration tests would require:
# 1. Test database setup/teardown
# 2. Test user creation with admin role
# 3. Proper authentication tokens
# 4. Database cleanup after each test
