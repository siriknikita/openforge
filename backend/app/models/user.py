"""
User model and related data structures
"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    """User model"""
    clerk_user_id: str = Field(..., description="Clerk authentication user ID")
    github_user_id: Optional[str] = Field(None, description="GitHub user ID if connected")
    name: str = Field(..., description="User's display name")
    email: str = Field(..., description="User's email address")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar")
    role: Literal["admin", "user"] = Field("user", description="User role")
    xp: int = Field(0, description="Total experience points")
    level: int = Field(1, description="Current level")
    github_connected: bool = Field(False, description="Whether GitHub OAuth is connected")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "clerk_user_id": "user_abc123",
                "github_user_id": "github_12345",
                "name": "John Doe",
                "email": "john@example.com",
                "avatar_url": "https://example.com/avatar.jpg",
                "role": "user",
                "xp": 1500,
                "level": 2,
                "github_connected": True,
            }
        }


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    clerk_user_id: str
    name: str
    email: str
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user"""
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    github_user_id: Optional[str] = None
    github_connected: Optional[bool] = None

