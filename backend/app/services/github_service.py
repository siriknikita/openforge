"""
GitHub API service for repository creation and management

This module handles GitHub API interactions for creating repositories, adding topics,
and managing repository files. It supports two authentication methods:

1. Clerk OAuth Integration: Retrieves GitHub OAuth tokens from Clerk
2. GitHub Personal Access Token: Falls back to GITHUB_TOKEN from environment

Token Priority:
- If Clerk OAuth token has 'repo' scope → uses Clerk token
- If Clerk token lacks 'repo' scope → falls back to GITHUB_TOKEN
- If no Clerk token available → uses GITHUB_TOKEN directly

All tokens are verified to have the 'repo' scope before use.

See GITHUB_TOKEN_SETUP.md for detailed setup instructions.
"""
import httpx
import asyncio
import base64
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import logging
from app.config import settings

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
MAX_RETRIES = 3
BASE_DELAY = 1  # seconds


async def check_token_has_repo_scope(token: str) -> bool:
    """
    Check if a GitHub token has the 'repo' scope
    
    Args:
        token: GitHub OAuth token
        
    Returns:
        True if token has repo scope, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                }
            )
            if response.status_code == 200:
                scopes = response.headers.get("X-OAuth-Scopes", "")
                return "repo" in scopes
    except Exception as e:
        logger.warning(f"Error checking token scope: {e}")
    return False


async def get_github_token_from_clerk(clerk_user_id: str, clerk_secret_key: str) -> Optional[str]:
    """
    Retrieve GitHub OAuth token from Clerk Backend API
    Falls back to GITHUB_TOKEN from environment if Clerk token lacks repo scope
    
    Args:
        clerk_user_id: Clerk user ID
        clerk_secret_key: Clerk secret key for API authentication
        
    Returns:
        GitHub OAuth token with repo scope if available, None otherwise
    """
    clerk_token = None
    
    # Try to get token from Clerk
    if clerk_secret_key:
        try:
            url = f"https://api.clerk.com/v1/users/{clerk_user_id}/oauth_access_tokens/github"
            headers = {
                "Authorization": f"Bearer {clerk_secret_key}",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    # Clerk returns a list of tokens, get the first one
                    if data and len(data) > 0:
                        clerk_token = data[0].get("token")
                elif response.status_code == 404:
                    logger.info(f"No GitHub OAuth token found for user {clerk_user_id}")
                else:
                    logger.error(f"Clerk API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error retrieving GitHub token from Clerk: {e}")
    
    # Check if Clerk token has repo scope
    if clerk_token:
        has_repo_scope = await check_token_has_repo_scope(clerk_token)
        if has_repo_scope:
            logger.info("Using Clerk OAuth token with repo scope")
            return clerk_token
        else:
            logger.warning("Clerk OAuth token lacks 'repo' scope")
    
    # Fall back to manual GITHUB_TOKEN if configured
    if settings.github_token:
        has_repo_scope = await check_token_has_repo_scope(settings.github_token)
        if has_repo_scope:
            logger.info("Falling back to GITHUB_TOKEN from environment (has repo scope)")
            return settings.github_token
        else:
            logger.warning("GITHUB_TOKEN from environment also lacks 'repo' scope")
    
    # No valid token available
    if clerk_token:
        logger.warning("Clerk token available but lacks repo scope, and no fallback token configured")
    else:
        logger.warning("No GitHub token available from Clerk or environment")
    
    return None


async def retry_with_backoff(func, *args, max_retries: int = MAX_RETRIES, **kwargs):
    """
    Retry a function with exponential backoff
    
    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts
        **kwargs: Keyword arguments for func
        
    Returns:
        Result of func
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = BASE_DELAY * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Retry attempt {attempt + 1}/{max_retries} after {delay}s: {e}")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All retry attempts failed: {e}")
                raise last_exception
    
    raise last_exception


