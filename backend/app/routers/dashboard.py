"""
Dashboard API router
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Dict, Any, Optional
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime, timedelta
from app.database import get_db
from app.auth.clerk import get_current_user_id
from app.services.xp_calculator import calculate_level_from_xp

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def convert_objectid_to_str(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB ObjectId to string"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("")
async def get_dashboard_data(
    request: Request,
    db: Optional[Database] = Depends(get_db),
):
    """
    Get dashboard data for authenticated user
    
    Returns:
        Complete dashboard data including stats, projects, and metrics
    """
    try:
        user_id = await get_current_user_id(request)
    except HTTPException:
        # Fallback to query param for development
        user_id = request.query_params.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
    
    # Check if database is available
    if db is None:
        # Return empty/default dashboard data when MongoDB is not available
        return {
            "user": {
                "id": user_id,
                "name": "User",
                "email": "",
                "avatarUrl": None,
                "xp": 0,
                "level": 1,
                "role": "user",
                "githubConnected": False,
            },
            "stats": {
                "newProjects": 0,
                "joinedProjects": 0,
                "commits": 0,
                "pullRequests": 0,
                "issuesClosed": 0,
                "timeSavedMinutes": 0,
            },
            "timeBreakdown": {
                "contributingToOSS": 0,
                "workingOnOwnProjects": 0,
            },
            "projects": {
                "owned": [],
                "contributed": [],
                "starred": [],
            },
            "additionalMetrics": {
                "totalContributions": 0,
                "activeProjects": 0,
                "streak": 0,
            },
        }
    
    # Get user
    user_collection = db.users
    user = user_collection.find_one({"clerk_user_id": user_id})
    
    if not user:
        # Create a default user if doesn't exist
        default_user = {
            "clerk_user_id": user_id,
            "name": "User",
            "email": "",
            "avatar_url": None,
            "role": "user",
            "xp": 0,
            "level": 1,
            "github_connected": False,
            "last_visit_date": None,
            "current_streak": 0,
        }
        user_id_inserted = user_collection.insert_one(default_user).inserted_id
        user = user_collection.find_one({"_id": user_id_inserted})
    
    user = convert_objectid_to_str(user)
    
    # Calculate and update streak
    now_utc = datetime.utcnow()
    today = datetime(now_utc.year, now_utc.month, now_utc.day)
    last_visit_date = user.get("last_visit_date")
    current_streak = user.get("current_streak", 0)
    
    if last_visit_date:
        # Handle both datetime objects and strings
        if isinstance(last_visit_date, str):
            try:
                # Try parsing ISO format
                last_visit_date = datetime.fromisoformat(last_visit_date.replace('Z', '+00:00'))
            except:
                # If parsing fails, treat as first visit
                streak = 1
                last_visit_date = None
        
        if last_visit_date and isinstance(last_visit_date, datetime):
            last_visit = datetime(last_visit_date.year, last_visit_date.month, last_visit_date.day)
            days_diff = (today - last_visit).days
            
            if days_diff == 0:
                # Same day, don't change streak
                streak = current_streak
            elif days_diff == 1:
                # Yesterday, increment streak
                streak = current_streak + 1
            else:
                # More than 1 day ago, reset to 1
                streak = 1
        else:
            # First visit, start streak at 1
            streak = 1
    else:
        # First visit, start streak at 1
        streak = 1
    
    # Update user's last visit date and streak
    user_collection.update_one(
        {"clerk_user_id": user_id},
        {"$set": {"last_visit_date": now_utc, "current_streak": streak}}
    )
    
    # Get projects
    project_collection = db.projects
    membership_collection = db.project_memberships
    star_collection = db.project_stars
    
    # Get owned projects
    owned_projects = list(
        project_collection.find({"owner_id": user_id})
    )
    
    # Filter owned projects by current month
    current_month_start = datetime(now_utc.year, now_utc.month, 1)
    owned_projects_this_month = []
    for p in owned_projects:
        created_at = p.get("created_at")
        if created_at:
            # Handle both datetime objects and strings
            if isinstance(created_at, datetime):
                if created_at >= current_month_start:
                    owned_projects_this_month.append(p)
            elif isinstance(created_at, str):
                try:
                    parsed_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if parsed_date >= current_month_start:
                        owned_projects_this_month.append(p)
                except:
                    pass
    
    # Get contributed projects (via memberships)
    memberships = list(
        membership_collection.find({"user_id": user_id})
    )
    contributed_project_ids = [m["project_id"] for m in memberships]
    contributed_projects = []
    if contributed_project_ids:
        try:
            object_ids = [ObjectId(pid) if not isinstance(pid, ObjectId) else pid for pid in contributed_project_ids]
            contributed_projects = list(
                project_collection.find({"_id": {"$in": object_ids}})
            )
        except Exception as e:
            print(f"Error fetching contributed projects: {e}")
            contributed_projects = []
    
    # Get starred projects
    stars = list(star_collection.find({"user_id": user_id}))
    starred_project_ids = [s["project_id"] for s in stars]
    starred_projects = []
    if starred_project_ids:
        try:
            object_ids = [ObjectId(pid) if not isinstance(pid, ObjectId) else pid for pid in starred_project_ids]
            starred_projects = list(
                project_collection.find({"_id": {"$in": object_ids}})
            )
        except Exception as e:
            print(f"Error fetching starred projects: {e}")
            starred_projects = []
    
    # Convert all projects
    all_projects = owned_projects + contributed_projects
    starred_project_id_strings = [str(pid) for pid in starred_project_ids]
    for project in all_projects:
        project = convert_objectid_to_str(project)
        project_id = str(project["_id"])
        project["starred"] = project_id in starred_project_id_strings
    
    # Get contributions for stats - filter by joined projects only
    contribution_collection = db.contributions
    all_contributions = list(contribution_collection.find({"user_id": user_id}))
    
    # Get project IDs from joined projects (contributed projects)
    joined_project_ids = [str(p["_id"]) for p in contributed_projects]
    
    # Filter contributions to only those from joined projects
    contributions = [
        c for c in all_contributions 
        if c.get("project_id") in joined_project_ids
    ]
    
    # Calculate stats from filtered contributions
    commits = sum(1 for c in contributions if c.get("type") == "commit")
    pull_requests = sum(1 for c in contributions if c.get("type") == "pull_request")
    issues_closed = sum(1 for c in contributions if c.get("type") == "issue")
    
    # Calculate time saved from joined projects only (sum setup_time_estimate_minutes)
    time_saved_minutes = sum(
        p.get("setup_time_estimate_minutes", 7) 
        for p in contributed_projects
    )
    
    # Calculate XP and level
    total_xp = sum(c.get("xp_awarded", 0) for c in contributions)
    if total_xp != user.get("xp", 0):
        # Update user XP
        level = calculate_level_from_xp(total_xp)
        user_collection.update_one(
            {"clerk_user_id": user_id},
            {"$set": {"xp": total_xp, "level": level}}
        )
        user["xp"] = total_xp
        user["level"] = level
    else:
        level = user.get("level", 1)
    
    # Time breakdown - fake data (50/50 split)
    total_hours = 10.0  # Fake total hours
    contributing_hours = total_hours * 0.5  # 50% contributing to OSS
    own_projects_hours = total_hours * 0.5  # 50% working on own projects
    
    # Format projects for response
    def format_project(p):
        p = convert_objectid_to_str(p)
        project_id_str = str(p["_id"])
        return {
            "id": project_id_str,
            "name": p.get("name", ""),
            "description": p.get("description"),
            "techStack": p.get("tech_stack", []),
            "starred": project_id_str in starred_project_id_strings,
            "metadata": {
                "commits": p.get("metadata", {}).get("commits", 0),
                "contributors": p.get("metadata", {}).get("contributors", 0),
                "openIssues": p.get("metadata", {}).get("open_issues", 0),
                "timeSavedMinutes": p.get("metadata", {}).get("time_saved_minutes", 0),
            },
            "createdAt": p.get("created_at", "").isoformat() if p.get("created_at") else "",
            "updatedAt": p.get("updated_at", "").isoformat() if p.get("updated_at") else "",
        }
    
    # Additional metrics
    total_contributions = commits  # Use commits count as total contributions
    active_projects = len(contributed_projects)  # Fake: use count of joined projects
    
    response = {
        "user": {
            "id": user["clerk_user_id"],
            "name": user.get("name", "User"),
            "email": user.get("email", ""),
            "avatarUrl": user.get("avatar_url"),
            "xp": user.get("xp", 0),
            "level": level,
            "role": user.get("role", "user"),
            "githubConnected": user.get("github_connected", False),
        },
        "stats": {
            "newProjects": len(owned_projects_this_month),
            "joinedProjects": len(contributed_projects),
            "commits": commits,
            "pullRequests": pull_requests,
            "issuesClosed": issues_closed,
            "timeSavedMinutes": time_saved_minutes,
        },
        "timeBreakdown": {
            "contributingToOSS": contributing_hours,
            "workingOnOwnProjects": own_projects_hours,
        },
        "projects": {
            "owned": [format_project(p) for p in owned_projects],
            "contributed": [format_project(p) for p in contributed_projects],
            "starred": [format_project(p) for p in starred_projects],
        },
        "additionalMetrics": {
            "totalContributions": total_contributions,
            "activeProjects": active_projects,
            "streak": streak,
        },
    }
    
    return response

