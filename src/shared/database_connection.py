"""
Shared Database Connection Utilities for Chaos Agent System

This module provides common database connection functionality that can be used across all agents
to eliminate code duplication and ensure consistent database access patterns.
"""
import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger(__name__)

# Cache for stack outputs to avoid repeated API calls
_stack_outputs_cache = {}
STACK_NAME = 'ChaosAgentDatabaseStack'
DATABASE_NAME = 'chaosagent'




def get_stack_outputs() -> Dict[str, str]:
    """
    Get CloudFormation stack outputs and cache them.
    
    Returns:
        Dict containing stack outputs
        
    Raises:
        RuntimeError: If stack outputs cannot be retrieved
    """
    global _stack_outputs_cache
    
    if _stack_outputs_cache:
        return _stack_outputs_cache
    
    try:
        cf_client = boto3.client('cloudformation')
        response = cf_client.describe_stacks(StackName=STACK_NAME)
        
        if not response['Stacks']:
            raise RuntimeError(f"Stack {STACK_NAME} not found")
        
        stack = response['Stacks'][0]
        outputs = stack.get('Outputs', [])
        
        # Convert outputs to a dictionary
        outputs_dict = {}
        for output in outputs:
            outputs_dict[output['OutputKey']] = output['OutputValue']
        
        _stack_outputs_cache = outputs_dict
        logger.info(f"Successfully cached stack outputs for {STACK_NAME}")
        return outputs_dict
        
    except ClientError as e:
        error_msg = f"Failed to get stack outputs for {STACK_NAME}: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Error retrieving stack outputs: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

def get_database_config() -> Dict[str, str]:
    """
    Get database configuration from CloudFormation stack outputs.
    
    Returns:
        Dict containing database configuration (cluster_arn, secret_arn, database_name)
        
    Raises:
        ValueError: If required configuration is missing
    """
    outputs = get_stack_outputs()
    
    # Map the CDK output names to our configuration
    cluster_arn = outputs.get('ClusterArn')
    secret_arn = outputs.get('SecretArn')
    
    if not cluster_arn:
        raise ValueError("ClusterArn not found in stack outputs")
    if not secret_arn:
        raise ValueError("SecretArn not found in stack outputs")
    
    return {
        'cluster_arn': cluster_arn,
        'secret_arn': secret_arn,
        'database_name': DATABASE_NAME
    }

def get_rds_data_client():
    """
    Get RDS Data API client.
    
    Returns:
        boto3 RDS Data API client
    """
    return boto3.client('rds-data')

def execute_sql(sql: str, parameters: list = None) -> Dict[str, Any]:
    """
    Execute a SQL statement using the RDS Data API.
    
    Args:
        sql: SQL statement to execute
        parameters: Optional list of parameters for the SQL statement
        
    Returns:
        Dict containing the response from RDS Data API
        
    Raises:
        RuntimeError: If SQL execution fails
    """
    try:
        client = get_rds_data_client()
        db_config = get_database_config()
        
        execute_params = {
            'resourceArn': db_config['cluster_arn'],
            'secretArn': db_config['secret_arn'],
            'database': db_config['database_name'],
            'sql': sql
        }
        
        if parameters:
            execute_params['parameters'] = parameters
        
        logger.debug(f"Executing SQL: {sql[:100]}...")
        response = client.execute_statement(**execute_params)
        logger.debug(f"SQL execution successful")
        
        return response
        
    except ClientError as e:
        error_msg = f"Database error executing SQL: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error executing SQL: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

def format_parameter(name: str, value: Any, is_json: bool = False) -> Dict[str, Any]:
    """
    Format a parameter for RDS Data API.
    
    Args:
        name: Parameter name
        value: Parameter value
        is_json: Whether the parameter should be treated as JSON/JSONB
        
    Returns:
        Dict formatted for RDS Data API parameters
    """
    param = {'name': name}
    
    if value is None:
        param['value'] = {'isNull': True}
    elif isinstance(value, bool):
        param['value'] = {'booleanValue': value}
    elif isinstance(value, int):
        param['value'] = {'longValue': value}
    elif isinstance(value, float):
        param['value'] = {'doubleValue': value}
    elif is_json:
        # For JSONB columns, we need to cast the string value to JSONB in SQL
        param['value'] = {'stringValue': str(value)}
        param['typeHint'] = 'JSON'
    else:
        param['value'] = {'stringValue': str(value)}
    
    return param
