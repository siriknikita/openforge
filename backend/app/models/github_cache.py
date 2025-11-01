"""
GitHub API cache model for MongoDB
"""
from typing import Any, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class GitHubCache(BaseModel):
    """GitHub API cache model"""
    cache_key: str = Field(..., description="Unique cache key (e.g., 'repo_list_', 'repo_detail_owner_repo')")
    data: Dict[str, Any] = Field(..., description="Cached API response data")
    expires_at: datetime = Field(..., description="When this cache entry expires")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When this cache entry was created")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "cache_key": "repo_list_openforge",
                "data": {"items": [], "total_count": 0},
                "expires_at": "2024-01-01T12:00:00Z",
                "created_at": "2024-01-01T11:00:00Z",
            }
        }


def create_cache_entry(key: str, data: Dict[str, Any], ttl_hours: int = 1) -> Dict[str, Any]:
    """
    Create a cache entry dictionary for MongoDB
    
    Args:
        key: Cache key
        data: Data to cache
        ttl_hours: Time to live in hours (default: 1 hour)
    
    Returns:
        Dictionary ready to be inserted into MongoDB
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=ttl_hours)
    return {
        "cache_key": key,
        "data": data,
        "expires_at": expires_at,
        "created_at": now,
    }

