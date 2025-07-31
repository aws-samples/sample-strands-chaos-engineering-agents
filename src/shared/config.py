"""
Centralized Configuration Management for Chaos Agent System

This module provides a single source of truth for AWS region and other global settings,
leveraging the CloudFormation stack location and supporting CLI/environment overrides.
"""
import os
import boto3
import logging
from typing import Dict, Optional
from botocore.exceptions import ClientError
from strands import tool

# Set up logging
logger = logging.getLogger(__name__)

# Global configuration cache
_config_cache = {}



def get_stack_region() -> str:
    """
    Get the AWS region where the CloudFormation stack is deployed.
    
    Returns:
        str: AWS region name where the stack is located
        
    Raises:
        RuntimeError: If stack region cannot be determined
    """
    try:
        # Import here to avoid circular imports
        from .database_connection import STACK_NAME
        
        # Use default session to get current region, then check if stack exists there
        session = boto3.Session()
        current_region = session.region_name
        
        if current_region:
            # Check if stack exists in current region
            cf_client = boto3.client('cloudformation', region_name=current_region)
            try:
                response = cf_client.describe_stacks(StackName=STACK_NAME)
                if response['Stacks']:
                    logger.info(f"Found stack {STACK_NAME} in region {current_region}")
                    return current_region
            except ClientError as e:
                if 'does not exist' not in str(e):
                    logger.warning(f"Error checking stack in {current_region}: {e}")
        
        # If not found in current region, try common regions
        common_regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
        
        for region in common_regions:
            if region == current_region:
                continue  # Already checked
                
            try:
                cf_client = boto3.client('cloudformation', region_name=region)
                response = cf_client.describe_stacks(StackName=STACK_NAME)
                if response['Stacks']:
                    logger.info(f"Found stack {STACK_NAME} in region {region}")
                    return region
            except ClientError:
                continue  # Stack not in this region
        
        # If stack not found anywhere, fall back to session region or default
        fallback_region = current_region or 'us-east-1'
        logger.warning(f"Stack {STACK_NAME} not found in any region, using fallback: {fallback_region}")
        return fallback_region
        
    except Exception as e:
        error_msg = f"Error determining stack region: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

def get_aws_region() -> str:
    """
    Get AWS region with precedence: CLI argument > Environment variable > Stack region > Default.
    
    Returns:
        str: AWS region name to use
    """
    global _config_cache
    
    # Check cache first
    if 'aws_region' in _config_cache:
        return _config_cache['aws_region']
    
    region = None
    
    # 1. Check if region was set via CLI (stored in environment by workflow)
    region = os.environ.get('CHAOS_AGENT_REGION')
    if region:
        logger.info(f"Using region from CLI/environment: {region}")
        _config_cache['aws_region'] = region
        return region
    
    # 2. Check standard AWS environment variables
    region = os.environ.get('AWS_DEFAULT_REGION') or os.environ.get('AWS_REGION')
    if region:
        logger.info(f"Using region from AWS environment variables: {region}")
        _config_cache['aws_region'] = region
        return region
    
    # 3. Try to get region from stack location
    try:
        region = get_stack_region()
        logger.info(f"Using region from stack location: {region}")
        _config_cache['aws_region'] = region
        return region
    except RuntimeError as e:
        logger.warning(f"Could not determine stack region: {e}")
    
    # 4. Final fallback
    region = 'us-east-1'
    logger.warning(f"Using default fallback region: {region}")
    _config_cache['aws_region'] = region
    return region



def set_region_override(region: str) -> None:
    """
    Set a region override (typically called from CLI).
    
    Args:
        region: AWS region name to use
    """
    global _config_cache
    
    # Validate region format (basic check)
    if not region or not isinstance(region, str):
        raise ValueError(f"Invalid region: {region}")
    
    # Store in cache only - don't modify environment
    _config_cache['aws_region'] = region
    
    logger.info(f"Region override set to: {region}")

def clear_config_cache() -> None:
    """Clear the configuration cache (useful for testing)."""
    global _config_cache
    _config_cache.clear()
    logger.debug("Configuration cache cleared")


# Model Configuration Functions

