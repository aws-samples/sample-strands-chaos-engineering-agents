from shared.config import get_default_model
# Import Strands-native observability
from shared.observability import get_callback
"""
Learning and Iteration Agent

This agent focuses on:
1. Analyzing experiment results and outcomes
2. Learning from successful and failed experiments
3. Iterating on hypotheses based on learnings
4. Recommending improvements to chaos engineering practices
5. Building organizational knowledge from experiment data
"""
from pathlib import Path
from strands import Agent
from strands_tools import current_time

# Import tool functions from subagents
from LearningAndIterationAgent.agents.analysis_agent.agent import analyze_experiment_outcomes, generate_improvement_recommendations
from LearningAndIterationAgent.agents.iteration_agent.agent import refine_hypothesis, suggest_follow_up_experiments

# Import shared database tools
from shared.learning_insights import get_experiment_results, save_learning_insights, get_learning_history, update_hypothesis_status

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

# Define the learning and iteration agent
agent = Agent(
    model=get_default_model(),
    tools=[
        # Core tools
        current_time,
        
        # Database tools for retrieving experiment data
        get_experiment_results,
        save_learning_insights,
        get_learning_history,
        update_hypothesis_status,
        
        # Analysis tools for learning from experiments
        analyze_experiment_outcomes,
        generate_improvement_recommendations,
        
        # Iteration tools for refining hypotheses
        refine_hypothesis,
        suggest_follow_up_experiments
    ],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=get_callback("learning-iteration")
)

# Example usage function for testing
def run_example():
    """Example usage of the agent."""
    message = """
    Analyze the results from our recent ECS task restart experiments and provide insights 
    on what we learned about system resilience. Suggest improvements for future experiments.
    """
    
    return agent(message)

if __name__ == "__main__":
    # Run the example
    result = run_example()
    print(result.message)
