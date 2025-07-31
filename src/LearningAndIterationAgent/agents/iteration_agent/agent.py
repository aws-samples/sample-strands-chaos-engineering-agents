from shared.config import get_default_model
# Import Strands-native observability
from shared.observability import get_callback
"""
Iteration Agent

Specialized agent for refining hypotheses and suggesting follow-up experiments.
Focuses on applying learnings to improve chaos engineering practices.
"""
from pathlib import Path
from strands import Agent, tool

# Import shared database tools
from shared.learning_insights import get_experiment_results, get_learning_history
from shared.hypotheses import get_hypotheses, update_hypothesis

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

# Create the iteration agent
iteration_agent = Agent(
    model=get_default_model(),
    tools=[
        get_experiment_results,
        get_hypotheses,
        update_hypothesis,
        get_learning_history
    ],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=get_callback("learning-iteration")
)

@tool
def refine_hypothesis(query: str) -> str:
    """
    Refine an existing hypothesis based on experiment results.
    
    Args:
        query: The query containing hypothesis ID, experiment ID, and refinement requirements
        
    Returns:
        Refined hypothesis with updated description, steady state, and failure mode
    """
    try:
        # Pass the query directly to the existing agent
        response = iteration_agent(query)
        return str(response.message)
    except Exception as e:
        return f"Error refining hypothesis: {str(e)}"

@tool
def suggest_follow_up_experiments(query: str) -> str:
    """
    Suggest follow-up experiments based on the results of a completed experiment.
    
    Args:
        query: The query containing experiment ID and requirements for follow-up experiments
        
    Returns:
        List of suggested follow-up experiments with rationale, including:
        - Experiment objectives
        - Failure scenarios to test
        - Expected outcomes
        - Relationship to original experiment
    """
    try:
        # Pass the query directly to the existing agent
        response = iteration_agent(query)
        return str(response.message)
    except Exception as e:
        return f"Error suggesting follow-up experiments: {str(e)}"
