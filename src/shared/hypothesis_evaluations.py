"""
Hypothesis Evaluation Database Tools

Tools for managing hypothesis evaluations in the database.
"""
from strands import tool
import logging
from typing import Dict, Any, List, Optional
from .database_connection import execute_sql, format_parameter

# Set up logging
logger = logging.getLogger(__name__)

@tool
def insert_hypothesis_evaluation(
    hypothesis_id: int,
    testability_score: int,
    specificity_score: int,
    realism_score: int,
    safety_score: int,
    learning_value_score: int,
    overall_score: float
) -> Dict[str, Any]:
    """
    Insert a new hypothesis evaluation into the database.
    
    Args:
        hypothesis_id: ID of the hypothesis being evaluated
        testability_score: Score for testability (1-5)
        specificity_score: Score for specificity (1-5)
        realism_score: Score for realism (1-5)
        safety_score: Score for safety (1-5)
        learning_value_score: Score for learning value (1-5)
        overall_score: Overall quality score (calculated average)
        
    Returns:
        Dict containing success status and evaluation ID
    """
    logger.info(f"Inserting evaluation for hypothesis ID: {hypothesis_id}")
    
    try:
        # Validate scores
        for score_name, score in [
            ("testability", testability_score),
            ("specificity", specificity_score),
            ("realism", realism_score),
            ("safety", safety_score),
            ("learning_value", learning_value_score)
        ]:
            if not isinstance(score, int) or score < 1 or score > 5:
                raise ValueError(f"{score_name}_score must be an integer between 1 and 5")
        
        if not isinstance(overall_score, (int, float)) or overall_score < 1 or overall_score > 5:
            raise ValueError("overall_score must be a number between 1 and 5")
        
        # Insert or update evaluation
        sql = """
        INSERT INTO hypothesis_evaluation (
            hypothesis_id, testability_score, specificity_score, realism_score,
            safety_score, learning_value_score, overall_score
        )
        VALUES (
            :hypothesis_id, :testability_score, :specificity_score, :realism_score,
            :safety_score, :learning_value_score, :overall_score
        )
        ON CONFLICT (hypothesis_id) DO UPDATE SET
            testability_score = EXCLUDED.testability_score,
            specificity_score = EXCLUDED.specificity_score,
            realism_score = EXCLUDED.realism_score,
            safety_score = EXCLUDED.safety_score,
            learning_value_score = EXCLUDED.learning_value_score,
            overall_score = EXCLUDED.overall_score,
            evaluation_timestamp = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        parameters = [
            format_parameter('hypothesis_id', hypothesis_id),
            format_parameter('testability_score', testability_score),
            format_parameter('specificity_score', specificity_score),
            format_parameter('realism_score', realism_score),
            format_parameter('safety_score', safety_score),
            format_parameter('learning_value_score', learning_value_score),
            format_parameter('overall_score', overall_score)
        ]
        
        logger.debug("Executing INSERT/UPDATE for hypothesis evaluation")
        response = execute_sql(sql, parameters)
        
        # Extract evaluation ID from response
        evaluation_id = response['records'][0][0]['longValue']
        logger.info(f"Successfully inserted/updated evaluation with ID: {evaluation_id}")
        
        return {
            "success": True,
            "evaluation_id": evaluation_id,
            "message": f"Successfully inserted/updated evaluation for hypothesis {hypothesis_id}"
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "message": "Failed to insert evaluation due to validation error"
        }
    except Exception as e:
        logger.error(f"Error inserting hypothesis evaluation: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to insert hypothesis evaluation"
        }

@tool
def batch_insert_hypothesis_evaluations(
    evaluations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Batch insert multiple hypothesis evaluations in a single database transaction.
    
    Args:
        evaluations: List of dictionaries with evaluation data:
                    [{"hypothesis_id": 1, 
                      "testability_score": 4,
                      "specificity_score": 3,
                      "realism_score": 5,
                      "safety_score": 4,
                      "learning_value_score": 3,
                      "overall_score": 3.8}, ...]
        
    Returns:
        Dict containing success status and inserted count
    """
    logger.info(f"Batch inserting {len(evaluations)} hypothesis evaluations")
    
    try:
        if not evaluations:
            logger.warning("No evaluations provided for batch insert")
            return {
                "success": False,
                "error": "No evaluations provided",
                "inserted_count": 0,
                "message": "No evaluations to insert"
            }
        
        # Validate input format
        for i, evaluation in enumerate(evaluations):
            if not isinstance(evaluation, dict):
                raise ValueError(f"Evaluation {i} is not a dictionary")
            
            required_keys = ['hypothesis_id', 'testability_score', 'specificity_score', 
                            'realism_score', 'safety_score', 'learning_value_score', 'overall_score']
            
            for key in required_keys:
                if key not in evaluation:
                    raise ValueError(f"Evaluation {i} missing required key '{key}'")
            
            # Validate score ranges
            for score_key in required_keys[1:-1]:  # All score keys except hypothesis_id and overall_score
                score = evaluation[score_key]
                if not isinstance(score, int) or score < 1 or score > 5:
                    raise ValueError(f"Evaluation {i}: {score_key} must be an integer between 1 and 5")
            
            overall_score = evaluation['overall_score']
            if not isinstance(overall_score, (int, float)) or overall_score < 1 or overall_score > 5:
                raise ValueError(f"Evaluation {i}: overall_score must be a number between 1 and 5")
        
        # Build batch UPSERT with VALUES clause
        values_clauses = []
        parameters = []
        
        for i, evaluation in enumerate(evaluations):
            # Create parameter placeholders for this evaluation
            values_clauses.append(f"(:hypothesis_id_{i}, :testability_score_{i}, :specificity_score_{i}, :realism_score_{i}, :safety_score_{i}, :learning_value_score_{i}, :overall_score_{i})")
            
            # Add parameters for this evaluation
            parameters.extend([
                format_parameter(f'hypothesis_id_{i}', evaluation['hypothesis_id']),
                format_parameter(f'testability_score_{i}', evaluation['testability_score']),
                format_parameter(f'specificity_score_{i}', evaluation['specificity_score']),
                format_parameter(f'realism_score_{i}', evaluation['realism_score']),
                format_parameter(f'safety_score_{i}', evaluation['safety_score']),
                format_parameter(f'learning_value_score_{i}', evaluation['learning_value_score']),
                format_parameter(f'overall_score_{i}', evaluation['overall_score'])
            ])
        
        # Create the batch upsert SQL
        sql = f"""
        INSERT INTO hypothesis_evaluation (
            hypothesis_id, testability_score, specificity_score, realism_score,
            safety_score, learning_value_score, overall_score
        )
        VALUES {', '.join(values_clauses)}
        ON CONFLICT (hypothesis_id) DO UPDATE SET
            testability_score = EXCLUDED.testability_score,
            specificity_score = EXCLUDED.specificity_score,
            realism_score = EXCLUDED.realism_score,
            safety_score = EXCLUDED.safety_score,
            learning_value_score = EXCLUDED.learning_value_score,
            overall_score = EXCLUDED.overall_score,
            evaluation_timestamp = CURRENT_TIMESTAMP
        """
        
        logger.debug(f"Executing batch UPSERT for {len(evaluations)} evaluations")
        response = execute_sql(sql, parameters)
        
        # Check how many rows were affected
        records_affected = response.get('numberOfRecordsUpdated', 0)
        
        logger.info(f"Successfully batch inserted/updated {records_affected} evaluations")
        return {
            "success": True,
            "inserted_count": records_affected,
            "requested_count": len(evaluations),
            "message": f"Successfully inserted/updated {records_affected} evaluations"
        }
        
    except ValueError as e:
        logger.error(f"Validation error in batch insert: {str(e)}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "inserted_count": 0,
            "message": "Failed to validate batch insert data"
        }
    except Exception as e:
        logger.error(f"Error in batch insert: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "inserted_count": 0,
            "message": "Failed to batch insert evaluations"
        }

