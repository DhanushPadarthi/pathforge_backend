"""
Utility functions for the backend
"""

from bson import ObjectId
from typing import Dict, Any

def serialize_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB ObjectId to string for JSON serialization"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def serialize_mongo_docs(docs: list) -> list:
    """Convert list of MongoDB documents"""
    return [serialize_mongo_doc(doc) for doc in docs]

def is_valid_object_id(id_string: str) -> bool:
    """Check if string is a valid MongoDB ObjectId"""
    try:
        ObjectId(id_string)
        return True
    except:
        return False
