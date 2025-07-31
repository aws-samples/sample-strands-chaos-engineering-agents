"""
Hypothesis Database Tools

Tools for managing hypotheses in the database.
"""
from strands import tool
import logging
from typing import Dict, Any, List, Optional
from .database_connection import execute_sql, format_parameter

# Set up logging
logger = logging.getLogger(__name__)

@tool
def insert_hypothesis(
    title: str,
    description: Optional[str] = None,
    persona: Optional[str] = None,
    steady_state_description: Optional[str] = None,
    failure_mode: Optional[str] = None,
    status: str = "proposed",
    priority: int = 1,
    notes: Optional[str] = None,
    system_component_id: Optional[int] = None
) -> Optional[int]:
    """
    Insert a new hypothesis into the database.
    
    Args:
        title: Title of the hypothesis
        description: Description of the hypothesis
        persona: Persona perspective (e.g., 'End User', 'Application Developer')
        steady_state_description: Description of the expected steady state
        failure_mode: Description of the failure mode to test
        status: Status of the hypothesis (default: 'proposed')
        priority: Priority level (default: 1)
        notes: Additional notes about the hypothesis
        system_component_id: ID of the related system component
        
    Returns:
        The ID of the inserted hypothesis, or None if insertion failed
    """
    logger.info(f"Inserting new hypothesis: '{title}' with status '{status}' and priority {priority}")
    
    try:
        # Insert new hypothesis
        sql = """
        INSERT INTO hypothesis (
            title, description, persona, steady_state_description, 
            failure_mode, status, priority, notes, system_component_id
        )
        VALUES (
            :title, :description, :persona, :steady_state_description,
            :failure_mode, :status, :priority, :notes, :system_component_id
        )
        RETURNING id
        """
        
        parameters = [
            format_parameter('title', title),
            format_parameter('description', description),
            format_parameter('persona', persona),
            format_parameter('steady_state_description', steady_state_description),
            format_parameter('failure_mode', failure_mode),
            format_parameter('status', status),
            format_parameter('priority', priority),
            format_parameter('notes', notes),
            format_parameter('system_component_id', system_component_id)
        ]
        
        logger.debug("Executing INSERT for hypothesis")
        response = execute_sql(sql, parameters)
        
        # Extract hypothesis ID from response
        hypothesis_id = response['records'][0][0]['longValue']
        logger.info(f"Successfully inserted hypothesis with ID: {hypothesis_id}")
        
        return hypothesis_id
        
    except RuntimeError as e:
        logger.error(f"Database error inserting hypothesis: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error inserting hypothesis: {str(e)}")
        return None

