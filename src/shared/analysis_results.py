"""
Analysis Results Database Tools

Essential tools for managing source code and AWS resource analysis results.
Only includes functions actually used by agents.
"""
from strands import tool
import logging
import json
from typing import Dict, Any, List, Optional
from .database_connection import execute_sql, format_parameter
from .json_utils import safe_json_parse

logger = logging.getLogger(__name__)

@tool
def insert_source_analysis(
    repository_url: str,
    framework_stack: Optional[List[str]] = None,
    aws_services_detected: Optional[List[str]] = None,
    infrastructure_patterns: Optional[Dict[str, str]] = None,
    deployment_methods: Optional[List[str]] = None,
    architectural_summary: Optional[str] = None,
    failure_points_analysis: Optional[str] = None,
    recommendations: Optional[str] = None
) -> Optional[int]:
    """Insert source code analysis results into the database."""
    logger.info(f"Inserting source code analysis for repository: {repository_url}")
    
    try:
        sql = """
        INSERT INTO source_code_analysis (
            repository_url, framework_stack, aws_services_detected, 
            infrastructure_patterns, deployment_methods,
            architectural_summary, failure_points_analysis, recommendations
        )
        VALUES (
            :repository_url, :framework_stack, :aws_services_detected,
            :infrastructure_patterns, :deployment_methods,
            :architectural_summary, :failure_points_analysis, :recommendations
        )
        RETURNING id
        """
        
        parameters = [
            format_parameter('repository_url', repository_url),
            format_parameter('framework_stack', json.dumps(framework_stack) if framework_stack else None, is_json=True),
            format_parameter('aws_services_detected', json.dumps(aws_services_detected) if aws_services_detected else None, is_json=True),
            format_parameter('infrastructure_patterns', json.dumps(infrastructure_patterns) if infrastructure_patterns else None, is_json=True),
            format_parameter('deployment_methods', json.dumps(deployment_methods) if deployment_methods else None, is_json=True),
            format_parameter('architectural_summary', architectural_summary),
            format_parameter('failure_points_analysis', failure_points_analysis),
            format_parameter('recommendations', recommendations)
        ]
        
        response = execute_sql(sql, parameters)
        analysis_id = response['records'][0][0]['longValue']
        logger.info(f"Successfully inserted source code analysis with ID: {analysis_id}")
        return analysis_id
        
    except Exception as e:
        logger.error(f"Error inserting source code analysis: {str(e)}")
        return None

@tool
def insert_resource_analysis(
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    aws_account_id: Optional[str] = None,
    region: Optional[str] = None,
    analysis_results: Optional[Dict[str, Any]] = None,
    deployment_status: str = 'unknown',
    resource_metadata: Optional[Dict[str, Any]] = None,
    **kwargs  # Accept legacy parameters but ignore them
) -> Optional[int]:
    """Insert AWS resource analysis with deployment filtering support."""
    logger.info(f"Inserting AWS resource analysis for {resource_type}: {resource_id}")
    
    try:
        sql = """
        INSERT INTO aws_resource_analysis (
            resource_type, resource_id, aws_account_id, region,
            analysis_results, deployment_status, resource_metadata
        )
        VALUES (
            :resource_type, :resource_id, :aws_account_id, :region,
            :analysis_results, :deployment_status, :resource_metadata
        )
        ON CONFLICT (resource_id) DO UPDATE SET
            analysis_results = EXCLUDED.analysis_results,
            deployment_status = EXCLUDED.deployment_status,
            resource_metadata = EXCLUDED.resource_metadata,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        parameters = [
            format_parameter('resource_type', resource_type),
            format_parameter('resource_id', resource_id),
            format_parameter('aws_account_id', aws_account_id),
            format_parameter('region', region),
            format_parameter('analysis_results', json.dumps(analysis_results) if analysis_results else None, is_json=True),
            format_parameter('deployment_status', deployment_status),
            format_parameter('resource_metadata', json.dumps(resource_metadata) if resource_metadata else None, is_json=True)
        ]
        
        response = execute_sql(sql, parameters)
        analysis_id = response['records'][0][0]['longValue']
        logger.info(f"Successfully inserted AWS resource analysis with ID: {analysis_id}")
        return analysis_id
        
    except Exception as e:
        logger.error(f"Error inserting AWS resource analysis: {str(e)}")
        return None

@tool
def get_source_analysis() -> Dict[str, Any]:
    """Get the latest source code analysis from the database."""
    logger.info("Getting latest source code analysis")
    
    try:
        sql = """
        SELECT id, repository_url, framework_stack, aws_services_detected,
               infrastructure_patterns, deployment_methods,
               architectural_summary, failure_points_analysis, recommendations,
               analysis_timestamp
        FROM source_code_analysis
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        
        response = execute_sql(sql)
        records = response.get('records', [])
        
        if not records:
            return {"success": False, "message": "No source code analysis found", "analysis": None}
        
        record = records[0]
        analysis = {
            'id': record[0].get('longValue'),
            'repository_url': record[1].get('stringValue', ''),
            'framework_stack': safe_json_parse(record[2], 'framework_stack', []),
            'aws_services_detected': safe_json_parse(record[3], 'aws_services_detected', []),
            'infrastructure_patterns': safe_json_parse(record[4], 'infrastructure_patterns', {}),
            'deployment_methods': safe_json_parse(record[5], 'deployment_methods', []),
            'architectural_summary': record[6].get('stringValue', '') if record[6] else None,
            'failure_points_analysis': record[7].get('stringValue', '') if record[7] else None,
            'recommendations': record[8].get('stringValue', '') if record[8] else None,
            'analysis_timestamp': record[9].get('stringValue', '')
        }
        
        return {"success": True, "message": "Source code analysis retrieved successfully", "analysis": analysis}
        
    except Exception as e:
        logger.error(f"Error getting source code analysis: {str(e)}")
        return {"success": False, "error": str(e), "message": "Failed to get source code analysis", "analysis": None}

@tool
def get_resource_analysis() -> Dict[str, Any]:
    """Get the latest AWS resource analysis from the database."""
    logger.info("Getting latest AWS resource analysis")
    
    try:
        sql = """
        SELECT id, aws_account_id, region, resource_metadata, analysis_timestamp
        FROM aws_resource_analysis
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        
        response = execute_sql(sql)
        records = response.get('records', [])
        
        if not records:
            return {"success": False, "message": "No AWS resource analysis found", "analysis": None}
        
        record = records[0]
        analysis = {
            'id': record[0].get('longValue'),
            'aws_account_id': record[1].get('stringValue', '') if record[1] else None,
            'region': record[2].get('stringValue', '') if record[2] else None,
            'resource_metadata': safe_json_parse(record[3], 'resource_metadata', {}),
            'analysis_timestamp': record[4].get('stringValue', '')
        }
        
        return {"success": True, "message": "AWS resource analysis retrieved successfully", "analysis": analysis}
        
    except Exception as e:
        logger.error(f"Error getting AWS resource analysis: {str(e)}")
        return {"success": False, "error": str(e), "message": "Failed to get AWS resource analysis", "analysis": None}
