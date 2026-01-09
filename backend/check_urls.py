import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('DATABASE_NAME', 'pathforge')]
roadmaps = db.roadmaps

roadmap = roadmaps.find_one({})
if roadmap and roadmap.get('modules'):
    print(f"Roadmap: {roadmap.get('target_role')}\n")
    for module in roadmap['modules'][:2]:  # First 2 modules
        print(f"Module: {module.get('title')}")
        for res in module.get('resources', [])[:3]:  # First 3 resources
            print(f"  - {res.get('title')}")
            print(f"    URL: {res.get('url', 'NO URL')}")
        print()
else:
    print("No roadmap found")

client.close()
