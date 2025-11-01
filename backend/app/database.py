"""
Database connection manager for MongoDB
"""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
from app.config import settings


class DatabaseManager:
    """Manages MongoDB connection"""
    
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    _connected: bool = False
    
    @classmethod
    def get_client(cls) -> Optional[MongoClient]:
        """Get or create MongoDB client"""
        if cls._client is None:
            try:
                cls._client = MongoClient(
                    settings.mongodb_url,
                    serverSelectionTimeoutMS=10000,  # 10 second timeout for Atlas
                )
                # Test connection
                cls._client.admin.command('ping')
                cls._connected = True
                print(f"✓ Successfully connected to MongoDB Atlas (database: {settings.mongodb_db_name})")
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                print(f"Warning: Could not connect to MongoDB: {e}")
                print("The application will continue with limited functionality.")
                cls._connected = False
                # Keep client as None to indicate no connection
                cls._client = None
        return cls._client
    
    @classmethod
    def get_database(cls) -> Optional[Database]:
        """Get database instance"""
        client = cls.get_client()
        if client is None or not cls._connected:
            return None
        if cls._db is None:
            cls._db = client[settings.mongodb_db_name]
        return cls._db
    
    @classmethod
    def is_connected(cls) -> bool:
        """Check if database is connected"""
        if cls._client is None:
            return False
        try:
            cls._client.admin.command('ping')
            cls._connected = True
            return True
        except:
            cls._connected = False
            return False
    
    @classmethod
    def close(cls):
        """Close database connection"""
        if cls._client:
            try:
                cls._client.close()
            except:
                pass
            cls._client = None
            cls._db = None
            cls._connected = False


def get_db() -> Optional[Database]:
    """Dependency for FastAPI to get database"""
    return DatabaseManager.get_database()

