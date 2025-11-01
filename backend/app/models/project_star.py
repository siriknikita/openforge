"""
Project star model for tracking starred projects
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ProjectStar(BaseModel):
    """Project star model"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    project_id: str = Field(..., description="Project ID")
    user_id: str = Field(..., description="Clerk user ID")
    starred_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

