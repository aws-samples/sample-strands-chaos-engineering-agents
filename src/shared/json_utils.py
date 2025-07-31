"""
JSON Utilities for Database Operations

Common utilities for safely parsing JSON fields from database responses.
"""
import json
import logging

logger = logging.getLogger(__name__)

from typing import Any, Dict, List, Union, Optional

def safe_json_parse(field: Any, field_name: str, default: Optional[Union[Dict[str, Any], List[Any]]] = None) -> Union[Dict[str, Any], List[Any]]:
    """
    Safely parse JSON field from database response with error logging.
    
    Args:
        field: Database field response
        field_name: Name of the field for error logging
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON data or default value
    """
    if field and field.get('stringValue') and field['stringValue'].strip():
        try:
            return json.loads(field['stringValue'])
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON for field '{field_name}': {e}")
            logger.warning(f"Raw value: {field['stringValue'][:200]}...")
            return default if default is not None else ([] if isinstance(default, list) else {})
    return default if default is not None else ([] if isinstance(default, list) else {})
