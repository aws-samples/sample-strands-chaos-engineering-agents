"""
Systems Manager Inventory Analysis Agent

Analyzes AWS Systems Manager inventory data to catalog what software, applications, 
and configurations are installed on online EC2 instances that are actively reporting 
to SSM inventory. Focuses exclusively on instances with PingStatus=Online.
"""
from pathlib import Path
from strands import Agent, tool
from strands_tools import use_aws

# Import shared utilities
from shared.config import get_small_model
from shared.observability import get_callback
from shared.resource_tags import get_workload_tags

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

@tool
def systems_manager_inventory_analysis_agent(query: str) -> str:
    """
    Analyze AWS Systems Manager inventory data to catalog what software,
    applications, and configurations are installed on online EC2 instances only.
    
    Args:
        query: Inventory request for Systems Manager data from online EC2 instances
        
    Returns:
        Detailed inventory report of installed software, services, and configurations on online EC2 instances
    """
    try:
        # Create the Systems Manager inventory analysis agent
        agent = Agent(
            model=get_small_model(),
            tools=[
                use_aws,
                get_workload_tags
            ],
            system_prompt=SYSTEM_PROMPT,
            callback_handler=get_callback("ssm-inventory-analysis")
        )
        
        # Execute the analysis
        response = agent(query)
        return str(response.message)
        
    except Exception as e:
        import traceback
        error_details = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc()
        }
        return f"Error in Systems Manager inventory analysis: {error_details['error_message']}\n\nError Type: {error_details['error_type']}\n\nFull traceback available in logs."

# Example usage function for testing
def run_example():
    """Example usage of the Systems Manager inventory analysis agent."""
    example_queries = [
        "Provide a complete inventory of all software installed on online EC2 instances",
        "List all applications and their versions across online EC2 instances only",
        "Report on all running services and their configurations on online EC2 instances",
        "Catalog all installed packages and components on online EC2 instances"
    ]
    
    print("Available example queries:")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    
    # Use the first example by default
    query = example_queries[0]
    print(f"\nRunning example: {query}")
    
    return systems_manager_inventory_analysis_agent(query)

if __name__ == "__main__":
    # Run the example
    result = run_example()
    print(result)