# Import Strands-native observability
from shared.observability import get_callback
"""
Workload Analysis Agent

Analyzes AWS workloads by coordinating source code analysis and AWS resource discovery.
Uses source_code_analysis_agent and aws_resource_analysis_agent as tools.
"""
from pathlib import Path
from strands import Agent, tool

# Import tool functions from other agents
from HypothesisGeneratorAgent.agents.source_code_analysis.agent import source_code_analysis_agent
from HypothesisGeneratorAgent.agents.aws_resource_analysis.agent import aws_resource_analysis_agent
from shared.config import get_default_model

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

@tool
def workload_analysis_agent(query: str) -> str:
    """
    Analyze AWS workloads by coordinating source code analysis and AWS resource discovery.
    
    Args:
        query: A workload analysis request with workload description and optional repository URL
        
    Returns:
        Comprehensive workload analysis including infrastructure patterns and failure points
    """
    try:
        # Create the workload analysis agent
        agent = Agent(
            model=get_default_model(),
            tools=[
                source_code_analysis_agent,
                aws_resource_analysis_agent
            ],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=get_callback("workload-analysis")
        )
        
        # Get response from the specialized agent
        response = agent(query)
        return str(response.message)
    except Exception as e:
        return f"Error in workload analysis: {str(e)}"
