from shared.config import get_default_model
# Import Strands-native observability
from shared.observability import get_callback
"""
AWS FIS Experiments Creation and Execution Agent

This agent focuses on:
1. Getting experiments from the database that are ready for creation
2. Discovering and validating AWS resources that match experiment targets using built-in AWS tools
3. Creating FIS experiments with validated resources
4. Optionally executing FIS experiments and monitoring completion
5. Updating experiment status in database throughout the process
"""
from strands import Agent
from strands_tools import current_time, python_repl, use_aws, retrieve

# Import tools
from shared.experiments import get_experiments, update_experiment
from shared.analysis_results import get_resource_analysis
from shared.config import get_aws_region
from shared.resource_tags import get_workload_tags
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
        # Core tools
        current_time,
        
        # Knowledge base tool for documentation lookup
        retrieve,
        
        # Database tools
        get_experiments,
        update_experiment,
        
        # Analysis tools for accessing previous workload analysis
        get_resource_analysis,
        
        # Configuration tools
        get_aws_region,
        
        # Resource tags tools
        get_workload_tags,
        
        # Built-in AWS tool for resource discovery and FIS experiment execution
        use_aws
    ],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=get_callback("experiments")
)

# Example usage function for testing
def run_example():
    """Example usage of the agent."""
    message = "Create and execute FIS experiments for all draft experiments in the database"
    
    return agent(message)

if __name__ == "__main__":
    # Run the example
    result = run_example()
    print(result.message)
