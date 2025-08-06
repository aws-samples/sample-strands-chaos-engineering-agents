from shared.config import get_small_model
# Import Strands-native observability
from shared.observability import get_callback
"""
AWS Resource Analysis Agent

Discovers and analyzes deployed AWS resources using the built-in use_aws tool.
Identifies architecture patterns, service dependencies, and potential failure points.
"""
from pathlib import Path
from strands import Agent, tool
from strands_tools import use_aws, shell

# Import database tools
import sys
from shared.analysis_results import insert_resource_analysis, get_source_analysis
from shared.resource_filtering import get_deployed_resources
from shared.resource_tags import get_workload_tags

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

@tool
def aws_resource_analysis_agent(query: str) -> str:
    """
    Discover and analyze deployed AWS resources for chaos engineering purposes.
    
    Args:
        query: An AWS resource analysis request
        
    Returns:
        AWS resource analysis results including discovered resources and potential failure points
    """
    try:
        # Create the AWS resource analysis agent
        agent = Agent(
            model=get_small_model(),
            tools=[
                use_aws,
                shell,
                insert_resource_analysis,
                get_workload_tags,
                get_source_analysis,
                get_deployed_resources
            ],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=get_callback("aws-resource-analysis")
        )
        
        # Get response from the specialized agent
        response = agent(query)
        return str(response.message)
    except Exception as e:
        import traceback
        error_details = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc()
        }
        return f"Error in AWS resource analysis: {error_details['error_message']}\n\nError Type: {error_details['error_type']}\n\nFull traceback available in logs."
