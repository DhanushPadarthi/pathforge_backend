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
        # Get connection URL
        mongo_url = os.getenv("MONGODB_URL")
        
        db.client = AsyncIOMotorClient(
            mongo_url,
            server_api=ServerApi('1'),
            ssl=True,  # Enable SSL/TLS
            retryWrites=True,
            w='majority',
            serverSelectionTimeoutMS=5000,  # Reduce timeout for faster feedback
            connectTimeoutMS=5000
        )
        
        # Don't verify connection on startup - do it lazily
        # This allows the app to start even if MongoDB is temporarily unavailable
        print("✓ MongoDB client initialized (connection verified on first request)")
        
    except Exception as e:
        print(f"✗ Error initializing MongoDB client: {e}")
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
