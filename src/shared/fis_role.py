"""
FIS Role Configuration Tool

Provides access to the pre-generated FIS execution role ARN from CloudFormation exports.
"""
from strands import tool
import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

@tool
def get_fis_execution_role() -> Dict[str, Any]:
    """
    Get the pre-generated FIS execution role ARN from CloudFormation exports.
    
    Returns:
        Dict containing the FIS execution role ARN and name
    """
    try:
        cf_client = boto3.client('cloudformation')
        
        # Get the exported role ARN from CloudFormation
        exports = cf_client.list_exports()
        
        role_arn = None
        role_name = None
        
        for export in exports['Exports']:
            if export['Name'] == 'ChaosAgentFISExecutionRoleArn':
                role_arn = export['Value']
            elif export['Name'] == 'ChaosAgentFISExecutionRoleName':
                role_name = export['Value']
        
        if not role_arn:
            raise ValueError("FIS execution role ARN not found in CloudFormation exports. Deploy the ChaosAgentDatabaseStack to create the pre-generated FIS role.")
        
        return {
            "success": True,
            "role_arn": role_arn,
            "role_name": role_name or "ChaosAgentFISExecutionRole",
            "message": f"Retrieved pre-generated FIS execution role: {role_arn}"
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS ClientError getting FIS role: {error_code} - {error_message}")
        
        raise RuntimeError(f"AWS API error ({error_code}): {error_message}")
        
    except Exception as e:
        logger.error(f"Unexpected error getting FIS role: {str(e)}")
        raise RuntimeError(f"Failed to retrieve FIS execution role: {str(e)}")