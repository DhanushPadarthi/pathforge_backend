import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def list_users():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['pathforge']
    users = await db['users'].find({}, {'email': 1, 'name': 1, 'role': 1}).to_list(length=20)
    
    if not users:
        print('No users found')
        return
    
    print('\nUsers in database:')
    for user in users:
        role = user.get('role', 'student')
        print(f"  - {user.get('email', 'N/A')} ({user.get('name', 'N/A')}) [Role: {role}]")
    
    client.close()

asyncio.run(list_users())
