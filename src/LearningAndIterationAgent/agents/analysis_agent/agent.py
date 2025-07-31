from shared.config import get_default_model
# Import Strands-native observability
from shared.observability import get_callback
"""
Analysis Agent

Specialized agent for analyzing experiment results and outcomes.
Focuses on extracting insights, identifying patterns, and understanding system behavior.
"""
from pathlib import Path
from strands import Agent, tool

# Import shared database tools
from shared.learning_insights import get_experiment_results, get_learning_history

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

# Create the analysis agent
analysis_agent = Agent(
    model=get_default_model(),
    tools=[
        get_experiment_results,
        get_learning_history
    ],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=get_callback("learning-analysis")
)

@tool
def analyze_experiment_outcomes(query: str) -> str:
    """
    Analyze the outcomes of a specific experiment to extract insights.
    
    Args:
        query: The analysis query containing experiment details and analysis requirements
        
    Returns:
        Comprehensive analysis of experiment outcomes, including:
        - Success/failure assessment
        - Observed system behavior
        - Comparison to expected behavior
        - Key insights and learnings
        - Implications for system resilience
    """
    try:
        # Pass the query directly to the existing agent
        response = analysis_agent(query)
        return str(response.message)
    except Exception as e:
        return f"Error analyzing experiment outcomes: {str(e)}"

@tool
def generate_improvement_recommendations(query: str) -> str:
    """
    Generate recommendations for improving system resilience based on experiment results.
    
    Args:
        query: The query containing experiment details and recommendation requirements
        
    Returns:
        Actionable recommendations for improving system resilience, including:
        - Architectural improvements
        - Configuration changes
        - Monitoring enhancements
        - Process improvements
        - Additional testing needed
    """
    try:
        # Pass the query directly to the existing agent
        response = analysis_agent(query)
        return str(response.message)
    except Exception as e:
        return f"Error generating improvement recommendations: {str(e)}"
