import json
import boto3
import logging
from typing import Dict, Any
import time

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Custom resource handler to sync knowledge base data sources.
    This function triggers ingestion jobs for all data sources in a knowledge base.
    Handles both CDK deployment triggers and scheduled EventBridge refreshes.
    """
    logger.info(f"Received event: {json.dumps(event, default=str)}")
    
    try:
        # Handle EventBridge scheduled events (direct Lambda invocation)
        if 'RequestType' in event and 'ResourceProperties' in event:
            # This is a custom resource or EventBridge event formatted as custom resource
            request_type = event['RequestType']
            resource_properties = event['ResourceProperties']
            trigger_type = resource_properties.get('TriggerType', 'Deployment')
            
            logger.info(f"Processing {trigger_type.lower()} trigger")
            
        else:
            # This shouldn't happen with our current setup, but handle gracefully
            logger.error("Unexpected event format")
            return {
                'statusCode': 400,
                'body': json.dumps('Unexpected event format')
            }
        
        knowledge_base_id = resource_properties.get('KnowledgeBaseId')
        data_source_ids = resource_properties.get('DataSourceIds', [])
        
        if not knowledge_base_id:
            raise ValueError("KnowledgeBaseId is required")
        
        if not data_source_ids:
            raise ValueError("DataSourceIds list is required")
        
        # Initialize Bedrock client
        bedrock_agent = boto3.client('bedrock-agent')
        
        response_data = {}
        
        if request_type in ['Create', 'Update']:
            logger.info(f"Starting sync for knowledge base: {knowledge_base_id}")
            
            # Start ingestion jobs for each data source
            ingestion_jobs = []
            
            for data_source_id in data_source_ids:
                try:
                    logger.info(f"Starting ingestion job for data source: {data_source_id}")
                    
                    # Determine description based on trigger type
                    if trigger_type == 'Scheduled':
                        description = f"Scheduled refresh of knowledge base documentation"
                    else:
                        description = f"Automated sync triggered by CDK deployment"
                    
                    # Start the ingestion job
                    response = bedrock_agent.start_ingestion_job(
                        knowledgeBaseId=knowledge_base_id,
                        dataSourceId=data_source_id,
                        description=description
                    )
                    
                    ingestion_job_id = response['ingestionJob']['ingestionJobId']
                    ingestion_jobs.append({
                        'dataSourceId': data_source_id,
                        'ingestionJobId': ingestion_job_id,
                        'status': 'STARTED'
                    })
                    
                    logger.info(f"Started ingestion job {ingestion_job_id} for data source {data_source_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to start ingestion job for data source {data_source_id}: {str(e)}")
                    ingestion_jobs.append({
                        'dataSourceId': data_source_id,
                        'ingestionJobId': None,
                        'status': 'FAILED',
                        'error': str(e)
                    })
            
            # Wait a bit and check initial status
            time.sleep(5)
            
            # Check status of ingestion jobs
            for job in ingestion_jobs:
                if job['ingestionJobId']:
                    try:
                        status_response = bedrock_agent.get_ingestion_job(
                            knowledgeBaseId=knowledge_base_id,
                            dataSourceId=job['dataSourceId'],
                            ingestionJobId=job['ingestionJobId']
                        )
                        job['status'] = status_response['ingestionJob']['status']
                        
                        if 'statistics' in status_response['ingestionJob']:
                            job['statistics'] = status_response['ingestionJob']['statistics']
                            
                    except Exception as e:
                        logger.error(f"Failed to get status for ingestion job {job['ingestionJobId']}: {str(e)}")
                        job['status'] = 'UNKNOWN'
                        job['error'] = str(e)
            
            successful_jobs = len([j for j in ingestion_jobs if j['status'] not in ['FAILED', 'UNKNOWN']])
            message = f"Started {successful_jobs} ingestion jobs"
            
            response_data = {
                'KnowledgeBaseId': knowledge_base_id,
                'IngestionJobs': ingestion_jobs,
                'Message': message
            }
            
        elif request_type == 'Delete':
            logger.info("Delete request - no action needed for knowledge base sync")
            response_data = {
                'Message': 'Knowledge base sync custom resource deleted successfully'
            }
        
        # Return success response
        return {
            'Status': 'SUCCESS',
            'PhysicalResourceId': f"kb-sync-{knowledge_base_id}",
            'Data': response_data,
            'Reason': 'Knowledge base sync completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error in knowledge base sync: {str(e)}")
        
        # Return failure response
        return {
            'Status': 'FAILED',
            'PhysicalResourceId': event.get('PhysicalResourceId', 'kb-sync-failed'),
            'Data': {},
            'Reason': f'Knowledge base sync failed: {str(e)}'
        }


def get_data_source_ids(bedrock_agent, knowledge_base_id: str) -> list:
    """
    Helper function to get all data source IDs for a knowledge base.
    """
    try:
        response = bedrock_agent.list_data_sources(
            knowledgeBaseId=knowledge_base_id
        )
        
        data_source_ids = []
        for data_source in response.get('dataSourceSummaries', []):
            data_source_ids.append(data_source['dataSourceId'])
        
        return data_source_ids
        
    except Exception as e:
        logger.error(f"Failed to list data sources for knowledge base {knowledge_base_id}: {str(e)}")
        return []
