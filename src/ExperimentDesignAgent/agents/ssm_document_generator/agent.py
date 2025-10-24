"""
Systems Manager Document Generator Agent

Creates AWS Systems Manager documents for executing chaos engineering experiments
directly on EC2 operating systems. Supports both Windows and Linux platforms
with safety mechanisms and rollback procedures.
"""
from pathlib import Path
from strands import Agent, tool
from strands_tools import use_aws, retrieve

# Import shared utilities
from shared.config import get_small_model
from shared.observability import get_callback
from shared.resource_tags import get_workload_tags

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

@tool
def create_ssm_document(document_name: str, document_content: str, document_type: str = "Command") -> str:
    """
    Create an SSM document in AWS Systems Manager.
    
    Args:
        document_name: Name for the SSM document
        document_content: JSON content of the SSM document
        document_type: Type of SSM document (default: Command)
        
    Returns:
        Result of document creation
    """
    import json
    import boto3
    
    try:
        # Parse JSON to validate
        json.loads(document_content)
        
        # Create SSM client
        ssm = boto3.client('ssm')
        
        # Create the document
        response = ssm.create_document(
            Content=document_content,
            Name=document_name,
            DocumentType=document_type,
            DocumentFormat='JSON'
        )
        
        return f"Successfully created SSM document: {document_name}"
        
    except ssm.exceptions.DocumentAlreadyExists:
        return f"SSM document {document_name} already exists"
    except json.JSONDecodeError as e:
        return f"Invalid JSON content: {str(e)}"
    except Exception as e:
        return f"Error creating SSM document: {str(e)}"

@tool
def ssm_document_generator_agent(query: str) -> str:
    """
    Generate and create AWS Systems Manager documents for executing chaos engineering experiments
    directly on EC2 operating systems.
    
    Args:
        query: Request for SSM document generation (experiment type, target OS, etc.)
        
    Returns:
        Complete SSM document JSON with experiment logic, safety mechanisms, and rollback procedures
    """
    try:
        # Create the SSM document generator agent
        agent = Agent(
            model=get_small_model(),
            tools=[
                use_aws,
                retrieve,
                get_workload_tags,
                create_ssm_document
            ],
            system_prompt=SYSTEM_PROMPT + "\n\n**IMPORTANT**: After generating an SSM document, use the create_ssm_document tool to deploy it to AWS Systems Manager.",
            callback_handler=get_callback("ssm-document-generator")
        )
        
        # Execute the document generation
        response = agent(query)
        return str(response.message)
        
    except Exception as e:
        import traceback
        error_details = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc()
        }
        return f"Error in SSM document generation: {error_details['error_message']}\n\nError Type: {error_details['error_type']}\n\nFull traceback available in logs."

# Example usage function for testing
def run_example():
    """Example usage of the SSM document generator agent."""
    example_queries = [
        "Create a production-ready SSM document to interrupt Windows IIS web services with safety checks and automatic rollback",
        "Generate an SSM document to stop and restart IIS web server service on Windows with configurable intensity levels",
        "Create an SSM document to stress test CPU on Windows Server instances for 5 minutes",
        "Generate an SSM document for memory pressure testing on Linux instances"
    ]
    
    print("Available example queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    
    # Use the first example by default
    query = example_queries[0]
    print(f"\nRunning example: {query}")
    
    return ssm_document_generator_agent(query)

if __name__ == "__main__":
    # Run the example
    result = run_example()
    print(result)