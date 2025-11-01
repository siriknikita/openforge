"""
Project membership model for tracking user-project relationships
"""
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectMembership(BaseModel):
    """Project membership model"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    project_id: str = Field(..., description="Project ID")
    user_id: str = Field(..., description="Clerk user ID")
    role: Literal["owner", "contributor"] = Field("contributor", description="User role in project")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "project_id": "project_123",
                "user_id": "user_abc123",
                "role": "contributor",
            }
        }

