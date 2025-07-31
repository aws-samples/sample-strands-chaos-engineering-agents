"""
Experiment Database Tools

Tools for managing experiments in the database.
"""
from strands import tool
import json
import logging
from typing import Dict, Any, List, Optional
try:
    from .database_connection import execute_sql, format_parameter
except ImportError:
    # Handle direct execution
    from database_connection import execute_sql, format_parameter

# Set up logging
logger = logging.getLogger(__name__)

@tool
def insert_experiment(
    experiment_name: str,
    hypothesis_id: int,
    description: str,
    experiment_plan: str,
    fis_configuration: Dict[str, Any],
    fis_role_configuration: Optional[Dict[str, Any]] = None,
    status: str = "draft"
) -> Optional[int]:
    """
    Insert an experiment into the database.
    
    Args:
        experiment_name: Name/title of the experiment
        hypothesis_id: ID of the hypothesis this experiment tests
        description: Description of the experiment
        experiment_plan: Detailed plan for the experiment
        fis_configuration: FIS template configuration as JSON
        fis_role_configuration: IAM role configuration for FIS execution (optional)
        status: Status of the experiment (draft, planned, scheduled, etc.)
        
    Returns:
        The ID of the inserted experiment, or None if insertion failed
    """
    logger.info(f"Inserting experiment into database: '{experiment_name}' for hypothesis {hypothesis_id}")
    logger.debug(f"Experiment details - Status: {status}, Description: {description[:100]}...")
    
    try:
        # Insert experiment into database
        sql = """
        INSERT INTO experiment (
            hypothesis_id, title, description, experiment_plan, 
            fis_configuration, fis_role_configuration, status
        ) VALUES (
            :hypothesis_id, :title, :description, :experiment_plan,
            :fis_configuration::jsonb, :fis_role_configuration::jsonb, :status
        )
        RETURNING id
        """
        
        logger.debug(f"FIS configuration size: {len(json.dumps(fis_configuration))} characters")
        
        # Prepare parameters
        parameters = [
            format_parameter('hypothesis_id', hypothesis_id),
            format_parameter('title', experiment_name),
            format_parameter('description', description),
            format_parameter('experiment_plan', experiment_plan),
            format_parameter('fis_configuration', json.dumps(fis_configuration)),
            format_parameter('fis_role_configuration', json.dumps(fis_role_configuration) if fis_role_configuration else None),
            format_parameter('status', status)
        ]
        
        logger.debug("Executing SQL INSERT statement for experiment")
        response = execute_sql(sql, parameters)
        
        # Extract experiment ID from response (using RETURNING clause)
        experiment_id = response['records'][0][0]['longValue']
        logger.info(f"Successfully inserted experiment with ID: {experiment_id}")
        
        return experiment_id
        
    except RuntimeError as e:
        logger.error(f"Database error inserting experiment: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error inserting experiment: {str(e)}")
        return None

