import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client['pathforge']
    roadmaps = db['roadmaps']
    
    # Count templates
    count = await roadmaps.count_documents({'is_template': True})
    print(f'✓ Total templates in DB: {count}')
    
    # List all templates
    templates = await roadmaps.find({'is_template': True}).to_list(100)
    print(f'\nTemplates:')
    for t in templates:
        print(f'  - {t.get("title")} ({t.get("category")}) - {len(t.get("modules", []))} modules')
    
    # Test query by category
    cloud = await roadmaps.find({'is_template': True, 'category': 'cloud'}).to_list(100)
    print(f'\n✓ Cloud templates: {len(cloud)}')
    
    client.close()

asyncio.run(test())
