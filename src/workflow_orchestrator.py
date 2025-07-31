"""
Chaos Agent Workflow Orchestrator

This module implements the workflow pattern using AWS Strands to orchestrate
the execution of specialized chaos engineering agents in sequence.
"""

from strands import Agent
from strands_tools import workflow, file_read, use_aws, python_repl
from shared.config import get_aws_region, get_default_model
from shared.resource_tags import set_workload_tags_from_string
from shared.observability import get_callback, get_logger


# Import agents
from HypothesisGeneratorAgent.agent import agent as hypothesis_agent
from HypothesisPrioritizationAgent.agent import agent as prioritization_agent
from ExperimentDesignAgent.agent import agent as design_agent
from ExperimentsAgent.agent import agent as experiments_agent
from LearningAndIterationAgent.agent import agent as learning_agent

# Use centralized configuration without modifying environment

# Create a workflow agent
workflow_agent = Agent(
    model=get_default_model(),
    tools=[workflow, file_read, use_aws, python_repl],
    system_prompt="You are a chaos engineering workflow coordinator that orchestrates the execution of specialized agents for testing AWS workload resilience.",
    callback_handler=get_callback("chaos-workflow")
)

def run_chaos_workflow(workload_repo=None, region=None, tags=None, top_experiments=3, verbose=False):
    """
    Execute the complete chaos engineering workflow using the workflow pattern.
    
    Args:
        workload_repo (str, optional): Repository URL for the workload to analyze.
                                      Defaults to AWS Retail Store Sample App.
        region (str, optional): AWS region where resources are deployed. If None, uses centralized config.
        tags (str, optional): Tag string for resource filtering.
                             Format: "Environment=prod,Application=web-app"
        top_experiments (int, optional): Number of top priority experiments to execute. Defaults to 3.
        verbose (bool, optional): Enable verbose logging. Defaults to False.
    
    Returns:
        dict: The workflow results including all outputs from each step
    """
    # Use centralized region configuration if not provided
    if region is None:
        region = get_aws_region()
    
    # Set workload tags if provided
    if tags:
        set_workload_tags_from_string(tags)
    
    # Get workflow logger
    logger = get_logger("workflow")
    logger.info("Starting chaos engineering workflow", extra={
        'workload_repo': workload_repo,
        'region': region,
        'tags': tags,
        'top_experiments': top_experiments
    })
    
    # Set default workload if not provided
    if not workload_repo:
        workload_repo = "https://github.com/aws-containers/retail-store-sample-app.git"
    
    # Define the workflow steps with dynamic inputs
    chaos_workflow = [
            {
                "name": "hypothesis_generation",
                "description": "Generate chaos engineering hypotheses by analyzing the AWS workload",
                "agent": "src.HypothesisGeneratorAgent.agent",
                "input": f"""
Analyze the AWS workload repository ({workload_repo}).
""",
                "output_key": "hypotheses"
            },
            {
                "name": "hypothesis_prioritization",
                "description": "Prioritize the generated hypotheses based on impact and feasibility",
                "agent": "src.HypothesisPrioritizationAgent.agent",
                "input": """
Prioritize all hypotheses in the database based on:

1. Business impact (customer experience, revenue impact)
2. Technical feasibility (ease of testing, resource requirements)
3. Risk level (blast radius, recovery time)
4. Learning value (insights gained from the experiment)

Update each hypothesis with a priority ranking from 1 to N (1 = highest priority).
Focus on experiments that provide maximum learning with acceptable risk.
""",
                "output_key": "prioritized_hypotheses"
            },
            {
                "name": "experiment_design",
                "description": "Design AWS FIS experiments based on the prioritized hypotheses",
                "agent": "src.ExperimentDesignAgent.agent",
                "input": """
Retrieve all hypotheses from the database (ordered by priority) and create experiment designs for each.
Make sure to look up the latest documentation for each experiment type.

1. Focus on the highest priority hypotheses first
2. Create a production-ready FIS experiment template for each
3. Save the experiment to the database using insert_experiment
4. Include both FIS configuration and IAM role configuration
5. Consider the priority ranking when designing experiments

Start with the top 10 highest priority hypotheses.
""",
                "output_key": "experiment_designs"
            },
            {
                "name": "fis_setup",
                "description": "Set up all experiments in AWS FIS",
                "agent": "src.ExperimentsAgent.agent",
                "input": f"""
Set up AWS FIS experiments for the workload:

1. Get all draft experiments from the database using get_experiments
2. For each experiment, discover AWS resources and create FIS experiments
3. Update experiment status to 'created' when successfully set up
4. I have my app deployed in {region} region
5. Prioritize setting up experiments based on their hypothesis priority

Focus on creating real, executable FIS experiments in AWS.
""",
                "output_key": "fis_setup_results"
            },
            {
                "name": "experiment_execution",
                "description": "Execute selected experiments and monitor results",
                "agent": "src.ExperimentsAgent.agent",
                "input": f"""
Execute chaos engineering experiments for the workload:

EXECUTION PLAN:
1. Get the top {top_experiments} highest priority experiments from the database that have status 'created'
2. For each experiment:
   a. Display experiment details (name, hypothesis, expected impact)
   b. Execute the experiment using AWS FIS start_experiment
   c. Monitor experiment progress with detailed status updates
   d. Wait for completion (completed, failed, or stopped)
   e. Capture execution results, duration, and any failure details
   f. Update database with final status and results
3. Provide a summary of all executed experiments

EXECUTION REQUIREMENTS:
- Execute experiments sequentially (one at a time)
- Wait for each experiment to complete before starting the next
- Capture detailed execution logs and timing information
- Update database status throughout the process
- Handle any execution failures gracefully
- Provide clear status updates for each step

SAFETY MEASURES:
- Verify experiment targets before execution
- Monitor for any unexpected behavior
- Capture stop reasons if experiments are terminated
- Log all AWS FIS API responses

Execute experiments safely and provide detailed progress updates.
""",
                "output_key": "execution_results"
            },
            {
                "name": "results_analysis",
                "description": "Analyze experiment results and generate insights",
                "agent": "src.LearningAndIterationAgent.agent",
                "input": """
Analyze and summarize the results of executed chaos engineering experiments:

ANALYSIS TASKS:
1. Get all experiments from the database with status 'completed', 'failed', or 'stopped'
2. For each executed experiment:
   a. Display experiment name and hypothesis
   b. Show execution status and duration
   c. Analyze any failure patterns or unexpected behaviors
   d. Extract key learnings and insights
3. Provide overall summary of chaos engineering results
4. Recommend next steps based on findings

REPORTING FORMAT:
- Clear experiment-by-experiment breakdown
- Success/failure rates and patterns
- Key insights and learnings discovered
- Recommendations for system improvements
- Suggestions for follow-up experiments

Focus on actionable insights that can improve system resilience.
""",
                "output_key": "insights"
            }
    ]
    
    # Execute the workflow
    result = workflow_agent(
        f"""
        Execute a complete chaos engineering workflow for the workload at {workload_repo}.
        The workflow should analyze the application architecture, generate and prioritize hypotheses,
        design and execute experiments using AWS FIS, and provide actionable insights for improving resilience.
        
        Follow these steps in sequence:
        1. Generate hypotheses from the workload repository
        2. Prioritize hypotheses based on impact and feasibility
        3. Create experiments for prioritized hypotheses
        4. Set up all experiments in AWS FIS (region: {region})
        5. Execute selected experiments (top {top_experiments})
        6. Review experiment results and generate insights
        """, 
        workflow_steps=chaos_workflow
    )
    
    return result

if __name__ == "__main__":
    # Example usage
    run_chaos_workflow()
