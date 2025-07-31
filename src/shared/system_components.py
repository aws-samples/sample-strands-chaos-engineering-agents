"""
System Component Database Tools

Tools for managing system components in the database.
"""
from strands import tool
import logging
from typing import Dict, Any, List, Optional
from .database_connection import execute_sql, format_parameter

# Set up logging
logger = logging.getLogger(__name__)

@tool
def insert_system_component(
    name: str,
    component_type: str,
    description: Optional[str] = None
) -> Optional[int]:
    """
    Insert a new system component into the database.
    
    Args:
        name: Name of the system component
        component_type: Type of the component (e.g., 'ECS Service', 'RDS PostgreSQL')
        description: Optional description of the component
        
    Returns:
        The ID of the inserted system component, or None if insertion failed
    """
    logger.info(f"Inserting new system component: '{name}' of type '{component_type}'")
    
    try:
        # Insert new system component
        sql = """
        INSERT INTO system_component (name, type, description)
        VALUES (:name, :type, :description)
        RETURNING id
        """
        
        parameters = [
            format_parameter('name', name),
            format_parameter('type', component_type),
            format_parameter('description', description)
        ]
        
        logger.debug("Executing INSERT for system component")
        response = execute_sql(sql, parameters)
        
        # Extract component ID from response
        component_id = response['records'][0][0]['longValue']
        logger.info(f"Successfully inserted system component with ID: {component_id}")
        
        return component_id
        
    except RuntimeError as e:
        logger.error(f"Database error inserting system component: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error inserting system component: {str(e)}")
        return None

@tool
def update_system_component(
    component_id: int,
    name: Optional[str] = None,
    component_type: Optional[str] = None,
    description: Optional[str] = None
) -> bool:
    """
    Update an existing system component in the database.
    
    Args:
        component_id: ID of the system component to update
        name: New name of the system component
        component_type: New type of the component
        description: New description of the component
        
    Returns:
        True if update was successful, False otherwise
    """
    logger.info(f"Updating system component ID: {component_id}")
    
    try:
        # Build dynamic UPDATE query based on provided parameters
        update_fields = []
        parameters = []
        
        if name is not None:
            update_fields.append("name = :name")
            parameters.append(format_parameter('name', name))
        
        if component_type is not None:
            update_fields.append("type = :type")
            parameters.append(format_parameter('type', component_type))
        
        if description is not None:
            update_fields.append("description = :description")
            parameters.append(format_parameter('description', description))
        
        if not update_fields:
            logger.warning("No fields provided for update")
            return False
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add the component_id parameter for WHERE clause
        parameters.append(format_parameter('component_id', component_id))
        
        sql = f"""
        UPDATE system_component SET
            {', '.join(update_fields)}
        WHERE id = :component_id
        """
        
        logger.debug("Executing UPDATE for system component")
        response = execute_sql(sql, parameters)
        
        # Check if any rows were updated
        records_updated = response.get('numberOfRecordsUpdated', 0)
        
        if records_updated > 0:
            logger.info(f"Successfully updated system component with ID: {component_id}")
            return True
        else:
            logger.warning(f"No system component found with ID: {component_id}")
            return False
        
    except RuntimeError as e:
        logger.error(f"Database error updating system component: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating system component: {str(e)}")
        return False