@tool
def update_hypothesis(
    hypothesis_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    persona: Optional[str] = None,
    steady_state_description: Optional[str] = None,
    failure_mode: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    notes: Optional[str] = None,
    system_component_id: Optional[int] = None
) -> bool:
    """
    Update an existing hypothesis in the database.
    
    Args:
        hypothesis_id: ID of the hypothesis to update
        title: New title of the hypothesis
        description: New description of the hypothesis
        persona: New persona perspective
        steady_state_description: New description of the expected steady state
        failure_mode: New description of the failure mode to test
        status: New status of the hypothesis
        priority: New priority level
        notes: New additional notes about the hypothesis
        system_component_id: New ID of the related system component
        
    Returns:
        True if update was successful, False otherwise
    """
    logger.info(f"Updating hypothesis ID: {hypothesis_id}")
    
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
        
        if persona is not None:
            update_fields.append("persona = :persona")
            parameters.append(format_parameter('persona', persona))
        
        if steady_state_description is not None:
            update_fields.append("steady_state_description = :steady_state_description")
            parameters.append(format_parameter('steady_state_description', steady_state_description))
        
        if failure_mode is not None:
            update_fields.append("failure_mode = :failure_mode")
            parameters.append(format_parameter('failure_mode', failure_mode))
        
        if status is not None:
            update_fields.append("status = :status")
            parameters.append(format_parameter('status', status))
        
        if priority is not None:
            update_fields.append("priority = :priority")
            parameters.append(format_parameter('priority', priority))
        
        if notes is not None:
            update_fields.append("notes = :notes")
            parameters.append(format_parameter('notes', notes))
        
        if system_component_id is not None:
            update_fields.append("system_component_id = :system_component_id")
            parameters.append(format_parameter('system_component_id', system_component_id))
        
        if not update_fields:
            logger.warning("No fields provided for update")
            return False
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add the hypothesis_id parameter for WHERE clause
        parameters.append(format_parameter('hypothesis_id', hypothesis_id))
        
        sql = f"""
        UPDATE hypothesis SET
            {', '.join(update_fields)}
        WHERE id = :hypothesis_id
        """
        
        logger.debug("Executing UPDATE for hypothesis")
        response = execute_sql(sql, parameters)
        
        # Check if any rows were updated
        records_updated = response.get('numberOfRecordsUpdated', 0)
        
        if records_updated > 0:
            logger.info(f"Successfully updated hypothesis with ID: {hypothesis_id}")
            return True
        else:
            logger.warning(f"No hypothesis found with ID: {hypothesis_id}")
            return False
        
    except RuntimeError as e:
        logger.error(f"Database error updating hypothesis: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating hypothesis: {str(e)}")
        return False

