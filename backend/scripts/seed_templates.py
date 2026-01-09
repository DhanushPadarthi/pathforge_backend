"""
Enhanced seed script with roadmap templates
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

# Import templates
from data.roadmap_templates import ROADMAP_TEMPLATES

load_dotenv()

# Sample admin user
ADMIN_USER = {
    "uid": "admin_template_creator",
    "email": "admin@pathforge.com",
    "name": "PathForge Admin",
    "role": "admin",
    "profile_completed": True,
    "has_resume": False,
    "current_skills": [],
    "target_roles": [],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

async def seed_roadmap_templates():
    """Seed the database with pre-built roadmap templates"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        db = client[os.getenv("DATABASE_NAME", "pathforge")]
        
        print("🌱 Starting roadmap templates seeding...")
        
        # Ensure admin user exists
        users_collection = db["users"]
        admin = await users_collection.find_one({"uid": ADMIN_USER["uid"]})
        
        if not admin:
            await users_collection.insert_one(ADMIN_USER)
            print("✓ Created template admin user")
        
        # Seed roadmap templates
        roadmaps_collection = db["roadmaps"]
        
        for template in ROADMAP_TEMPLATES:
            # Check if template already exists
            existing = await roadmaps_collection.find_one({
                "title": template["title"],
                "is_template": True
            })
            
            if existing:
                print(f"⊘ Template '{template['title']}' already exists")
                continue
            
            # Prepare roadmap document
            roadmap_doc = {
                "user_id": ADMIN_USER["uid"],
                "title": template["title"],
                "description": template["description"],
                "category": template["category"],
                "difficulty": template["difficulty"],
                "estimated_weeks": template["estimated_weeks"],
                "is_template": True,  # Mark as template
                "is_public": True,    # Public templates
                "is_deleted": False,
                "progress_percentage": 0,
                "current_module_index": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "modules": []
            }
            
            # Process modules
            for module_data in template["modules"]:
                module = {
                    "id": f"mod_{len(roadmap_doc['modules']) + 1}",
                    "title": module_data["title"],
                    "description": module_data["description"],
                    "order": module_data["order"],
                    "completed": False,
                    "resources": []
                }
                
                # Process resources
                for res_data in module_data["resources"]:
                    resource = {
                        "id": f"res_{len(module['resources']) + 1}",
                        "title": res_data["title"],
                        "type": res_data["type"],
                        "url": res_data["url"],
                        "status": "not_started",
                        "rating": 0,
                        "time_spent_seconds": 0,
                        "estimated_minutes": res_data["estimated_minutes"],
                        "completed": False,
                        "notes": ""
                    }
                    module["resources"].append(resource)
                
                roadmap_doc["modules"].append(module)
            
            # Insert template
            result = await roadmaps_collection.insert_one(roadmap_doc)
            print(f"✓ Created template: '{template['title']}' ({len(roadmap_doc['modules'])} modules)")
        
        print(f"\n✅ Successfully seeded {len(ROADMAP_TEMPLATES)} roadmap templates!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error seeding roadmap templates: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_roadmap_templates())