def validate_repository_name(name: str) -> bool:
    """
    Validate repository name according to GitHub rules
    
    Args:
        name: Repository name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name or len(name) < 1 or len(name) > 100:
        return False
    
    # GitHub allows: alphanumeric, hyphens, underscores, dots
    # Cannot start or end with a dot, hyphen, or underscore
    if name.startswith(('.', '-', '_')) or name.endswith(('.', '-', '_')):
        return False
    
    # Check for valid characters
    valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._')
    if not all(c in valid_chars for c in name):
        return False
    
    return True


async def create_github_repository(
    github_token: str,
    name: str,
    description: Optional[str] = None,
    is_private: bool = False
) -> Dict[str, Any]:
    """
    Create a new GitHub repository
    
    Args:
        github_token: GitHub OAuth token
        name: Repository name
        description: Repository description
        is_private: Whether repository is private
        
    Returns:
        GitHub repository data
        
    Raises:
        HTTPException: If repository creation fails
    """
    if not validate_repository_name(name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid repository name. Must be 1-100 characters, alphanumeric with hyphens, underscores, or dots."
        )
    
    url = f"{GITHUB_API_BASE}/user/repos"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenForge/1.0",
    }
    
    payload = {
        "name": name,
        "description": description or "",
        "private": is_private,
        "auto_init": False,  # We'll create files manually
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 422:
            error_data = response.json()
            errors = error_data.get("errors", [])
            if errors and any(e.get("field") == "name" for e in errors):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Repository name already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_data.get("message", "Invalid repository data")
            )
        elif response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient GitHub OAuth permissions. Please ensure your GitHub account has 'repo' scope."
            )
        elif response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired GitHub token"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"GitHub API error: {response.status_code} - {response.text}"
            )


async def add_repository_topic(
    github_token: str,
    owner: str,
    repo: str,
    topics: list
) -> Dict[str, Any]:
    """
    Add topics to a GitHub repository
    
    Args:
        github_token: GitHub OAuth token
        owner: Repository owner
        repo: Repository name
        topics: List of topics to add
        
    Returns:
        Updated topics data
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/topics"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.mercy-preview+json",
        "User-Agent": "OpenForge/1.0",
    }
    
    payload = {
        "names": topics
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.put(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to add topics: {response.status_code} - {response.text}")
            # Don't fail the whole operation if topics fail
            return {"names": topics}


async def create_file_in_repository(
    github_token: str,
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str
) -> bool:
    """
    Create a file in a GitHub repository
    
    Args:
        github_token: GitHub OAuth token
        owner: Repository owner
        repo: Repository name
        path: File path (e.g., "README.md")
        content: File content (will be base64 encoded)
        message: Commit message
        
    Returns:
        True if successful
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenForge/1.0",
    }
    
    # Encode content to base64
    content_bytes = content.encode('utf-8')
    content_b64 = base64.b64encode(content_bytes).decode('utf-8')
    
    payload = {
        "message": message,
        "content": content_b64,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.put(url, headers=headers, json=payload)
        
        if response.status_code in [201, 200]:
            return True
        else:
            logger.warning(f"Failed to create file {path}: {response.status_code} - {response.text}")
            return False


def generate_readme_template(name: str, description: str, tech_stack: list) -> str:
    """
    Generate README.md template
    
    Args:
        name: Project name
        description: Project description
        tech_stack: List of technologies
        
    Returns:
        README.md content
    """
    tech_stack_list = "\n".join([f"- {tech}" for tech in tech_stack]) if tech_stack else "- (To be added)"
    
    return f"""# {name}

{description or "A new open-source project created with OpenForge"}

## Tech Stack

{tech_stack_list}

## Getting Started

[Add setup instructions here]

## Contributing

This project uses the `openforge-demo` topic. Join us on [OpenForge](https://openforge.dev)!

## License

[Add license information]
"""


def generate_gitignore_template(tech_stack: list) -> str:
    """
    Generate .gitignore template based on tech stack
    
    Args:
        tech_stack: List of technologies
        
    Returns:
        .gitignore content
    """
    gitignore_sections = []
    
    # Python
    if any(tech.lower() in ["python", "fastapi", "django", "flask", "pytest"] for tech in tech_stack):
        gitignore_sections.append("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/""")
    
    # Node/JavaScript
    if any(tech.lower() in ["node", "nodejs", "javascript", "typescript", "react", "next", "vue", "angular"] for tech in tech_stack):
        gitignore_sections.append("""# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.next/
dist/
build/
.cache/""")
    
    # General
    gitignore_sections.append("""# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/""")
    
    return "\n\n".join(gitignore_sections) if gitignore_sections else "\n".join([
        "# IDE",
        ".vscode/",
        ".idea/",
        "",
        "# OS",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Logs",
        "*.log"
    ])

