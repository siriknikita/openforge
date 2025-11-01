"""
Time tracking service for calculating time saved per project setup
"""
from typing import Optional
from datetime import datetime


# Average time (in minutes) to set up a project from scratch
DEFAULT_SETUP_TIME_MINUTES = 240  # 4 hours

# Time saved when using templates/boilerplate (in minutes)
TEMPLATE_TIME_SAVED_MINUTES = 180  # 3 hours saved


def calculate_time_saved(
    project_type: Optional[str] = None,
    used_template: bool = True,
) -> int:
    """
    Calculate time saved in minutes for project setup
    
    Args:
        project_type: Type of project (e.g., "web", "api", "library")
        used_template: Whether a template/boilerplate was used
        
    Returns:
        Time saved in minutes
    """
    if not used_template:
        return 0
    
    base_time_saved = TEMPLATE_TIME_SAVED_MINUTES
    
    # Adjust based on project type (future enhancement)
    type_multipliers = {
        "web": 1.0,
        "api": 0.8,
        "library": 0.9,
        "cli": 0.7,
    }
    
    multiplier = type_multipliers.get(project_type, 1.0)
    return int(base_time_saved * multiplier)


def aggregate_time_saved(projects: list) -> int:
    """
    Calculate total time saved across multiple projects
    
    Args:
        projects: List of projects with time_saved_minutes field
        
    Returns:
        Total time saved in minutes
    """
    total = 0
    for project in projects:
        if isinstance(project, dict):
            metadata = project.get("metadata", {})
            total += metadata.get("time_saved_minutes", 0)
        else:
            # Assume it's a Project model
            total += getattr(project.metadata, "time_saved_minutes", 0)
    return total

