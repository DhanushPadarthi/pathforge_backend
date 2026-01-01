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
        # Get connection URL - should already have tlsInsecure parameter if needed
        mongo_url = os.getenv("MONGODB_URL")
        
        db.client = AsyncIOMotorClient(
            mongo_url,
            server_api=ServerApi('1'),
            ssl=True,  # Enable SSL/TLS
            retryWrites=True,
            w='majority'
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
