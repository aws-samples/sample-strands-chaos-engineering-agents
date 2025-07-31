"""
Hypothesis Generator Agent

Main agent that coordinates workload analysis and hypothesis generation.
Uses workload_analysis_agent, hypothesis_builder_agent, and source_code_analysis_agent as tools.
"""
from pathlib import Path
from strands import Agent, tool

# Import tool functions from agents - direct coordination without workload analysis middleman
from HypothesisGeneratorAgent.agents.hypothesis_builder.agent import hypothesis_builder_agent
from HypothesisGeneratorAgent.agents.source_code_analysis.agent import source_code_analysis_agent
from HypothesisGeneratorAgent.agents.aws_resource_analysis.agent import aws_resource_analysis_agent

# Import shared database tools
from shared.hypotheses import insert_hypothesis, get_hypotheses, update_hypothesis
from shared.analysis_results import get_source_analysis, get_resource_analysis
from shared.resource_tags import get_workload_tags
from shared.config import get_large_model

# Import observability
from shared.observability import get_callback

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()


@tool

def agent(query: str) -> str:
    """
    Generate chaos engineering hypotheses by coordinating workload analysis and hypothesis generation.
    
    Args:
        query: A natural language description of the AWS workload to analyze
        
    Returns:
        Comprehensive analysis and hypothesis generation results
    """
    try:
        
        # Create the main hypothesis generator agent with direct coordination
        hypothesis_agent = Agent(
            model=get_large_model(),
            tools=[
                source_code_analysis_agent,
                aws_resource_analysis_agent,
                hypothesis_builder_agent,
                get_workload_tags,
                get_source_analysis,
                get_resource_analysis
            ],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=get_callback("hypothesis-generator")
        )
        
        # Get response from the specialized agent
        response = hypothesis_agent(query)
        result = str(response.message)
        
        return result
        
    except Exception as e:
        return f"Error in hypothesis generation: {str(e)}"