@tool
def get_hypothesis_evaluations(
    hypothesis_ids: Optional[List[int]] = None,
    min_overall_score: Optional[float] = None,
    max_overall_score: Optional[float] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get hypothesis evaluations from the database with flexible filtering options.
    
    Args:
        hypothesis_ids: Optional list of specific hypothesis IDs to retrieve evaluations for
        min_overall_score: Optional minimum overall score filter
        max_overall_score: Optional maximum overall score filter
        limit: Maximum number of evaluations to return
        
    Returns:
        Dict containing list of evaluations and query metadata
    """
    logger.info(f"Getting hypothesis evaluations with filters - IDs: {hypothesis_ids}, score range: {min_overall_score}-{max_overall_score}")
    
    try:
        # Build SQL query with optional filters
        where_conditions = []
        parameters = []
        
        # Handle specific hypothesis IDs
        if hypothesis_ids:
            placeholders = ','.join([f':id_{i}' for i in range(len(hypothesis_ids))])
            where_conditions.append(f"he.hypothesis_id IN ({placeholders})")
            for i, hyp_id in enumerate(hypothesis_ids):
                parameters.append(format_parameter(f'id_{i}', hyp_id))
        
        # Handle score range filters
        if min_overall_score is not None:
            where_conditions.append("he.overall_score >= :min_score")
            parameters.append(format_parameter('min_score', min_overall_score))
        
        if max_overall_score is not None:
            where_conditions.append("he.overall_score <= :max_score")
            parameters.append(format_parameter('max_score', max_overall_score))
        
        # Base query with joins to get hypothesis information
        base_sql = """
        SELECT he.id, he.hypothesis_id, h.title as hypothesis_title,
               he.testability_score, he.specificity_score, he.realism_score,
               he.safety_score, he.learning_value_score, he.overall_score,
               he.evaluation_timestamp
        FROM hypothesis_evaluation he
        JOIN hypothesis h ON he.hypothesis_id = h.id
        """
        
        if where_conditions:
            sql = base_sql + " WHERE " + " AND ".join(where_conditions)
        else:
            sql = base_sql
        
        sql += " ORDER BY he.overall_score DESC LIMIT :limit"
        parameters.append(format_parameter('limit', limit))
        
        logger.debug("Executing SQL SELECT for hypothesis evaluations")
        response = execute_sql(sql, parameters)
        
        # Parse the response
        evaluations = []
        records = response.get('records', [])
        
        for record in records:
            evaluation = {
                'id': record[0].get('longValue'),
                'hypothesis_id': record[1].get('longValue'),
                'hypothesis_title': record[2].get('stringValue', ''),
                'testability_score': record[3].get('longValue'),
                'specificity_score': record[4].get('longValue'),
                'realism_score': record[5].get('longValue'),
                'safety_score': record[6].get('longValue'),
                'learning_value_score': record[7].get('longValue'),
                'overall_score': float(record[8].get('doubleValue', 0)),
                'evaluation_timestamp': record[9].get('stringValue', '')
            }
            evaluations.append(evaluation)
        
        logger.info(f"Retrieved {len(evaluations)} evaluations from database")
        
        return {
            "success": True,
            "evaluations": evaluations,
            "count": len(evaluations),
            "filters": {
                "hypothesis_ids": hypothesis_ids,
                "min_overall_score": min_overall_score,
                "max_overall_score": max_overall_score
            },
            "message": f"Retrieved {len(evaluations)} evaluations"
        }
        
    except Exception as e:
        logger.error(f"Error getting hypothesis evaluations: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "evaluations": [],
            "count": 0,
            "message": "Failed to get evaluations from database"
        }
