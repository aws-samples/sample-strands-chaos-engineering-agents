"""
Resource Tags Configuration Management for Chaos Agent System

This module provides tag-based resource filtering capabilities for chaos engineering.
Tags are set via prompts/inputs and used to filter AWS resources during experiments.
"""
import os
import logging
from typing import List, Dict, Optional
from strands import tool

# Set up logging
logger = logging.getLogger(__name__)

# Global configuration cache
_tags_cache = {}

@tool
def get_workload_tags() -> List[Dict[str, str]]:
    """
    Get workload tags for resource filtering.
    
    Returns:
        List[Dict[str, str]]: List of tag key-value pairs for filtering resources.
                             Empty list if no tags are configured.
    """
    global _tags_cache
    
    # Check cache first
    if 'workload_tags' in _tags_cache:
        return _tags_cache['workload_tags']
    
    # Return empty list if no tags configured (default behavior)
    logger.info("No workload tags configured - will consider all resources")
    _tags_cache['workload_tags'] = []
    return []

def parse_tags_string(tags_string: str) -> List[Dict[str, str]]:
    """
    Parse a tags string into a list of tag dictionaries.
    
    Supports formats:
    - "Environment=prod,Application=retail-store"
    - "Environment=prod Application=retail-store"
    - "Environment:prod,Application:retail-store"
    
    Args:
        tags_string: String representation of tags
        
    Returns:
        List[Dict[str, str]]: Parsed tags
        
    Raises:
        ValueError: If tags string format is invalid
    """
    if not tags_string or not tags_string.strip():
        return []
    
    tags = []
    
    # Split by comma first, then by space as fallback
    tag_pairs = []
    if ',' in tags_string:
        tag_pairs = [pair.strip() for pair in tags_string.split(',')]
    else:
        tag_pairs = [pair.strip() for pair in tags_string.split()]
    
    for pair in tag_pairs:
        if not pair:
            continue
            
        # Support both = and : as separators
        if '=' in pair:
            key, value = pair.split('=', 1)
        elif ':' in pair:
            key, value = pair.split(':', 1)
        else:
            raise ValueError(f"Invalid tag format: '{pair}'. Expected 'key=value' or 'key:value'")
        
        key = key.strip()
        value = value.strip()
        
        if not key or not value:
            raise ValueError(f"Invalid tag format: '{pair}'. Key and value cannot be empty")
        
        tags.append({key: value})
    
    return tags

def set_workload_tags_from_string(tags_string: str) -> None:
    """
    Set workload tags from a string representation.
    
    Args:
        tags_string: String representation of tags (e.g., "Environment=prod,Application=web")
    """
    global _tags_cache
    
    tags = parse_tags_string(tags_string)
    
    # Store in cache
    _tags_cache['workload_tags'] = tags
    
    logger.info(f"Workload tags set to: {tags}")

def clear_workload_tags() -> None:
    """Clear workload tags (useful for testing)."""
    global _tags_cache
    if 'workload_tags' in _tags_cache:
        del _tags_cache['workload_tags']
    logger.info("Workload tags cleared")



def clear_tags_cache() -> None:
    """Clear the tags configuration cache (useful for testing)."""
    global _tags_cache
    _tags_cache.clear()
    logger.debug("Tags configuration cache cleared")
