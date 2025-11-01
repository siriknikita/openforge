"""
Authorization utilities for checking permissions
"""
from typing import Optional
from fastapi import HTTPException, status
from pymongo.database import Database
from app.models.user import User


async def is_admin(db: Database, user_id: str) -> bool:
    """
    Check if user is an admin
    
    Args:
        db: MongoDB database instance
        user_id: Clerk user ID
        
    Returns:
        True if user is admin, False otherwise
    """
    user_collection = db.users
    user_doc = user_collection.find_one({"clerk_user_id": user_id})
    
    if not user_doc:
        return False
    
    return user_doc.get("role") == "admin"


async def is_project_member(db: Database, project_id: str, user_id: str) -> bool:
    """
    Check if user is a member of the project
    
    Args:
        db: MongoDB database instance
        project_id: Project ID
        user_id: Clerk user ID
        
    Returns:
        True if user is a project member, False otherwise
    """
    membership_collection = db.project_memberships
    membership = membership_collection.find_one({
        "project_id": project_id,
        "user_id": user_id,
    })
    
    if membership:
        return True
    
    # Also check if user is the project owner
    project_collection = db.projects
    project = project_collection.find_one({"_id": project_id})
    
    if project and project.get("owner_id") == user_id:
        return True
    
    return False


async def is_github_connected(db: Database, user_id: str) -> bool:
    """
    Check if user has GitHub OAuth connected
    
    Args:
        db: MongoDB database instance
        user_id: Clerk user ID
        
    Returns:
        True if GitHub is connected, False otherwise
    """
    user_collection = db.users
    user_doc = user_collection.find_one({"clerk_user_id": user_id})
    
    if not user_doc:
        return False
    
    return user_doc.get("github_connected", False)


async def check_project_access(
    db: Database,
    project_id: str,
    user_id: str,
    require_github: bool = True,
) -> bool:
    """
    Check if user can access a project
    User must be either:
    - An admin, OR
    - A project member with GitHub connected
    
    Args:
        db: MongoDB database instance
        project_id: Project ID
        user_id: Clerk user ID
        require_github: Whether GitHub connection is required
        
    Returns:
        True if access granted, False otherwise
    """
    # Check if admin
    if await is_admin(db, user_id):
        return True
    
    # Check if project member with GitHub connected
    if await is_project_member(db, project_id, user_id):
        if require_github:
            return await is_github_connected(db, user_id)
        return True
    
    return False


async def require_project_access(
    db: Database,
    project_id: str,
    user_id: str,
    require_github: bool = True,
):
    """
    Require project access or raise HTTPException
    
    Raises:
        HTTPException: If access is denied
    """
    has_access = await check_project_access(db, project_id, user_id, require_github)
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project. Must be admin or project member with GitHub connected.",
        )

