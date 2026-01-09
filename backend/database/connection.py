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
        
        # Ensure tlsInsecure is set for Render environment
        if "tlsInsecure" not in mongo_url:
            # Add tlsInsecure=true for SSL compatibility
            separator = "&" if "?" in mongo_url else "?"
            mongo_url = f"{mongo_url}{separator}tlsInsecure=true"
        
        db.client = AsyncIOMotorClient(
            mongo_url,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
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
