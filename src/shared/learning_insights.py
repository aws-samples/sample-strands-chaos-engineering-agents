"""
Learning Insights Database Tools

Tools for managing learning insights in the database.
"""
from strands import tool
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
try:
    from .database_connection import execute_sql, format_parameter
except ImportError:
    # Handle direct execution
    from database_connection import execute_sql, format_parameter

# Set up logging
logger = logging.getLogger(__name__)

@tool
def save_learning_insights(experiment_id: int, key_learnings: str, recommendations: str, 
                         refined_hypotheses: str, risk_assessment: str, 
                         knowledge_gaps: str, follow_up_experiments: str) -> Dict[str, Any]:
    """
    Save learning insights and recommendations to the database.
    
    Args:
        experiment_id: ID of the related experiment
        key_learnings: Main insights from the experiment
        recommendations: Actionable recommendations
        refined_hypotheses: Updated hypotheses based on findings
        risk_assessment: Updated risk understanding
        knowledge_gaps: Areas needing further investigation
        follow_up_experiments: Suggested follow-up experiments
    
    Returns:
        Dictionary indicating success or failure
    """
    logger.info(f"Saving learning insights for experiment ID: {experiment_id}")
    
    try:
        # Insert the learning insights
        sql = """
        INSERT INTO learning_insights (
            experiment_id, key_learnings, recommendations, refined_hypotheses,
            risk_assessment, knowledge_gaps, follow_up_experiments
        ) VALUES (
            :experiment_id, :key_learnings, :recommendations, :refined_hypotheses,
            :risk_assessment, :knowledge_gaps, :follow_up_experiments
        )
        """
        
        parameters = [
            format_parameter('experiment_id', experiment_id),
            format_parameter('key_learnings', key_learnings),
            format_parameter('recommendations', recommendations),
            format_parameter('refined_hypotheses', refined_hypotheses),
            format_parameter('risk_assessment', risk_assessment),
            format_parameter('knowledge_gaps', knowledge_gaps),
            format_parameter('follow_up_experiments', follow_up_experiments)
        ]
        
        response = execute_sql(sql, parameters)
        
        return {
            'success': True,
            'message': 'Learning insights saved successfully'
        }
        
    except RuntimeError as e:
        logger.error(f"Database error saving learning insights: {str(e)}")
        return {
            'success': False,
            'error': f'Failed to save learning insights: {str(e)}'
        }
    except Exception as e:
        logger.error(f"Unexpected error saving learning insights: {str(e)}")
        return {
            'success': False,
            'error': f'Failed to save learning insights: {str(e)}'
        }


@tool
def get_learning_history(days_back: int = 30) -> Dict[str, Any]:
    """
    Retrieve historical learning insights for trend analysis.
    
    Args:
        days_back: Number of days to look back (default: 30)
    
    Returns:
        Dictionary containing historical learning insights
    """
    logger.info(f"Retrieving learning history for past {days_back} days")
    
    try:
        # Calculate date threshold
        threshold_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
        
        sql = """
        SELECT li.*, e.title as experiment_title 
        FROM learning_insights li
        JOIN experiment e ON li.experiment_id = e.id
        WHERE li.created_at >= :threshold_date
        ORDER BY li.created_at DESC
        """
        
        parameters = [
            format_parameter('threshold_date', threshold_date)
        ]
        
        response = execute_sql(sql, parameters)
        
        # Convert response to readable format
        insights = []
        for record in response.get('records', []):
            if len(record) > 0:
                insight = {
                    'id': record[0].get('longValue'),
                    'experiment_id': record[1].get('longValue'),
                    'experiment_title': record[9].get('stringValue', ''),
                    'key_learnings': record[2].get('stringValue', ''),
                    'recommendations': record[3].get('stringValue', ''),
                    'refined_hypotheses': record[4].get('stringValue', ''),
                    'risk_assessment': record[5].get('stringValue', ''),
                    'knowledge_gaps': record[6].get('stringValue', ''),
                    'follow_up_experiments': record[7].get('stringValue', ''),
                    'created_at': record[8].get('stringValue', '')
                }
                insights.append(insight)
        
        return {
            'success': True,
            'insights': insights,
            'count': len(insights),
            'period_days': days_back
        }
        
    except RuntimeError as e:
        logger.error(f"Database error retrieving learning history: {str(e)}")
        return {
            'success': False,
            'error': f'Failed to retrieve learning history: {str(e)}'
        }
    except Exception as e:
        logger.error(f"Unexpected error retrieving learning history: {str(e)}")
        return {
            'success': False,
            'error': f'Failed to retrieve learning history: {str(e)}'
        }


@tool
def update_hypothesis_status(hypothesis_id: int, 
                           status: str, 
                           learning_notes: str) -> Dict[str, Any]:
    """
    Update hypothesis status based on experiment learnings.
    
    Args:
        hypothesis_id: ID of the hypothesis to update
        status: New status (proposed, prioritized, validated, refuted, needs_refinement)
        learning_notes: Notes about what was learned
    
    Returns:
        Dictionary indicating success or failure
    """
    logger.info(f"Updating hypothesis {hypothesis_id} status to '{status}'")
    
    try:
        # Import the update_hypothesis function from hypotheses.py
        from .hypotheses import update_hypothesis
        
        # Use the update_hypothesis function to update the status and notes
        success = update_hypothesis(
            hypothesis_id=hypothesis_id,
            status=status,
            notes=learning_notes
        )
        
        if success:
            return {
                'success': True,
                'hypothesis_id': hypothesis_id,
                'message': 'Hypothesis status updated successfully'
            }
        else:
            return {
                'success': False,
                'error': f'Failed to update hypothesis status'
            }
        
    except Exception as e:
        logger.error(f"Unexpected error updating hypothesis status: {str(e)}")
        return {
            'success': False,
            'error': f'Failed to update hypothesis status: {str(e)}'
        }


@tool
def get_experiment_results(experiment_id: Optional[int] = None, 
                         status: Optional[str] = None,
                         limit: int = 50) -> Dict[str, Any]:
    """
    Retrieve experiment results from the database for analysis.
    
    Args:
        experiment_id: Specific experiment ID to retrieve (optional)
        status: Filter by experiment status (optional)
        limit: Maximum number of results to return (default: 50)
    
    Returns:
        Dictionary containing experiment results and metadata
    """
    logger.info(f"Retrieving experiment results - ID: {experiment_id}, Status: {status}, Limit: {limit}")
    
    try:
        # Import the get_experiments function from experiments.py
        from .experiments import get_experiments
        
        # Use the get_experiments function with appropriate parameters
        if experiment_id:
            # For a specific experiment, we use hypothesis_id parameter
            result = get_experiments(
                hypothesis_id=None,  # Not filtering by hypothesis
                status_filter=status,
                limit=1 if experiment_id else limit
            )
            
            # Filter the results to get only the requested experiment
            if result['success'] and result['experiments']:
                experiments = [exp for exp in result['experiments'] if exp['id'] == experiment_id]
                result['experiments'] = experiments
                result['count'] = len(experiments)
                
            return result
        else:
            # For multiple experiments, just pass the status filter
            return get_experiments(
                status_filter=status,
                limit=limit
            )
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving experiment results: {str(e)}")
        return {
            'success': False,
            'error': f'Failed to retrieve experiment results: {str(e)}',
            'experiments': [],
            'count': 0
        }