@tool
def get_experiments(
    status_filter: Optional[str] = None,
    hypothesis_id: Optional[int] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get experiments from the database.
    
    Args:
        status_filter: Optional status to filter by (e.g., "draft", "planned", "validation_failed")
        hypothesis_id: Optional hypothesis ID to filter by
        limit: Maximum number of experiments to return
        
    Returns:
        Dict containing list of experiments and query metadata
    """
    logger.info(f"Getting experiments from database with status filter: {status_filter}, hypothesis: {hypothesis_id}")
    
    try:
        # Build SQL query with optional filters
        where_conditions = []
        parameters = []
        
        if status_filter:
            where_conditions.append("e.status = :status")
            parameters.append(format_parameter('status', status_filter))
        
        if hypothesis_id is not None:
            where_conditions.append("e.hypothesis_id = :hypothesis_id")
            parameters.append(format_parameter('hypothesis_id', hypothesis_id))
        
        # Base query with joins to get hypothesis and component information
        base_sql = """
        SELECT e.id, e.hypothesis_id, e.title, e.description, e.experiment_plan,
               e.fis_configuration, e.fis_role_configuration, e.status, e.created_at, e.updated_at,
               h.title as hypothesis_title, h.description as hypothesis_description,
               sc.name as component_name, sc.type as component_type
        FROM experiment e
        LEFT JOIN hypothesis h ON e.hypothesis_id = h.id
        LEFT JOIN system_component sc ON h.system_component_id = sc.id
        """
        
        if where_conditions:
            sql = base_sql + " WHERE " + " AND ".join(where_conditions)
        else:
            sql = base_sql
        
        sql += " ORDER BY e.created_at DESC LIMIT :limit"
        parameters.append(format_parameter('limit', limit))
        
        logger.debug("Executing SQL SELECT statement for experiments")
        response = execute_sql(sql, parameters)
        
        logger.debug(f"Database response records count: {len(response.get('records', []))}")
        
        # Parse the response
        experiments = []
        records = response.get('records', [])
        
        for record in records:
            # Parse fis_role_configuration if it exists
            fis_role_config = None
            if record[6] and record[6].get('stringValue'):
                try:
                    fis_role_config = json.loads(record[6].get('stringValue'))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse fis_role_configuration for experiment {record[0].get('longValue')}")
                    fis_role_config = None
            
            experiment = {
                'id': record[0].get('longValue'),
                'hypothesis_id': record[1].get('longValue'),
                'title': record[2].get('stringValue', ''),
                'description': record[3].get('stringValue', ''),
                'experiment_plan': record[4].get('stringValue', ''),
                'fis_configuration': json.loads(record[5].get('stringValue', '{}')),
                'fis_role_configuration': fis_role_config,
                'status': record[7].get('stringValue', ''),
                'created_at': record[8].get('stringValue', ''),
                'updated_at': record[9].get('stringValue', ''),
                'hypothesis_title': record[10].get('stringValue', '') if record[10] else None,
                'hypothesis_description': record[11].get('stringValue', '') if record[11] else None,
                'component_name': record[12].get('stringValue', '') if record[12] else None,
                'component_type': record[13].get('stringValue', '') if record[13] else None
            }
            experiments.append(experiment)
        
        logger.info(f"Retrieved {len(experiments)} experiments from database")
        
        return {
            "success": True,
            "experiments": experiments,
            "count": len(experiments),
            "filters": {
                "status": status_filter,
                "hypothesis_id": hypothesis_id
            },
            "message": f"Retrieved {len(experiments)} experiments"
        }
        
    except RuntimeError as e:
        logger.error(f"Database error getting experiments: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "experiments": [],
            "count": 0,
            "message": "Failed to get experiments from database"
        }
    except Exception as e:
        logger.error(f"Unexpected error getting experiments: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "experiments": [],
            "count": 0,
            "message": "Failed to get experiments from database"
        }

@tool
def update_experiment(
    experiment_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    experiment_plan: Optional[str] = None,
    status: Optional[str] = None,
    fis_experiment_id: Optional[str] = None,
    experiment_notes: Optional[str] = None,
    scheduled_for: Optional[str] = None,
    executed_at: Optional[str] = None,
    completed_at: Optional[str] = None
) -> bool:
    """
    Update an existing experiment in the database.
    
    Args:
        experiment_id: ID of the experiment to update
        title: New title for the experiment
        description: New description for the experiment
        experiment_plan: New experiment plan
        status: New status for the experiment
        fis_experiment_id: FIS experiment ID to store
        experiment_notes: Notes about the experiment
        scheduled_for: When the experiment is scheduled (ISO timestamp)
        executed_at: When the experiment was executed (ISO timestamp)
        completed_at: When the experiment was completed (ISO timestamp)
        
    Returns:
        True if update was successful, False otherwise
    """
    logger.info(f"Updating experiment ID: {experiment_id}")
    
    try:
        # Build dynamic UPDATE query based on provided parameters
        update_fields = []
        parameters = []
        
        if title is not None:
            update_fields.append("title = :title")
            parameters.append(format_parameter('title', title))
        
        if description is not None:
            update_fields.append("description = :description")
            parameters.append(format_parameter('description', description))
        
        if experiment_plan is not None:
            update_fields.append("experiment_plan = :experiment_plan")
            parameters.append(format_parameter('experiment_plan', experiment_plan))
        
        if status is not None:
            update_fields.append("status = :status")
            parameters.append(format_parameter('status', status))
        
        if fis_experiment_id is not None:
            update_fields.append("fis_experiment_id = :fis_experiment_id")
            parameters.append(format_parameter('fis_experiment_id', fis_experiment_id))
        
        if experiment_notes is not None:
            update_fields.append("experiment_notes = :experiment_notes")
            parameters.append(format_parameter('experiment_notes', experiment_notes))
        
        if scheduled_for is not None:
            update_fields.append("scheduled_for = :scheduled_for::timestamp with time zone")
            parameters.append(format_parameter('scheduled_for', scheduled_for))
        
        if executed_at is not None:
            update_fields.append("executed_at = :executed_at::timestamp with time zone")
            parameters.append(format_parameter('executed_at', executed_at))
        
        if completed_at is not None:
            update_fields.append("completed_at = :completed_at::timestamp with time zone")
            parameters.append(format_parameter('completed_at', completed_at))
        
        if not update_fields:
            logger.warning("No fields provided for update")
            return False
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add the experiment_id parameter for WHERE clause
        parameters.append(format_parameter('experiment_id', experiment_id))
        
        sql = f"""
        UPDATE experiment SET
            {', '.join(update_fields)}
        WHERE id = :experiment_id
        """
        
        logger.debug("Executing UPDATE for experiment")
        response = execute_sql(sql, parameters)
        
        # Check if any rows were updated
        records_updated = response.get('numberOfRecordsUpdated', 0)
        
        if records_updated > 0:
            logger.info(f"Successfully updated experiment with ID: {experiment_id}")
            return True
        else:
            logger.warning(f"No experiment found with ID: {experiment_id}")
            return False
        
    except RuntimeError as e:
        logger.error(f"Database error updating experiment: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating experiment: {str(e)}")
        return False
