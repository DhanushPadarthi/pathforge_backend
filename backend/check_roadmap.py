import asyncio
from database.connection import get_collection

async def check():
    coll = await get_collection('roadmaps')
    count = await coll.count_documents({})
    print(f'Total roadmaps in DB: {count}')
    
    roadmap = await coll.find_one({})
    if roadmap:
        print(f'Sample roadmap ID: {roadmap["_id"]}')
        print(f'User ID: {roadmap.get("user_id")}')
        print(f'Target Role: {roadmap.get("target_role")}')
        print(f'Modules: {len(roadmap.get("modules", []))}')
        print(f'Progress: {roadmap.get("progress_percentage", 0)}%')
        
        module = roadmap['modules'][0] if roadmap.get('modules') else None
        if module:
            print(f'\nFirst module:')
            print(f'  Title: {module.get("title")}')
            print(f'  Week number: {module.get("week_number", "MISSING")}')
            print(f'  Resources: {len(module.get("resources", []))}')
            
            if module.get('resources'):
                res = module['resources'][0]
                print(f'\nFirst resource:')
                print(f'  Title: {res.get("title")}')
                print(f'  URL: {res.get("url", "MISSING")}')
                print(f'  Status: {res.get("status")}')
                print(f'  Time spent: {res.get("time_spent_seconds", "MISSING")}')
                print(f'  Opened at: {res.get("opened_at", "MISSING")}')
                
                # Show first 3 resource URLs
                print(f'\nFirst 3 resource URLs:')
                for i, r in enumerate(module['resources'][:3], 1):
                    print(f'  {i}. {r.get("title")}: {r.get("url", "NO URL")}')

asyncio.run(check())