@tool
def get_system_components(
    component_type: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get system components from the database.
    
    Args:
        component_type: Optional filter by component type
        limit: Maximum number of components to return
        
    Returns:
        Dict containing list of system components and query metadata
    """
    logger.info(f"Getting system components with type filter: {component_type}")
    
    try:
        # Build SQL query with optional type filter
        if component_type:
            sql = """
            SELECT id, name, type, description, created_at, updated_at
            FROM system_component
            WHERE type = :component_type
            ORDER BY name
            LIMIT :limit
            """
            parameters = [
                format_parameter('component_type', component_type),
                format_parameter('limit', limit)
            ]
        else:
            sql = """
            SELECT id, name, type, description, created_at, updated_at
            FROM system_component
            ORDER BY name
            LIMIT :limit
            """
            parameters = [
                format_parameter('limit', limit)
            ]
        
        logger.debug("Executing SQL SELECT for system components")
        response = execute_sql(sql, parameters)
        
        # Parse the response
        components = []
        records = response.get('records', [])
        
        for record in records:
            component = {
                'id': record[0].get('longValue'),
                'name': record[1].get('stringValue', ''),
                'type': record[2].get('stringValue', ''),
                'description': record[3].get('stringValue', '') if record[3] else None,
                'created_at': record[4].get('stringValue', ''),
                'updated_at': record[5].get('stringValue', '')
            }
            components.append(component)
        
        logger.info(f"Retrieved {len(components)} system components from database")
        
        return {
            "success": True,
            "components": components,
            "count": len(components),
            "type_filter": component_type,
            "message": f"Retrieved {len(components)} system components"
        }
        
    except RuntimeError as e:
        logger.error(f"Database error getting system components: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "components": [],
            "count": 0,
            "message": "Failed to get system components from database"
        }
    except Exception as e:
        logger.error(f"Unexpected error getting system components: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "components": [],
            "count": 0,
            "message": "Failed to get system components from database"
        }

@tool
def batch_insert_system_components(
    components: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Batch insert multiple system components in a single database transaction.
    
    This tool significantly improves performance by inserting all system components
    in one database call instead of making N individual insert calls.
    
    Args:
        components: List of dictionaries with component data:
                   [{"name": "...", "type": "...", "description": "..."}, ...]
                   Required keys: name, type
                   Optional keys: description
        
    Returns:
        Dict containing success status, inserted count, and component IDs
    """
    logger.info(f"Batch inserting {len(components)} system components")
    
    try:
        if not components:
            logger.warning("No system components provided for batch insert")
            return {
                "success": False,
                "error": "No system components provided",
                "inserted_count": 0,
                "component_ids": [],
                "message": "No system components to insert"
            }
        
        # Validate input format
        for i, component in enumerate(components):
            if not isinstance(component, dict):
                raise ValueError(f"Component {i} is not a dictionary")
            if 'name' not in component or 'type' not in component:
                raise ValueError(f"Component {i} missing required keys 'name' or 'type'")
            if not isinstance(component['name'], str) or not component['name'].strip():
                raise ValueError(f"Component {i} has invalid name")
            if not isinstance(component['type'], str) or not component['type'].strip():
                raise ValueError(f"Component {i} has invalid type")
        
        # Build batch INSERT with VALUES clause
        values_clauses = []
        parameters = []
        
        for i, component in enumerate(components):
            # Set defaults for optional fields
            name = component['name']
            component_type = component['type']
            description = component.get('description')
            
            # Create parameter placeholders for this component
            values_clauses.append(f"(:name_{i}, :type_{i}, :description_{i})")
            
            # Add parameters for this component
            parameters.extend([
                format_parameter(f'name_{i}', name),
                format_parameter(f'type_{i}', component_type),
                format_parameter(f'description_{i}', description)
            ])
        
        # Create the batch insert SQL
        sql = f"""
        INSERT INTO system_component (name, type, description)
        VALUES {', '.join(values_clauses)}
        RETURNING id
        """
        
        logger.debug(f"Executing batch INSERT for {len(components)} system components")
        response = execute_sql(sql, parameters)
        
        # Extract component IDs from response
        component_ids = []
        records = response.get('records', [])
        
        for record in records:
            if record and len(record) > 0:
                component_id = record[0].get('longValue')
                if component_id:
                    component_ids.append(component_id)
        
        inserted_count = len(component_ids)
        
        if inserted_count > 0:
            logger.info(f"Successfully batch inserted {inserted_count} system components")
            return {
                "success": True,
                "inserted_count": inserted_count,
                "requested_count": len(components),
                "component_ids": component_ids,
                "message": f"Successfully inserted {inserted_count} system components"
            }
        else:
            logger.warning("No system components were inserted")
            return {
                "success": False,
                "error": "No system components were inserted",
                "inserted_count": 0,
                "component_ids": [],
                "requested_count": len(components),
                "message": "Failed to insert system components"
            }
        
    except ValueError as e:
        logger.error(f"Validation error in batch insert: {str(e)}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "inserted_count": 0,
            "component_ids": [],
            "message": "Failed to validate batch insert data"
        }
    except RuntimeError as e:
        logger.error(f"Database error in batch insert: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "inserted_count": 0,
            "component_ids": [],
            "message": "Database error during batch insert"
        }
    except Exception as e:
        logger.error(f"Unexpected error in batch insert: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "inserted_count": 0,
            "component_ids": [],
            "message": "Failed to batch insert system components"
        }
