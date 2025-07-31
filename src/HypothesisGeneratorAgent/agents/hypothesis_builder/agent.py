from shared.config import get_large_model
# Import Strands-native observability
from shared.observability import get_callback
"""
Hypothesis Builder Agent

Generates chaos engineering hypotheses based on workload analysis.
Uses built-in tools and focuses on creating structured JSON hypotheses.
"""
from pathlib import Path
from strands import Agent, tool
from strands_tools import file_read, file_write
import sys
import os

# Add the shared directory to the path
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared')
sys.path.insert(0, shared_path)

# Import database tools
from shared.hypotheses import get_hypotheses, batch_insert_hypotheses
from shared.system_components import get_system_components, batch_insert_system_components
from shared.analysis_results import get_source_analysis, get_resource_analysis

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

@tool
def hypothesis_builder_agent(query: str) -> str:
    """
    Build chaos engineering hypotheses based on workload analysis.
    
    Args:
        query: A hypothesis building request with workload analysis results
        
    Returns:
        JSON array of structured chaos engineering hypotheses
    """
    try:
        # Create the hypothesis builder agent
        agent = Agent(
            model=get_large_model(),
            tools=[
                file_read,
                file_write,
                get_hypotheses, 
                batch_insert_hypotheses, 
                get_system_components, 
                batch_insert_system_components,
                get_source_analysis,
                get_resource_analysis
            ],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=get_callback("hypothesis-builder")
        )
        
        # Get response from the specialized agent
        response = agent(query)
        return str(response.message)
    except Exception as e:
        return f"Error in hypothesis generation: {str(e)}"
