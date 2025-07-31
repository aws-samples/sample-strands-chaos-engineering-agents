"""
Resource Filtering Tools

Tools for filtering and querying AWS resources based on deployment status.
Used by hypothesis generation agents to focus on deployed infrastructure.
"""
from strands import tool
import logging
from typing import Dict, Any
from .database_connection import execute_sql
from .json_utils import safe_json_parse

logger = logging.getLogger(__name__)

@tool
def get_deployed_resources() -> Dict[str, Any]:
    """Get only deployed AWS resources for hypothesis generation."""
    logger.info("Getting deployed AWS resources for hypothesis generation")
    
    try:
        sql = """
        SELECT resource_type, resource_id, resource_metadata, analysis_results,
               aws_account_id, region, created_at
        FROM aws_resource_analysis
        WHERE deployment_status = 'deployed'
        ORDER BY created_at DESC
        """
        
        response = execute_sql(sql)
        records = response.get('records', [])
        
        if not records:
            return {"success": False, "message": "No deployed resources found", "resources": []}
        
        deployed_resources = []
        for record in records:
            # Safely extract field values
            def get_field_value(field, default=''):
                return field.get('stringValue', default) if field and isinstance(field, dict) else default
            
            resource_metadata_raw = safe_json_parse(record[2], 'resource_metadata', {})
            analysis_results_raw = safe_json_parse(record[3], 'analysis_results', {})
            
            # Ensure we have dictionaries (type assertion for Pylance)
            resource_metadata: Dict[str, Any] = resource_metadata_raw if isinstance(resource_metadata_raw, dict) else {}
            analysis_results: Dict[str, Any] = analysis_results_raw if isinstance(analysis_results_raw, dict) else {}
            
            resource = {
                'resource_type': get_field_value(record[0]),
                'resource_id': get_field_value(record[1]),
                'resource_metadata': resource_metadata,
                'analysis_results': analysis_results,
                'aws_account_id': get_field_value(record[4]) or None,
                'region': get_field_value(record[5]) or None,
                'created_at': get_field_value(record[6]),
                # Extract key metadata for easy access
                'deployment_type': resource_metadata.get('deployment_type'),
                'namespace': resource_metadata.get('namespace'),  # Critical for EKS
                'cluster_name': resource_metadata.get('cluster_name')
            }
            deployed_resources.append(resource)
        
        # Group by deployment type for easier analysis
        resources_by_type = {}
        for resource in deployed_resources:
            resource_type = resource['resource_type']
            if resource_type not in resources_by_type:
                resources_by_type[resource_type] = []
            resources_by_type[resource_type].append(resource)
        
        return {
            "success": True,
            "message": f"Retrieved {len(deployed_resources)} deployed resources",
            "resources": deployed_resources,
            "resources_by_type": resources_by_type,
            "total_count": len(deployed_resources)
        }
        
    except Exception as e:
        logger.error(f"Error getting deployed resources: {str(e)}")
        return {"success": False, "error": str(e), "message": "Failed to get deployed resources", "resources": []}
