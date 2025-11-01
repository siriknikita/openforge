"""
Contribution model for tracking user contributions
"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Contribution(BaseModel):
    """Contribution model"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    user_id: str = Field(..., description="Clerk user ID who made the contribution")
    project_id: str = Field(..., description="Project ID")
    type: Literal["commit", "pull_request", "issue"] = Field(..., description="Type of contribution")
    title: str = Field(..., description="Contribution title")
    description: Optional[str] = Field(None, description="Contribution description")
    lines_added: int = Field(0, description="Lines of code added")
    lines_removed: int = Field(0, description="Lines of code removed")
    xp_awarded: int = Field(0, description="XP points awarded for this contribution")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "project_id": "project_123",
                "type": "commit",
                "title": "Fix bug in authentication",
                "lines_added": 50,
                "lines_removed": 10,
                "xp_awarded": 10,
            }
        }