@tool
def get_hypotheses(
    hypothesis_ids: Optional[List[int]] = None,
    status_filter: Optional[str] = None,
    priority_filter: Optional[int] = None,
    system_component_id: Optional[int] = None,
    service_filter: Optional[str] = None,
    top_n: Optional[int] = None,
    priority_range: Optional[tuple] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get hypotheses from the database with flexible filtering options.
    
    Args:
        hypothesis_ids: Optional list of specific hypothesis IDs to retrieve
        status_filter: Optional filter by status (e.g., 'proposed', 'prioritized', 'tested')
        priority_filter: Optional filter by priority level
        system_component_id: Optional filter by system component ID
        service_filter: Optional filter by service/component type (e.g., 'ECS', 'RDS')
        top_n: Optional get top N hypotheses by priority (1 = highest priority)
        priority_range: Optional tuple (min_priority, max_priority) for priority range
        limit: Maximum number of hypotheses to return
        
    Returns:
        Dict containing list of hypotheses and query metadata
    """
    logger.info(f"Getting hypotheses with filters - IDs: {hypothesis_ids}, status: {status_filter}, priority: {priority_filter}, component: {system_component_id}, service: {service_filter}, top_n: {top_n}, priority_range: {priority_range}")
    
    try:
        # Build SQL query with optional filters
        where_conditions = []
        parameters = []
        
        # Handle specific hypothesis IDs
        if hypothesis_ids:
            placeholders = ','.join([f':id_{i}' for i in range(len(hypothesis_ids))])
            where_conditions.append(f"h.id IN ({placeholders})")
            for i, hyp_id in enumerate(hypothesis_ids):
                parameters.append(format_parameter(f'id_{i}', hyp_id))
        
        if status_filter:
            where_conditions.append("h.status = :status")
            parameters.append(format_parameter('status', status_filter))
        
        if priority_filter is not None:
            where_conditions.append("h.priority = :priority")
            parameters.append(format_parameter('priority', priority_filter))
        
        if system_component_id is not None:
            where_conditions.append("h.system_component_id = :system_component_id")
            parameters.append(format_parameter('system_component_id', system_component_id))
        
        # Handle service filter (search in component type or hypothesis title/description)
        if service_filter:
            where_conditions.append("(UPPER(sc.type) LIKE UPPER(:service_filter) OR UPPER(h.title) LIKE UPPER(:service_filter_title) OR UPPER(h.description) LIKE UPPER(:service_filter_desc))")
            parameters.append(format_parameter('service_filter', f'%{service_filter}%'))
            parameters.append(format_parameter('service_filter_title', f'%{service_filter}%'))
            parameters.append(format_parameter('service_filter_desc', f'%{service_filter}%'))
        
        # Handle priority range
        if priority_range and len(priority_range) == 2:
            min_priority, max_priority = priority_range
            where_conditions.append("h.priority BETWEEN :min_priority AND :max_priority")
            parameters.append(format_parameter('min_priority', min_priority))
            parameters.append(format_parameter('max_priority', max_priority))
        
        # Base query with joins to get component information
        base_sql = """
        SELECT h.id, h.title, h.description, h.persona, h.steady_state_description,
               h.failure_mode, h.status, h.priority, h.notes, h.system_component_id,
               h.created_at, h.updated_at,
               sc.name as component_name, sc.type as component_type
        FROM hypothesis h
        LEFT JOIN system_component sc ON h.system_component_id = sc.id
        """
        
        if where_conditions:
            sql = base_sql + " WHERE " + " AND ".join(where_conditions)
        else:
            sql = base_sql
        
        # Handle top_n parameter (overrides limit)
        if top_n is not None:
            sql += " ORDER BY h.priority ASC, h.created_at DESC LIMIT :top_n"
            parameters.append(format_parameter('top_n', top_n))
        else:
            sql += " ORDER BY h.priority ASC, h.created_at DESC LIMIT :limit"
            parameters.append(format_parameter('limit', limit))
        
        logger.debug("Executing SQL SELECT for hypotheses")
        response = execute_sql(sql, parameters)
        
        # Parse the response
        hypotheses = []
        records = response.get('records', [])
        
        for record in records:
            hypothesis = {
                'id': record[0].get('longValue'),
                'title': record[1].get('stringValue', ''),
                'description': record[2].get('stringValue', '') if record[2] else None,
                'persona': record[3].get('stringValue', '') if record[3] else None,
                'steady_state_description': record[4].get('stringValue', '') if record[4] else None,
                'failure_mode': record[5].get('stringValue', '') if record[5] else None,
                'status': record[6].get('stringValue', ''),
                'priority': record[7].get('longValue'),
                'notes': record[8].get('stringValue', '') if record[8] else None,
                'system_component_id': record[9].get('longValue') if record[9] else None,
                'created_at': record[10].get('stringValue', ''),
                'updated_at': record[11].get('stringValue', ''),
                'component_name': record[12].get('stringValue', '') if record[12] else None,
                'component_type': record[13].get('stringValue', '') if record[13] else None
            }
            hypotheses.append(hypothesis)
        
        logger.info(f"Retrieved {len(hypotheses)} hypotheses from database")
        
        return {
            "success": True,
            "hypotheses": hypotheses,
            "count": len(hypotheses),
            "filters": {
                "status": status_filter,
                "priority": priority_filter,
                "system_component_id": system_component_id
            },
            "message": f"Retrieved {len(hypotheses)} hypotheses"
        }
        
    except RuntimeError as e:
        logger.error(f"Database error getting hypotheses: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "hypotheses": [],
            "count": 0,
            "message": "Failed to get hypotheses from database"
        }
    except Exception as e:
        logger.error(f"Unexpected error getting hypotheses: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "hypotheses": [],
            "count": 0,
            "message": "Failed to get hypotheses from database"
        }

@tool
def batch_update_hypothesis_priorities(
    priority_updates: List[Dict[str, int]]
) -> Dict[str, Any]:
    """
    Batch update hypothesis priorities in a single database transaction.
    
    This tool significantly improves performance by updating all hypothesis priorities
    in one database call instead of making N individual update calls.
    
    Args:
        priority_updates: List of dictionaries with format:
                         [{"hypothesis_id": 1, "priority": 3}, 
                          {"hypothesis_id": 2, "priority": 1}, ...]
                         Each dict must have 'hypothesis_id' and 'priority' keys.
        
    Returns:
        Dict containing success status, update count, and any error information
    """
    logger.info(f"Batch updating priorities for {len(priority_updates)} hypotheses")
    
    try:
        if not priority_updates:
            logger.warning("No priority updates provided")
            return {
                "success": False,
                "error": "No priority updates provided",
                "updated_count": 0,
                "message": "No hypotheses to update"
            }
        
        # Validate input format
        for i, update in enumerate(priority_updates):
            if not isinstance(update, dict):
                raise ValueError(f"Update {i} is not a dictionary")
            if 'hypothesis_id' not in update or 'priority' not in update:
                raise ValueError(f"Update {i} missing required keys 'hypothesis_id' or 'priority'")
            if not isinstance(update['hypothesis_id'], int) or not isinstance(update['priority'], int):
                raise ValueError(f"Update {i} has non-integer values")
        
        # Build CASE statement for batch update
        case_statements = []
        hypothesis_ids = []
        parameters = []
        
        for i, update in enumerate(priority_updates):
            hypothesis_id = update['hypothesis_id']
            priority = update['priority']
            
            case_statements.append(f"WHEN :id_{i} THEN :priority_{i}")
            hypothesis_ids.append(str(hypothesis_id))
            
            parameters.append(format_parameter(f'id_{i}', hypothesis_id))
            parameters.append(format_parameter(f'priority_{i}', priority))
        
        # Create the batch update SQL
        ids_placeholder = ','.join([f':id_{i}' for i in range(len(priority_updates))])
        
        sql = f"""
        UPDATE hypothesis 
        SET priority = CASE id
            {' '.join(case_statements)}
            END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id IN ({ids_placeholder})
        """
        
        logger.debug(f"Executing batch UPDATE for {len(priority_updates)} hypotheses")
        response = execute_sql(sql, parameters)
        
        # Check how many rows were updated
        records_updated = response.get('numberOfRecordsUpdated', 0)
        
        if records_updated > 0:
            logger.info(f"Successfully batch updated {records_updated} hypothesis priorities")
            return {
                "success": True,
                "updated_count": records_updated,
                "requested_count": len(priority_updates),
                "message": f"Successfully updated {records_updated} hypothesis priorities"
            }
        else:
            logger.warning("No hypotheses were updated - check if hypothesis IDs exist")
            return {
                "success": False,
                "error": "No hypotheses were updated",
                "updated_count": 0,
                "requested_count": len(priority_updates),
                "message": "No hypotheses found with provided IDs"
            }
        
    except ValueError as e:
        logger.error(f"Validation error in batch update: {str(e)}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "updated_count": 0,
            "message": "Failed to validate batch update data"
        }
    except RuntimeError as e:
        logger.error(f"Database error in batch update: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "updated_count": 0,
            "message": "Database error during batch update"
        }
    except Exception as e:
        logger.error(f"Unexpected error in batch update: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "updated_count": 0,
            "message": "Failed to batch update hypothesis priorities"
        }

@tool
def batch_insert_hypotheses(
    hypotheses: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Batch insert multiple hypotheses in a single database transaction.
    
    This tool significantly improves performance by inserting all hypotheses
    in one database call instead of making N individual insert calls.
    
    Args:
        hypotheses: List of dictionaries with hypothesis data:
                   [{"title": "...", "description": "...", "persona": "...", 
                     "steady_state_description": "...", "failure_mode": "...", 
                     "status": "proposed", "priority": 1, "notes": "...", 
                     "system_component_id": 1}, ...]
                   Required keys: title
                   Optional keys: description, persona, steady_state_description, 
                                failure_mode, status, priority, notes, system_component_id
        
    Returns:
        Dict containing success status, inserted count, and hypothesis IDs
    """
    logger.info(f"Batch inserting {len(hypotheses)} hypotheses")
    
    try:
        if not hypotheses:
            logger.warning("No hypotheses provided for batch insert")
            return {
                "success": False,
                "error": "No hypotheses provided",
                "inserted_count": 0,
                "hypothesis_ids": [],
                "message": "No hypotheses to insert"
            }
        
        # Validate input format
        for i, hypothesis in enumerate(hypotheses):
            if not isinstance(hypothesis, dict):
                raise ValueError(f"Hypothesis {i} is not a dictionary")
            if 'title' not in hypothesis:
                raise ValueError(f"Hypothesis {i} missing required key 'title'")
            if not isinstance(hypothesis['title'], str) or not hypothesis['title'].strip():
                raise ValueError(f"Hypothesis {i} has invalid title")
        
        # Build batch INSERT with VALUES clause
        values_clauses = []
        parameters = []
        
        for i, hypothesis in enumerate(hypotheses):
            # Set defaults for optional fields
            title = hypothesis['title']
            description = hypothesis.get('description')
            persona = hypothesis.get('persona')
            steady_state_description = hypothesis.get('steady_state_description')
            failure_mode = hypothesis.get('failure_mode')
            status = hypothesis.get('status', 'proposed')
            priority = hypothesis.get('priority', 1)
            notes = hypothesis.get('notes')
            system_component_id = hypothesis.get('system_component_id')
            
            # Create parameter placeholders for this hypothesis
            values_clauses.append(f"(:title_{i}, :description_{i}, :persona_{i}, :steady_state_description_{i}, :failure_mode_{i}, :status_{i}, :priority_{i}, :notes_{i}, :system_component_id_{i})")
            
            # Add parameters for this hypothesis
            parameters.extend([
                format_parameter(f'title_{i}', title),
                format_parameter(f'description_{i}', description),
                format_parameter(f'persona_{i}', persona),
                format_parameter(f'steady_state_description_{i}', steady_state_description),
                format_parameter(f'failure_mode_{i}', failure_mode),
                format_parameter(f'status_{i}', status),
                format_parameter(f'priority_{i}', priority),
                format_parameter(f'notes_{i}', notes),
                format_parameter(f'system_component_id_{i}', system_component_id)
            ])
        
        # Create the batch insert SQL
        sql = f"""
        INSERT INTO hypothesis (
            title, description, persona, steady_state_description, 
            failure_mode, status, priority, notes, system_component_id
        )
        VALUES {', '.join(values_clauses)}
        RETURNING id
        """
        
        logger.debug(f"Executing batch INSERT for {len(hypotheses)} hypotheses")
        response = execute_sql(sql, parameters)
        
        # Extract hypothesis IDs from response
        hypothesis_ids = []
        records = response.get('records', [])
        
        for record in records:
            if record and len(record) > 0:
                hypothesis_id = record[0].get('longValue')
                if hypothesis_id:
                    hypothesis_ids.append(hypothesis_id)
        
        inserted_count = len(hypothesis_ids)
        
        if inserted_count > 0:
            logger.info(f"Successfully batch inserted {inserted_count} hypotheses")
            return {
                "success": True,
                "inserted_count": inserted_count,
                "requested_count": len(hypotheses),
                "hypothesis_ids": hypothesis_ids,
                "message": f"Successfully inserted {inserted_count} hypotheses"
            }
        else:
            logger.warning("No hypotheses were inserted")
            return {
                "success": False,
                "error": "No hypotheses were inserted",
                "inserted_count": 0,
                "hypothesis_ids": [],
                "requested_count": len(hypotheses),
                "message": "Failed to insert hypotheses"
            }
        
    except ValueError as e:
        logger.error(f"Validation error in batch insert: {str(e)}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "inserted_count": 0,
            "hypothesis_ids": [],
            "message": "Failed to validate batch insert data"
        }
    except RuntimeError as e:
        logger.error(f"Database error in batch insert: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "inserted_count": 0,
            "hypothesis_ids": [],
            "message": "Database error during batch insert"
        }
    except Exception as e:
        logger.error(f"Unexpected error in batch insert: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "inserted_count": 0,
            "hypothesis_ids": [],
            "message": "Failed to batch insert hypotheses"
        }
