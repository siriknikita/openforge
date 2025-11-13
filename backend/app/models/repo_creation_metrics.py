"""
Repository creation metrics model
"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class RepoCreationMetrics(BaseModel):
    """Repository creation metrics model"""
    user_id: str = Field(..., description="Clerk user ID")
    repository_name: str = Field(..., description="Repository name")
    github_repo_id: Optional[str] = Field(None, description="GitHub repository ID")
    status: Literal["success", "failure"] = Field(..., description="Creation status")
    error_type: Optional[Literal["github_api", "database", "validation", "auth"]] = Field(
        None, description="Error type if status is failure"
    )
    error_message: Optional[str] = Field(None, description="Error message if status is failure")
    retry_count: int = Field(0, description="Number of retry attempts")
    duration_ms: int = Field(0, description="Duration in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "repository_name": "my-project",
                "github_repo_id": "123456789",
                "status": "success",
                "error_type": None,
                "error_message": None,
                "retry_count": 0,
                "duration_ms": 1250,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

