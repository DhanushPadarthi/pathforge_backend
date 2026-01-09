from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def get_database():
    return db.client[os.getenv("DATABASE_NAME", "pathforge")]

async def connect_to_mongo():
    """Connect to MongoDB"""
    try:
        db.client = AsyncIOMotorClient(
            os.getenv("MONGODB_URL"),
            server_api=ServerApi('1')
        )
        # Verify connection
        await db.client.admin.command('ping')
        print("✓ Connected to MongoDB successfully!")
    except Exception as e:
        print(f"✗ Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("✓ MongoDB connection closed")

async def get_collection(collection_name: str):
    """Get a collection from the database"""
    database = await get_database()
    return database[collection_name]
