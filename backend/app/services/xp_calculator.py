"""
XP calculation service for user leveling system
"""
from typing import Dict


# XP values for different activities
XP_VALUES = {
    "commit": 10,
    "pull_request": 50,
    "issue": 25,
    "new_project": 100,
}


def get_level_thresholds(level: int) -> Dict[str, int]:
    """
    Get XP thresholds for a given level
    Returns: dict with 'min' and 'max' XP values
    """
    thresholds = {
        1: {"min": 0, "max": 1000},
        2: {"min": 1000, "max": 2500},
        3: {"min": 2500, "max": 5000},
        4: {"min": 5000, "max": 10000},
        5: {"min": 10000, "max": 20000},
    }
    
    if level in thresholds:
        return thresholds[level]
    
    # For levels 6+, exponential growth
    base = 20000
    multiplier = 1.5 ** (level - 5)
    max_xp = int(base * multiplier)
    prev_max = get_level_thresholds(level - 1)["max"]
    
    return {"min": prev_max, "max": max_xp}


def calculate_level_from_xp(xp: int) -> int:
    """
    Calculate user level based on total XP
    """
    level = 1
    while True:
        threshold = get_level_thresholds(level)
        if xp < threshold["max"]:
            return level
        level += 1
        # Safety check to prevent infinite loop
        if level > 100:
            return 100


def calculate_xp_for_contribution(contribution_type: str) -> int:
    """
    Calculate XP awarded for a contribution type
    """
    return XP_VALUES.get(contribution_type, 0)


def calculate_total_xp(commits: int, pull_requests: int, issues: int, projects: int) -> int:
    """
    Calculate total XP from contribution counts
    """
    return (
        commits * XP_VALUES["commit"]
        + pull_requests * XP_VALUES["pull_request"]
        + issues * XP_VALUES["issue"]
        + projects * XP_VALUES["new_project"]
    )


def get_xp_to_next_level(current_xp: int, current_level: int) -> int:
    """
    Calculate XP needed to reach next level
    """
    threshold = get_level_thresholds(current_level)
    return max(0, threshold["max"] - current_xp)

