# STRANDS Agents Style Guide

This style guide provides comprehensive patterns and standards for creating new STRANDS agents based on the common patterns identified in the ExperimentDesignAgent and ExperimentsAgent implementations.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Agent Definition Pattern](#agent-definition-pattern)
3. [Tool Development Pattern](#tool-development-pattern)
4. [System Prompt Structure](#system-prompt-structure)
5. [Database Integration Pattern](#database-integration-pattern)
6. [AWS Integration Pattern](#aws-integration-pattern)
7. [Error Handling Standards](#error-handling-standards)
8. [Documentation Standards](#documentation-standards)
9. [Testing and Examples](#testing-and-examples)
10. [Best Practices](#best-practices)

## Project Structure

### Required File Structure
```
src/YourAgentName/
├── agent.py                    # Main agent implementation
├── system_prompt.md           # Agent system prompt and capabilities
├── README.md                 # Complete agent documentation
├── __init__.py               # Python package initialization
├── [domain]_tools.py         # Specialized tool files (multiple allowed)
├── database_tools.py         # Database operations (if needed)
```

### Dependency Management

**Consolidated Requirements**: All Python dependencies should be managed from a single `requirements.txt` file at the project root level, not in individual agent directories.

```
# Project root structure
/
├── requirements.txt           # Single consolidated requirements file
├── src/
│   ├── AgentOne/
│   │   ├── agent.py
│   │   └── ...
│   └── AgentTwo/
│       ├── agent.py
│       └── ...
```

**Benefits of consolidated requirements:**
- **Single Source of Truth**: All dependencies managed in one location
- **Version Consistency**: Prevents version conflicts between agents
- **Simplified Installation**: One `pip install -r requirements.txt` command
- **Easier Maintenance**: Updates and security patches applied consistently
- **Deployment Simplification**: Single requirements file for containerization

**Requirements Organization Pattern:**
```txt
# Core AWS and CLI tools
boto3>=1.34.0
awscli

# Strands Agents framework
strands-agents>=0.1.0
strands-agents-tools>=0.1.0
strands-agents-builder

# Configuration and data handling
pyyaml>=6.0

# Model Context Protocol
mcp

# Add other dependencies with appropriate version constraints
```

### File Naming Conventions
- **Agent directory**: PascalCase (e.g., `ExperimentDesignAgent`, `DataAnalysisAgent`)
- **Tool files**: snake_case with domain prefix (e.g., `fis_tools.py`, `database_tools.py`, `aws_resource_tools.py`)
- **Main files**: Standard names (`agent.py`, `system_prompt.md`, `README.md`)

## Agent Definition Pattern

### Standard Agent Implementation (`agent.py`)

```python
"""
[Agent Name] - Brief description

This agent focuses on:
1. Primary capability
2. Secondary capability  
3. Integration points
"""
from strands import Agent
from strands_tools import current_time, http_request  # Import standard tools as needed

# Import domain-specific tools with try/except for direct execution
try:
    from .domain_tools import tool1, tool2
    from .database_tools import db_tool1, db_tool2  # If database integration needed
except ImportError:
    # Handle direct execution
    from domain_tools import tool1, tool2
    from database_tools import db_tool1, db_tool2

# Load system prompt from external file
with open("system_prompt.md", 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

# Model configuration - choose the model that best fits your agent's needs
MODEL_NAME = "us.amazon.nova-pro-v1:0"  # Example model - change as needed
# Available model options to choose from:
# MODEL_NAME = "us.amazon.nova-lite-v1:0"     # For lighter workloads
# MODEL_NAME = "us.amazon.nova-micro-v1:0"    # For simple tasks
# MODEL_NAME = "anthropic.claude-3-5-sonnet-20241022-v2:0"  # For complex reasoning
# MODEL_NAME = "anthropic.claude-3-haiku-20240307-v1:0"     # For faster responses

# Define the agent with configurable model
agent = Agent(
    model=MODEL_NAME,
    tools=[
        # Core Strands tools (always include current_time)
        current_time,
        # Add other standard tools as needed: http_request, python_repl
        
        # Domain-specific tools (organized by category)
        tool1,
        tool2,
        
        # Database tools (if applicable)
        db_tool1,
        db_tool2
    ],
    system_prompt=SYSTEM_PROMPT
)

# Example usage function for testing
def run_example():
    """Example usage of the agent."""
    message = "Example input that demonstrates agent capabilities"
    
    return agent(message)

if __name__ == "__main__":
    # Run the example
    result = run_example()
    print(result.message)
```

### Key Patterns:
- **Import Pattern**: Use try/except for relative imports to support both module and direct execution
- **External Prompt**: Store system prompt in separate `.md` file for better maintainability
- **Model Selection**: Choose the model that best fits your agent's requirements and complexity
- **Tool Organization**: Group tools by category with clear comments
- **Example Function**: Always include `run_example()` for testing

## Tool Development Pattern

### Standard Tool Structure

```python
"""
[Domain] Tools for [Agent Name]
"""
from strands import tool
import boto3  # If AWS integration needed
import json
import logging
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError  # If AWS integration needed

# Set up logging (required for all tools)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Module-level constants and configuration
CONFIG_CONSTANTS = {
    "default_value": "example",
    "timeout": 30
}

@tool
def domain_action_tool(
    required_param: str,
    optional_param: Optional[str] = None,
    numeric_param: int = 10
) -> Dict[str, Any]:
    """
    Clear, concise description of what this tool does.
    
    Include practical usage information and any important constraints.
    
    Args:
        required_param: Clear description of required parameter
        optional_param: Description of optional parameter with default behavior
        numeric_param: Numeric parameter with reasonable default
        
    Returns:
        Dict containing structured result with success status and data
    """
    logger.info(f"Executing {tool.__name__} with {required_param}")
    logger.debug(f"Optional params - optional_param: {optional_param}, numeric_param: {numeric_param}")
    
    try:
        # Implementation logic here
        result_data = perform_operation(required_param, optional_param)
        
        logger.info(f"Successfully completed operation: {len(result_data)} items processed")
        
        return {
            "success": True,
            "data": result_data,
            "count": len(result_data) if isinstance(result_data, list) else 1,
            "message": f"Successfully processed {required_param}"
        }
        
    except ClientError as e:  # AWS-specific errors
        logger.error(f"AWS ClientError in {tool.__name__}: {str(e)}")
        return {
            "success": False,
            "error": f"AWS error: {str(e)}",
            "error_type": "client_error",
            "message": "Failed due to AWS service error"
        }
    except Exception as e:  # General errors
        logger.error(f"Unexpected error in {tool.__name__}: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "general_error", 
            "message": "Failed due to unexpected error"
        }

def perform_operation(param1: str, param2: Optional[str]) -> List[Dict[str, Any]]:
    """Helper function for complex logic (not a @tool)."""
    # Implementation details
    pass
```

### Tool Development Standards:
- **Logging**: Always include comprehensive logging (info, debug, error levels)
- **Type Hints**: Use complete type hints for all parameters and return values
- **Error Handling**: Distinguish between AWS/service errors and general errors
- **Return Format**: Standardized dict with `success`, `data`, and `message` fields
- **Documentation**: Clear docstrings with Args and Returns sections
- **Helper Functions**: Extract complex logic into non-tool helper functions

## System Prompt Structure

### Required System Prompt Sections (`system_prompt.md`)

```markdown
# [Agent Name] Agent

Brief description of the agent's purpose and specialization.

## Your Mission

**Clear, action-oriented mission statement** describing the agent's primary goal.

## Your Workflow

Numbered list of the agent's standard workflow:

1. **Step Name**: Description of what happens in this step
2. **Step Name**: Description with specific tool usage
3. **Step Name**: Description of validation or processing
4. **Final Step**: Description of completion and output

## Core Capabilities

- **Capability 1**: Description of key capability
- **Capability 2**: Description with tool reference
- **Integration Points**: How this agent works with other systems

## [Domain] Standards

### Specific Requirements for Your Domain
- **Requirement 1**: Clear requirement with justification
- **Requirement 2**: Requirement with examples
- **Quality Standards**: What constitutes good output

### Template/Configuration Standards (if applicable)
Specific standards for generated templates, configs, or structured output.

## Response Format

For each [agent operation]:
1. **Show input understanding** - what you understood from the user
2. **Reference sources** - what documentation/data you checked  
3. **Explain reasoning** - why you made specific choices
4. **Present results** - formatted output with proper structure
5. **Confirm completion** - status and next steps
6. **Provide guidance** - safety notes or recommendations

## Safety Guidelines

- **Safety Rule 1**: Specific safety constraint with rationale
- **Safety Rule 2**: What the agent should never do
- **Best Practices**: Recommended approaches for safe operation

## Error Handling

How the agent should handle various error scenarios:
- **Error Type 1**: Response strategy
- **Error Type 2**: Fallback approach
- **Escalation**: When to involve humans

## Example [Operation] Structure

```json
{
  "example": "structure",
  "showing": "expected output format"
}
```

**Remember**: Key principles that the agent should always follow.
```

### System Prompt Best Practices:
- **Clear Mission**: Single, focused mission statement
- **Numbered Workflow**: Step-by-step process the agent follows
- **Specific Standards**: Domain-specific requirements and quality criteria
- **Response Format**: Consistent structure for agent responses
- **Safety First**: Clear safety guidelines and constraints
- **Examples**: Concrete examples of expected output

## Database Integration Pattern

### Database Tools Structure (`database_tools.py`)

```python
"""
Database Tools for [Agent Name]
"""
from strands import tool
import json
import boto3
import logging
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Cache for stack outputs to avoid repeated API calls
_stack_outputs_cache = {}
STACK_NAME = 'YourStackName'  # Configure for your infrastructure
DATABASE_NAME = 'your_database'

def get_stack_outputs() -> Dict[str, str]:
    """Get CloudFormation stack outputs and cache them."""
    global _stack_outputs_cache
    
    if _stack_outputs_cache:
        return _stack_outputs_cache
    
    try:
        cf_client = boto3.client('cloudformation')
        response = cf_client.describe_stacks(StackName=STACK_NAME)
        
        if not response['Stacks']:
            raise Exception(f"Stack {STACK_NAME} not found")
        
        stack = response['Stacks'][0]
        outputs = stack.get('Outputs', [])
        
        # Convert outputs to a dictionary
        outputs_dict = {}
        for output in outputs:
            outputs_dict[output['OutputKey']] = output['OutputValue']
        
        _stack_outputs_cache = outputs_dict
        return outputs_dict
        
    except ClientError as e:
        raise Exception(f"Failed to get stack outputs for {STACK_NAME}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error retrieving stack outputs: {str(e)}")

def get_database_config() -> Dict[str, str]:
    """Get database configuration from CloudFormation stack outputs."""
    outputs = get_stack_outputs()
    
    cluster_arn = outputs.get('ClusterArn')
    secret_arn = outputs.get('SecretArn')
    
    if not cluster_arn:
        raise Exception("ClusterArn not found in stack outputs")
    if not secret_arn:
        raise Exception("SecretArn not found in stack outputs")
    
    return {
        'cluster_arn': cluster_arn,
        'secret_arn': secret_arn,
        'database_name': DATABASE_NAME
    }

def get_rds_data_client():
    """Get RDS Data API client."""
    return boto3.client('rds-data')

@tool
def database_operation_tool(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """
    Perform database operation with standardized error handling.
    
    Args:
        param1: Required parameter
        param2: Optional parameter
        
    Returns:
        Dict containing operation results
    """
    logger.info(f"Performing database operation: {param1}")
    
    try:
        client = get_rds_data_client()
        db_config = get_database_config()
        
        logger.debug(f"Using database cluster: {db_config['cluster_arn'][:50]}...")
        
        # SQL query
        sql = """
        SELECT column1, column2 
        FROM table_name 
        WHERE condition = :param1
        """
        
        parameters = [
            {'name': 'param1', 'value': {'stringValue': param1}}
        ]
        
        logger.debug("Executing SQL statement")
        response = client.execute_statement(
            resourceArn=db_config['cluster_arn'],
            secretArn=db_config['secret_arn'],
            database=db_config['database_name'],
            sql=sql,
            parameters=parameters
        )
        
        # Process response
        records = response.get('records', [])
        results = []
        
        for record in records:
            result = {
                'column1': record[0].get('stringValue', ''),
                'column2': record[1].get('longValue', 0)
            }
            results.append(result)
        
        logger.info(f"Successfully retrieved {len(results)} records")
        
        return {
            "success": True,
            "data": results,
            "count": len(results),
            "message": f"Retrieved {len(results)} records"
        }
        
    except ClientError as e:
        logger.error(f"AWS ClientError: {str(e)}")
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "message": "Failed to perform database operation"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "message": "Failed to perform database operation"
        }
```

### Database Integration Standards:
- **CloudFormation Integration**: Use stack outputs for configuration
- **Connection Caching**: Cache stack outputs to avoid repeated API calls
- **RDS Data API**: Use RDS Data API for serverless database access
- **Parameter Binding**: Always use parameterized queries
- **Error Distinction**: Separate AWS errors from general errors

## AWS Integration Pattern

### AWS Service Tools Structure

```python
"""
AWS [Service] Tools for [Agent Name]
"""
from strands import tool
import boto3
import logging
import os
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Service-specific constants - use environment variables for region
SERVICE_LIMITS = {
    'max_results': 100,
    'timeout': 30
}

@tool
def discover_aws_resources(
    resource_filter: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Discover AWS resources using read-only operations.
    
    This tool uses only read-only AWS API calls for safety.
    Region is automatically resolved by boto3 through the AWS credential chain.
    
    Args:
        resource_filter: Optional filters for resource discovery
        
    Returns:
        Dict containing discovered resources with detailed information
    """
    logger.info("Discovering AWS resources")
    if resource_filter:
        logger.debug(f"Applying filters: {resource_filter}")
    
    try:
        # Initialize AWS client - boto3 handles region resolution automatically
        client = boto3.client('service-name')
        region = client.meta.region_name  # Get region for logging/response
        
        # Use only read-only operations
        logger.debug("Executing read-only AWS API call")
        response = client.describe_resources()  # Use appropriate describe/list method
        
        # Process and structure the response
        resources = []
        for item in response.get('Resources', []):
            resource = {
                'id': item.get('ResourceId'),
                'arn': item.get('ResourceArn'), 
                'name': item.get('ResourceName'),
                'state': item.get('State'),
                'tags': item.get('Tags', []),
                'region': region
            }
            
            # Apply filters if provided
            if resource_filter and not matches_filter(resource, resource_filter):
                continue
                
            resources.append(resource)
        
        logger.info(f"Discovered {len(resources)} resources in {region}")
        
        return {
            "success": True,
            "resources": resources,
            "count": len(resources),
            "region": region,
            "message": f"Successfully discovered {len(resources)} resources"
        }
        
    except ClientError as e:
        logger.error(f"AWS ClientError discovering resources: {str(e)}")
        return {
            "success": False,
            "error": f"AWS service error: {str(e)}",
            "resources": [],
            "count": 0,
            "message": "Failed to discover AWS resources"
        }
    except Exception as e:
        logger.error(f"Unexpected error discovering resources: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "resources": [],
            "count": 0,
            "message": "Failed to discover AWS resources"
        }

def matches_filter(resource: Dict[str, Any], filter_criteria: Dict[str, str]) -> bool:
    """Helper function to check if resource matches filter criteria."""
    # Implementation for filtering logic
    pass
```

### AWS Integration Standards:
- **Read-Only Safety**: Use only `describe_*`, `list_*`, `get_*` operations
- **Environment-Based Region**: Use AWS_DEFAULT_REGION or AWS_REGION environment variables instead of hardcoded regions
- **Structured Returns**: Consistent resource data structure
- **Error Handling**: AWS-specific error handling with ClientError including configuration errors
- **Resource Limits**: Respect AWS service limits and pagination

### Environment Variable Best Practices:
- **Region Configuration**: Use `AWS_DEFAULT_REGION` or `AWS_REGION` environment variables
- **Credential Management**: Rely on AWS credential chain (environment, IAM roles, profiles)
- **Configuration Flexibility**: Allow runtime configuration without code changes
- **Error Handling**: Provide clear error messages when environment variables are missing
- **Documentation**: Document all required environment variables in README

## Error Handling Standards

### Standard Error Response Format

```python
# Success response
{
    "success": True,
    "data": result_data,
    "count": len(result_data),  # For collections
    "message": "Clear success message"
}

# Error response
{
    "success": False,
    "error": "Detailed error description",
    "error_type": "client_error|validation_error|general_error",
    "message": "User-friendly error message",
    "data": [],  # Empty or default value
    "count": 0   # For collections
}
```

### Error Handling Patterns:

1. **AWS Service Errors**:
   ```python
   except ClientError as e:
       logger.error(f"AWS ClientError: {str(e)}")
       return {
           "success": False,
           "error": f"AWS service error: {str(e)}",
           "error_type": "client_error"
       }
   ```

2. **Validation Errors**:
   ```python
   except ValueError as e:
       logger.error(f"Validation error: {str(e)}")
       return {
           "success": False,
           "error": f"Invalid input: {str(e)}",
           "error_type": "validation_error"
       }
   ```

3. **General Errors**:
   ```python
   except Exception as e:
       logger.error(f"Unexpected error: {str(e)}")
       return {
           "success": False,
           "error": f"Unexpected error: {str(e)}",
           "error_type": "general_error"
       }
   ```

## Documentation Standards

### README.md Structure

```markdown
# [AgentName]

Brief description of what the agent does and its primary use case.

## Features

- **Feature 1**: Description of key capability
- **Feature 2**: Description with technical details
- **Integration**: How it works with other systems

## Installation

Step-by-step installation instructions:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Agent

```python
from agent import agent

result = agent("Example input")
print(result.message)
```

### Interactive Usage

Multiple examples showing different use cases.

## Available Tools

Document each tool with:
- **`tool_name(...)`**: Purpose and usage
  - Parameter descriptions
  - Return value explanation

## Agent Workflow

Detailed explanation of the agent's workflow with examples.

## Configuration

Environment setup and configuration requirements.

## Requirements

- Technical requirements
- Dependencies
- Permissions needed

## File Structure

```
src/AgentName/
├── file1.py    # Description
├── file2.py    # Description
└── ...
```

## Contributing

Guidelines for extending the agent.
```

### Documentation Standards:
- **Clear Purpose**: Explain what the agent does and why
- **Complete Examples**: Show real usage examples
- **Tool Documentation**: Document all available tools
- **Configuration Guide**: Clear setup instructions
- **File Structure**: Explain the purpose of each file

## Testing and Examples

### Example Function Pattern

```python
def run_example():
    """Example usage of the agent."""
    # Example that demonstrates core functionality
    message = "Realistic example input that shows agent capabilities"
    
    result = agent(message)
    return result

def run_comprehensive_test():
    """Comprehensive test covering multiple scenarios."""
    test_cases = [
        "Simple test case",
        "Complex test case with multiple parameters",
        "Edge case or error scenario"
    ]
    
    results = []
    for test_case in test_cases:
        try:
            result = agent(test_case)
            results.append({
                "input": test_case,
                "success": True,
                "output": result.message
            })
        except Exception as e:
            results.append({
                "input": test_case,
                "success": False,
                "error": str(e)
            })
    
    return results

if __name__ == "__main__":
    # Run basic example
    print("=== Basic Example ===")
    result = run_example()
    print(result.message)
    
    # Run comprehensive test
    print("\n=== Comprehensive Test ===")
    test_results = run_comprehensive_test()
    for result in test_results:
        status = "✓" if result["success"] else "✗"
        print(f"{status} {result['input']}")
```

### Testing Standards:
- **Basic Example**: Simple example that demonstrates core functionality
- **Comprehensive Test**: Multiple test cases covering different scenarios
- **Error Testing**: Include test cases that may fail
- **Clear Output**: Formatted test results with success/failure indicators

## Best Practices

### Code Organization
- **Single Responsibility**: Each tool should have a single, clear purpose
- **Modular Design**: Separate concerns into different tool files
- **Clear Naming**: Use descriptive names for tools and functions
- **Consistent Patterns**: Follow the established patterns throughout

### Security and Safety
- **Read-Only Default**: Prefer read-only operations unless modification is explicitly required
- **Input Validation**: Validate all inputs before processing
- **Error Handling**: Always handle errors gracefully
- **Logging**: Comprehensive logging for debugging and monitoring

### Performance
- **Caching**: Cache expensive operations (like CloudFormation stack outputs)
- **Pagination**: Handle AWS API pagination properly
- **Timeouts**: Set reasonable timeouts for external calls
- **Resource Limits**: Respect service limits and quotas

### Integration
- **Standard Interfaces**: Use consistent interfaces between agents
- **Database Schema**: Follow established database patterns
- **Error Propagation**: Propagate errors with sufficient context
- **Status Tracking**: Track operation status for monitoring

### Maintenance
- **Documentation**: Keep documentation up-to-date with code changes
- **Version Compatibility**: Consider compatibility when updating dependencies
- **Backward Compatibility**: Maintain backward compatibility in tool interfaces
- **Deprecation**: Provide clear deprecation paths for obsolete functionality

## Quick Start Checklist

When creating a new STRANDS agent:

- [ ] Create directory structure following the standard pattern
- [ ] Implement `agent.py` with standard imports and structure
- [ ] Create `system_prompt.md` with all required sections
- [ ] Implement tools following the standard pattern
- [ ] Add comprehensive error handling and logging
- [ ] Create `requirements.txt` with necessary dependencies
- [ ] Write complete `README.md` documentation
- [ ] Add example usage functions
- [ ] Test with multiple scenarios
- [ ] Validate integration points (database, AWS, etc.)

## Common Pitfalls to Avoid

1. **Missing Error Handling**: Always include comprehensive error handling
2. **Inconsistent Return Formats**: Use the standard success/error response format
3. **Missing Logging**: Include logging at appropriate levels
4. **Hardcoded Values**: Use configuration constants instead of hardcoded values
5. **Missing Documentation**: Document all tools and their parameters
6. **Unsafe Operations**: Prefer read-only operations unless modification is required
7. **Poor Import Handling**: Use try/except for relative imports
8. **Missing Type Hints**: Always include complete type hints

## Support and Resources

- **Strands SDK Documentation**: [Link to official docs]
- **AWS SDK Documentation**: [Link to boto3 docs]
- **Example Agents**: Reference ExperimentDesignAgent and ExperimentsAgent
- **Team Standards**: Follow established team coding standards
- **Code Review**: Submit all new agents for peer review

---

This style guide should be treated as a living document and updated as new patterns emerge or requirements change.