@tool
def get_default_model() -> str:
    """
    Get the default model ID for all agents with precedence: Environment > Default.
    
    Returns:
        str: Model ID to use for all agents
    """
    global _config_cache
    
    # Check cache first
    if 'default_model' in _config_cache:
        return _config_cache['default_model']
    
    # 1. Check environment variable
    model = os.environ.get('CHAOS_AGENT_MODEL')
    if model:
        logger.info(f"Using model from environment: {model}")
        _config_cache['default_model'] = model
        return model
    
    # 2. Default model (Sonnet for backward compatibility)
    default_model = 'us.anthropic.claude-3-7-sonnet-20250219-v1:0'
    logger.info(f"Using default model: {default_model}")
    _config_cache['default_model'] = default_model
    return default_model

@tool
def get_small_model() -> str:
    """
    Get the small/fast model ID for analysis tasks with precedence: Environment > Default.
    
    Returns:
        str: Small model ID optimized for speed and analysis tasks
    """
    global _config_cache
    
    # Check cache first
    if 'small_model' in _config_cache:
        return _config_cache['small_model']
    
    # 1. Check environment variable
    model = os.environ.get('CHAOS_AGENT_SMALL_MODEL')
    if model:
        logger.info(f"Using small model from environment: {model}")
        _config_cache['small_model'] = model
        return model
    
    # 2. Default small model (Claude 3.5 Haiku for fast analysis)
    small_model = 'us.anthropic.claude-3-5-haiku-20241022-v1:0'
    logger.info(f"Using default small model: {small_model}")
    _config_cache['small_model'] = small_model
    return small_model

@tool
def get_large_model() -> str:
    """
    Get the large/quality model ID for complex reasoning tasks with precedence: Environment > Default.
    
    Returns:
        str: Large model ID optimized for quality and complex reasoning
    """
    global _config_cache
    
    # Check cache first
    if 'large_model' in _config_cache:
        return _config_cache['large_model']
    
    # 1. Check environment variable
    model = os.environ.get('CHAOS_AGENT_LARGE_MODEL')
    if model:
        logger.info(f"Using large model from environment: {model}")
        _config_cache['large_model'] = model
        return model
    
    # 2. Default large model (Sonnet for quality reasoning)
    large_model = 'us.anthropic.claude-3-7-sonnet-20250219-v1:0'
    logger.info(f"Using default large model: {large_model}")
    _config_cache['large_model'] = large_model
    return large_model


# Observability Configuration Constants

# Set to False to disable all observability/logging
OBSERVABILITY_ENABLED = True

# Log level for all observability components
LOG_LEVEL = 'INFO'

# Log file pattern - use None to log to stderr only
LOG_FILE_PATTERN = 'chaos_agent_{agent_name}.log'

def is_observability_enabled() -> bool:
    """
    Check if observability/logging is enabled.
    
    Returns:
        bool: True if observability should be enabled
    """
    return OBSERVABILITY_ENABLED

def get_log_level() -> str:
    """
    Get the logging level.
    
    Returns:
        str: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    return LOG_LEVEL

def get_log_file_path(agent_name: str) -> Optional[str]:
    """
    Get the log file path for an agent.
    
    Args:
        agent_name: Name of the agent for log file naming
        
    Returns:
        Optional[str]: Log file path or None to use stderr
    """
    if LOG_FILE_PATTERN is None:
        return None
    return LOG_FILE_PATTERN.format(agent_name=agent_name)

def should_log_to_stdout() -> bool:
    """
    Check if structured logs should go to stdout instead of files.
    
    This is automatically enabled in container environments (Docker, Fargate, etc.)
    but can be overridden with the CHAOS_AGENT_LOG_TO_STDOUT environment variable.
    
    Returns:
        bool: True if structured logs should go to stdout
    """
    # Check for explicit override
    override = os.environ.get('CHAOS_AGENT_LOG_TO_STDOUT', '').lower()
    if override in ('true', '1', 'yes'):
        return True
    elif override in ('false', '0', 'no'):
        return False
    
    # Auto-detect container environment (default behavior)
    return False  # Let the observability system handle auto-detection
