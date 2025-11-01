"""
Marketplace API router for GitHub repository discovery
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any, List
from datetime import datetime
from pymongo.database import Database
from app.database import get_db
from app.config import settings
from app.models.github_cache import create_cache_entry
import httpx
import base64

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

GITHUB_API_BASE = "https://api.github.com"
CACHE_TTL_HOURS = 1


async def get_cached_data(db: Optional[Database], cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached data if it exists and hasn't expired"""
    if db is None:
        return None
    
    cache_collection = db.github_cache
    cached_entry = cache_collection.find_one({"cache_key": cache_key})
    
    if cached_entry:
        expires_at = cached_entry.get("expires_at")
        if expires_at and datetime.utcnow() < expires_at:
            return cached_entry.get("data")
        else:
            # Remove expired entry
            cache_collection.delete_one({"cache_key": cache_key})
    
    return None


async def set_cached_data(db: Optional[Database], cache_key: str, data: Dict[str, Any]):
    """Store data in cache"""
    if db is None:
        return
    
    cache_collection = db.github_cache
    cache_entry = create_cache_entry(cache_key, data, CACHE_TTL_HOURS)
    
    # Use upsert to update or create
    cache_collection.update_one(
        {"cache_key": cache_key},
        {"$set": cache_entry},
        upsert=True
    )


async def fetch_from_github(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Fetch data from GitHub API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


@router.get("/repos")
async def get_repositories(
    search: Optional[str] = Query(None, description="Search filter for repository name"),
    db: Optional[Database] = Depends(get_db),
):
    """
    Fetch GitHub repositories with 'openforge' topic
    
    Query params:
        - search: Optional filter to search repositories by name
    
    Returns:
        List of repositories with basic information
    """
    # Build cache key
    search_query = search.strip() if search and search.strip() else ""
    cache_key = f"repo_list_{search_query}"
    
    # Check cache
    cached_data = await get_cached_data(db, cache_key)
    if cached_data is not None:
        return cached_data
    
    # Build GitHub API query
    query = "topic:openforge"
    if search_query:
        query = f"{query} {search_query} in:name"
    
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {"q": query}
    
    # Prepare headers
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenForge/1.0",
    }
    
    # Add auth token if available
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"
    
    try:
        # Fetch from GitHub
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            github_data = response.json()
        
        # Transform GitHub response to our format
        repos = []
        for item in github_data.get("items", []):
            repos.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "description": item.get("description"),
                "html_url": item.get("html_url"),
                "topics": item.get("topics", []),
                "stargazers_count": item.get("stargazers_count", 0),
                "forks_count": item.get("forks_count", 0),
                "language": item.get("language"),
                "owner": {
                    "login": item.get("owner", {}).get("login"),
                    "avatar_url": item.get("owner", {}).get("avatar_url"),
                },
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
            })
        
        result = {
            "total_count": github_data.get("total_count", 0),
            "repositories": repos,
        }
        
        # Cache the result
        await set_cached_data(db, cache_key, result)
        
        return result
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            raise HTTPException(
                status_code=503,
                detail="GitHub API rate limit exceeded. Please try again later."
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"GitHub API error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to GitHub API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/repos/{owner}/{repo}")
async def get_repository_details(
    owner: str,
    repo: str,
    db: Optional[Database] = Depends(get_db),
):
    """
    Fetch detailed information about a specific repository including README
    
    Returns:
        Repository details with README content
    """
    # Build cache key
    cache_key = f"repo_detail_{owner}_{repo}"
    
    # Check cache
    cached_data = await get_cached_data(db, cache_key)
    if cached_data is not None:
        return cached_data
    
    # Prepare headers
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenForge/1.0",
    }
    
    # Add auth token if available
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch repository details
            repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
            repo_response = await client.get(repo_url, headers=headers)
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            # Fetch README
            readme_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
            readme_content = None
            readme_html_url = None
            
            try:
                readme_response = await client.get(readme_url, headers=headers)
                if readme_response.status_code == 200:
                    readme_data = readme_response.json()
                    # Decode base64 content
                    if readme_data.get("content"):
                        readme_content = base64.b64decode(readme_data["content"]).decode("utf-8")
                    readme_html_url = readme_data.get("html_url")
            except httpx.HTTPStatusError:
                # README not found, that's okay
                pass
        
        # Transform GitHub response to our format
        result = {
            "id": repo_data.get("id"),
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "html_url": repo_data.get("html_url"),
            "topics": repo_data.get("topics", []),
            "stargazers_count": repo_data.get("stargazers_count", 0),
            "forks_count": repo_data.get("forks_count", 0),
            "watchers_count": repo_data.get("watchers_count", 0),
            "open_issues_count": repo_data.get("open_issues_count", 0),
            "language": repo_data.get("language"),
            "languages_url": repo_data.get("languages_url"),
            "license": repo_data.get("license"),
            "default_branch": repo_data.get("default_branch"),
            "created_at": repo_data.get("created_at"),
            "updated_at": repo_data.get("updated_at"),
            "pushed_at": repo_data.get("pushed_at"),
            "owner": {
                "login": repo_data.get("owner", {}).get("login"),
                "avatar_url": repo_data.get("owner", {}).get("avatar_url"),
                "html_url": repo_data.get("owner", {}).get("html_url"),
                "type": repo_data.get("owner", {}).get("type"),
            },
            "readme": {
                "content": readme_content,
                "html_url": readme_html_url,
            },
        }
        
        # Cache the result
        await set_cached_data(db, cache_key, result)
        
        return result
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )
        if e.response.status_code == 403:
            raise HTTPException(
                status_code=503,
                detail="GitHub API rate limit exceeded. Please try again later."
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"GitHub API error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to GitHub API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

