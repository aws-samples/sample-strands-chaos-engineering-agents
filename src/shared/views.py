"""
Database View Access Tools

Tools for accessing database views that provide joined data.
"""
from strands import tool
import logging
from typing import Dict, Any, List, Optional
from .database_connection import execute_sql, format_parameter

# Set up logging
logger = logging.getLogger(__name__)

@tool
def get_experiments_with_context(
    status_filter: Optional[str] = None,
    hypothesis_status_filter: Optional[str] = None,
    component_type_filter: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get experiments with their hypothesis and system component context from the database view.
    
    This function uses the experiment_with_hypothesis view to provide rich context
    about experiments including their related hypothesis and system component information.
    
    Args:
        status_filter: Optional experiment status to filter by (e.g., "draft", "planned")
        hypothesis_status_filter: Optional hypothesis status to filter by (e.g., "proposed", "prioritized")
        component_type_filter: Optional system component type to filter by (e.g., "ECS Service")
        limit: Maximum number of experiments to return
        
    Returns:
        Dict containing list of experiments with full context and query metadata
    """
    logger.info(f"Getting experiments with context - status: {status_filter}, hypothesis_status: {hypothesis_status_filter}, component_type: {component_type_filter}")
    
    try:
        # Build SQL query with optional filters
        where_conditions = []
        parameters = []
        
        if status_filter:
            where_conditions.append("status = :status")
            parameters.append(format_parameter('status', status_filter))
        
        if hypothesis_status_filter:
            where_conditions.append("hypothesis_status = :hypothesis_status")
            parameters.append(format_parameter('hypothesis_status', hypothesis_status_filter))
        
        if component_type_filter:
            where_conditions.append("component_type = :component_type")
            parameters.append(format_parameter('component_type', component_type_filter))
        
        # Query the view
        base_sql = """
        SELECT id, title, description, experiment_plan, status, 
               scheduled_for, executed_at, completed_at, created_at,
               hypothesis_title, hypothesis_description, hypothesis_status,
               component_name, component_type
        FROM experiment_with_hypothesis
        """
        
        if where_conditions:
            sql = base_sql + " WHERE " + " AND ".join(where_conditions)
        else:
            sql = base_sql
        
        sql += " ORDER BY created_at DESC LIMIT :limit"
        parameters.append(format_parameter('limit', limit))
        
        logger.debug("Executing SQL SELECT from experiment_with_hypothesis view")
        response = execute_sql(sql, parameters)
        
        # Parse the response
        experiments = []
        records = response.get('records', [])
        
        for record in records:
            experiment = {
                'id': record[0].get('longValue'),
                'title': record[1].get('stringValue', ''),
                'description': record[2].get('stringValue', ''),
                'experiment_plan': record[3].get('stringValue', ''),
                'status': record[4].get('stringValue', ''),
                'scheduled_for': record[5].get('stringValue', '') if record[5] else None,
                'executed_at': record[6].get('stringValue', '') if record[6] else None,
                'completed_at': record[7].get('stringValue', '') if record[7] else None,
                'created_at': record[8].get('stringValue', ''),
                'hypothesis_title': record[9].get('stringValue', '') if record[9] else None,
                'hypothesis_description': record[10].get('stringValue', '') if record[10] else None,
                'hypothesis_status': record[11].get('stringValue', '') if record[11] else None,
                'component_name': record[12].get('stringValue', '') if record[12] else None,
                'component_type': record[13].get('stringValue', '') if record[13] else None
            }
            experiments.append(experiment)
        
        logger.info(f"Retrieved {len(experiments)} experiments with context from view")
        
        return {
            "success": True,
            "experiments": experiments,
            "count": len(experiments),
            "filters": {
                "status": status_filter,
                "hypothesis_status": hypothesis_status_filter,
                "component_type": component_type_filter
            },
            "message": f"Retrieved {len(experiments)} experiments with context"
        }
        
    except RuntimeError as e:
        logger.error(f"Database error getting experiments with context: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "experiments": [],
            "count": 0,
            "message": "Failed to get experiments with context from database"
        }
    except Exception as e:
        logger.error(f"Unexpected error getting experiments with context: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "experiments": [],
            "count": 0,
            "message": "Failed to get experiments with context from database"
        }
