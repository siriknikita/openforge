"""
Projects API router
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Dict, Any, Optional
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime
import time
import logging
from app.database import get_db
from app.auth.clerk import get_current_user_id
from app.auth.authorization import require_project_access
from app.models.project import ProjectStar
from app.services.github_service import (
    get_github_token_from_clerk,
    create_github_repository,
    add_repository_topic,
    create_file_in_repository,
    generate_readme_template,
    generate_gitignore_template,
    retry_with_backoff,
)
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


def convert_objectid_to_str(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB ObjectId to string"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("")
async def get_projects(
    request: Request,
    db: Optional[Database] = Depends(get_db),
):
    """
    Get user's projects (owned, contributed, starred)
    Protected: Only accessible by admins or authenticated users who are project members with GitHub connected
    
    Query params:
        - user_id: User ID (for authentication)
        - filter: 'owned', 'contributed', 'starred', or 'all' (default: 'all')
    """
    try:
        user_id = await get_current_user_id(request)
    except HTTPException:
        user_id = request.query_params.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    # Check if database is available
    if db is None:
        return {"projects": []}
    
    filter_type = request.query_params.get("filter", "all")
    
    project_collection = db.projects
    membership_collection = db.project_memberships
    star_collection = db.project_stars
    
    # Get user's starred project IDs
    stars = list(star_collection.find({"user_id": user_id}))
    starred_project_ids = [str(s["project_id"]) for s in stars]
    
    projects = []
    
    if filter_type in ["owned", "all"]:
        owned = list(project_collection.find({"owner_id": user_id}))
        for p in owned:
            p = convert_objectid_to_str(p)
            p["starred"] = str(p["_id"]) in starred_project_ids
            p["filter"] = "owned"
            projects.append(p)
    
    if filter_type in ["contributed", "all"]:
        memberships = list(membership_collection.find({"user_id": user_id}))
        if memberships:
            try:
                contributed_ids = [
                    ObjectId(m["project_id"]) if not isinstance(m["project_id"], ObjectId) else m["project_id"]
                    for m in memberships
                ]
                contributed = list(
                    project_collection.find({"_id": {"$in": contributed_ids}})
                )
                for p in contributed:
                    p = convert_objectid_to_str(p)
                    p["starred"] = str(p["_id"]) in starred_project_ids
                    p["filter"] = "contributed"
                    projects.append(p)
            except Exception as e:
                print(f"Error fetching contributed projects: {e}")
    
    if filter_type == "starred":
        if starred_project_ids:
            try:
                starred_ids = [
                    ObjectId(pid) if not isinstance(pid, ObjectId) else pid
                    for pid in starred_project_ids
                ]
                starred = list(
                    project_collection.find({"_id": {"$in": starred_ids}})
                )
                for p in starred:
                    p = convert_objectid_to_str(p)
                    p["starred"] = True
                    p["filter"] = "starred"
                    projects.append(p)
            except Exception as e:
                print(f"Error fetching starred projects: {e}")
    
    # Format projects
    formatted_projects = []
    for p in projects:
        formatted_projects.append({
            "id": str(p["_id"]),
            "name": p.get("name", ""),
            "description": p.get("description"),
            "techStack": p.get("tech_stack", []),
            "starred": p.get("starred", False),
            "metadata": {
                "commits": p.get("metadata", {}).get("commits", 0),
                "contributors": p.get("metadata", {}).get("contributors", 0),
                "openIssues": p.get("metadata", {}).get("open_issues", 0),
                "timeSavedMinutes": p.get("metadata", {}).get("time_saved_minutes", 0),
            },
            "createdAt": p.get("created_at", "").isoformat() if p.get("created_at") else "",
            "updatedAt": p.get("updated_at", "").isoformat() if p.get("updated_at") else "",
        })
    
    return {"projects": formatted_projects}


@router.post("/{project_id}/star")
async def toggle_project_star(
    project_id: str,
    request: Request,
    db: Optional[Database] = Depends(get_db),
):
    """
    Toggle star status for a project
    Protected: Requires authentication only. Any authenticated user can star/unstar any project.
    
    Body:
        - user_id: User ID (for authentication)
    """
    try:
        user_id = await get_current_user_id(request)
    except HTTPException:
        # Try to get from request body
        try:
            body = await request.json()
            user_id = body.get("user_id")
        except:
            pass
        
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    # Check if database is available
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available. Please ensure MongoDB is running.",
        )
    
    # Verify project exists
    project_collection = db.projects
    try:
        project_obj_id = ObjectId(project_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID",
        )
    
    project = project_collection.find_one({"_id": project_obj_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Toggle star
    star_collection = db.project_stars
    existing_star = star_collection.find_one({
        "project_id": project_id,
        "user_id": user_id,
    })
    
    if existing_star:
        # Unstar
        star_collection.delete_one({"_id": existing_star["_id"]})
        starred = False
    else:
        # Star
        star_collection.insert_one({
            "project_id": project_id,
            "user_id": user_id,
        })
        starred = True
    
    return {"starred": starred}


@router.post("/{project_id}/join")
async def join_project(
    project_id: str,
    request: Request,
    db: Optional[Database] = Depends(get_db),
):
    """
    Join a project as a contributor
    Protected: Requires authentication
    
    This will:
    - Create a ProjectMembership document
    - Add user's name to project's joined_members array
    - Set project's setup_time_estimate_minutes to 7 if not already set
    """
    try:
        user_id = await get_current_user_id(request)
    except HTTPException:
        # Try to get from request body
        try:
            body = await request.json()
            user_id = body.get("user_id")
        except:
            pass
        
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    # Check if database is available
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available. Please ensure MongoDB is running.",
        )
    
    # Verify project exists
    project_collection = db.projects
    membership_collection = db.project_memberships
    user_collection = db.users
    
    try:
        project_obj_id = ObjectId(project_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID",
        )
    
    project = project_collection.find_one({"_id": project_obj_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Check if user is already a member
    existing_membership = membership_collection.find_one({
        "project_id": project_id,
        "user_id": user_id,
    })
    
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project",
        )
    
    # Check if user is the owner
    if project.get("owner_id") == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project owner cannot join their own project",
        )
    
    # Get user's name
    user = user_collection.find_one({"clerk_user_id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user_name = user.get("name", "Unknown User")
    
    # Create membership
    membership_collection.insert_one({
        "project_id": project_id,
        "user_id": user_id,
        "role": "contributor",
        "joined_at": datetime.utcnow(),
    })
    
    # Update project: add user to joined_members and set setup_time_estimate_minutes if not set
    update_data = {
        "$addToSet": {"joined_members": user_name},  # Use addToSet to avoid duplicates
    }
    
    # Set setup_time_estimate_minutes to 7 if not already set
    if "setup_time_estimate_minutes" not in project or project.get("setup_time_estimate_minutes") is None:
        update_data["$set"] = {"setup_time_estimate_minutes": 7}
        project_collection.update_one(
            {"_id": project_obj_id},
            update_data
        )
    else:
        # Only update joined_members if setup_time_estimate_minutes is already set
        project_collection.update_one(
            {"_id": project_obj_id},
            update_data
        )
    
    return {"message": "Successfully joined project", "project_id": project_id}


@router.get("/github-status")
async def get_github_status(
    request: Request,
    db: Optional[Database] = Depends(get_db),
):
    """
    Get user's GitHub connection status
    Protected: Requires authentication
    """
    try:
        user_id = await get_current_user_id(request)
    except HTTPException:
        user_id = request.query_params.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
    
    if db is None:
        return {
            "github_connected": False,
            "github_username": None,
            "has_repo_scope": False,
        }
    
    user_collection = db.users
    user = user_collection.find_one({"clerk_user_id": user_id})
    
    if not user:
        return {
            "github_connected": False,
            "github_username": None,
            "has_repo_scope": False,
        }
    
    github_connected = user.get("github_connected", False)
    github_username = None
    
    # Try to get GitHub username from token
    has_repo_scope = False
    if settings.clerk_secret_key:
        try:
            github_token = await get_github_token_from_clerk(user_id, settings.clerk_secret_key)
            if github_token:
                # Verify token has repo scope by making a test API call
                import httpx
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        "https://api.github.com/user",
                        headers={
                            "Authorization": f"token {github_token}",
                            "Accept": "application/vnd.github.v3+json",
                        }
                    )
                    if response.status_code == 200:
                        user_data = response.json()
                        github_username = user_data.get("login")
                        # Check scopes from response headers
                        scopes = response.headers.get("X-OAuth-Scopes", "")
                        has_repo_scope = "repo" in scopes
                        
                        # If we have a token but github_connected is False, update it
                        if not github_connected:
                            github_user_id = str(user_data.get("id"))
                            user_collection.update_one(
                                {"clerk_user_id": user_id},
                                {
                                    "$set": {
                                        "github_connected": True,
                                        "github_user_id": github_user_id,
                                        "updated_at": datetime.utcnow(),
                                    }
                                }
                            )
                            github_connected = True
        except Exception as e:
            logger.warning(f"Error checking GitHub token: {e}")
    
    return {
        "github_connected": github_connected,
        "github_username": github_username,
        "has_repo_scope": has_repo_scope,
    }


@router.post("/connect-github")
async def connect_github(
    request: Request,
    db: Optional[Database] = Depends(get_db),
):
    """
    Connect GitHub account by checking for OAuth token from Clerk
    Protected: Requires authentication
    """
    try:
        user_id = await get_current_user_id(request)
    except HTTPException:
        body = await request.json()
        user_id = body.get("user_id") if body else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
    
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available. Please ensure MongoDB is running.",
        )
    
    user_collection = db.users
    user = user_collection.find_one({"clerk_user_id": user_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Try to get GitHub token from Clerk (with fallback to GITHUB_TOKEN)
    github_token = None
    if settings.clerk_secret_key:
        github_token = await get_github_token_from_clerk(user_id, settings.clerk_secret_key)
    
    if not github_token:
        error_msg = (
            "No GitHub token available with 'repo' scope. "
            "Please either:\n"
            "1. Sign in with GitHub via Clerk and reconnect with repository access, or\n"
            "2. Configure GITHUB_TOKEN in backend/.env with 'repo' scope"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    
    # Verify token and get GitHub user info
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid GitHub token. Please check your token configuration.",
                )
            
            github_user_data = response.json()
            github_user_id = str(github_user_data.get("id"))
            github_username = github_user_data.get("login")
            
            # Check scopes (should already be verified by get_github_token_from_clerk, but double-check)
            scopes = response.headers.get("X-OAuth-Scopes", "")
            has_repo_scope = "repo" in scopes
            
            if not has_repo_scope:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="GitHub token does not have 'repo' scope. Please configure a token with repository access.",
                )
            
            # Update user record
            user_collection.update_one(
                {"clerk_user_id": user_id},
                {
                    "$set": {
                        "github_connected": True,
                        "github_user_id": github_user_id,
                        "updated_at": datetime.utcnow(),
                    }
                }
            )
            
            return {
                "message": "GitHub account connected successfully",
                "github_username": github_username,
                "has_repo_scope": True,
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting GitHub: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect GitHub account: {str(e)}",
        )


@router.post("/create-github-repo")
async def create_github_repo(
    request: Request,
    db: Optional[Database] = Depends(get_db),
):
    """
    Create a new GitHub repository with openforge-demo topic
    Protected: Requires authentication and GitHub connection
    """
    start_time = time.time()
    
    try:
        user_id = await get_current_user_id(request)
    except HTTPException:
        body = await request.json()
        user_id = body.get("user_id") if body else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
    
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available. Please ensure MongoDB is running.",
        )
    
    # Get request body
    try:
        body = await request.json()
    except:
        body = {}
    
    name = body.get("name")
    description = body.get("description")
    tech_stack = body.get("tech_stack", [])
    is_private = body.get("is_private", False)
    
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repository name is required",
        )
    
    # Check if user has GitHub connected
    user_collection = db.users
    user = user_collection.find_one({"clerk_user_id": user_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.get("github_connected", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub not connected. Please connect your GitHub account.",
        )
    
    # Get GitHub token from Clerk (with fallback to GITHUB_TOKEN)
    github_token = None
    if settings.clerk_secret_key:
        github_token = await get_github_token_from_clerk(user_id, settings.clerk_secret_key)
    
    if not github_token:
        error_msg = (
            "GitHub OAuth token not available or lacks 'repo' scope. "
            "Please either:\n"
            "1. Reconnect your GitHub account through Clerk with repository access, or\n"
            "2. Configure GITHUB_TOKEN in backend/.env with 'repo' scope"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    
    # Track metrics
    metrics_collection = db.repo_creation_metrics
    retry_count = 0
    error_type = None
    error_message = None
    github_repo_id = None
    
    try:
        # Create GitHub repository
        github_repo = await create_github_repository(
            github_token=github_token,
            name=name,
            description=description,
            is_private=is_private,
        )
        
        github_repo_id = str(github_repo.get("id"))
        owner = github_repo.get("owner", {}).get("login")
        repo_name = github_repo.get("name")
        full_name = github_repo.get("full_name")
        
        # Add openforge-demo topic
        try:
            await add_repository_topic(
                github_token=github_token,
                owner=owner,
                repo=repo_name,
                topics=["openforge-demo"],
            )
        except Exception as e:
            logger.warning(f"Failed to add topic to repository: {e}")
            # Continue even if topic addition fails
        
        # Create template files
        readme_content = generate_readme_template(name, description or "", tech_stack)
        gitignore_content = generate_gitignore_template(tech_stack)
        
        # Create README.md
        try:
            await create_file_in_repository(
                github_token=github_token,
                owner=owner,
                repo=repo_name,
                path="README.md",
                content=readme_content,
                message="Initial commit: Add README.md",
            )
        except Exception as e:
            logger.warning(f"Failed to create README.md: {e}")
        
        # Create .gitignore
        try:
            await create_file_in_repository(
                github_token=github_token,
                owner=owner,
                repo=repo_name,
                path=".gitignore",
                content=gitignore_content,
                message="Initial commit: Add .gitignore",
            )
        except Exception as e:
            logger.warning(f"Failed to create .gitignore: {e}")
        
        # Create project in database with retry
        project_collection = db.projects
        project_data = {
            "name": name,
            "description": description,
            "tech_stack": tech_stack,
            "owner_id": user_id,
            "github_repo_id": github_repo_id,
            "metadata": {
                "commits": 0,
                "contributors": 0,
                "open_issues": 0,
                "time_saved_minutes": 0,
            },
            "joined_members": [],
            "setup_time_estimate_minutes": 7,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        async def create_project_in_db():
            result = project_collection.insert_one(project_data)
            return result.inserted_id
        
        try:
            project_id = await retry_with_backoff(create_project_in_db)
        except Exception as e:
            # GitHub repo was created but DB failed - log for manual cleanup
            logger.error(
                f"GitHub repo {full_name} created but database insert failed: {e}. "
                f"Manual cleanup required. Repo ID: {github_repo_id}"
            )
            error_type = "database"
            error_message = str(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Repository created on GitHub but failed to sync with database. Please contact support.",
            )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log successful creation
        metrics_collection.insert_one({
            "user_id": user_id,
            "repository_name": name,
            "github_repo_id": github_repo_id,
            "status": "success",
            "error_type": None,
            "error_message": None,
            "retry_count": retry_count,
            "duration_ms": duration_ms,
            "created_at": datetime.utcnow(),
        })
        
        return {
            "message": "Repository created successfully",
            "project": {
                "id": str(project_id),
                "name": name,
                "description": description,
                "github_repo_id": github_repo_id,
                "github_url": github_repo.get("html_url"),
                "tech_stack": tech_stack,
                "created_at": project_data["created_at"].isoformat(),
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_type = "github_api" if "github" in str(e).lower() else "unknown"
        error_message = str(e)
        
        # Log failed creation
        metrics_collection.insert_one({
            "user_id": user_id,
            "repository_name": name,
            "github_repo_id": github_repo_id,
            "status": "failure",
            "error_type": error_type,
            "error_message": error_message,
            "retry_count": retry_count,
            "duration_ms": duration_ms,
            "created_at": datetime.utcnow(),
        })
        
        logger.error(f"Repository creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create repository: {error_message}",
        )

