"""
Project model and related data structures
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectMetadata(BaseModel):
    """Project metadata"""
    commits: int = Field(0, description="Total number of commits")
    contributors: int = Field(0, description="Number of contributors")
    open_issues: int = Field(0, description="Number of open issues")
    time_saved_minutes: int = Field(0, description="Time saved in minutes during setup")


class Project(BaseModel):
    """Project model"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    owner_id: str = Field(..., description="Clerk user ID of the owner")
    github_repo_id: Optional[str] = Field(None, description="GitHub repository ID")
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)
    joined_members: List[str] = Field(default_factory=list, description="List of usernames who joined this project")
    setup_time_estimate_minutes: int = Field(7, description="Estimated setup time in minutes (default 7)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "My Awesome Project",
                "description": "A cool open-source project",
                "tech_stack": ["Python", "FastAPI", "React"],
                "owner_id": "user_abc123",
                "metadata": {
                    "commits": 150,
                    "contributors": 5,
                    "open_issues": 3,
                    "time_saved_minutes": 120,
                },
            }
        }


class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    name: str
    description: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    github_repo_id: Optional[str] = None


class ProjectStar(BaseModel):
    """Schema for starring/unstarring a project"""
    starred: bool = Field(..., description="Whether the project is starred")
    user_id: str = Field(..., description="User ID who starred/unstarred")

