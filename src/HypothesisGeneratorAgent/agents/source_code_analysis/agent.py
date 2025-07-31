from shared.config import get_small_model
# Import Strands-native observability
from shared.observability import get_callback
"""
Source Code Analysis Agent

Analyzes source code repositories to understand infrastructure patterns and AWS service usage.
Uses built-in tools like http_request to fetch and analyze repository content.
"""
import os
from pathlib import Path
from strands import Agent, tool
from strands_tools import http_request, shell, file_read

# Import database tools
import sys
sys.path.append('/Users/fisherrn/projects/chaos-agent/src')
from shared.analysis_results import insert_source_analysis

# Bypass tool consent for shell commands
os.environ["BYPASS_TOOL_CONSENT"] = "true"

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

@tool
def source_code_analysis_agent(query: str) -> str:
    """
    Analyze source code repositories to understand infrastructure patterns and AWS service usage.
    
    Args:
        query: A source code analysis request with repository URL
        
    Returns:
        Detailed source code analysis including infrastructure patterns and AWS service usage
    """
    try:
        # Create the source code analysis agent
        agent = Agent(
            model=get_small_model(),
            tools=[
                http_request,
                shell,
                file_read,
                insert_source_analysis
            ],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=get_callback("source-code-analysis")
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
        return f"Error in source code analysis: {error_details['error_message']}\n\nError Type: {error_details['error_type']}\n\nFull traceback available in logs."
