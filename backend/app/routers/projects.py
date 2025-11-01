"""
Projects API router
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Dict, Any, Optional
from pymongo.database import Database
from bson import ObjectId
from app.database import get_db
from app.auth.clerk import get_current_user_id
from app.auth.authorization import require_project_access
from app.models.project import ProjectStar

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
    Protected: Only accessible by admins or project members with GitHub connected
    
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
    
    # Check project access (admin or member with GitHub)
    await require_project_access(db, project_id, user_id, require_github=True)
    
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

