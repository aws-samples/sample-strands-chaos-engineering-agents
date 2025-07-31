"""
Hypothesis Evaluator Agent

Evaluates the quality of chaos engineering hypotheses using LLM Judge Evaluation pattern.
"""
from pathlib import Path
from strands import Agent, tool
import json
import logging

# Import shared tools
from shared.hypotheses import get_hypotheses
from shared.config import get_default_model
from shared.observability import get_callback

# Import evaluation database tools
from shared.hypothesis_evaluations import (
    insert_hypothesis_evaluation,
    get_hypothesis_evaluations,
    batch_insert_hypothesis_evaluations
)

# Set up logging
logger = logging.getLogger(__name__)

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

@tool
def hypothesis_evaluator_agent(query: str) -> str:
    """
    Evaluate the quality of chaos engineering hypotheses.
    
    Args:
        query: A request to evaluate hypotheses, can include filters like:
              - hypothesis_ids: List of specific hypothesis IDs to evaluate
              - status_filter: Filter by status (e.g., 'proposed', 'prioritized')
              - limit: Maximum number of hypotheses to evaluate
        
    Returns:
        Evaluation results with quality scores for each hypothesis
    """
    try:
        # Parse the query to extract filters
        try:
            query_params = json.loads(query)
        except json.JSONDecodeError:
            # If not valid JSON, use the query as a simple message
            query_params = {"message": query}
        
        # Extract filters for hypothesis retrieval
        hypothesis_ids = query_params.get("hypothesis_ids")
        status_filter = query_params.get("status_filter")
        limit = query_params.get("limit", 10)  # Default to 10 hypotheses
        
        # Get the model ID
        model_id = get_default_model()
        logger.info(f"Using model: {model_id}")
        
        # Define the tools to use
        tools = [
            get_hypotheses,
            insert_hypothesis_evaluation,
            get_hypothesis_evaluations,
            batch_insert_hypothesis_evaluations
        ]
        
        # Create the callback handler
        callback = get_callback("hypothesis-evaluator")
        
        # Create the evaluator agent
        try:
            # Try with the standard constructor
            evaluator = Agent(
                model=model_id,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
                callback_handler=callback
            )
        except TypeError as e:
            logger.warning(f"Standard constructor failed: {e}")
            # Try with a different constructor signature
            evaluator = Agent(
                model_id,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
                callback_handler=callback
            )
        
        # Construct the evaluation request
        evaluation_request = {
            "action": "evaluate_hypotheses",
            "hypothesis_ids": hypothesis_ids,
            "status_filter": status_filter,
            "limit": limit
        }
        
        # Get response from the evaluator agent
        response = evaluator(json.dumps(evaluation_request))
        return str(response.message)
        
    except Exception as e:
        logger.error(f"Error in hypothesis evaluation: {str(e)}")
        return f"Error in hypothesis evaluation: {str(e)}"
