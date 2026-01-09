import asyncio
from database.connection import get_collection
from bson import ObjectId

async def check_videos():
    roadmaps = await get_collection('roadmaps')
    rm = await roadmaps.find_one({'_id': ObjectId('6955122db02ce37e7c4e7479')})
    if rm:
        for i, mod in enumerate(rm.get('modules', [])):
            print(f'\n📚 Module {i}: {mod.get("title")}')
            for j, res in enumerate(mod.get('resources', [])):
                url = res.get('url', 'N/A')
                title = res.get('title', 'N/A')
                print(f'   {j}. {title}')
                print(f'      URL: {url}')

asyncio.run(check_videos())
