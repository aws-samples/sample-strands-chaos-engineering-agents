"""
Experiment Design Agent

This agent focuses on:
1. Getting a hypothesis from the user
2. Retrieving AWS FIS documentation from knowledge base to verify schema
3. Generating a valid FIS template (without tools)
4. Saving the experiment to database
"""
from strands import Agent
from strands_tools import retrieve

# Import only the essential tools
from shared.experiments import insert_experiment, update_experiment
from shared.hypotheses import get_hypotheses
from shared.fis_role import get_fis_execution_role
from shared.config import get_default_model
from shared.observability import get_callback
from shared.analysis_results import get_resource_analysis
from strands.models import BedrockModel

# Load system prompt directly
from pathlib import Path
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

bedrock_model = BedrockModel(
    model_id=get_default_model(),
    additional_request_fields={
        "thinking": {
            "type": "enabled",
            "budget_tokens": 2048 # Minimum of 1,024
        }
    }
)

# Define the FIS expert agent with sliding window conversation manager
agent = Agent(
    model=bedrock_model,
    tools=[
        # Core tools for documentation lookup from knowledge base
        retrieve,
        
        # Database tools (from shared module)
        get_hypotheses,
        insert_experiment,
        update_experiment,

        # Analysis tools for accessing previous workload analysis
        get_resource_analysis,
        
        # FIS role tool
        get_fis_execution_role
    ],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=get_callback("experiment-design")
)

# Example usage function for testing
def run_example():
    """Example usage of the agent with database-first approach."""
    # Example natural language requests
    examples = [
        "Generate experiment for hypothesis ID 1",
        "Generate experiments for hypothesis IDs 1, 2",
        "Generate experiments for all ECS hypotheses",
        "Generate experiments for high priority hypotheses"
    ]
    
    print("Available example requests:")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    # Use the first example by default
    message = examples[0]
    print(f"\nRunning example: {message}")
    
    return agent(message)

if __name__ == "__main__":
    # Run the example
    result = run_example()
    print(result.message)
