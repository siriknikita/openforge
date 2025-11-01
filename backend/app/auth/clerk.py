"""
Clerk authentication integration
"""
from typing import Optional
from fastapi import HTTPException, status
from app.config import settings


async def verify_clerk_token(token: str) -> Optional[dict]:
    """
    Verify Clerk JWT token and extract user information
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User payload if valid, None otherwise
    """
    if not settings.clerk_secret_key:
        # In development, allow bypassing auth
        # In production, this should always be set
        return None
    
    try:
        # Clerk provides a verification endpoint
        # For production, use Clerk's SDK or verify JWT locally
        # This is a simplified version - in production, use proper JWT verification
        
        # For now, we'll accept the user_id from query params or headers
        # In production, implement proper JWT verification using Clerk's secret
        return None
    except Exception as e:
        print(f"Error verifying Clerk token: {e}")
        return None


def extract_user_id_from_request(request) -> Optional[str]:
    """
    Extract user ID from request headers or query params
    This is a temporary solution - in production, use proper JWT verification
    
    Args:
        request: FastAPI request object
        
    Returns:
        User ID if found, None otherwise
    """
    # Check Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header:
        # Extract token (format: "Bearer <token>")
        parts = auth_header.split(" ")
        if len(parts) == 2:
            # In production, verify this token with Clerk
            # For now, we'll use query param as fallback
            pass
    
    # Fallback to query param (for development)
    user_id = request.query_params.get("user_id")
    if user_id:
        return user_id
    
    # Check request body for user_id
    if hasattr(request, "json") and request.json:
        body = request.json()
        if isinstance(body, dict) and "user_id" in body:
            return body["user_id"]
    
    return None


async def get_current_user_id(request) -> str:
    """
    Get current authenticated user ID from request
    
    Raises:
        HTTPException: If user is not authenticated
    """
    user_id = extract_user_id_from_request(request)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    return user_id

